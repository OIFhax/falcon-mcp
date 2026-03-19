"""
Quick Scan module for Falcon MCP Server.

This module provides search, aggregation, detail, and sample-submission tools for Quick Scan.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.quick_scan import QUICK_SCAN_FQL_GUIDE, QUICK_SCAN_SAFETY_GUIDE

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class QuickScanModule(BaseModule):
    """Module for Falcon Quick Scan operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_quick_scans, name="search_quick_scans")
        self._add_tool(server=server, method=self.query_quick_scan_ids, name="query_quick_scan_ids")
        self._add_tool(server=server, method=self.get_quick_scans, name="get_quick_scans")
        self._add_tool(server=server, method=self.aggregate_quick_scans, name="aggregate_quick_scans")
        self._add_tool(
            server=server,
            method=self.scan_quick_samples,
            name="scan_quick_samples",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://quick-scan/fql-guide"),
                name="falcon_quick_scan_fql_guide",
                description="FQL guidance for Quick Scan history queries.",
                text=QUICK_SCAN_FQL_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://quick-scan/safety-guide"),
                name="falcon_quick_scan_safety_guide",
                description="Safety guidance for Quick Scan sample submission.",
                text=QUICK_SCAN_SAFETY_GUIDE,
            ),
        )

    def search_quick_scans(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for Quick Scan search. IMPORTANT: use `falcon://quick-scan/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000),
        offset: int = Field(default=0, ge=0),
        sort: str | None = Field(default=None),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Quick Scan submissions and return scan details."""
        scan_ids = self._base_search_api_call(
            operation="QuerySubmissionsMixin0",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search quick scans",
        )

        if self._is_error(scan_ids):
            return self._format_fql_error_response([scan_ids], filter, QUICK_SCAN_FQL_GUIDE)

        if not scan_ids:
            if filter:
                return self._format_fql_error_response([], filter, QUICK_SCAN_FQL_GUIDE)
            return []

        details = self._base_get_by_ids(
            operation="GetScans",
            ids=scan_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def query_quick_scan_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for Quick Scan ID query. IMPORTANT: use `falcon://quick-scan/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000),
        offset: int = Field(default=0, ge=0),
        sort: str | None = Field(default=None),
    ) -> list[str] | dict[str, Any]:
        """Query Quick Scan submission IDs."""
        result = self._base_search_api_call(
            operation="QuerySubmissionsMixin0",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to query quick scan IDs",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response([result], filter, QUICK_SCAN_FQL_GUIDE)

        if not result and filter:
            return self._format_fql_error_response([], filter, QUICK_SCAN_FQL_GUIDE)

        return result

    def get_quick_scans(
        self,
        ids: list[str] | None = Field(default=None, description="Quick Scan submission IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve Quick Scan records by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve quick scan details.",
                    operation="GetScans",
                )
            ]

        result = self._base_get_by_ids(
            operation="GetScans",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def aggregate_quick_scans(
        self,
        body: dict[str, Any] | None = None,
        field: str | None = None,
        filter: str | None = None,
        interval: str | None = None,
        min_doc_count: int | None = None,
        name: str | None = None,
        q: str | None = None,
        size: int | None = None,
        sort: str | None = None,
        time_zone: str | None = None,
        type: str | None = None,
        date_ranges: list[dict[str, Any]] | None = None,
        ranges: list[dict[str, Any]] | None = None,
        sub_aggregates: list[Any] | None = None,
        missing: str | None = None,
    ) -> list[dict[str, Any]]:
        """Run Quick Scan aggregate queries."""
        request_body = body or {
            key: value
            for key, value in {
                "field": field,
                "filter": filter,
                "interval": interval,
                "min_doc_count": min_doc_count,
                "missing": missing,
                "name": name,
                "q": q,
                "size": size,
                "sort": sort,
                "time_zone": time_zone,
                "type": type,
                "date_ranges": date_ranges,
                "ranges": ranges,
                "sub_aggregates": sub_aggregates,
            }.items()
            if value is not None
        }
        if not request_body:
            return [
                _format_error_response(
                    "Provide `body` or aggregate fields to run quick scan aggregation.",
                    operation="GetScansAggregates",
                )
            ]

        result = self._base_query_api_call(
            operation="GetScansAggregates",
            body_params=request_body,
            error_message="Failed to aggregate quick scans",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def scan_quick_samples(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = None,
        samples: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Submit sample hashes for Quick Scan."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="ScanSamples",
                )
            ]

        request_body = body or ({"samples": samples} if samples else None)
        if request_body is None:
            return [
                _format_error_response(
                    "Provide `body` or `samples` to submit a quick scan.",
                    operation="ScanSamples",
                )
            ]

        result = self._base_query_api_call(
            operation="ScanSamples",
            body_params=request_body,
            error_message="Failed to submit quick scan samples",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
