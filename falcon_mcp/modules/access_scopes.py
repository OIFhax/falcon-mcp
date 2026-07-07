"""
Access Scopes module for Falcon MCP Server.

This module wraps FalconPy's Access Scopes service collection.
"""

from __future__ import annotations

from typing import Any

from falconpy.access_scopes import AccessScopes  # type: ignore[import-untyped]
from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule

ACCESS_SCOPES_FQL_GUIDE = """
# Access Scopes FQL Guide

Use `falcon_query_access_scopes` to search access-scope IDs.

Supported FQL fields:
- `name`
- `created_by`
- `created_at`

Examples:
- `name:'API Clients'`
- `created_by:'user@example.com'`
"""

OPERATION_SCOPES = {
    "ListAccessScopesExternal": ["access-scope:read"],
    "QueryAccessScopesExternal": ["access-scope:read"],
}


class AccessScopesModule(BaseModule):
    """Module for Falcon access-scope lookup."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server, self.query_access_scopes, "query_access_scopes")
        self._add_tool(server, self.list_access_scopes, "list_access_scopes")

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://access-scopes/fql-guide"),
                name="falcon_access_scopes_fql_guide",
                description="FQL guidance for access-scope lookup.",
                text=ACCESS_SCOPES_FQL_GUIDE,
            ),
        )

    def query_access_scopes(
        self,
        filter: str | None = Field(default=None, description="Access Scopes FQL filter."),
        member_cid: str | None = Field(
            default=None, description="Optional Flight Control child CID."
        ),
        limit: int = Field(default=500, ge=1, le=500),
        offset: int = Field(default=0, ge=0),
        sort: str | None = Field(default=None),
    ) -> list[str] | dict[str, Any]:
        """Query access-scope IDs."""
        service = self._service(member_cid)
        response = service.query_access_scopes_external(
            parameters={"filter": filter, "limit": limit, "offset": offset, "sort": sort}
        )
        return self._handle_response(
            response,
            operation="QueryAccessScopesExternal",
            error_message="Failed to query access scopes",
        )

    def list_access_scopes(
        self,
        ids: list[str] = Field(description="Access-scope IDs to retrieve."),
        member_cid: str | None = Field(
            default=None, description="Optional Flight Control child CID."
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """List access scopes by ID."""
        if not ids:
            return _format_error_response(
                "`ids` is required.", operation="ListAccessScopesExternal"
            )
        service = self._service(member_cid)
        response = service.list_access_scopes_external(ids=ids)
        return self._handle_response(
            response,
            operation="ListAccessScopesExternal",
            error_message="Failed to list access scopes",
        )

    def _service(self, member_cid: str | None = None) -> AccessScopes:
        params: dict[str, Any] = {
            "client_id": self.client.client_id,
            "client_secret": self.client.client_secret,
            "base_url": self.client.base_url,
            "debug": self.client.debug,
            "user_agent": self.client.get_user_agent(),
        }
        if member_cid:
            params["member_cid"] = member_cid
        proxy = getattr(self.client, "proxy", None)
        if proxy:
            params["proxy"] = {"https": proxy}
        http_timeout = getattr(self.client, "http_timeout", None)
        if http_timeout:
            params["timeout"] = http_timeout
        return AccessScopes(**params)

    @staticmethod
    def _handle_response(
        response: Any,
        operation: str,
        error_message: str,
    ) -> Any:
        if not isinstance(response, dict):
            return _format_error_response(
                f"{error_message}: unexpected response type {type(response).__name__}",
                operation=operation,
            )

        status_code = response.get("status_code")
        if status_code is None or status_code >= 300:
            error = _format_error_response(
                f"{error_message}: request failed with status code {status_code}",
                details=response,
                operation=operation,
            )
            required_scopes = OPERATION_SCOPES.get(operation)
            if status_code == 403 and required_scopes:
                error["required_scopes"] = required_scopes
                error["resolution"] = (
                    "Grant the API client these Falcon scopes before retrying: "
                    + ", ".join(required_scopes)
                )
            return error

        return response.get("body", {}).get("resources", [])
