"""
ThreatGraph module for Falcon MCP Server.

This module provides read-only tools for ThreatGraph vertices, edges, and indicator pivots.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.threatgraph import THREATGRAPH_USAGE_GUIDE


class ThreatGraphModule(BaseModule):
    """Module for Falcon ThreatGraph operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.get_threatgraph_edge_types, name="get_threatgraph_edge_types")
        self._add_tool(server=server, method=self.get_threatgraph_edges, name="get_threatgraph_edges")
        self._add_tool(server=server, method=self.get_threatgraph_ran_on, name="get_threatgraph_ran_on")
        self._add_tool(server=server, method=self.get_threatgraph_summary, name="get_threatgraph_summary")
        self._add_tool(server=server, method=self.get_threatgraph_vertices_v1, name="get_threatgraph_vertices_v1")
        self._add_tool(server=server, method=self.get_threatgraph_vertices_v2, name="get_threatgraph_vertices_v2")

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://threatgraph/usage-guide"),
                name="falcon_threatgraph_usage_guide",
                description="Usage guidance for ThreatGraph pivot workflows.",
                text=THREATGRAPH_USAGE_GUIDE,
            ),
        )

    def get_threatgraph_edge_types(self) -> list[dict[str, Any]]:
        """List available ThreatGraph edge types."""
        result = self._base_query_api_call(
            operation="queries_edgetypes_get",
            error_message="Failed to retrieve ThreatGraph edge types",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def get_threatgraph_edges(
        self,
        ids: str | None = Field(default=None, description="Single vertex ID to inspect."),
        edge_type: str | None = Field(default=None, description="ThreatGraph edge type to retrieve."),
        direction: str | None = Field(default=None),
        limit: int = Field(default=100, ge=1, le=100),
        offset: int | None = Field(default=None),
        nano: bool | None = Field(default=None),
        scope: str | None = Field(default=None),
    ) -> list[dict[str, Any]]:
        """Retrieve ThreatGraph edges for a vertex."""
        if not ids or not edge_type:
            return [
                _format_error_response(
                    "Both `ids` and `edge_type` are required to retrieve ThreatGraph edges.",
                    operation="combined_edges_get",
                )
            ]

        result = self._base_query_api_call(
            operation="combined_edges_get",
            query_params={
                "ids": ids,
                "edge_type": edge_type,
                "direction": direction,
                "limit": limit,
                "offset": offset,
                "nano": nano,
                "scope": scope,
            },
            error_message="Failed to retrieve ThreatGraph edges",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def get_threatgraph_ran_on(
        self,
        type: str | None = Field(default=None, description="Indicator type such as domain or sha256."),
        value: str | None = Field(default=None, description="Indicator value to pivot on."),
        limit: int = Field(default=100, ge=1, le=100),
        offset: int | None = Field(default=None),
        nano: bool | None = Field(default=None),
    ) -> list[dict[str, Any]]:
        """Retrieve indicator sightings via ThreatGraph."""
        if not type or not value:
            return [
                _format_error_response(
                    "Both `type` and `value` are required to retrieve ThreatGraph ran-on results.",
                    operation="combined_ran_on_get",
                )
            ]

        result = self._base_query_api_call(
            operation="combined_ran_on_get",
            query_params={
                "type": type,
                "value": value,
                "limit": limit,
                "offset": offset,
                "nano": nano,
            },
            error_message="Failed to retrieve ThreatGraph ran-on results",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def get_threatgraph_summary(
        self,
        ids: list[str] | None = Field(default=None, description="ThreatGraph vertex IDs."),
        vertex_type: str = Field(default="any-vertex"),
        scope: str | None = Field(default=None),
        nano: bool | None = Field(default=None),
    ) -> list[dict[str, Any]]:
        """Retrieve a ThreatGraph summary for vertex IDs."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve a ThreatGraph summary.",
                    operation="combined_summary_get",
                )
            ]
        return self._run_vertex_operation(
            operation="combined_summary_get",
            ids=ids,
            vertex_type=vertex_type,
            scope=scope,
            nano=nano,
            error_message="Failed to retrieve ThreatGraph summary",
        )

    def get_threatgraph_vertices_v1(
        self,
        ids: list[str] | None = Field(default=None, description="ThreatGraph vertex IDs."),
        vertex_type: str = Field(default="any-vertex"),
        scope: str | None = Field(default=None),
        nano: bool | None = Field(default=None),
    ) -> list[dict[str, Any]]:
        """Retrieve ThreatGraph vertex metadata using the v1 endpoint."""
        return self._get_vertices(
            operation="entities_vertices_get",
            ids=ids,
            vertex_type=vertex_type,
            scope=scope,
            nano=nano,
        )

    def get_threatgraph_vertices_v2(
        self,
        ids: list[str] | None = Field(default=None, description="ThreatGraph vertex IDs."),
        vertex_type: str = Field(default="any-vertex"),
        scope: str | None = Field(default=None),
        nano: bool | None = Field(default=None),
    ) -> list[dict[str, Any]]:
        """Retrieve ThreatGraph vertex metadata using the v2 endpoint."""
        return self._get_vertices(
            operation="entities_vertices_getv2",
            ids=ids,
            vertex_type=vertex_type,
            scope=scope,
            nano=nano,
        )

    def _get_vertices(
        self,
        operation: str,
        ids: list[str] | None,
        vertex_type: str,
        scope: str | None,
        nano: bool | None,
    ) -> list[dict[str, Any]]:
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve ThreatGraph vertex metadata.",
                    operation=operation,
                )
            ]
        return self._run_vertex_operation(
            operation=operation,
            ids=ids,
            vertex_type=vertex_type,
            scope=scope,
            nano=nano,
            error_message="Failed to retrieve ThreatGraph vertex metadata",
        )

    def _run_vertex_operation(
        self,
        operation: str,
        ids: list[str],
        vertex_type: str,
        scope: str | None,
        nano: bool | None,
        error_message: str,
    ) -> list[dict[str, Any]]:
        response = self.client.command(
            operation,
            vertex_type=vertex_type,
            parameters=prepare_api_parameters(
                {
                    "ids": ids,
                    "scope": scope,
                    "nano": nano,
                }
            ),
        )

        result = handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result
