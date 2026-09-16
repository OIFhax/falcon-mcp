"""
NGSIEM module for Falcon MCP Server.

This module provides full FalconPy NGSIEM service collection coverage for
search jobs, dashboards, lookup files, parsers, and saved queries.
"""

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, cast

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.ngsiem import (
    NGSIEM_REPOSITORY_GUIDE,
    NGSIEM_SAFETY_GUIDE,
    NGSIEM_SEARCH_GUIDE,
)

# Hint appended to error/empty responses steering the model to the CQL guide.
_CQL_ERROR_HINT = (
    "Review the CQL guide above and correct your query. CQL is a pipe-based "
    "language (filter | command | command) — not SQL or Splunk SPL. Consult "
    "`falcon://ngsiem/search-guide` for the syntax and working examples."
)
# The API demotes unrecognized CQL words to free-text stages instead of erroring, so
# `job.parsed_query` (its own normalization of what ran) is the only misparse signal.
_CQL_CONFIRMED_ZERO_HINT = (
    "No rows matched, and the job scanned {processed_events:,} events — a real "
    "negative. Report it as such rather than retrying. If you expected rows, check "
    "`job.parsed_query` against the query you sent."
)

# A correct filter over an empty partition and a misparsed query both scan nothing.
_CQL_UNSCANNED_ZERO_HINT = (
    "No rows, and `job.processed_events` does not show a completed scan, so this alone "
    "is not a confirmed negative. Compare `job.parsed_query` to the query you sent: "
    "unrecognized words become free-text stages instead of an error. If it matches your "
    "intent the negative is real; if not, correct the syntax using the guide above."
)

# Configurable polling settings
POLL_INTERVAL_SECONDS = int(os.environ.get("FALCON_MCP_NGSIEM_POLL_INTERVAL", "5"))
TIMEOUT_SECONDS = int(os.environ.get("FALCON_MCP_NGSIEM_TIMEOUT", "300"))

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)
NGSIEM_SEARCH_GUIDE_URI = "falcon://ngsiem/search-guide"
NATURAL_LANGUAGE_PREFIXES = (
    "show ",
    "find ",
    "search ",
    "list ",
    "display ",
    "tell ",
    "look ",
    "get ",
    "what ",
    "which ",
)
CQL_MARKERS = ("|", "=", ":", "!=", ">=", "<=", "<", ">", "(", ")", "[", "]", "*", "#")
SEARCH_DOMAIN_OPERATIONS = {
    "GetLookupFile",
    "CreateLookupFile",
    "UpdateLookupFile",
    "DeleteLookupFile",
    "ListLookupFiles",
}
_UNSAFE_REPOSITORY_CHARS = ("/", "\\", "%")
_DOT_SEGMENTS = (".", "..")


def _validate_repository(repository: Any) -> dict[str, Any] | None:
    """Reject repository values that could alter FalconPy path routing."""
    if not isinstance(repository, str):
        return None
    if not repository.strip():
        return _format_error_response(
            "Invalid repository: must be a non-empty repository or view name.",
            operation="StartSearchV1",
        )
    if any(char in repository for char in _UNSAFE_REPOSITORY_CHARS) or repository in _DOT_SEGMENTS:
        return _format_error_response(
            f"Invalid repository {repository!r}: must not contain '/', '\\', or '%', "
            "or be '.' or '..'.",
            operation="StartSearchV1",
        )
    return None


def _iso_to_epoch_ms(iso_timestamp: str) -> int:
    """Convert ISO 8601 timestamp to Unix epoch milliseconds."""
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


