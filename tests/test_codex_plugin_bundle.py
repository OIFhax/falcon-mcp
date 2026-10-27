"""Local marketplace bundles include runtime source and exclude operator data."""

import json

import pytest

from scripts.build_codex_plugin import REQUIRED_FILES, build_bundle


@pytest.fixture
def source_repo(tmp_path):
    root = tmp_path / "source"
    for relative in REQUIRED_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("runtime metadata\n")
    (root / ".codex-plugin/plugin.json").write_text(
        json.dumps({"name": "falcon-mcp", "mcpServers": "./.mcp.json"})
    )
    (root / ".mcp.json").write_text(
        json.dumps({"mcpServers": {"falcon": {"cwd": ".", "command": "uv"}}})
    )
    for relative in (
        "falcon_mcp/__init__.py",
        "falcon_mcp/codex_plugin.py",
        "falcon_mcp/modules/__init__.py",
        "falcon_mcp/modules/hosts.py",
        "docs/deployment/codex-plugin.md",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# runtime source\n")
    return root


def test_bundle_resolves_to_a_self_contained_local_plugin(source_repo, tmp_path):
    output = tmp_path / "bundle with spaces"
    assert build_bundle(output, source_repo) == output
    marketplace = json.loads((output / ".agents/plugins/marketplace.json").read_text())
    source = marketplace["plugins"][0]["source"]
    assert source == {"source": "local", "path": "./plugins/falcon-mcp"}
    plugin_root = output / source["path"]
    manifest = json.loads((plugin_root / ".codex-plugin/plugin.json").read_text())
    assert (plugin_root / manifest["mcpServers"]).is_file()
    for relative in (
        *REQUIRED_FILES,
        "falcon_mcp/codex_plugin.py",
        "falcon_mcp/modules/hosts.py",
        "docs/deployment/codex-plugin.md",
    ):
        assert (plugin_root / relative).read_bytes() == (source_repo / relative).read_bytes()


def test_bundle_does_not_copy_local_secrets_environments_or_evidence(source_repo, tmp_path):
    excluded = (
        ".env",
        ".env.production",
        ".git/config",
        ".venv/lib/local.py",
        "evidence/private.json",
        "reports/private.json",
        "codex.json",
        "falcon_mcp/.env",
        "falcon_mcp/credentials.json",
        "falcon_mcp/__pycache__/codex_plugin.pyc",
        "falcon_mcp/.venv/private.py",
        "falcon_mcp/.git/private.py",
    )
    for relative in excluded:
        path = source_repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("operator-secret-sentinel")
    output = build_bundle(tmp_path / "bundle", source_repo)
    for path in output.rglob("*"):
        if path.is_file():
            assert "operator-secret-sentinel" not in path.read_text()
    for relative in excluded:
        assert not (output / "plugins/falcon-mcp" / relative).exists()


def test_existing_output_is_preserved(source_repo, tmp_path):
    output = tmp_path / "already-exists"
    output.mkdir()
    sentinel = output / "user-file.txt"
    sentinel.write_text("keep me")
    with pytest.raises(FileExistsError):
        build_bundle(output, source_repo)
    assert sentinel.read_text() == "keep me"
    assert list(output.iterdir()) == [sentinel]


def test_missing_runtime_file_fails_before_creating_output(source_repo, tmp_path):
    (source_repo / "uv.lock").unlink()
    output = tmp_path / "incomplete-bundle"
    with pytest.raises(ValueError, match="regular file"):
        build_bundle(output, source_repo)
    assert not output.exists()


def test_symlink_cannot_import_external_content(source_repo, tmp_path):
    private = tmp_path / "private.py"
    private.write_text("operator-secret-sentinel")
    (source_repo / "falcon_mcp/external.py").symlink_to(private)
    output = tmp_path / "unsafe-bundle"
    with pytest.raises(ValueError, match="regular file"):
        build_bundle(output, source_repo)
    assert not output.exists()
