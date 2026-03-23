"""
Falcon API Client for MCP Server

This module provides the Falcon API client and authentication utilities for the Falcon MCP server.
"""

import contextvars
import os
import platform
import sys
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from time import sleep
from typing import Any
from urllib.parse import urlparse

# Import the APIHarnessV2 from FalconPy
from falconpy import APIHarnessV2  # type: ignore[import-untyped]
from requests.exceptions import Timeout as RequestsTimeout

from falcon_mcp.common.logging import get_logger

logger = get_logger(__name__)

DEFAULT_TOOL_IO_HISTORY_LIMIT = 200
DEFAULT_RETRY_ATTEMPTS = 1
DEFAULT_RETRY_BACKOFF_SECONDS = 0.5
DEFAULT_RTR_HTTP_TIMEOUT_SECONDS = 15.0
TRANSIENT_STATUS_CODES = frozenset({500, 502, 503, 504})
RETRYABLE_OPERATIONS = frozenset(
    {
        "RTR_InitSession",
        "BatchInitSessions",
        "BatchRefreshSessions",
        "RTR_PulseSession",
    }
)
TRACE_ID_KEYS = frozenset(
    {
        "trace_id",
        "traceid",
        "x-cs-traceid",
        "x-cs-trace-id",
        "x-cs-requestid",
        "request_id",
    }
)
TARGET_DEVICE_ID_KEYS = frozenset(
    {
        "device_id",
        "host_id",
        "host_ids",
        "optional_hosts",
        "hosts_to_remove",
        "aid",
        "aids",
    }
)
_TOOL_CONTEXT: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar(
    "falcon_mcp_tool_context",
    default=None,
)


def _get_int_env(name: str, default: int) -> int:
    """Read an integer environment variable with safe fallback."""
    value = os.environ.get(name)
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        logger.warning("Invalid integer value for %s=%r; using default %d", name, value, default)
        return default


def _get_float_env(name: str, default: float) -> float:
    """Read a float environment variable with safe fallback."""
    value = os.environ.get(name)
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        logger.warning("Invalid float value for %s=%r; using default %.2f", name, value, default)
        return default


def _get_timeout_env(name: str, default: float | None) -> float | None:
    """Read a positive timeout value from the environment."""
    value = os.environ.get(name)
    if value in (None, ""):
        return default

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        logger.warning(
            "Invalid timeout value for %s=%r; using default %s",
            name,
            value,
            default,
        )
        return default

    if parsed <= 0:
        logger.warning(
            "Non-positive timeout value for %s=%r; using default %s",
            name,
            value,
            default,
        )
        return default

    return parsed


def _utc_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


