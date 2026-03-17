"""
Scheduled Reports module for Falcon MCP Server.

This module provides full Scheduled Reports and Report Executions coverage:
query/get/launch operations for scheduled report entities, query/get/retry/download
operations for report executions, and search convenience tools.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.scheduled_reports import (
    SEARCH_REPORT_EXECUTIONS_FQL_DOCUMENTATION,
    SEARCH_SCHEDULED_REPORTS_FQL_DOCUMENTATION,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class ScheduledReportsModule(BaseModule):
    """Module for CrowdStrike Falcon scheduled reports and executions."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_scheduled_reports,
            name="search_scheduled_reports",
        )
        self._add_tool(
            server=server,
            method=self.query_scheduled_report_ids,
            name="query_scheduled_report_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_scheduled_report_details,
            name="get_scheduled_report_details",
        )
        self._add_tool(
            server=server,
            method=self.launch_scheduled_report,
            name="launch_scheduled_report",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.search_report_executions,
            name="search_report_executions",
        )
        self._add_tool(
            server=server,
            method=self.query_report_execution_ids,
            name="query_report_execution_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_report_execution_details,
            name="get_report_execution_details",
        )
        self._add_tool(
            server=server,
            method=self.retry_report_execution,
            name="retry_report_execution",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.download_report_execution,
            name="download_report_execution",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_scheduled_reports_fql_resource = TextResource(
            uri=AnyUrl("falcon://scheduled-reports/search/fql-guide"),
            name="falcon_search_scheduled_reports_fql_guide",
            description="Contains the guide for the `filter` parameter of scheduled report query/search tools.",
            text=SEARCH_SCHEDULED_REPORTS_FQL_DOCUMENTATION,
        )

        search_report_executions_fql_resource = TextResource(
            uri=AnyUrl("falcon://scheduled-reports/executions/search/fql-guide"),
            name="falcon_search_report_executions_fql_guide",
            description="Contains the guide for the `filter` parameter of report execution query/search tools.",
            text=SEARCH_REPORT_EXECUTIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_scheduled_reports_fql_resource)
        self._add_resource(server, search_report_executions_fql_resource)

    def search_scheduled_reports(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for scheduled report search. IMPORTANT: use the `falcon://scheduled-reports/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(default=20, ge=1, le=5000, description="Maximum number of records to return. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search scheduled reports and return full details."""
        report_ids = self.query_scheduled_report_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            q=q,
        )

        if self._is_error(report_ids):
            return [report_ids]
        if isinstance(report_ids, dict):
            return report_ids
        if not report_ids:
            return []

        return self.get_scheduled_report_details(ids=report_ids)

    def query_scheduled_report_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for scheduled report ID query. IMPORTANT: use the `falcon://scheduled-reports/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs to return. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query."),
    ) -> list[str] | dict[str, Any]:
        """Query scheduled report IDs."""
        result = self._base_search_api_call(
            operation="scheduled_reports_query",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to query scheduled report IDs",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_SCHEDULED_REPORTS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_SCHEDULED_REPORTS_FQL_DOCUMENTATION,
            )

        return result

    def get_scheduled_report_details(
        self,
        ids: list[str] | None = Field(default=None, description="Scheduled report IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get scheduled report detail records by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve scheduled report details.",
                    operation="scheduled_reports_get",
                )
            ]

        result = self._base_get_by_ids(
            operation="scheduled_reports_get",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def launch_scheduled_report(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this operation.",
        ),
        id: str | None = Field(
            default=None,
            description="Scheduled report/search entity ID to execute.",
        ),
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Optional full list body override for `scheduled_reports_launch`.",
        ),
    ) -> list[dict[str, Any]]:
        """Launch a scheduled report/search on demand."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="scheduled_reports_launch",
                )
            ]

        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided.",
                        operation="scheduled_reports_launch",
                    )
            ]
            request_body = [{"id": id}]

        response = self.client.command(
            "scheduled_reports_launch",
            body=request_body,
        )
        result = handle_api_response(
            response,
            operation="scheduled_reports_launch",
            error_message="Failed to launch scheduled report",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_report_executions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for execution search. IMPORTANT: use the `falcon://scheduled-reports/executions/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(default=20, ge=1, le=5000, description="Maximum number of records to return. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search report executions and return full details."""
        execution_ids = self.query_report_execution_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(execution_ids):
            return [execution_ids]
        if isinstance(execution_ids, dict):
            return execution_ids
        if not execution_ids:
            return []

        return self.get_report_execution_details(ids=execution_ids)

    def query_report_execution_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for execution ID query. IMPORTANT: use the `falcon://scheduled-reports/executions/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs to return. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[str] | dict[str, Any]:
        """Query report execution IDs."""
        result = self._base_search_api_call(
            operation="report_executions_query",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query report execution IDs",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_REPORT_EXECUTIONS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_REPORT_EXECUTIONS_FQL_DOCUMENTATION,
            )

        return result

    def get_report_execution_details(
        self,
        ids: list[str] | None = Field(default=None, description="Report execution IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get report execution detail records by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve report execution details.",
                    operation="report_executions_get",
                )
            ]

        result = self._base_get_by_ids(
            operation="report_executions_get",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def retry_report_execution(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this operation.",
        ),
        id: str | None = Field(
            default=None,
            description="Report execution ID to retry.",
        ),
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Optional full list body override for `report_executions_retry`.",
        ),
    ) -> list[dict[str, Any]]:
        """Retry a failed/eligible report execution."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="report_executions_retry",
                )
            ]

        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided.",
                        operation="report_executions_retry",
                    )
            ]
            request_body = [{"id": id}]

        response = self.client.command(
            "report_executions_retry",
            body=request_body,
        )
        result = handle_api_response(
            response,
            operation="report_executions_retry",
            error_message="Failed to retry report execution",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def download_report_execution(
        self,
        id: str = Field(description="Report execution ID to download."),
    ) -> str | list[dict[str, Any]] | dict[str, Any]:
        """Download generated report results."""
        prepared_params = prepare_api_parameters({"ids": id})
        response = self.client.command(
            "report_executions_download_get",
            parameters=prepared_params,
        )

        if isinstance(response, bytes):
            if response[:4] == b"%PDF":
                return {
                    "error": "PDF format not supported for LLM consumption. "
                    "Please configure the scheduled report to use CSV or JSON format instead."
                }
            return response.decode("utf-8")

        if isinstance(response, dict):
            status_code = response.get("status_code")
            if status_code != 200:
                return handle_api_response(
                    response,
                    operation="report_executions_download_get",
                    error_message="Failed to download report execution",
                    default_result=[],
                )
            return response.get("body", {}).get("resources", [])

        return {"error": f"Unexpected response type: {type(response).__name__}"}
