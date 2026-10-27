"""Credential isolation and startup contracts for the Codex stdio plugin."""

import os
import stat
from pathlib import Path
from unittest.mock import Mock

import pytest

from falcon_mcp import codex_plugin, server

STORED_CREDENTIALS = {
    "FALCON_CLIENT_ID": "stored-client-id",
    "FALCON_CLIENT_SECRET": "stored-client-secret",
}


@pytest.fixture
def config_file(tmp_path, monkeypatch):
    """Isolate tests from both operator credentials and persistent user config."""
    for key in codex_plugin.CONFIG_KEYS:
        monkeypatch.delenv(key, raising=False)
    for key in (
        "FALCON_MCP_TRANSPORT",
        "FALCON_MCP_PORT",
        "FALCON_MCP_HOST",
        "FALCON_MCP_STATELESS_HTTP",
        "FALCON_MCP_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    path = tmp_path / "private" / "codex.json"
    monkeypatch.setenv("FALCON_MCP_CONFIG_FILE", str(path))
    return path


@pytest.mark.parametrize(
    "stored",
    [
        {},
        {"FALCON_CLIENT_ID": "id"},
        {"FALCON_CLIENT_SECRET": "secret"},
        {"FALCON_CLIENT_ID": " ", "FALCON_CLIENT_SECRET": "secret"},
        {"FALCON_CLIENT_ID": "id", "FALCON_CLIENT_SECRET": "\t"},
    ],
)
def test_missing_or_blank_credentials_fail_before_server_start(
    stored, config_file, monkeypatch, capsys
):
    codex_plugin.save_config(config_file, stored)
    start = Mock()
    monkeypatch.setattr(server, "main", start)

    with pytest.raises(SystemExit) as failure:
        codex_plugin.main([])

    assert failure.value.code == 1
    start.assert_not_called()
    output = capsys.readouterr()
    assert output.out == ""
    assert "Falcon API credentials are required" in output.err


@pytest.mark.parametrize("key", codex_plugin.CREDENTIAL_KEYS)
def test_environment_cannot_supply_half_a_credential_pair(key):
    with pytest.raises(codex_plugin.ConfigurationError, match="Set both"):
        codex_plugin.resolve_settings(STORED_CREDENTIALS, {key: "different-tenant"})


def test_environment_overrides_the_full_pair_and_optional_settings():
    settings = codex_plugin.resolve_settings(
        {**STORED_CREDENTIALS, "FALCON_MEMBER_CID": "stored-cid"},
        {
            "FALCON_CLIENT_ID": "override-id",
            "FALCON_CLIENT_SECRET": "override-secret",
            "FALCON_MEMBER_CID": "override-cid",
            "UNRELATED_KEY": "ignored",
        },
    )
    assert settings == {
        "FALCON_CLIENT_ID": "override-id",
        "FALCON_CLIENT_SECRET": "override-secret",
        "FALCON_MEMBER_CID": "override-cid",
    }


def test_blank_environment_secret_does_not_fall_back_to_stored_credentials():
    with pytest.raises(codex_plugin.ConfigurationError, match="required"):
        codex_plugin.resolve_settings(
            STORED_CREDENTIALS, {"FALCON_CLIENT_ID": "new-id", "FALCON_CLIENT_SECRET": " "}
        )


def test_default_config_path_is_independent_of_working_directory(tmp_path, monkeypatch):
    monkeypatch.delenv("FALCON_MCP_CONFIG_FILE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "user")
    monkeypatch.chdir(tmp_path)
    assert codex_plugin.config_path() == tmp_path / "user" / ".config/falcon-mcp/codex.json"


@pytest.mark.parametrize("path", ["", "codex.json", "~/codex.json"])
def test_config_override_requires_absolute_path(path, monkeypatch):
    monkeypatch.setenv("FALCON_MCP_CONFIG_FILE", path)
    with pytest.raises(codex_plugin.ConfigurationError, match="absolute"):
        codex_plugin.config_path()


@pytest.mark.parametrize(
    "contents",
    ["{bad JSON secret-value", "[]", '{"UNKNOWN": "secret-value"}', '{"FALCON_CLIENT_ID": 1}'],
)
def test_invalid_config_never_reports_its_values(contents, config_file):
    config_file.parent.mkdir()
    config_file.write_text(contents)
    with pytest.raises(codex_plugin.ConfigurationError) as failure:
        codex_plugin.read_config(config_file)
    assert "secret-value" not in str(failure.value)


def test_configure_uses_hidden_credentials_and_preserves_optional_settings(
    config_file, monkeypatch, capsys
):
    codex_plugin.save_config(
        config_file,
        {**STORED_CREDENTIALS, "FALCON_MCP_MODULES": "hosts", "FALCON_MEMBER_CID": "child"},
    )
    prompt = Mock(side_effect=["new-client-id", "new-client-secret"])
    monkeypatch.setattr(codex_plugin.getpass, "getpass", prompt)
    monkeypatch.setattr("builtins.input", lambda: "https://api.us-2.crowdstrike.com")

    codex_plugin.main(["--configure"])

    settings = codex_plugin.read_config(config_file)
    assert settings == {
        "FALCON_CLIENT_ID": "new-client-id",
        "FALCON_CLIENT_SECRET": "new-client-secret",
        "FALCON_BASE_URL": "https://api.us-2.crowdstrike.com",
        "FALCON_MCP_MODULES": "hosts",
        "FALCON_MEMBER_CID": "child",
    }
    assert prompt.call_count == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert str(config_file) in output.err
    assert "new-client-id" not in output.err
    assert "new-client-secret" not in output.err


@pytest.mark.skipif(os.name == "nt", reason="POSIX permissions")
def test_new_config_directory_and_file_are_private(config_file):
    codex_plugin.save_config(config_file, STORED_CREDENTIALS)
    assert stat.S_IMODE(config_file.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(config_file.stat().st_mode) == 0o600
    config_file.chmod(0o644)
    codex_plugin.save_config(config_file, STORED_CREDENTIALS)
    assert stat.S_IMODE(config_file.stat().st_mode) == 0o600


@pytest.mark.parametrize("failure", [EOFError(), KeyboardInterrupt()])
def test_interrupted_prompt_preserves_existing_config(config_file, monkeypatch, failure):
    codex_plugin.save_config(config_file, STORED_CREDENTIALS)
    original = config_file.read_bytes()
    monkeypatch.setattr(codex_plugin.getpass, "getpass", Mock(side_effect=["new-id", failure]))

    with pytest.raises(SystemExit):
        codex_plugin.main(["--configure"])

    assert config_file.read_bytes() == original
    assert list(config_file.parent.iterdir()) == [config_file]


def test_failed_atomic_replace_preserves_existing_config(config_file, monkeypatch):
    codex_plugin.save_config(config_file, STORED_CREDENTIALS)
    original = config_file.read_bytes()
    monkeypatch.setattr(codex_plugin.os, "replace", Mock(side_effect=OSError("synthetic failure")))

    with pytest.raises(codex_plugin.ConfigurationError, match="Could not save"):
        codex_plugin.save_config(config_file, {**STORED_CREDENTIALS, "FALCON_MEMBER_CID": "new"})

    assert config_file.read_bytes() == original
    assert list(config_file.parent.iterdir()) == [config_file]


def test_setup_refuses_echoed_getpass_fallback(config_file, monkeypatch):
    def fallback_prompt(prompt):
        codex_plugin.warnings.warn("Echoed input", codex_plugin.getpass.GetPassWarning)
        pytest.fail("The warning must stop input before it can be echoed")

    monkeypatch.setattr(codex_plugin.getpass, "getpass", fallback_prompt)
    with pytest.raises(SystemExit) as failure:
        codex_plugin.main(["--configure"])
    assert failure.value.code == 1
    assert not config_file.exists()


def test_offline_check_does_not_contact_falcon_or_disclose_credentials(
    config_file, monkeypatch, capsys
):
    codex_plugin.save_config(config_file, STORED_CREDENTIALS)
    start = Mock()
    monkeypatch.setattr(server, "main", start)
    codex_plugin.main(["--check-config"])
    start.assert_not_called()
    output = capsys.readouterr()
    assert output.out == ""
    assert "API connectivity has not been checked" in output.err
    for value in STORED_CREDENTIALS.values():
        assert value not in output.err


def test_plugin_reuses_runtime_with_stdio_and_never_loads_dotenv(
    config_file, monkeypatch, tmp_path
):
    codex_plugin.save_config(
        config_file,
        {**STORED_CREDENTIALS, "FALCON_MCP_MODULES": "hosts", "FALCON_MCP_READ_ONLY": "true"},
    )
    (tmp_path / ".env").write_text("FALCON_CLIENT_SECRET=unwanted-workspace-secret\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FALCON_MCP_TRANSPORT", "streamable-http")
    monkeypatch.setenv("FALCON_MCP_PORT", "invalid-http-only-port")
    load_dotenv = Mock(side_effect=AssertionError("Plugin must not discover .env files"))
    instance = Mock()
    constructor = Mock(return_value=instance)
    monkeypatch.setattr(server, "load_dotenv", load_dotenv)
    monkeypatch.setattr(server, "FalconMCPServer", constructor)
    monkeypatch.setattr(server.registry, "get_module_names", lambda: ["hosts"])

    codex_plugin.main([])

    load_dotenv.assert_not_called()
    instance.run.assert_called_once_with("stdio")
    assert constructor.call_args.kwargs["enabled_modules"] == {"hosts"}
    assert constructor.call_args.kwargs["read_only"] is True
    assert os.environ["FALCON_MCP_TRANSPORT"] == "streamable-http"
    assert "FALCON_CLIENT_SECRET" not in os.environ


def test_workspace_dotenv_cannot_supply_missing_credentials(
    config_file, monkeypatch, tmp_path
):
    (tmp_path / ".env").write_text(
        "FALCON_CLIENT_ID=unwanted-id\nFALCON_CLIENT_SECRET=unwanted-secret\n"
    )
    monkeypatch.chdir(tmp_path)
    start = Mock()
    monkeypatch.setattr(server, "main", start)
    with pytest.raises(SystemExit) as failure:
        codex_plugin.main([])
    assert failure.value.code == 1
    start.assert_not_called()


def test_authentication_failure_exits_without_running_server(config_file, monkeypatch):
    codex_plugin.save_config(config_file, STORED_CREDENTIALS)
    client = Mock()
    client.authenticate.return_value = False
    client.auth_failure_message.return_value = "Failed to authenticate with the Falcon API (HTTP 401)"
    monkeypatch.setattr(server, "FalconClient", Mock(return_value=client))
    monkeypatch.setattr(server.registry, "get_module_names", lambda: [])
    mcp = Mock()
    monkeypatch.setattr(server, "FastMCP", mcp)

    with pytest.raises(SystemExit) as failure:
        codex_plugin.main([])

    assert failure.value.code == 1
    client.authenticate.assert_called_once()
    mcp.assert_not_called()


def test_command_line_does_not_accept_or_echo_secrets(capsys):
    with pytest.raises(SystemExit) as failure:
        codex_plugin.main(["--client-secret", "do-not-display-this-value"])
    assert failure.value.code == 2
    output = capsys.readouterr()
    assert "do-not-display-this-value" not in output.out + output.err


def test_existing_server_cli_keeps_dotenv_behavior(config_file, monkeypatch):
    load_dotenv = Mock()
    instance = Mock()
    monkeypatch.setattr(server, "load_dotenv", load_dotenv)
    monkeypatch.setattr(server, "FalconMCPServer", Mock(return_value=instance))
    monkeypatch.setattr(server.registry, "get_module_names", lambda: [])
    monkeypatch.setattr(server, "parse_args", Mock(return_value=server.parse_args([])))

    server.main([])

    load_dotenv.assert_called_once_with()
