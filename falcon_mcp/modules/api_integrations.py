"""
API Integrations module for Falcon MCP Server.

This module provides tools for searching plugin configs and executing plugin operations.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.api_integrations import (
    API_INTEGRATIONS_FQL_GUIDE,
    API_INTEGRATIONS_SAFETY_GUIDE,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class APIIntegrationsModule(BaseModule):
    """Module for Falcon API Integrations operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_api_integration_plugin_configs,
            name="search_api_integration_plugin_configs",
        )
        self._add_tool(
            server=server,
            method=self.execute_api_integration_command,
            name="execute_api_integration_command",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.execute_api_integration_command_proxy,
            name="execute_api_integration_command_proxy",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://api-integrations/plugin-configs/fql-guide"),
                name="falcon_api_integrations_fql_guide",
                description="FQL guidance for API Integrations plugin config search.",
                text=API_INTEGRATIONS_FQL_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://api-integrations/safety-guide"),
                name="falcon_api_integrations_safety_guide",
                description="Safety guidance for API Integrations execution tools.",
                text=API_INTEGRATIONS_SAFETY_GUIDE,
            ),
        )

    def search_api_integration_plugin_configs(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for plugin config search. IMPORTANT: use `falcon://api-integrations/plugin-configs/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=500),
        offset: int = Field(default=0, ge=0),
        sort: str | None = Field(default=None),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search API Integration plugin configs and return combined details."""
        result = self._base_search_api_call(
            operation="GetCombinedPluginConfigs",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search API integration plugin configs",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response([result], filter, API_INTEGRATIONS_FQL_GUIDE)

        if not result and filter:
            return self._format_fql_error_response([], filter, API_INTEGRATIONS_FQL_GUIDE)

        return result

    def execute_api_integration_command(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = None,
        config_auth_type: str | None = None,
        config_id: str | None = None,
        definition_id: str | None = None,
        plugin_id: str | None = None,
        operation_id: str | None = None,
        request: dict[str, Any] | None = None,
        description: str | None = None,
        version: int | None = None,
    ) -> list[dict[str, Any]]:
        """Execute an API Integration command."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="ExecuteCommand",
                )
            ]

        request_body = body or self._build_execution_body(
            config_auth_type=config_auth_type,
            config_id=config_id,
            definition_id=definition_id,
            plugin_id=plugin_id,
            operation_id=operation_id,
            request=request or ({"description": description} if description else None),
            version=version,
        )
        if request_body is None:
            return [
                _format_error_response(
                    "Provide `body` or command fields to execute an API integration command.",
                    operation="ExecuteCommand",
                )
            ]

        result = self._base_query_api_call(
            operation="ExecuteCommand",
            body_params=request_body,
            error_message="Failed to execute API integration command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_api_integration_command_proxy(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = None,
        config_auth_type: str | None = None,
        config_id: str | None = None,
        definition_id: str | None = None,
        plugin_id: str | None = None,
        operation_id: str | None = None,
        request: dict[str, Any] | None = None,
        version: int | None = None,
    ) -> list[dict[str, Any]]:
        """Execute an API Integration proxy command."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="ExecuteCommandProxy",
                )
            ]

        request_body = body or self._build_execution_body(
            config_auth_type=config_auth_type,
            config_id=config_id,
            definition_id=definition_id,
            plugin_id=plugin_id,
            operation_id=operation_id,
            request=request,
            version=version,
        )
        if request_body is None:
            return [
                _format_error_response(
                    "Provide `body` or proxy command fields to execute an API integration proxy command.",
                    operation="ExecuteCommandProxy",
                )
            ]

        result = self._base_query_api_call(
            operation="ExecuteCommandProxy",
            body_params=request_body,
            error_message="Failed to execute API integration proxy command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    @staticmethod
    def _build_execution_body(
        config_auth_type: str | None,
        config_id: str | None,
        definition_id: str | None,
        plugin_id: str | None,
        operation_id: str | None,
        request: dict[str, Any] | None,
        version: int | None,
    ) -> dict[str, Any] | None:
        resource = {
            key: value
            for key, value in {
                "config_auth_type": config_auth_type,
                "config_id": config_id,
                "definition_id": definition_id,
                "id": plugin_id,
                "operation_id": operation_id,
                "request": request,
                "version": version,
            }.items()
            if value is not None
        }
        if not resource:
            return None
        return {"resources": [resource]}
