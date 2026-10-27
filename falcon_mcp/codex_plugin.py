"""Docker-free Codex entrypoint with explicit, user-owned Falcon credentials."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import tempfile
import warnings
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import NoReturn

CREDENTIAL_KEYS = ("FALCON_CLIENT_ID", "FALCON_CLIENT_SECRET")
CONFIG_KEYS = frozenset(
    {
        *CREDENTIAL_KEYS,
        "FALCON_BASE_URL",
        "FALCON_MEMBER_CID",
        "FALCON_PROXY_URL",
        "FALCON_MCP_MODULES",
        "FALCON_MCP_DEBUG",
        "FALCON_MCP_USER_AGENT_COMMENT",
        "FALCON_MCP_DYNAMIC",
        "FALCON_MCP_READ_ONLY",
        "FALCON_MCP_TOOLS",
        "FALCON_MCP_EXCLUDE_TOOLS",
        "FALCON_MCP_HTTP_TIMEOUT_SECONDS",
        "FALCON_MCP_RTR_HTTP_TIMEOUT_SECONDS",
        "FALCON_MCP_RETRY_ATTEMPTS",
        "FALCON_MCP_RETRY_BACKOFF_SECONDS",
    }
)
DEFAULT_BASE_URL = "https://api.crowdstrike.com"


class ConfigurationError(ValueError):
    """A user-actionable configuration failure that does not expose its values."""


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        # argparse normally includes rejected argument values in its error message.
        super().error("Invalid arguments. Use --help; supply credentials with --configure.")


def config_path() -> Path:
    """Locate the persistent config independently of the current workspace."""
    override = os.environ.get("FALCON_MCP_CONFIG_FILE")
    if override is not None:
        path = Path(override)
        if not path.is_absolute():
            raise ConfigurationError("FALCON_MCP_CONFIG_FILE must be an absolute path.")
        return path
    return Path.home() / ".config" / "falcon-mcp" / "codex.json"


def read_config(path: Path) -> dict[str, str]:
    """Read only the explicitly selected JSON file; never discover .env files."""
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError, UnicodeError) as exc:
        raise ConfigurationError(
            "Cannot read the Falcon plugin configuration. Check its path and JSON format."
        ) from exc
    if not isinstance(data, dict) or any(
        key not in CONFIG_KEYS or not isinstance(value, str) for key, value in data.items()
    ):
        raise ConfigurationError(
            "Falcon plugin configuration must contain supported FALCON_* keys with string values."
        )
    return data


def resolve_settings(
    stored: Mapping[str, str], environment: Mapping[str, str]
) -> dict[str, str]:
    """Overlay environment settings without combining credentials from two sources."""
    if any(key in environment for key in CREDENTIAL_KEYS) and not all(
        key in environment for key in CREDENTIAL_KEYS
    ):
        raise ConfigurationError(
            "Set both FALCON_CLIENT_ID and FALCON_CLIENT_SECRET when overriding credentials."
        )
    settings = dict(stored)
    settings.update({key: environment[key] for key in CONFIG_KEYS if key in environment})
    if not all(settings.get(key, "").strip() for key in CREDENTIAL_KEYS):
        raise ConfigurationError(
            "Falcon API credentials are required: configure a client ID and client secret with "
            "--configure, or set both FALCON_CLIENT_ID and FALCON_CLIENT_SECRET."
        )
    return settings


def save_config(path: Path, settings: Mapping[str, str]) -> None:
    """Replace the credential file atomically, with private POSIX permissions."""
    temporary: Path | None = None
    try:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        descriptor, filename = tempfile.mkstemp(prefix=".codex-", suffix=".json", dir=path.parent)
        temporary = Path(filename)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            # mkstemp uses 0600; chmod also covers platforms with a permissive umask.
            os.chmod(temporary, 0o600)
            json.dump(dict(settings), handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        raise ConfigurationError("Could not save the Falcon plugin configuration.") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def configure(path: Path) -> None:
    """Prompt only when explicitly requested, retaining existing optional settings."""
    settings = read_config(path)
    print("Configure Falcon API credentials (client ID and client secret).", file=sys.stderr)
    try:
        with warnings.catch_warnings():
            # Refuse getpass's fallback to echoed input if no protected terminal is available.
            warnings.simplefilter("error", getpass.GetPassWarning)
            client_id = getpass.getpass("Falcon API client ID (hidden): ").strip()
            client_secret = getpass.getpass("Falcon API client secret (hidden): ").strip()
    except (EOFError, getpass.GetPassWarning) as exc:
        raise ConfigurationError(
            "Credential setup requires an interactive terminal with hidden input."
        ) from exc
    settings.update(zip(CREDENTIAL_KEYS, (client_id, client_secret)))
    resolve_settings(settings, {})
    default_url = settings.get("FALCON_BASE_URL") or DEFAULT_BASE_URL
    print(f"Falcon API base URL [{default_url}]: ", end="", file=sys.stderr, flush=True)
    try:
        settings["FALCON_BASE_URL"] = input().strip() or default_url
    except EOFError as exc:
        raise ConfigurationError("Configuration cancelled before saving.") from exc
    save_config(path, settings)
    print(f"Saved Falcon plugin configuration to {path}", file=sys.stderr)


@contextmanager
def _runtime_environment(settings: Mapping[str, str]) -> Iterator[None]:
    # HTTP-only environment values cannot affect this stdio child process.
    overrides = {
        **settings,
        "FALCON_MCP_TRANSPORT": "stdio",
        "FALCON_MCP_HOST": "127.0.0.1",
        "FALCON_MCP_PORT": "8000",
        "FALCON_MCP_STATELESS_HTTP": "false",
        "FALCON_MCP_API_KEY": "",
    }
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        os.environ.update(overrides)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main(argv: list[str] | None = None) -> None:
    """Configure, inspect, or start the plugin without exposing secrets in arguments."""
    parser = _ArgumentParser(
        description="Falcon MCP Codex plugin (stdio; no Docker required)",
        epilog="Runtime options use the existing FALCON_* environment or JSON settings.",
        allow_abbrev=False,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--configure", action="store_true", help="save credentials using hidden prompts")
    mode.add_argument(
        "--check-config", action="store_true", help="validate local credentials without contacting Falcon"
    )
    args = parser.parse_args(argv)
    try:
        path = config_path()
        if args.configure:
            configure(path)
            return
        settings = resolve_settings(read_config(path), os.environ)
        if args.check_config:
            print(
                "Falcon plugin configuration is valid. Credentials are present; "
                "API connectivity has not been checked.",
                file=sys.stderr,
            )
            return
        # Keep configuration and credential validation independent of MCP dependencies.
        from falcon_mcp.server import main as server_main

        with _runtime_environment(settings):
            server_main(["--transport", "stdio"], load_env=False)
    except ConfigurationError as exc:
        print(f"Falcon plugin: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
    except KeyboardInterrupt:
        print("Falcon plugin: cancelled.", file=sys.stderr)
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()
