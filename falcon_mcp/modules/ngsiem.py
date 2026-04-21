"""
NGSIEM module for Falcon MCP Server.

This module provides full FalconPy NGSIEM service collection coverage for
search jobs, dashboards, lookup files, parsers, and saved queries.
"""

import asyncio
import os
from datetime import datetime
from typing import Any

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


def _iso_to_epoch_ms(iso_timestamp: str) -> int:
    """Convert ISO 8601 timestamp to Unix epoch milliseconds."""
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


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
        query_validation_error = self._validate_ngsiem_query_string(
            query_string=query_string,
            operation="StartSearchV1",
        )
        if query_validation_error:
            return query_validation_error

        start_result = self.start_ngsiem_search(
            confirm_execution=True,
            query_string=query_string,
            start=start,
            repository=repository,
            end=end,
            body=None,
        )
        if self._is_error(start_result):
            return start_result
        if isinstance(start_result, list):
            return start_result

        job_id = start_result.get("id")
        if not job_id:
            return _format_error_response(
                message="Failed to start NGSIEM search: no job ID returned",
                details=start_result,
                operation="StartSearchV1",
            )

        elapsed = 0.0
        while elapsed < TIMEOUT_SECONDS:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

            status_result = self.get_ngsiem_search_status(
                repository=repository,
                search_id=job_id,
            )
            if self._is_error(status_result):
                return status_result
            if isinstance(status_result, list):
                return status_result

            if status_result.get("done"):
                events = status_result.get("events")
                if isinstance(events, list):
                    return events
                return []

        self.stop_ngsiem_search(
            confirm_execution=True,
            repository=repository,
            search_id=job_id,
        )

        return _format_error_response(
            message=f"NGSIEM search timed out after {TIMEOUT_SECONDS} seconds. "
            "Try narrowing your query or reducing the time range.",
            details={"job_id": job_id, "timeout_seconds": TIMEOUT_SECONDS},
            operation="GetSearchStatusV1",
        )

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
                return [
                    {
                        "filename": item,
                        "name": item,
                    }
                    for item in result
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
