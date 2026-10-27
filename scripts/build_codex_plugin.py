"""Build a self-contained local Codex marketplace without copying user data."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REQUIRED_FILES = (
    ".codex-plugin/plugin.json",
    ".mcp.json",
    "pyproject.toml",
    "uv.lock",
    "README.md",
    "LICENSE",
)
OPTIONAL_FILES = ("docs/deployment/codex-plugin.md",)
EXCLUDED_DIRECTORIES = frozenset({"__pycache__", "evidence", "reports", "venv"})


def _runtime_files(repo_root: Path) -> list[Path]:
    """Select an explicit metadata allow-list and Python source files only."""
    files = [repo_root / name for name in REQUIRED_FILES]
    files.extend(repo_root / name for name in OPTIONAL_FILES if (repo_root / name).exists())
    package = repo_root / "falcon_mcp"
    if not (package / "__init__.py").is_file():
        raise ValueError("The source repository is missing the falcon_mcp package.")
    for source in sorted(package.rglob("*.py")):
        relative = source.relative_to(package)
        if any(part.startswith(".") or part in EXCLUDED_DIRECTORIES for part in relative.parts):
            continue
        files.append(source)
    for source in files:
        if (
            not source.is_file()
            or source.is_symlink()
            or not source.resolve().is_relative_to(repo_root)
        ):
            raise ValueError(
                f"Required bundle source must be a regular file inside the repository: "
                f"{source.relative_to(repo_root)}"
            )
    return files


def build_bundle(output: Path, repo_root: Path | None = None) -> Path:
    """Create a new local marketplace directory; never replace an existing path."""
    source_root = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    files = _runtime_files(source_root)
    output = output.absolute()
    # exist_ok=False protects all existing files, directories, and symlink paths.
    output.mkdir(parents=True, exist_ok=False)
    plugin_root = output / "plugins" / "falcon-mcp"
    for source in files:
        destination = plugin_root / source.relative_to(source_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    marketplace = {
        "name": "falcon-mcp",
        "interface": {"displayName": "Falcon MCP"},
        "plugins": [
            {
                "name": "falcon-mcp",
                "source": {"source": "local", "path": "./plugins/falcon-mcp"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Security",
            }
        ],
    }
    marketplace_file = output / ".agents" / "plugins" / "marketplace.json"
    marketplace_file.parent.mkdir(parents=True)
    marketplace_file.write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> None:
    """Build a marketplace suitable for `codex plugin marketplace add PATH`."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new bundle directory to create")
    args = parser.parse_args()
    try:
        output = build_bundle(args.output)
    except FileExistsError:
        parser.exit(1, "Output already exists. Choose a new directory; existing files were preserved.\n")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Could not build the Falcon MCP plugin bundle: {exc}\n")
    print(f"Built local Falcon MCP marketplace: {output}")
    print(f"Add it with: codex plugin marketplace add \"{output}\"")


if __name__ == "__main__":
    main()
