"""
Drift Indicators module for Falcon MCP Server.

This module provides tools for counting, querying, and retrieving
drift indicator entities.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.drift_indicators import SEARCH_DRIFT_INDICATORS_FQL_DOCUMENTATION


class DriftIndicatorsModule(BaseModule):
    """Module for Drift Indicators operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.get_drift_indicator_values_by_date,
            name="get_drift_indicator_values_by_date",
        )
        self._add_tool(
            server=server,
            method=self.get_drift_indicator_count,
            name="get_drift_indicator_count",
        )
        self._add_tool(
            server=server,
            method=self.query_drift_indicator_ids,
            name="query_drift_indicator_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_drift_indicator_details,
            name="get_drift_indicator_details",
        )
        self._add_tool(
            server=server,
            method=self.search_drift_indicator_entities,
            name="search_drift_indicator_entities",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        drift_indicators_guide = TextResource(
            uri=AnyUrl("falcon://drift-indicators/fql-guide"),
            name="falcon_drift_indicators_fql_guide",
            description="FQL guidance for Drift Indicators query and search tools.",
            text=SEARCH_DRIFT_INDICATORS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, drift_indicators_guide)

    def get_drift_indicator_values_by_date(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for drift indicator counts by date. IMPORTANT: use `falcon://drift-indicators/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=7,
            ge=1,
            le=365,
            description="Maximum number of date buckets to return. [1-365]",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Return drift indicator counts grouped by date."""
        result = self._base_query_api_call(
            operation="GetDriftIndicatorsValuesByDate",
            query_params={"filter": filter, "limit": limit},
            error_message="Failed to retrieve drift indicator values by date",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_drift_indicator_count(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for total drift indicator count. IMPORTANT: use `falcon://drift-indicators/fql-guide` when building this parameter.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Return the total count of drift indicators."""
        result = self._base_query_api_call(
            operation="ReadDriftIndicatorsCount",
            query_params={"filter": filter},
            error_message="Failed to retrieve drift indicator count",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def query_drift_indicator_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for drift indicator ID query. IMPORTANT: use `falcon://drift-indicators/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of IDs to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for drift indicator IDs.",
            examples={"occurred_at.desc", "severity.asc"},
        ),
    ) -> list[str] | dict[str, Any]:
        """Query drift indicator IDs."""
        result = self._base_search_api_call(
            operation="SearchDriftIndicators",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query drift indicator IDs",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_DRIFT_INDICATORS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_DRIFT_INDICATORS_FQL_DOCUMENTATION,
            )

        return result

    def get_drift_indicator_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Drift indicator IDs to retrieve. Maximum 100 IDs.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve drift indicator entities by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve drift indicator details.",
                    operation="ReadDriftIndicatorEntities",
                )
            ]

        result = self._base_get_by_ids(
            operation="ReadDriftIndicatorEntities",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def search_drift_indicator_entities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for combined drift indicator search. IMPORTANT: use `falcon://drift-indicators/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of drift indicators to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for combined drift indicator search.",
            examples={"occurred_at.desc", "severity.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search drift indicators and return full entity records."""
        result = self._base_search_api_call(
            operation="SearchAndReadDriftIndicatorEntities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search drift indicator entities",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_DRIFT_INDICATORS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_DRIFT_INDICATORS_FQL_DOCUMENTATION,
            )

        return result
