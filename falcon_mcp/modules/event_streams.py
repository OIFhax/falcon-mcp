"""
Event Streams module for Falcon MCP Server.

This module provides tools for discovering available event streams and
refreshing active stream sessions.
"""

import re
from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule, READ_ONLY_ANNOTATIONS
from falcon_mcp.resources.event_streams import EVENT_STREAMS_USAGE_GUIDE

REFRESH_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

APP_ID_PATTERN = re.compile(r"^[A-Za-z0-9]{1,32}$")


class EventStreamsModule(BaseModule):
    """Module for Event Streams operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.list_event_streams,
            name="list_event_streams",
            annotations=READ_ONLY_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.refresh_event_stream_session,
            name="refresh_event_stream_session",
            annotations=REFRESH_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        event_streams_usage_resource = TextResource(
            uri=AnyUrl("falcon://event-streams/usage-guide"),
            name="falcon_event_streams_usage_guide",
            description="Usage guidance for Event Streams discovery and refresh tools.",
            text=EVENT_STREAMS_USAGE_GUIDE,
        )

        self._add_resource(server, event_streams_usage_resource)

    @staticmethod
    def _validate_app_id(app_id: str | None, operation: str) -> dict[str, Any] | None:
        """Validate the Event Streams app identifier."""
        if not app_id:
            return _format_error_response(
                "`app_id` is required for Event Streams operations.",
                operation=operation,
            )

        if not APP_ID_PATTERN.fullmatch(app_id):
            return _format_error_response(
                "`app_id` must be 1 to 32 alphanumeric characters.",
                operation=operation,
            )

        return None

    def list_event_streams(
        self,
        app_id: str | None = Field(
            default=None,
            description="Consumer label for the event stream connection. Must be 1 to 32 alphanumeric characters. IMPORTANT: use the `falcon://event-streams/usage-guide` resource before using this tool.",
            examples={"FalconMCP01"},
        ),
        format: Literal["json", "flatjson"] = Field(
            default="json",
            description="Output format for stream events.",
        ),
    ) -> list[dict[str, Any]]:
        """Discover available event streams for a specific consumer label."""
        operation = "listAvailableStreamsOAuth2"
        validation_error = self._validate_app_id(app_id, operation)
        if validation_error:
            return [validation_error]

        response = self.client.command(
            operation,
            parameters=prepare_api_parameters({"appId": app_id, "format": format}),
        )
        result = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to list available event streams",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def refresh_event_stream_session(
        self,
        app_id: str | None = Field(
            default=None,
            description="Consumer label for the event stream connection. Must match the active stream session. IMPORTANT: use the `falcon://event-streams/usage-guide` resource before using this tool.",
            examples={"FalconMCP01"},
        ),
        partition: int = Field(
            default=0,
            ge=0,
            description="Stream partition to refresh.",
        ),
    ) -> list[dict[str, Any]]:
        """Refresh an already-active event stream session for a partition."""
        operation = "refreshActiveStreamSession"
        validation_error = self._validate_app_id(app_id, operation)
        if validation_error:
            return [validation_error]

        response = self.client.command(
            operation,
            appId=app_id,
            partition=partition,
            action_name="refresh_active_stream_session",
        )
        result = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to refresh active event stream session",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