class FalconClient:
    """Client for interacting with the CrowdStrike Falcon API."""

    def __init__(
        self,
        base_url: str | None = None,
        debug: bool = False,
        user_agent_comment: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        """Initialize the Falcon client.

        Args:
            base_url: Falcon API base URL (defaults to FALCON_BASE_URL env var)
            debug: Enable debug logging
            user_agent_comment: Additional information to include in the User-Agent comment section
            client_id: Falcon API Client ID (defaults to FALCON_CLIENT_ID env var)
            client_secret: Falcon API Client Secret (defaults to FALCON_CLIENT_SECRET env var)
        """
        # Get credentials from parameters or environment variables (parameters take precedence)
        self.client_id = client_id or os.environ.get("FALCON_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("FALCON_CLIENT_SECRET")
        self.base_url = base_url or os.environ.get(
            "FALCON_BASE_URL", "https://api.crowdstrike.com"
        )
        self.debug = debug
        self.user_agent_comment = user_agent_comment or os.environ.get(
            "FALCON_MCP_USER_AGENT_COMMENT"
        )
        self.http_timeout = _get_timeout_env("FALCON_MCP_HTTP_TIMEOUT_SECONDS", default=None)
        self.rtr_http_timeout = _get_timeout_env(
            "FALCON_MCP_RTR_HTTP_TIMEOUT_SECONDS",
            default=DEFAULT_RTR_HTTP_TIMEOUT_SECONDS,
        )
        self.max_retries = _get_int_env("FALCON_MCP_RETRY_ATTEMPTS", DEFAULT_RETRY_ATTEMPTS)
        self.retry_backoff_seconds = _get_float_env(
            "FALCON_MCP_RETRY_BACKOFF_SECONDS",
            DEFAULT_RETRY_BACKOFF_SECONDS,
        )
        self.tool_io_history: deque[dict[str, Any]] = deque(maxlen=DEFAULT_TOOL_IO_HISTORY_LIMIT)

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Falcon API credentials not provided. Either pass client_id and client_secret "
                "parameters or set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET environment variables."
            )

        self.client = self._build_api_client(timeout=self.http_timeout)
        self._rtr_client: APIHarnessV2 | None = None

        logger.debug("Initialized Falcon client with base URL: %s", self.base_url)

    def authenticate(self) -> bool:
        """Authenticate with the Falcon API.

        Returns:
            bool: True if authentication was successful
        """
        result: bool = self.client.login()
        return result

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated.

        Returns:
            bool: True if the client is authenticated
        """
        result: bool = self.client.token_valid
        return result

    @contextmanager
    def tool_context(
        self,
        tool_name: str,
        tool_parameters: dict[str, Any] | None = None,
    ):
        """Attach MCP tool context to downstream Falcon API calls."""
        token = _TOOL_CONTEXT.set(
            {
                "tool_name": tool_name,
                "tool_parameters": self._make_json_safe(tool_parameters or {}),
            }
        )
        try:
            yield
        finally:
            _TOOL_CONTEXT.reset(token)

    def command(self, operation: str, **kwargs: Any) -> dict[str, Any] | bytes:
        """Execute a Falcon API command.

        Args:
            operation: The API operation to execute
            **kwargs: Additional arguments to pass to the API

        Returns:
            dict[str, Any] | bytes: The API response
        """
        retry_attempts = self.max_retries if operation in RETRYABLE_OPERATIONS else 0
        api_client = self._get_operation_client(operation)

        for attempt in range(retry_attempts + 1):
            timestamp = _utc_timestamp()
            try:
                result = api_client.command(operation, **kwargs)
            except RequestsTimeout as exc:
                result = self._build_timeout_response(
                    operation=operation,
                    timeout_seconds=self._get_operation_timeout(operation),
                    exc=exc,
                )
            except Exception as exc:
                self._record_tool_io(
                    operation=operation,
                    parameters=kwargs,
                    timestamp=timestamp,
                    raw_response=None,
                    error_object={
                        "type": type(exc).__name__,
                        "message": str(exc),
                    },
                    attempt=attempt + 1,
                )
                raise

            self._record_tool_io(
                operation=operation,
                parameters=kwargs,
                timestamp=timestamp,
                raw_response=result,
                error_object=self._extract_error_object(result),
                attempt=attempt + 1,
            )

            if attempt < retry_attempts and self._should_retry(operation, result):
                backoff = self.retry_backoff_seconds * (2**attempt)
                logger.warning(
                    "Retrying Falcon operation %s after transient %s response (attempt %d/%d)",
                    operation,
                    result.get("status_code"),
                    attempt + 1,
                    retry_attempts + 1,
                )
                sleep(backoff)
                continue

            return result

        raise RuntimeError(f"Unexpected retry flow termination for operation {operation}")

    def get_user_agent(self) -> str:
        """Get RFC-compliant user agent string for API requests.

        Returns:
            str: User agent string in RFC format "falcon-mcp/VERSION (comment; falconpy/VERSION; Python/VERSION; Platform/VERSION)"
        """
        # Get falcon-mcp version
        falcon_mcp_version = get_version()

        # Get Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # Get platform information
        platform_info = f"{platform.system()}/{platform.release()}"

        # Get FalconPy version
        try:
            falconpy_version = version("crowdstrike-falconpy")
        except PackageNotFoundError:
            falconpy_version = "unknown"
            logger.debug("crowdstrike-falconpy package version not found")

        # Build comment section components (RFC-compliant format)
        comment_parts = []
        if self.user_agent_comment:
            comment_parts.append(self.user_agent_comment.strip())
        comment_parts.extend(
            [f"falconpy/{falconpy_version}", f"Python/{python_version}", platform_info]
        )

        return f"falcon-mcp/{falcon_mcp_version} ({'; '.join(comment_parts)})"

    def _build_api_client(self, timeout: float | None) -> APIHarnessV2:
        """Create a FalconPy client with the configured transport timeout."""
        return APIHarnessV2(
            client_id=self.client_id,
            client_secret=self.client_secret,
            base_url=self.base_url,
            debug=self.debug,
            user_agent=self.get_user_agent(),
            timeout=timeout,
        )

    def _get_operation_client(self, operation: str) -> APIHarnessV2:
        """Return the appropriate Falcon client for a given operation."""
        if operation not in RETRYABLE_OPERATIONS:
            return self.client

        if self.rtr_http_timeout == self.http_timeout:
            return self.client

        if self._rtr_client is None:
            self._rtr_client = self._build_api_client(timeout=self.rtr_http_timeout)

        return self._rtr_client

    def _get_operation_timeout(self, operation: str) -> float | None:
        """Return the configured HTTP timeout for an operation."""
        if operation in RETRYABLE_OPERATIONS and self.rtr_http_timeout != self.http_timeout:
            return self.rtr_http_timeout
        return self.http_timeout

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests.

        This method returns the authentication headers from the underlying Falcon API client,
        which can be used for custom HTTP requests or advanced integration scenarios.

        Returns:
            dict[str, str]: Authentication headers including the bearer token
        """
        headers: dict[str, str] = self.client.auth_headers
        return headers

    def get_region(self) -> str:
        """Derive the Falcon region hint from the configured base URL."""
        hostname = urlparse(self.base_url).hostname or ""
        host_parts = hostname.split(".")
        if len(host_parts) >= 4 and host_parts[0] == "api":
            return host_parts[1]
        return "default"

    def get_tool_io_history(
        self,
        limit: int = 20,
        tool_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent Falcon tool I/O history."""
        history = list(self.tool_io_history)
        if tool_name:
            history = [entry for entry in history if entry.get("tool_name") == tool_name]
        if limit > 0:
            history = history[-limit:]
        return history

    def generate_support_bundle(
        self,
        limit: int = 50,
        tool_name: str | None = None,
        device_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate a support bundle from preserved raw Falcon tool I/O."""
        requested_device_ids = set(device_ids or [])
        history = self.get_tool_io_history(limit=limit, tool_name=tool_name)

        if requested_device_ids:
            history = [
                entry
                for entry in history
                if requested_device_ids.intersection(entry.get("target_device_ids", []))
            ]

        return {
            "generated_at": _utc_timestamp(),
            "base_url": self.base_url,
            "region": self.get_region(),
            "tool_name_filter": tool_name,
            "device_id_filter": sorted(requested_device_ids),
            "trace_ids": sorted(
                {
                    trace_id
                    for entry in history
                    for trace_id in entry.get("trace_ids", [])
                }
            ),
            "tool_functions": [
                {
                    "tool_name": tool_name_value,
                    "falcon_operation": operation_value,
                }
                for tool_name_value, operation_value in sorted(
                    {
                        (
                            entry.get("tool_name"),
                            entry.get("falcon_operation"),
                        )
                        for entry in history
                    }
                )
            ],
            "timestamps": [entry["timestamp"] for entry in history],
            "target_device_ids": sorted(
                {
                    device_id
                    for entry in history
                    for device_id in entry.get("target_device_ids", [])
                }
            ),
            "entries": history,
        }

    def _build_timeout_response(
        self,
        operation: str,
        timeout_seconds: float | None,
        exc: RequestsTimeout,
    ) -> dict[str, Any]:
        """Convert a FalconPy timeout into a structured API-style response."""
        timeout_hint = (
            f" after {timeout_seconds:g} seconds" if timeout_seconds is not None else ""
        )
        message = f"Falcon API request timed out{timeout_hint} during {operation}"
        logger.warning(message)
        return {
            "status_code": 504,
            "body": {
                "errors": [
                    {
                        "message": message,
                    }
                ]
            },
            "meta": {
                "timed_out": True,
                "operation": operation,
                "configured_timeout_seconds": timeout_seconds,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            },
        }

    def _record_tool_io(
        self,
        operation: str,
        parameters: dict[str, Any],
        timestamp: str,
        raw_response: Any,
        error_object: dict[str, Any] | None,
        attempt: int,
    ) -> None:
        """Persist tool I/O details for grounding and support workflows."""
        tool_context = _TOOL_CONTEXT.get() or {}
        entry = {
            "tool_name": tool_context.get("tool_name"),
            "tool_parameters": tool_context.get("tool_parameters", {}),
            "falcon_operation": operation,
            "parameters": self._make_json_safe(parameters),
            "timestamp": timestamp,
            "attempt": attempt,
            "status_code": raw_response.get("status_code")
            if isinstance(raw_response, dict)
            else None,
            "raw_response": self._make_json_safe(raw_response),
            "error_object": self._make_json_safe(error_object),
            "trace_ids": self._extract_trace_ids(raw_response),
            "target_device_ids": self._extract_target_device_ids(
                tool_context.get("tool_parameters", {}),
                parameters,
                raw_response,
            ),
        }
        self.tool_io_history.append(entry)

    def _should_retry(self, operation: str, response: Any) -> bool:
        """Return True when the Falcon response is retryable."""
        if not isinstance(response, dict):
            return False
        status_code = response.get("status_code")
        return operation in RETRYABLE_OPERATIONS and status_code in TRANSIENT_STATUS_CODES

    def _extract_error_object(self, response: Any) -> dict[str, Any] | None:
        """Extract a compact error object from a Falcon response."""
        if not isinstance(response, dict):
            return None

        status_code = response.get("status_code")
        errors = response.get("body", {}).get("errors")
        if status_code is None and not errors:
            return None
        if status_code is not None and status_code < 400 and not errors:
            return None

        return {
            "status_code": status_code,
            "errors": self._make_json_safe(errors or []),
        }

    def _extract_trace_ids(self, payload: Any) -> list[str]:
        """Extract Falcon trace identifiers from nested payloads."""
        trace_ids: set[str] = set()

        def _walk(value: Any) -> None:
            if isinstance(value, dict):
                for key, nested_value in value.items():
                    normalized_key = str(key).lower()
                    if normalized_key in TRACE_ID_KEYS and nested_value:
                        trace_ids.add(str(nested_value))
                    _walk(nested_value)
            elif isinstance(value, list):
                for item in value:
                    _walk(item)

        _walk(payload)
        return sorted(trace_ids)

    def _extract_target_device_ids(self, *payloads: Any) -> list[str]:
        """Extract target device identifiers from tool inputs and Falcon request payloads."""
        device_ids: set[str] = set()

        def _record_device_ids(value: Any) -> None:
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item:
                        device_ids.add(item)
            elif isinstance(value, str) and value:
                device_ids.add(value)

        def _walk(value: Any) -> None:
            if isinstance(value, dict):
                for key, nested_value in value.items():
                    if str(key).lower() in TARGET_DEVICE_ID_KEYS:
                        _record_device_ids(nested_value)
                    _walk(nested_value)
            elif isinstance(value, list):
                for item in value:
                    _walk(item)

        for payload in payloads:
            _walk(payload)

        return sorted(device_ids)

    def _make_json_safe(self, value: Any) -> Any:
        """Convert nested values into a JSON-safe structure."""
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        if isinstance(value, dict):
            return {str(key): self._make_json_safe(nested) for key, nested in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._make_json_safe(item) for item in value]
        return repr(value)


def get_version() -> str:
    """Get falcon-mcp version with multiple fallback methods.

    This function tries multiple methods to determine the version:
    1. importlib.metadata (works when package is properly installed)
    2. pyproject.toml (works in development/Docker environments)
    3. Hardcoded fallback

    Returns:
        str: The version string
    """
    # Try importlib.metadata first (works when properly installed)
    try:
        return version("falcon-mcp")
    except PackageNotFoundError:
        logger.debug(
            "falcon-mcp package not found via importlib.metadata, trying pyproject.toml"
        )

    # Try reading from pyproject.toml (works in development/Docker)
    try:
        import pathlib
        import tomllib  # Python 3.11+

        # Look for pyproject.toml in current directory and parent directories
        current_path = pathlib.Path(__file__).parent
        for _ in range(3):  # Check up to 3 levels up
            pyproject_path = current_path / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    version_str: str = data["project"]["version"]
                    logger.debug(
                        "Found version %s in pyproject.toml at %s",
                        version_str,
                        pyproject_path,
                    )
                    return version_str
            current_path = current_path.parent

        logger.debug("pyproject.toml not found in current or parent directories")
    except (KeyError, ImportError, OSError, TypeError) as e:
        logger.debug("Failed to read version from pyproject.toml: %s", e)

    # Final fallback
    fallback_version = "0.1.0"
    logger.debug("Using fallback version: %s", fallback_version)
    return fallback_version
