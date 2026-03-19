"""
Intelligence Feeds module for Falcon MCP Server.

This module provides tools for listing, querying, and downloading intelligence feeds.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.intelligence_feeds import INTELLIGENCE_FEEDS_USAGE_GUIDE


class IntelligenceFeedsModule(BaseModule):
    """Module for Falcon Intelligence Feeds operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.list_intelligence_feeds, name="list_intelligence_feeds")
        self._add_tool(
            server=server,
            method=self.query_intelligence_feed_archives,
            name="query_intelligence_feed_archives",
        )
        self._add_tool(
            server=server,
            method=self.download_intelligence_feed_archive,
            name="download_intelligence_feed_archive",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://intelligence-feeds/usage-guide"),
                name="falcon_intelligence_feeds_usage_guide",
                description="Usage guidance for Falcon Intelligence Feeds tools.",
                text=INTELLIGENCE_FEEDS_USAGE_GUIDE,
            ),
        )

    def list_intelligence_feeds(self) -> list[dict[str, Any]]:
        """List accessible intelligence feed types."""
        result = self._base_query_api_call(
            operation="ListFeedTypes",
            error_message="Failed to list intelligence feeds",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def query_intelligence_feed_archives(
        self,
        feed_name: str | None = Field(default=None, description="Feed name to query."),
        feed_interval: str | None = Field(default=None, description="Feed interval: dump, daily, hourly, or minutely."),
        since: str | None = Field(default=None, description="RFC3339 timestamp lower bound."),
    ) -> list[dict[str, Any]]:
        """Query accessible feed archives."""
        if not feed_name:
            return [
                _format_error_response(
                    "`feed_name` is required to query feed archives.",
                    operation="QueryFeedArchives",
                )
            ]

        result = self._base_query_api_call(
            operation="QueryFeedArchives",
            query_params={
                "feed_name": feed_name,
                "feed_interval": feed_interval,
                "since": since,
            },
            error_message="Failed to query intelligence feed archives",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def download_intelligence_feed_archive(
        self,
        feed_item_id: str | None = Field(
            default=None,
            description="Feed archive item identifier to download. Use the query tool first to discover valid IDs.",
        ),
    ) -> list[dict[str, Any]] | str:
        """Download an intelligence feed archive."""
        if not feed_item_id:
            return [
                _format_error_response(
                    "`feed_item_id` is required to download a feed archive.",
                    operation="DownloadFeedArchive",
                )
            ]

        command_response = self.client.command(
            "DownloadFeedArchive",
            parameters=prepare_api_parameters({"feed_item_id": feed_item_id}),
        )

        if isinstance(command_response, (bytes, bytearray)):
            return [
                {
                    "message": (
                        "Archive content is binary and is not rendered inline by this MCP tool. "
                        "Use a file download-capable client to save and extract it."
                    ),
                    "operation": "DownloadFeedArchive",
                    "size_bytes": len(command_response),
                }
            ]

        if not isinstance(command_response, dict):
            return [
                _format_error_response(
                    f"Unexpected response type: {type(command_response).__name__}",
                    operation="DownloadFeedArchive",
                )
            ]

        body = command_response.get("body")
        if isinstance(body, (bytes, bytearray)):
            return [
                {
                    "message": (
                        "Archive content is binary and is not rendered inline by this MCP tool. "
                        "Use a file download-capable client to save and extract it."
                    ),
                    "operation": "DownloadFeedArchive",
                    "size_bytes": len(body),
                }
            ]

        result = handle_api_response(
            command_response,
            operation="DownloadFeedArchive",
            error_message="Failed to download intelligence feed archive",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