def _epoch_ms_to_iso(epoch_ms: Any) -> str | None:
    """Convert Unix epoch milliseconds to an ISO 8601 UTC timestamp.

    Args:
        epoch_ms: Unix epoch time in milliseconds

    Returns:
        ISO 8601 timestamp string, or None if the value is not a usable number
    """
    if isinstance(epoch_ms, bool) or not isinstance(epoch_ms, (int, float)):
        return None
    try:
        return (
            datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
    except (OSError, OverflowError, ValueError):
        return None


class NGSIEMModule(BaseModule):
    """Module for Falcon NGSIEM operations."""

    def _is_structured_ngsiem_query(self, query_string: str) -> bool:
        """Return True when the provided NGSIEM query looks like explicit CQL."""
        stripped = query_string.strip()
        if stripped == "*":
            return True
        if any(marker in stripped for marker in CQL_MARKERS):
            return True
        lowered = stripped.lower()
        if lowered.startswith(NATURAL_LANGUAGE_PREFIXES) or stripped.endswith("?"):
            return False
        return False

    def _validate_ngsiem_query_string(
        self,
        query_string: str | None,
        operation: str,
    ) -> dict[str, Any] | None:
        """Block natural-language or improvised NGSIEM queries."""
        if query_string is None:
            return None

        if not isinstance(query_string, str):
            error = _format_error_response(
                "NGSIEM `query_string` must be a string containing complete CQL.",
                details={"guide": NGSIEM_SEARCH_GUIDE_URI},
                operation=operation,
                error_type="malformed_query",
            )
            error["resolution"] = (
                "Use `falcon://ngsiem/search-guide` to build a complete, validated CQL query string."
            )
            return error

        stripped = query_string.strip()
        if not stripped:
            error = _format_error_response(
                "NGSIEM `query_string` cannot be empty.",
                details={"guide": NGSIEM_SEARCH_GUIDE_URI},
                operation=operation,
                error_type="malformed_query",
            )
            error["resolution"] = (
                "Read `falcon://ngsiem/search-guide` and submit a complete, validated CQL query."
            )
            return error

        if self._is_structured_ngsiem_query(stripped):
            return None

        error = _format_error_response(
            "NGSIEM queries must be explicit CQL. Improvised natural-language queries are blocked.",
            details={"query_string": stripped, "guide": NGSIEM_SEARCH_GUIDE_URI},
            operation=operation,
            error_type="malformed_query",
        )
        error["resolution"] = (
            "Use `falcon://ngsiem/search-guide` to build a complete CQL query before calling this tool."
        )
        return error

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_ngsiem, name="search_ngsiem")
        self._add_tool(
            server=server,
            method=self.start_ngsiem_search,
            name="start_ngsiem_search",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_search_status,
            name="get_ngsiem_search_status",
        )
        self._add_tool(
            server=server,
            method=self.stop_ngsiem_search,
            name="stop_ngsiem_search",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_dashboard_template,
            name="get_ngsiem_dashboard_template",
        )
        self._add_tool(
            server=server,
            method=self.create_ngsiem_dashboard_from_template,
            name="create_ngsiem_dashboard_from_template",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_ngsiem_dashboard_from_template,
            name="update_ngsiem_dashboard_from_template",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_ngsiem_dashboard,
            name="delete_ngsiem_dashboard",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(server=server, method=self.list_ngsiem_dashboards, name="list_ngsiem_dashboards")
        self._add_tool(server=server, method=self.upload_ngsiem_lookup, name="upload_ngsiem_lookup", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.get_ngsiem_lookup, name="get_ngsiem_lookup")
        self._add_tool(
            server=server,
            method=self.get_ngsiem_lookup_from_package,
            name="get_ngsiem_lookup_from_package",
        )
        self._add_tool(
            server=server,
            method=self.get_ngsiem_lookup_from_namespace_package,
            name="get_ngsiem_lookup_from_namespace_package",
        )
        self._add_tool(server=server, method=self.get_ngsiem_lookup_file, name="get_ngsiem_lookup_file")
        self._add_tool(
            server=server,
            method=self.create_ngsiem_lookup_file,
            name="create_ngsiem_lookup_file",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_ngsiem_lookup_file,
            name="update_ngsiem_lookup_file",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_ngsiem_lookup_file,
            name="delete_ngsiem_lookup_file",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(server=server, method=self.list_ngsiem_lookup_files, name="list_ngsiem_lookup_files")
        self._add_tool(server=server, method=self.get_ngsiem_parser_template, name="get_ngsiem_parser_template")
        self._add_tool(
            server=server,
            method=self.create_ngsiem_parser_from_template,
            name="create_ngsiem_parser_from_template",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(server=server, method=self.get_ngsiem_parser, name="get_ngsiem_parser")
        self._add_tool(
            server=server,
            method=self.create_ngsiem_parser,
            name="create_ngsiem_parser",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_ngsiem_parser,
            name="update_ngsiem_parser",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_ngsiem_parser,
            name="delete_ngsiem_parser",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(server=server, method=self.list_ngsiem_parsers, name="list_ngsiem_parsers")
        self._add_tool(
            server=server,
            method=self.get_ngsiem_saved_query_template,
            name="get_ngsiem_saved_query_template",
        )
        self._add_tool(
            server=server,
            method=self.create_ngsiem_saved_query,
            name="create_ngsiem_saved_query",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_ngsiem_saved_query_from_template,
            name="update_ngsiem_saved_query_from_template",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_ngsiem_saved_query,
            name="delete_ngsiem_saved_query",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(server=server, method=self.list_ngsiem_saved_queries, name="list_ngsiem_saved_queries")

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        repository_guide_resource = TextResource(
            uri=AnyUrl("falcon://ngsiem/repository-guide"),
            name="falcon_ngsiem_repository_guide",
            description="Repository and operation guidance for NGSIEM tools.",
            text=NGSIEM_REPOSITORY_GUIDE,
        )

        search_guide_resource = TextResource(
            uri=AnyUrl("falcon://ngsiem/search-guide"),
            name="falcon_ngsiem_search_guide",
            description="Search workflow guidance for NGSIEM tools.",
            text=NGSIEM_SEARCH_GUIDE,
        )

        safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://ngsiem/safety-guide"),
            name="falcon_ngsiem_safety_guide",
            description="Safety and operational guidance for NGSIEM write tools.",
            text=NGSIEM_SAFETY_GUIDE,
        )

        self._add_resource(server, repository_guide_resource)
        self._add_resource(server, search_guide_resource)
        self._add_resource(server, safety_guide_resource)

    def _format_cql_error_response(
        self,
        error_response: dict[str, Any],
        query_string: str,
    ) -> dict[str, Any]:
        """Augment an error response with the CQL guide and a repair hint.

        Reaches the model with the full CQL authoring guide exactly when its query
        failed, so it can correct the syntax and retry. Mirrors
        `_format_fql_error_response` but for CQL (the API returns no CQL parser
        diagnostics, so the guide is the only actionable signal).

        Args:
            error_response: The error dict produced by the shared error handlers
            query_string: The CQL query that was attempted

        Returns:
            The error dict with `cql_guide`, `hint`, and `query_used` added
        """
        error_response["query_used"] = query_string
        error_response["cql_guide"] = NGSIEM_SEARCH_GUIDE
        error_response["hint"] = _CQL_ERROR_HINT
        return error_response

    @staticmethod
    def _extract_job_metadata(
        body: dict[str, Any],
        repository: str,
        job_id: str,
    ) -> dict[str, Any]:
        """Map a search-status body onto the `job` block of the response envelope.

        Fields the response omits are reported as None, never defaulted to 0.

        Args:
            body: The `body` of a 200 GetSearchStatusV1 response
            repository: The repository the job ran against
            job_id: The search job ID

        Returns:
            Dict of job metadata suitable for the `job` key of the response envelope
        """
        meta = body.get("metaData") or {}
        filter_query = meta.get("filterQuery") or {}
        # Job-level and query-level warnings are scoped separately; callers want both.
        warnings = [*(body.get("warnings") or []), *(meta.get("warnings") or [])]

        return {
            "job_id": job_id,
            "repository": repository,
            "event_count": meta.get("eventCount"),
            "processed_events": meta.get("processedEvents"),
            "processed_bytes": meta.get("processedBytes"),
            "parsed_query": filter_query.get("queryString"),
            "search_start": _epoch_ms_to_iso(meta.get("queryStart")),
            "search_end": _epoch_ms_to_iso(meta.get("queryEnd")),
            "duration_ms": meta.get("timeMillis"),
            "is_aggregate": meta.get("isAggregate"),
            "cancelled": body.get("cancelled"),
            "warnings": warnings,
        }

    def _build_job_envelope(
        self,
        events: list[dict[str, Any]],
        job: dict[str, Any],
        query_string: str,
    ) -> dict[str, Any]:
        """Assemble the response envelope, identical in shape for any row count.

        NG-SIEM jobs carry no `meta.pagination`, so this keeps the house `results` key
        and swaps the pagination block for a `job` block. Zero rows also get the CQL
        guide and a hint chosen from `job.processed_events`.

        Args:
            events: The event records returned by the job
            job: Job metadata from `_extract_job_metadata`
            query_string: The CQL query as submitted

        Returns:
            Dict with `results`, `query_used`, `job`, and on zero rows also
            `cql_guide` and `hint`
        """
        envelope: dict[str, Any] = {
            "results": events,
            "query_used": query_string,
            "job": job,
        }

        if events:
            return envelope

        processed = job.get("processed_events")
        if isinstance(processed, int) and not isinstance(processed, bool) and processed > 0:
            hint = _CQL_CONFIRMED_ZERO_HINT.format(processed_events=processed)
        else:
            hint = _CQL_UNSCANNED_ZERO_HINT

        envelope["cql_guide"] = NGSIEM_SEARCH_GUIDE
        envelope["hint"] = hint
        return envelope

    async def search_ngsiem(
        self,
        query_string: str = Field(
            description="Complete CQL query string to execute.",
        ),
        start: str = Field(
            description="Search start time in ISO-8601 UTC format (example: `2026-03-17T00:00:00Z`).",
        ),
        repository: str = Field(
            default="search-all",
            description="Repository to search. See `falcon://ngsiem/repository-guide`.",
        ),
        end: str | None = Field(
            default=None,
            description="Optional search end time in ISO-8601 UTC format.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Execute asynchronous NGSIEM search and return matching events."""
        repository_error = _validate_repository(repository)
        if repository_error is not None:
            return repository_error

        query_validation_error = self._validate_ngsiem_query_string(
            query_string=query_string,
            operation="StartSearchV1",
        )
        if query_validation_error:
            return query_validation_error

        body_params: dict[str, Any] = {
            "queryString": query_string,
            "start": _iso_to_epoch_ms(start),
        }
        if isinstance(end, str):
            body_params["end"] = _iso_to_epoch_ms(end)

        start_response = await self.client.command_async(
            operation="StartSearchV1",
            repository=repository,
            body=body_params,
        )
        if start_response.get("status_code") != 200:
            error_response = handle_api_response(
                start_response,
                operation="StartSearchV1",
                error_message="Failed to start NGSIEM search",
                default_result=[],
            )
            return self._format_cql_error_response(error_response, query_string)

        job_id = start_response.get("body", {}).get("id")
        if not job_id:
            error_response = _format_error_response(
                message="Failed to start NGSIEM search: no job ID returned",
                details=start_response.get("body", {}),
                operation="StartSearchV1",
            )
            return self._format_cql_error_response(error_response, query_string)

        elapsed = 0.0
        last_job_meta: dict[str, Any] | None = None
        while elapsed < TIMEOUT_SECONDS:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

            poll_response = await self.client.command_async(
                operation="GetSearchStatusV1",
                repository=repository,
                search_id=job_id,
            )
            if poll_response.get("status_code") != 200:
                error_response = handle_api_response(
                    poll_response,
                    operation="GetSearchStatusV1",
                    error_message="Failed to poll NGSIEM search status",
                    default_result=[],
                )
                return self._format_cql_error_response(error_response, query_string)

            status_body = poll_response.get("body", {})
            last_job_meta = self._extract_job_metadata(status_body, repository, job_id)
            if status_body.get("done"):
                events = status_body.get("events")
                if isinstance(events, list):
                    return events
                return []

        stop_response = await self.client.command_async(
            operation="StopSearchV1",
            repository=repository,
            id=job_id,
        )

        # How far the job got, and whether cleanup actually stopped it.
        details: dict[str, Any] = {
            "job_id": job_id,
            "timeout_seconds": TIMEOUT_SECONDS,
            "stop_status_code": stop_response.get("status_code"),
        }
        if last_job_meta is not None:
            details["last_job_status"] = last_job_meta

        error_response = _format_error_response(
            message=f"NGSIEM search timed out after {TIMEOUT_SECONDS} seconds. "
            "Try narrowing your query or reducing the time range.",
            details=details,
            operation="GetSearchStatusV1",
        )
        return self._format_cql_error_response(error_response, query_string)

    def start_ngsiem_search(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this operation.",
        ),
        query_string: str | None = Field(
            default=None,
            description="CQL query string. Required when `body` is not provided.",
        ),
        start: str | None = Field(
            default=None,
            description="Start time in ISO-8601 UTC. Required when `body` is not provided.",
        ),
        repository: str = Field(
            default="search-all",
            description="Repository name.",
        ),
        end: str | None = Field(
            default=None,
            description="Optional end time in ISO-8601 UTC.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `StartSearchV1`.",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Start an NGSIEM search job and return job metadata."""
        request_body = body
        if request_body is None:
            if not query_string or not start:
                return _format_error_response(
                    "`query_string` and `start` are required when `body` is not provided.",
                    operation="StartSearchV1",
                )
            request_body = {
                "queryString": query_string,
                "start": _iso_to_epoch_ms(start),
            }
            if end:
                request_body["end"] = _iso_to_epoch_ms(end)

        query_validation_error = self._validate_ngsiem_query_string(
            query_string=request_body.get("queryString") if isinstance(request_body, dict) else None,
            operation="StartSearchV1",
        )
        if query_validation_error:
            return query_validation_error

        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="StartSearchV1",
            repository=repository,
            body=request_body,
            error_message="Failed to start NGSIEM search",
            default_result={},
        )

    def get_ngsiem_search_status(
        self,
        repository: str = Field(default="search-all", description="Repository name."),
        search_id: str | None = Field(default=None, description="Search job ID."),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get NGSIEM search job status and results payload."""
        if not search_id:
            return _format_error_response(
                "`search_id` is required.",
                operation="GetSearchStatusV1",
            )

        return self._call_ngsiem_api(
            operation="GetSearchStatusV1",
            repository=repository,
            path_params={"search_id": search_id},
            error_message="Failed to get NGSIEM search status",
            default_result={},
        )

    def stop_ngsiem_search(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this operation.",
        ),
        repository: str = Field(default="search-all", description="Repository name."),
        search_id: str | None = Field(default=None, description="Search job ID."),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Stop an NGSIEM search job."""
        if not search_id:
            return _format_error_response(
                "`search_id` is required.",
                operation="StopSearchV1",
            )

        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="StopSearchV1",
            repository=repository,
            path_params={"id": search_id},
            error_message="Failed to stop NGSIEM search",
            default_result={},
        )

    def get_ngsiem_dashboard_template(self) -> list[dict[str, Any]] | dict[str, Any]:
        """Get NGSIEM dashboard template."""
        return self._call_ngsiem_api(
            operation="GetDashboardTemplate",
            error_message="Failed to get NGSIEM dashboard template",
            default_result={},
        )

    def create_ngsiem_dashboard_from_template(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(default=None, description="Request body for `CreateDashboardFromTemplate`."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create NGSIEM dashboard from template."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="CreateDashboardFromTemplate",
            body=body,
            error_message="Failed to create NGSIEM dashboard from template",
        )

    def update_ngsiem_dashboard_from_template(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(default=None, description="Request body for `UpdateDashboardFromTemplate`."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update NGSIEM dashboard from template."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="UpdateDashboardFromTemplate",
            body=body,
            error_message="Failed to update NGSIEM dashboard from template",
        )

    def delete_ngsiem_dashboard(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        id: str | None = Field(default=None, description="Dashboard ID."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Delete NGSIEM dashboard by ID."""
        if not id:
            return _format_error_response("`id` is required.", operation="DeleteDashboard")
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="DeleteDashboard",
            path_params={"id": id},
            error_message="Failed to delete NGSIEM dashboard",
        )

    def list_ngsiem_dashboards(self) -> list[dict[str, Any]] | dict[str, Any]:
        """List NGSIEM dashboards."""
        return self._call_ngsiem_api(
            operation="ListDashboards",
            error_message="Failed to list NGSIEM dashboards",
        )

    def upload_ngsiem_lookup(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        repository: str | None = Field(default=None, description="Repository name."),
        body: dict[str, Any] | None = Field(default=None, description="Request body for `UploadLookupV1`."),
        path_params: dict[str, Any] | None = Field(
            default=None,
            description="Optional path parameters such as `lookup_file`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Upload NGSIEM lookup file."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="UploadLookupV1",
            repository=repository,
            path_params=path_params,
            body=body,
            error_message="Failed to upload NGSIEM lookup",
        )

    def get_ngsiem_lookup(
        self,
        repository: str | None = Field(default=None, description="Repository name."),
        filename: str | None = Field(default=None, description="Lookup filename."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get NGSIEM lookup by repository and filename."""
        return self._call_ngsiem_api(
            operation="GetLookupV1",
            repository=repository,
            path_params={"filename": filename},
            error_message="Failed to get NGSIEM lookup",
            default_result={},
        )

    def get_ngsiem_lookup_from_package(
        self,
        repository: str | None = Field(default=None, description="Repository name."),
        package: str | None = Field(default=None, description="Package name."),
        filename: str | None = Field(default=None, description="Lookup filename."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get NGSIEM lookup from package."""
        return self._call_ngsiem_api(
            operation="GetLookupFromPackageV1",
            repository=repository,
            path_params={"package": package, "filename": filename},
            error_message="Failed to get NGSIEM lookup from package",
            default_result={},
        )

    def get_ngsiem_lookup_from_namespace_package(
        self,
        repository: str | None = Field(default=None, description="Repository name."),
        namespace: str | None = Field(default=None, description="Namespace."),
        package: str | None = Field(default=None, description="Package name."),
        filename: str | None = Field(default=None, description="Lookup filename."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get NGSIEM lookup from namespace and package."""
        return self._call_ngsiem_api(
            operation="GetLookupFromPackageWithNamespaceV1",
            repository=repository,
            path_params={
                "namespace": namespace,
                "package": package,
                "filename": filename,
            },
            error_message="Failed to get NGSIEM lookup from namespace/package",
            default_result={},
        )

    def get_ngsiem_lookup_file(
        self,
        repository: str | None = Field(default=None, description="Repository name."),
        filename: str | None = Field(default=None, description="Lookup filename."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get NGSIEM lookup file metadata/content response."""
        return self._call_ngsiem_api(
            operation="GetLookupFile",
            repository=repository,
            path_params={"filename": filename},
            error_message="Failed to get NGSIEM lookup file",
            default_result={},
        )

    def create_ngsiem_lookup_file(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(default=None, description="Request body for `CreateLookupFile`."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create NGSIEM lookup file."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="CreateLookupFile",
            body=body,
            error_message="Failed to create NGSIEM lookup file",
        )

    def update_ngsiem_lookup_file(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(default=None, description="Request body for `UpdateLookupFile`."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update NGSIEM lookup file."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="UpdateLookupFile",
            body=body,
            error_message="Failed to update NGSIEM lookup file",
        )

    def delete_ngsiem_lookup_file(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        filename: str | None = Field(default=None, description="Lookup filename."),
        repository: str | None = Field(default=None, description="Repository name."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Delete NGSIEM lookup file."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="DeleteLookupFile",
            repository=repository,
            path_params={"filename": filename},
            error_message="Failed to delete NGSIEM lookup file",
        )

    def list_ngsiem_lookup_files(
        self,
        repository: str | None = Field(default=None, description="Repository name."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List NGSIEM lookup files."""
        result = self._call_ngsiem_api(
            operation="ListLookupFiles",
            repository=repository,
            error_message="Failed to list NGSIEM lookup files",
        )
        if isinstance(result, list):
            if all(isinstance(item, str) for item in result):
                filenames = cast(list[str], result)
                return [
                    {
                        "filename": item,
                        "name": item,
                    }
                    for item in filenames
                    if item.strip()
                ]
        return result

    def get_ngsiem_parser_template(
        self,
        repository: str | None = Field(default=None, description="Repository name."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get NGSIEM parser template."""
        return self._call_ngsiem_api(
            operation="GetParserTemplate",
            repository=repository,
            error_message="Failed to get NGSIEM parser template",
            default_result={},
        )

    def create_ngsiem_parser_from_template(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `CreateParserFromTemplate`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create NGSIEM parser from template."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="CreateParserFromTemplate",
            body=body,
            error_message="Failed to create NGSIEM parser from template",
        )

    def get_ngsiem_parser(
        self,
        repository: str | None = Field(default=None, description="Repository name."),
        id: str | None = Field(default=None, description="Parser ID."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get NGSIEM parser by ID."""
        return self._call_ngsiem_api(
            operation="GetParser",
            repository=repository,
            path_params={"id": id},
            error_message="Failed to get NGSIEM parser",
            default_result={},
        )

    def create_ngsiem_parser(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(default=None, description="Request body for `CreateParser`."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create NGSIEM parser."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="CreateParser",
            body=body,
            error_message="Failed to create NGSIEM parser",
        )

    def update_ngsiem_parser(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(default=None, description="Request body for `UpdateParser`."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update NGSIEM parser."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="UpdateParser",
            body=body,
            error_message="Failed to update NGSIEM parser",
        )

    def delete_ngsiem_parser(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        repository: str | None = Field(default=None, description="Repository name."),
        id: str | None = Field(default=None, description="Parser ID."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Delete NGSIEM parser."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="DeleteParser",
            repository=repository,
            path_params={"id": id},
            error_message="Failed to delete NGSIEM parser",
        )

    def list_ngsiem_parsers(
        self,
        repository: str | None = Field(default=None, description="Repository name."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List NGSIEM parsers."""
        return self._call_ngsiem_api(
            operation="ListParsers",
            repository=repository,
            error_message="Failed to list NGSIEM parsers",
        )

    def get_ngsiem_saved_query_template(self) -> list[dict[str, Any]] | dict[str, Any]:
        """Get NGSIEM saved query template."""
        return self._call_ngsiem_api(
            operation="GetSavedQueryTemplate",
            error_message="Failed to get NGSIEM saved query template",
            default_result={},
        )

    def create_ngsiem_saved_query(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(default=None, description="Request body for `CreateSavedQuery`."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Create NGSIEM saved query."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="CreateSavedQuery",
            body=body,
            error_message="Failed to create NGSIEM saved query",
        )

    def update_ngsiem_saved_query_from_template(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `UpdateSavedQueryFromTemplate`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update NGSIEM saved query from template."""
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="UpdateSavedQueryFromTemplate",
            body=body,
            error_message="Failed to update NGSIEM saved query from template",
        )

    def delete_ngsiem_saved_query(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this operation."),
        id: str | None = Field(default=None, description="Saved query ID."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Delete NGSIEM saved query."""
        if not id:
            return _format_error_response("`id` is required.", operation="DeleteSavedQuery")
        return self._write_ngsiem_operation(
            confirm_execution=confirm_execution,
            operation="DeleteSavedQuery",
            path_params={"id": id},
            error_message="Failed to delete NGSIEM saved query",
        )

    def list_ngsiem_saved_queries(self) -> list[dict[str, Any]] | dict[str, Any]:
        """List NGSIEM saved queries."""
        return self._call_ngsiem_api(
            operation="ListSavedQueries",
            error_message="Failed to list NGSIEM saved queries",
        )

    def _write_ngsiem_operation(
        self,
        confirm_execution: bool,
        operation: str,
        error_message: str,
        repository: str | None = None,
        path_params: dict[str, Any] | None = None,
        parameters: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        default_result: Any | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        if not confirm_execution:
            return _format_error_response(
                "This operation requires `confirm_execution=true`.",
                operation=operation,
            )

        return self._call_ngsiem_api(
            operation=operation,
            repository=repository,
            path_params=path_params,
            parameters=parameters,
            body=body,
            error_message=error_message,
            default_result=default_result,
        )

    def _call_ngsiem_api(
        self,
        operation: str,
        error_message: str,
        repository: str | None = None,
        path_params: dict[str, Any] | None = None,
        parameters: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        default_result: Any | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        repository_error = _validate_repository(repository)
        if repository_error is not None:
            return repository_error

        call_args: dict[str, Any] = {"operation": operation}
        prepared_parameters = prepare_api_parameters(parameters) if parameters else {}

        if repository:
            if operation in SEARCH_DOMAIN_OPERATIONS:
                prepared_parameters.setdefault("search_domain", repository)
            else:
                call_args["repository"] = repository

        if path_params:
            prepared_path = prepare_api_parameters(path_params)
            for key, value in prepared_path.items():
                call_args[key] = value

        if prepared_parameters:
            call_args["parameters"] = prepared_parameters

        if body is not None:
            call_args["body"] = prepare_api_parameters(body)

        response = self.client.command(**call_args)

        if isinstance(response, bytes):
            return {"content": response.decode("utf-8")}

        status_code = response.get("status_code")
        if status_code is None or status_code >= 300:
            return handle_api_response(
                response,
                operation=operation,
                error_message=error_message,
                default_result=default_result if default_result is not None else [],
            )

        body_response = response.get("body", {})
        if isinstance(body_response, dict) and "resources" in body_response:
            resources = body_response.get("resources")
            if not resources and default_result is not None:
                return default_result
            return resources

        if not body_response and default_result is not None:
            return default_result

        return body_response
