"""
Spotlight module for Falcon MCP Server.

This module provides full Falcon Spotlight Vulnerabilities service collection coverage:
combined search, ID query, vulnerability detail retrieval, and remediation retrieval.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.spotlight import (
    REMEDIATIONS_USAGE_GUIDE,
    SEARCH_VULNERABILITIES_FQL_DOCUMENTATION,
)


class SpotlightModule(BaseModule):
    """Module for CrowdStrike Falcon Spotlight vulnerabilities."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_vulnerabilities,
            name="search_vulnerabilities",
        )
        self._add_tool(
            server=server,
            method=self.query_vulnerability_ids,
            name="query_vulnerability_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_vulnerability_details,
            name="get_vulnerability_details",
        )
        self._add_tool(
            server=server,
            method=self.get_remediation_details,
            name="get_remediation_details",
        )
        self._add_tool(
            server=server,
            method=self.get_remediation_details_v2,
            name="get_remediation_details_v2",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_vulnerabilities_fql_resource = TextResource(
            uri=AnyUrl("falcon://spotlight/vulnerabilities/fql-guide"),
            name="falcon_search_vulnerabilities_fql_guide",
            description="FQL guidance for Spotlight vulnerability search and query tools.",
            text=SEARCH_VULNERABILITIES_FQL_DOCUMENTATION,
        )

        remediations_usage_resource = TextResource(
            uri=AnyUrl("falcon://spotlight/remediations/usage-guide"),
            name="falcon_spotlight_remediations_usage_guide",
            description="Guidance for retrieving Spotlight remediations by remediation ID.",
            text=REMEDIATIONS_USAGE_GUIDE,
        )

        self._add_resource(server, search_vulnerabilities_fql_resource)
        self._add_resource(server, remediations_usage_resource)

    def search_vulnerabilities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for combined vulnerability search. IMPORTANT: use the `falcon://spotlight/vulnerabilities/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of vulnerability records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort vulnerabilities. Example: `created_timestamp|desc`.",
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token from previous response.",
        ),
        facet: str | None = Field(
            default=None,
            description="Optional detail block. Example: `host_info`, `cve`, `remediation`, or `evaluation_logic`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Spotlight vulnerabilities using the combined endpoint."""
        result = self._base_search_api_call(
            operation="combinedQueryVulnerabilities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "after": after,
                "facet": facet,
            },
            error_message="Failed to search vulnerabilities",
        )

        if self._is_error(result):
            if filter:
                return self._format_fql_error_response(
                    [result],
                    filter,
                    SEARCH_VULNERABILITIES_FQL_DOCUMENTATION,
                )
            return [result]

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_VULNERABILITIES_FQL_DOCUMENTATION,
            )

        return result

    def query_vulnerability_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for vulnerability ID query. IMPORTANT: use the `falcon://spotlight/vulnerabilities/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=400,
            description="Maximum number of IDs to return. [1-400]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort vulnerabilities. Example: `created_timestamp|desc`.",
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token from previous response.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query Spotlight vulnerability IDs."""
        result = self._base_search_api_call(
            operation="queryVulnerabilities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "after": after,
            },
            error_message="Failed to query vulnerability IDs",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_VULNERABILITIES_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_VULNERABILITIES_FQL_DOCUMENTATION,
            )

        return result

    def get_vulnerability_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Vulnerability IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Get vulnerability detail records by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve vulnerability details.",
                    operation="getVulnerabilities",
                )
            ]

        result = self._base_get_by_ids(
            operation="getVulnerabilities",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def get_remediation_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Remediation IDs to retrieve using `getRemediations`.",
        ),
    ) -> list[dict[str, Any]]:
        """Get remediation detail records by ID (v1 endpoint)."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve remediation details.",
                    operation="getRemediations",
                )
            ]

        result = self._base_get_by_ids(
            operation="getRemediations",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def get_remediation_details_v2(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Remediation IDs to retrieve using `getRemediationsV2`.",
        ),
    ) -> list[dict[str, Any]]:
        """Get remediation detail records by ID (v2 endpoint)."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve remediation details.",
                    operation="getRemediationsV2",
                )
            ]

        result = self._base_get_by_ids(
            operation="getRemediationsV2",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result
