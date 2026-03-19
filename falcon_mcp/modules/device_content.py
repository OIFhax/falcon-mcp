"""
Device Content module for Falcon MCP Server.

This module provides tools for querying and retrieving Device Content state data.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.device_content import DEVICE_CONTENT_FQL_DOCUMENTATION


class DeviceContentModule(BaseModule):
    """Module for Falcon Device Content operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_device_content_states,
            name="search_device_content_states",
        )
        self._add_tool(
            server=server,
            method=self.query_device_content_state_ids,
            name="query_device_content_state_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_device_content_states,
            name="get_device_content_states",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://device-content/states/fql-guide"),
                name="falcon_device_content_fql_guide",
                description="FQL guidance for Device Content state queries.",
                text=DEVICE_CONTENT_FQL_DOCUMENTATION,
            ),
        )

    def search_device_content_states(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for Device Content state search. IMPORTANT: use `falcon://device-content/states/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000),
        offset: int | None = Field(default=None),
        sort: str | None = Field(default=None),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Device Content states and return full state details."""
        state_ids = self._base_search_api_call(
            operation="queries_states_v1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search device content states",
        )

        if self._is_error(state_ids):
            if filter:
                return self._format_fql_error_response(
                    [state_ids],
                    filter,
                    DEVICE_CONTENT_FQL_DOCUMENTATION,
                )
            return [state_ids]

        if not state_ids:
            if filter:
                return self._format_fql_error_response(
                    [],
                    filter,
                    DEVICE_CONTENT_FQL_DOCUMENTATION,
                )
            return []

        details = self._base_get_by_ids(
            operation="entities_states_v1",
            ids=state_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def query_device_content_state_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for Device Content state ID query. IMPORTANT: use `falcon://device-content/states/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000),
        offset: int | None = Field(default=None),
        sort: str | None = Field(default=None),
    ) -> list[str] | dict[str, Any]:
        """Query Device Content state IDs."""
        result = self._base_search_api_call(
            operation="queries_states_v1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query device content state IDs",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                DEVICE_CONTENT_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                DEVICE_CONTENT_FQL_DOCUMENTATION,
            )

        return result

    def get_device_content_states(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Device Content state IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve Device Content state details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve device content state details.",
                    operation="entities_states_v1",
                )
            ]

        result = self._base_get_by_ids(
            operation="entities_states_v1",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result
