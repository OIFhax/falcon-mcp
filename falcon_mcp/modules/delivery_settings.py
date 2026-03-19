"""
Delivery Settings module for Falcon MCP Server.

This module provides tools to retrieve and update Falcon Delivery Settings.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.delivery_settings import (
    DELIVERY_SETTINGS_SAFETY_GUIDE,
    DELIVERY_SETTINGS_USAGE_GUIDE,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class DeliverySettingsModule(BaseModule):
    """Module for Falcon Delivery Settings operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.get_delivery_settings,
            name="get_delivery_settings",
        )
        self._add_tool(
            server=server,
            method=self.create_delivery_settings,
            name="create_delivery_settings",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://delivery-settings/usage-guide"),
                name="falcon_delivery_settings_usage_guide",
                description="Guidance for Falcon Delivery Settings tools.",
                text=DELIVERY_SETTINGS_USAGE_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://delivery-settings/safety-guide"),
                name="falcon_delivery_settings_safety_guide",
                description="Safety guidance for Falcon Delivery Settings write operations.",
                text=DELIVERY_SETTINGS_SAFETY_GUIDE,
            ),
        )

    def get_delivery_settings(self) -> list[dict[str, Any]]:
        """Retrieve Falcon Delivery Settings."""
        result = self._base_query_api_call(
            operation="GetDeliverySettings",
            error_message="Failed to retrieve delivery settings",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_delivery_settings(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = None,
        delivery_settings: list[dict[str, Any]] | None = None,
        delivery_cadence: str | None = Field(
            default=None,
            description="Convenience field for a single delivery setting cadence.",
        ),
        delivery_type: str | None = Field(
            default=None,
            description="Convenience field for a single delivery setting type.",
        ),
    ) -> list[dict[str, Any]]:
        """Create or update Falcon Delivery Settings."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="PostDeliverySettings",
                )
            ]

        request_body = body
        if request_body is None:
            if delivery_settings is not None:
                request_body = {"delivery_settings": delivery_settings}
            elif delivery_cadence or delivery_type:
                setting = {
                    key: value
                    for key, value in {
                        "delivery_cadence": delivery_cadence,
                        "delivery_type": delivery_type,
                    }.items()
                    if value is not None
                }
                request_body = {"delivery_settings": [setting]}
            else:
                return [
                    _format_error_response(
                        "Provide `body`, `delivery_settings`, or convenience fields to create delivery settings.",
                        operation="PostDeliverySettings",
                    )
                ]

        result = self._base_query_api_call(
            operation="PostDeliverySettings",
            body_params=request_body,
            error_message="Failed to create delivery settings",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
