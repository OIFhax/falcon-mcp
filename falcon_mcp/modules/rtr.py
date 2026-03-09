"""
Real Time Response (RTR) module for Falcon MCP Server.

This module provides tools for searching RTR sessions and managing
single-host RTR session workflows.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.rtr import SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION


class RTRModule(BaseModule):
    """Module for Real Time Response operations via FalconPy."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_rtr_sessions,
            name="search_rtr_sessions",
        )

        self._add_tool(
            server=server,
            method=self.init_rtr_session,
            name="init_rtr_session",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.execute_rtr_command,
            name="execute_rtr_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.check_rtr_command_status,
            name="check_rtr_command_status",
        )

        self._add_tool(
            server=server,
            method=self.delete_rtr_session,
            name="delete_rtr_session",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.delete_rtr_queued_session,
            name="delete_rtr_queued_session",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_rtr_sessions_fql_resource = TextResource(
            uri=AnyUrl("falcon://rtr/sessions/fql-guide"),
            name="falcon_search_rtr_sessions_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_rtr_sessions` tool.",
            text=SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_rtr_sessions_fql_resource)

    def search_rtr_sessions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for RTR session search. IMPORTANT: use the `falcon://rtr/sessions/fql-guide` resource when building this filter parameter.",
            examples={"user_id:'@me'", "aid:'1234567890abcdef1234567890abcdef'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of session IDs to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort RTR sessions using FQL syntax.

                Supported examples: date_created.asc, date_updated.desc, user_id|asc
            """).strip(),
            examples={"date_created.desc", "user_id|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR sessions and return full session details."""
        session_ids = self._base_search_api_call(
            operation="RTR_ListAllSessions",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search RTR sessions",
        )

        if self._is_error(session_ids):
            if filter:
                return self._format_fql_error_response(
                    [session_ids], filter, SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION
                )
            return [session_ids]

        if not session_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="RTR_ListSessions",
            ids=session_ids,
        )

        if self._is_error(details):
            return [details]

        return details

    def init_rtr_session(
        self,
        device_id: str | None = Field(
            default=None,
            description="Host agent ID to initialize the RTR session on. Required when `body` is not provided.",
        ),
        origin: str | None = Field(
            default=None,
            description="Optional origin label for the session request.",
        ),
        queue_offline: bool | None = Field(
            default=None,
            description="Queue the request for execution when the host is offline.",
        ),
        timeout: int | None = Field(
            default=None,
            ge=1,
            le=600,
            description="Timeout for the request in seconds. (Min: 1, Max: 600)",
        ),
        timeout_duration: str | None = Field(
            default=None,
            description="Timeout duration string (for example: 30s, 2m).",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Initialize an RTR session on a single host."""
        request_body = body
        if request_body is None:
            if not device_id:
                return [
                    _format_error_response(
                        "`device_id` is required when `body` is not provided.",
                        operation="RTR_InitSession",
                    )
                ]

            request_body = {"device_id": device_id}
            if origin:
                request_body["origin"] = origin
            if queue_offline is not None:
                request_body["queue_offline"] = queue_offline

        result = self._base_query_api_call(
            operation="RTR_InitSession",
            query_params={
                "timeout": timeout,
                "timeout_duration": timeout_duration,
            },
            body_params=request_body,
            error_message="Failed to initialize RTR session",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_rtr_command(
        self,
        base_command: str | None = Field(
            default=None,
            description="RTR read-only command to execute (for example: ls, cd, ps). Required when `body` is not provided.",
        ),
        command_string: str | None = Field(
            default=None,
            description="Full command string to execute. Required when `body` is not provided.",
        ),
        session_id: str | None = Field(
            default=None,
            description="RTR session ID for command execution. Required when `device_id` is not provided and `body` is not provided.",
        ),
        device_id: str | None = Field(
            default=None,
            description="Host agent ID to target if a session ID is not provided.",
        ),
        sequence_id: int | None = Field(
            default=None,
            ge=0,
            description="Command sequence ID. Mapped to the `id` field in the Falcon API request body.",
        ),
        persist: bool | None = Field(
            default=None,
            description="Execute this command when the host returns to service.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Execute an RTR read-only command on a single host."""
        request_body = body
        if request_body is None:
            if not base_command or not command_string:
                return [
                    _format_error_response(
                        "`base_command` and `command_string` are required when `body` is not provided.",
                        operation="RTR_ExecuteCommand",
                    )
                ]

            if not session_id and not device_id:
                return [
                    _format_error_response(
                        "Either `session_id` or `device_id` is required when `body` is not provided.",
                        operation="RTR_ExecuteCommand",
                    )
                ]

            request_body = {
                "base_command": base_command,
                "command_string": command_string,
            }
            if session_id:
                request_body["session_id"] = session_id
            if device_id:
                request_body["device_id"] = device_id
            if sequence_id is not None:
                request_body["id"] = sequence_id
            if persist is not None:
                request_body["persist"] = persist

        result = self._base_query_api_call(
            operation="RTR_ExecuteCommand",
            body_params=request_body,
            error_message="Failed to execute RTR command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def check_rtr_command_status(
        self,
        cloud_request_id: str | None = Field(
            default=None,
            description="Cloud request ID returned from `falcon_execute_rtr_command`.",
        ),
        sequence_id: int = Field(
            default=0,
            ge=0,
            description="Command response sequence chunk index.",
        ),
    ) -> list[dict[str, Any]]:
        """Check status for an RTR command execution request."""
        if not cloud_request_id:
            return [
                _format_error_response(
                    "`cloud_request_id` is required to check command status.",
                    operation="RTR_CheckCommandStatus",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_CheckCommandStatus",
            query_params={
                "cloud_request_id": cloud_request_id,
                "sequence_id": sequence_id,
            },
            error_message="Failed to check RTR command status",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_rtr_session(
        self,
        session_id: str | None = Field(
            default=None,
            description="RTR session ID to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete an RTR session by session ID."""
        if not session_id:
            return [
                _format_error_response(
                    "`session_id` is required when deleting an RTR session.",
                    operation="RTR_DeleteSession",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_DeleteSession",
            query_params={"session_id": session_id},
            error_message="Failed to delete RTR session",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_rtr_queued_session(
        self,
        session_id: str | None = Field(
            default=None,
            description="Queued RTR session ID to delete.",
        ),
        cloud_request_id: str | None = Field(
            default=None,
            description="Cloud request ID tied to the queued command.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete a queued RTR session by session and request IDs."""
        if not session_id or not cloud_request_id:
            return [
                _format_error_response(
                    "Both `session_id` and `cloud_request_id` are required to delete a queued RTR session.",
                    operation="RTR_DeleteQueuedSession",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_DeleteQueuedSession",
            query_params={
                "session_id": session_id,
                "cloud_request_id": cloud_request_id,
            },
            error_message="Failed to delete queued RTR session",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
