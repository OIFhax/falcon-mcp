"""
Real Time Response (RTR) module for Falcon MCP Server.

This module provides tools for searching RTR sessions, running RTR / RTR Admin
commands, and querying RTR audit sessions.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.rtr import (
    SEARCH_RTR_ADMIN_FQL_DOCUMENTATION,
    SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION,
    SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION,
)


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
            method=self.search_rtr_admin_scripts,
            name="search_rtr_admin_scripts",
        )

        self._add_tool(
            server=server,
            method=self.search_rtr_admin_put_files,
            name="search_rtr_admin_put_files",
        )

        self._add_tool(
            server=server,
            method=self.execute_rtr_admin_command,
            name="execute_rtr_admin_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.execute_rtr_admin_batch_command,
            name="execute_rtr_admin_batch_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.check_rtr_admin_command_status,
            name="check_rtr_admin_command_status",
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

        self._add_tool(
            server=server,
            method=self.search_rtr_audit_sessions,
            name="search_rtr_audit_sessions",
        )
        self._add_tool(
            server=server,
            method=self.aggregate_rtr_sessions,
            name="aggregate_rtr_sessions",
        )
        self._add_tool(
            server=server,
            method=self.search_rtr_queued_sessions,
            name="search_rtr_queued_sessions",
        )
        self._add_tool(
            server=server,
            method=self.pulse_rtr_session,
            name="pulse_rtr_session",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.execute_rtr_active_responder_command,
            name="execute_rtr_active_responder_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.check_rtr_active_responder_command_status,
            name="check_rtr_active_responder_command_status",
        )
        self._add_tool(
            server=server,
            method=self.batch_init_rtr_sessions,
            name="batch_init_rtr_sessions",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.batch_refresh_rtr_sessions,
            name="batch_refresh_rtr_sessions",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.execute_rtr_batch_command,
            name="execute_rtr_batch_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.execute_rtr_batch_active_responder_command,
            name="execute_rtr_batch_active_responder_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.execute_rtr_batch_get_command,
            name="execute_rtr_batch_get_command",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.check_rtr_batch_get_command_status,
            name="check_rtr_batch_get_command_status",
        )
        self._add_tool(
            server=server,
            method=self.get_rtr_extracted_file_contents,
            name="get_rtr_extracted_file_contents",
        )
        self._add_tool(
            server=server,
            method=self.list_rtr_files_v1,
            name="list_rtr_files_v1",
        )
        self._add_tool(
            server=server,
            method=self.list_rtr_files_v2,
            name="list_rtr_files_v2",
        )
        self._add_tool(
            server=server,
            method=self.delete_rtr_file_v1,
            name="delete_rtr_file_v1",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.delete_rtr_file_v2,
            name="delete_rtr_file_v2",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.search_rtr_falcon_scripts,
            name="search_rtr_falcon_scripts",
        )
        self._add_tool(
            server=server,
            method=self.get_rtr_falcon_script_details,
            name="get_rtr_falcon_script_details",
        )
        self._add_tool(
            server=server,
            method=self.get_rtr_put_file_contents,
            name="get_rtr_put_file_contents",
        )
        self._add_tool(
            server=server,
            method=self.get_rtr_admin_put_file_details_v2,
            name="get_rtr_admin_put_file_details_v2",
        )
        self._add_tool(
            server=server,
            method=self.create_rtr_admin_put_file_v1,
            name="create_rtr_admin_put_file_v1",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.create_rtr_admin_put_file_v2,
            name="create_rtr_admin_put_file_v2",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.delete_rtr_admin_put_file,
            name="delete_rtr_admin_put_file",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.get_rtr_admin_script_details_v2,
            name="get_rtr_admin_script_details_v2",
        )
        self._add_tool(
            server=server,
            method=self.create_rtr_admin_script_v1,
            name="create_rtr_admin_script_v1",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.create_rtr_admin_script_v2,
            name="create_rtr_admin_script_v2",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.update_rtr_admin_script_v1,
            name="update_rtr_admin_script_v1",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.update_rtr_admin_script_v2,
            name="update_rtr_admin_script_v2",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.delete_rtr_admin_script,
            name="delete_rtr_admin_script",
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

        search_rtr_admin_fql_resource = TextResource(
            uri=AnyUrl("falcon://rtr/admin/fql-guide"),
            name="falcon_search_rtr_admin_fql_guide",
            description="Contains the guide for the `filter` parameter of RTR admin search tools.",
            text=SEARCH_RTR_ADMIN_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_rtr_admin_fql_resource)

        search_rtr_audit_sessions_fql_resource = TextResource(
            uri=AnyUrl("falcon://rtr/audit/sessions/fql-guide"),
            name="falcon_search_rtr_audit_sessions_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_rtr_audit_sessions` tool.",
            text=SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_rtr_audit_sessions_fql_resource)

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

    def search_rtr_admin_scripts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for RTR admin script search. IMPORTANT: use the `falcon://rtr/admin/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of script IDs to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort RTR admin scripts using FQL syntax.

                Supported examples: created_at.desc, modified_at.asc, name|asc
            """).strip(),
            examples={"created_at.desc", "name|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR admin scripts and return full script details."""
        script_ids = self._base_search_api_call(
            operation="RTR_ListScripts",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search RTR admin scripts",
        )

        if self._is_error(script_ids):
            if filter:
                return self._format_fql_error_response(
                    [script_ids], filter, SEARCH_RTR_ADMIN_FQL_DOCUMENTATION
                )
            return [script_ids]

        if not script_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_RTR_ADMIN_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="RTR_GetScripts",
            ids=script_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_rtr_admin_put_files(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for RTR admin put-file search. IMPORTANT: use the `falcon://rtr/admin/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of put-file IDs to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort RTR admin put-files using FQL syntax.

                Supported examples: created_at.desc, modified_at.asc, name|asc
            """).strip(),
            examples={"created_at.desc", "name|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR admin put-files and return full put-file details."""
        put_file_ids = self._base_search_api_call(
            operation="RTR_ListPut_Files",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search RTR admin put-files",
        )

        if self._is_error(put_file_ids):
            if filter:
                return self._format_fql_error_response(
                    [put_file_ids], filter, SEARCH_RTR_ADMIN_FQL_DOCUMENTATION
                )
            return [put_file_ids]

        if not put_file_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_RTR_ADMIN_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="RTR_GetPut_Files",
            ids=put_file_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def execute_rtr_admin_command(
        self,
        base_command: str | None = Field(
            default=None,
            description="RTR admin command to execute (for example: get, cp, runscript). Required when `body` is not provided.",
        ),
        command_string: str | None = Field(
            default=None,
            description="Full admin command string to execute. Required when `body` is not provided.",
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
        """Execute an RTR admin command on a single host."""
        request_body = body
        if request_body is None:
            if not base_command or not command_string:
                return [
                    _format_error_response(
                        "`base_command` and `command_string` are required when `body` is not provided.",
                        operation="RTR_ExecuteAdminCommand",
                    )
                ]

            if not session_id and not device_id:
                return [
                    _format_error_response(
                        "Either `session_id` or `device_id` is required when `body` is not provided.",
                        operation="RTR_ExecuteAdminCommand",
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
            operation="RTR_ExecuteAdminCommand",
            body_params=request_body,
            error_message="Failed to execute RTR admin command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_rtr_admin_batch_command(
        self,
        base_command: str | None = Field(
            default=None,
            description="RTR admin command to execute in batch mode. Required when `body` is not provided.",
        ),
        batch_id: str | None = Field(
            default=None,
            description="Batch session ID returned from RTR batch session initialization. Required when `body` is not provided.",
        ),
        command_string: str | None = Field(
            default=None,
            description="Full command string to execute across the batch. Required when `body` is not provided.",
        ),
        optional_hosts: list[str] | None = Field(
            default=None,
            description="Optional subset of host IDs from the batch to target.",
        ),
        persist_all: bool | None = Field(
            default=None,
            description="Execute this command for offline hosts when they return to service.",
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
        host_timeout_duration: str | None = Field(
            default=None,
            description="Per-host timeout duration string (for example: 20s, 1m).",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Execute an RTR admin command in batch mode."""
        request_body = body
        if request_body is None:
            if not base_command or not batch_id or not command_string:
                return [
                    _format_error_response(
                        "`base_command`, `batch_id`, and `command_string` are required when `body` is not provided.",
                        operation="BatchAdminCmd",
                    )
                ]

            request_body = {
                "base_command": base_command,
                "batch_id": batch_id,
                "command_string": command_string,
            }
            if optional_hosts:
                request_body["optional_hosts"] = optional_hosts
            if persist_all is not None:
                request_body["persist_all"] = persist_all

        result = self._base_query_api_call(
            operation="BatchAdminCmd",
            query_params={
                "timeout": timeout,
                "timeout_duration": timeout_duration,
                "host_timeout_duration": host_timeout_duration,
            },
            body_params=request_body,
            error_message="Failed to execute RTR admin batch command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def check_rtr_admin_command_status(
        self,
        cloud_request_id: str | None = Field(
            default=None,
            description="Cloud request ID returned from `falcon_execute_rtr_admin_command` or `falcon_execute_rtr_admin_batch_command`.",
        ),
        sequence_id: int = Field(
            default=0,
            ge=0,
            description="Command response sequence chunk index.",
        ),
    ) -> list[dict[str, Any]]:
        """Check status for an RTR admin command request."""
        if not cloud_request_id:
            return [
                _format_error_response(
                    "`cloud_request_id` is required to check admin command status.",
                    operation="RTR_CheckAdminCommandStatus",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_CheckAdminCommandStatus",
            query_params={
                "cloud_request_id": cloud_request_id,
                "sequence_id": sequence_id,
            },
            error_message="Failed to check RTR admin command status",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_rtr_audit_sessions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for RTR audit session search. IMPORTANT: use the `falcon://rtr/audit/sessions/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of audit sessions to return. (Max: 5000)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return sessions.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort RTR audit sessions using FQL syntax.

                Supported examples: created_at.desc, updated_at.asc, deleted_at|desc
            """).strip(),
            examples={"created_at.desc", "updated_at|asc"},
        ),
        with_command_info: bool = Field(
            default=False,
            description="Include command metadata (cloud request IDs and log fields) in session records.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search RTR audit sessions."""
        result = self._base_search_api_call(
            operation="RTRAuditSessions",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "with_command_info": with_command_info,
            },
            error_message="Failed to search RTR audit sessions",
        )

        if self._is_error(result):
            if filter:
                return self._format_fql_error_response(
                    [result], filter, SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION
                )
            return [result]

        if not result:
            if filter:
                return self._format_fql_error_response(
                    [], filter, SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION
                )
            return []

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

    def aggregate_rtr_sessions(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Aggregation specification body for `RTR_AggregateSessions`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate analysis over RTR session data."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for RTR session aggregation.",
                    operation="RTR_AggregateSessions",
                )
            ]

        command_response = self.client.command("RTR_AggregateSessions", body=body)
        result = handle_api_response(
            command_response,
            operation="RTR_AggregateSessions",
            error_message="Failed to aggregate RTR sessions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_rtr_queued_sessions(
        self,
        session_ids: list[str] | None = Field(
            default=None,
            description="RTR session IDs to retrieve queued command metadata for.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve queued-session metadata by session IDs."""
        if not session_ids:
            return [
                _format_error_response(
                    "`session_ids` is required to retrieve queued RTR sessions.",
                    operation="RTR_ListQueuedSessions",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_ListQueuedSessions",
            body_params={"ids": session_ids},
            error_message="Failed to search queued RTR sessions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def pulse_rtr_session(
        self,
        device_id: str | None = Field(
            default=None,
            description="Host agent ID to refresh the RTR session on. Required when `body` is not provided.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Refresh a session timeout on a single host."""
        request_body = body
        if request_body is None:
            if not device_id:
                return [
                    _format_error_response(
                        "`device_id` is required when `body` is not provided.",
                        operation="RTR_PulseSession",
                    )
                ]
            request_body = {"device_id": device_id}

        result = self._base_query_api_call(
            operation="RTR_PulseSession",
            body_params=request_body,
            error_message="Failed to pulse RTR session",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_rtr_active_responder_command(
        self,
        base_command: str | None = Field(
            default=None,
            description="Active-responder command to execute. Required when `body` is not provided.",
        ),
        command_string: str | None = Field(
            default=None,
            description="Full command string. Required when `body` is not provided.",
        ),
        session_id: str | None = Field(
            default=None,
            description="RTR session ID. Required when `device_id` is not provided and `body` is not provided.",
        ),
        device_id: str | None = Field(
            default=None,
            description="Host agent ID to target if a session ID is not provided.",
        ),
        sequence_id: int | None = Field(
            default=None,
            ge=0,
            description="Optional command sequence ID.",
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
        """Execute an active-responder command on a single host."""
        request_body = body
        if request_body is None:
            if not base_command or not command_string:
                return [
                    _format_error_response(
                        "`base_command` and `command_string` are required when `body` is not provided.",
                        operation="RTR_ExecuteActiveResponderCommand",
                    )
                ]

            if not session_id and not device_id:
                return [
                    _format_error_response(
                        "Either `session_id` or `device_id` is required when `body` is not provided.",
                        operation="RTR_ExecuteActiveResponderCommand",
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
            operation="RTR_ExecuteActiveResponderCommand",
            body_params=request_body,
            error_message="Failed to execute RTR active-responder command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def check_rtr_active_responder_command_status(
        self,
        cloud_request_id: str | None = Field(
            default=None,
            description="Cloud request ID returned from `falcon_execute_rtr_active_responder_command`.",
        ),
        sequence_id: int = Field(
            default=0,
            ge=0,
            description="Command response sequence chunk index.",
        ),
    ) -> list[dict[str, Any]]:
        """Check status for an active-responder command request."""
        if not cloud_request_id:
            return [
                _format_error_response(
                    "`cloud_request_id` is required to check active-responder command status.",
                    operation="RTR_CheckActiveResponderCommandStatus",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_CheckActiveResponderCommandStatus",
            query_params={
                "cloud_request_id": cloud_request_id,
                "sequence_id": sequence_id,
            },
            error_message="Failed to check RTR active-responder command status",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def batch_init_rtr_sessions(
        self,
        host_ids: list[str] | None = Field(
            default=None,
            description="Host agent IDs to initialize sessions on. Required when `body` is not provided.",
        ),
        existing_batch_id: str | None = Field(
            default=None,
            description="Optional existing batch ID to append hosts to.",
        ),
        queue_offline: bool | None = Field(
            default=None,
            description="Queue sessions for offline hosts.",
        ),
        timeout: int | None = Field(default=None, ge=1, le=600, description="Timeout in seconds."),
        timeout_duration: str | None = Field(default=None, description="Request timeout duration string."),
        host_timeout_duration: str | None = Field(default=None, description="Per-host timeout duration string."),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Initialize RTR sessions in batch mode."""
        request_body = body
        if request_body is None:
            if not host_ids:
                return [
                    _format_error_response(
                        "`host_ids` is required when `body` is not provided.",
                        operation="BatchInitSessions",
                    )
                ]
            request_body = {"host_ids": host_ids}
            if existing_batch_id:
                request_body["existing_batch_id"] = existing_batch_id
            if queue_offline is not None:
                request_body["queue_offline"] = queue_offline

        result = self._base_query_api_call(
            operation="BatchInitSessions",
            query_params={
                "timeout": timeout,
                "timeout_duration": timeout_duration,
                "host_timeout_duration": host_timeout_duration,
            },
            body_params=request_body,
            error_message="Failed to batch initialize RTR sessions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def batch_refresh_rtr_sessions(
        self,
        batch_id: str | None = Field(
            default=None,
            description="Batch ID to refresh. Required when `body` is not provided.",
        ),
        hosts_to_remove: list[str] | None = Field(
            default=None,
            description="Optional host IDs to remove from the batch session.",
        ),
        timeout: int | None = Field(default=None, ge=1, le=600, description="Timeout in seconds."),
        timeout_duration: str | None = Field(default=None, description="Request timeout duration string."),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Refresh RTR batch session heartbeats."""
        request_body = body
        if request_body is None:
            if not batch_id:
                return [
                    _format_error_response(
                        "`batch_id` is required when `body` is not provided.",
                        operation="BatchRefreshSessions",
                    )
                ]
            request_body = {"batch_id": batch_id}
            if hosts_to_remove:
                request_body["hosts_to_remove"] = hosts_to_remove

        result = self._base_query_api_call(
            operation="BatchRefreshSessions",
            query_params={
                "timeout": timeout,
                "timeout_duration": timeout_duration,
            },
            body_params=request_body,
            error_message="Failed to batch refresh RTR sessions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_rtr_batch_command(
        self,
        base_command: str | None = Field(
            default=None,
            description="Read-only RTR command to execute in batch mode. Required when `body` is not provided.",
        ),
        batch_id: str | None = Field(
            default=None,
            description="Batch session ID. Required when `body` is not provided.",
        ),
        command_string: str | None = Field(
            default=None,
            description="Full command string. Required when `body` is not provided.",
        ),
        optional_hosts: list[str] | None = Field(
            default=None,
            description="Optional subset of host IDs from the batch to target.",
        ),
        timeout: int | None = Field(default=None, ge=1, le=600, description="Timeout in seconds."),
        timeout_duration: str | None = Field(default=None, description="Request timeout duration string."),
        host_timeout_duration: str | None = Field(default=None, description="Per-host timeout duration string."),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Execute a read-only RTR command in batch mode."""
        request_body = body
        if request_body is None:
            if not base_command or not batch_id or not command_string:
                return [
                    _format_error_response(
                        "`base_command`, `batch_id`, and `command_string` are required when `body` is not provided.",
                        operation="BatchCmd",
                    )
                ]

            request_body = {
                "base_command": base_command,
                "batch_id": batch_id,
                "command_string": command_string,
            }
            if optional_hosts:
                request_body["optional_hosts"] = optional_hosts

        result = self._base_query_api_call(
            operation="BatchCmd",
            query_params={
                "timeout": timeout,
                "timeout_duration": timeout_duration,
                "host_timeout_duration": host_timeout_duration,
            },
            body_params=request_body,
            error_message="Failed to execute RTR batch command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_rtr_batch_active_responder_command(
        self,
        base_command: str | None = Field(
            default=None,
            description="Active-responder RTR command to execute in batch mode. Required when `body` is not provided.",
        ),
        batch_id: str | None = Field(
            default=None,
            description="Batch session ID. Required when `body` is not provided.",
        ),
        command_string: str | None = Field(
            default=None,
            description="Full command string. Required when `body` is not provided.",
        ),
        optional_hosts: list[str] | None = Field(
            default=None,
            description="Optional subset of host IDs from the batch to target.",
        ),
        timeout: int | None = Field(default=None, ge=1, le=600, description="Timeout in seconds."),
        timeout_duration: str | None = Field(default=None, description="Request timeout duration string."),
        host_timeout_duration: str | None = Field(default=None, description="Per-host timeout duration string."),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Execute an active-responder RTR command in batch mode."""
        request_body = body
        if request_body is None:
            if not base_command or not batch_id or not command_string:
                return [
                    _format_error_response(
                        "`base_command`, `batch_id`, and `command_string` are required when `body` is not provided.",
                        operation="BatchActiveResponderCmd",
                    )
                ]

            request_body = {
                "base_command": base_command,
                "batch_id": batch_id,
                "command_string": command_string,
            }
            if optional_hosts:
                request_body["optional_hosts"] = optional_hosts

        result = self._base_query_api_call(
            operation="BatchActiveResponderCmd",
            query_params={
                "timeout": timeout,
                "timeout_duration": timeout_duration,
                "host_timeout_duration": host_timeout_duration,
            },
            body_params=request_body,
            error_message="Failed to execute RTR batch active-responder command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_rtr_batch_get_command(
        self,
        batch_id: str | None = Field(
            default=None,
            description="Batch session ID to execute `get` against. Required when `body` is not provided.",
        ),
        file_path: str | None = Field(
            default=None,
            description="Full path to file to retrieve from hosts. Required when `body` is not provided.",
        ),
        optional_hosts: list[str] | None = Field(
            default=None,
            description="Optional subset of host IDs from the batch to target.",
        ),
        timeout: int | None = Field(default=None, ge=1, le=600, description="Timeout in seconds."),
        timeout_duration: str | None = Field(default=None, description="Request timeout duration string."),
        host_timeout_duration: str | None = Field(default=None, description="Per-host timeout duration string."),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Execute batch `get` file retrieval command."""
        request_body = body
        if request_body is None:
            if not batch_id or not file_path:
                return [
                    _format_error_response(
                        "`batch_id` and `file_path` are required when `body` is not provided.",
                        operation="BatchGetCmd",
                    )
                ]

            request_body = {
                "batch_id": batch_id,
                "file_path": file_path,
            }
            if optional_hosts:
                request_body["optional_hosts"] = optional_hosts

        result = self._base_query_api_call(
            operation="BatchGetCmd",
            query_params={
                "timeout": timeout,
                "timeout_duration": timeout_duration,
                "host_timeout_duration": host_timeout_duration,
            },
            body_params=request_body,
            error_message="Failed to execute RTR batch get command",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def check_rtr_batch_get_command_status(
        self,
        batch_get_cmd_req_id: str | None = Field(
            default=None,
            description="Batch get command request ID returned from `falcon_execute_rtr_batch_get_command`.",
        ),
        timeout: int | None = Field(default=None, ge=1, le=600, description="Timeout in seconds."),
        timeout_duration: str | None = Field(default=None, description="Request timeout duration string."),
    ) -> list[dict[str, Any]]:
        """Check status for a batch get command request."""
        if not batch_get_cmd_req_id:
            return [
                _format_error_response(
                    "`batch_get_cmd_req_id` is required to check batch get status.",
                    operation="BatchGetCmdStatus",
                )
            ]

        result = self._base_query_api_call(
            operation="BatchGetCmdStatus",
            query_params={
                "batch_get_cmd_req_id": batch_get_cmd_req_id,
                "timeout": timeout,
                "timeout_duration": timeout_duration,
            },
            error_message="Failed to check RTR batch get command status",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_rtr_extracted_file_contents(
        self,
        session_id: str | None = Field(
            default=None,
            description="RTR session ID.",
        ),
        sha256: str | None = Field(
            default=None,
            description="Extracted file SHA256 identifier.",
        ),
        filename: str | None = Field(
            default=None,
            description="Optional filename for archive naming.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve extracted file contents for a session SHA256 artifact."""
        if not session_id or not sha256:
            return [
                _format_error_response(
                    "Both `session_id` and `sha256` are required to retrieve extracted file contents.",
                    operation="RTR_GetExtractedFileContents",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_GetExtractedFileContents",
            query_params={
                "session_id": session_id,
                "sha256": sha256,
                "filename": filename,
            },
            error_message="Failed to get RTR extracted file contents",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def list_rtr_files_v1(
        self,
        session_id: str | None = Field(
            default=None,
            description="RTR session ID to list files for.",
        ),
    ) -> list[dict[str, Any]]:
        """List session files using RTR_ListFiles (v1)."""
        if not session_id:
            return [
                _format_error_response(
                    "`session_id` is required to list RTR files.",
                    operation="RTR_ListFiles",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_ListFiles",
            query_params={"session_id": session_id},
            error_message="Failed to list RTR files (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def list_rtr_files_v2(
        self,
        session_id: str | None = Field(
            default=None,
            description="RTR session ID to list files for.",
        ),
    ) -> list[dict[str, Any]]:
        """List session files using RTR_ListFilesV2."""
        if not session_id:
            return [
                _format_error_response(
                    "`session_id` is required to list RTR files.",
                    operation="RTR_ListFilesV2",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_ListFilesV2",
            query_params={"session_id": session_id},
            error_message="Failed to list RTR files (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_rtr_file_v1(
        self,
        session_id: str | None = Field(
            default=None,
            description="RTR session ID that owns the file.",
        ),
        file_id: str | None = Field(
            default=None,
            description="RTR session file ID to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete an RTR session file using RTR_DeleteFile (v1)."""
        if not session_id or not file_id:
            return [
                _format_error_response(
                    "Both `session_id` and `file_id` are required to delete an RTR file.",
                    operation="RTR_DeleteFile",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_DeleteFile",
            query_params={"session_id": session_id, "ids": file_id},
            error_message="Failed to delete RTR file (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_rtr_file_v2(
        self,
        session_id: str | None = Field(
            default=None,
            description="RTR session ID that owns the file.",
        ),
        file_id: str | None = Field(
            default=None,
            description="RTR session file ID to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete an RTR session file using RTR_DeleteFileV2."""
        if not session_id or not file_id:
            return [
                _format_error_response(
                    "Both `session_id` and `file_id` are required to delete an RTR file.",
                    operation="RTR_DeleteFileV2",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_DeleteFileV2",
            query_params={"session_id": session_id, "ids": file_id},
            error_message="Failed to delete RTR file (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_rtr_falcon_scripts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for Falcon RTR script search. IMPORTANT: use `falcon://rtr/admin/fql-guide` when building this filter parameter.",
        ),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of Falcon script IDs to return."),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Falcon-provided RTR scripts and return full script details."""
        script_ids = self._base_search_api_call(
            operation="RTR_ListFalconScripts",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search Falcon RTR scripts",
        )

        if self._is_error(script_ids):
            if filter:
                return self._format_fql_error_response(
                    [script_ids], filter, SEARCH_RTR_ADMIN_FQL_DOCUMENTATION
                )
            return [script_ids]

        if not script_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_RTR_ADMIN_FQL_DOCUMENTATION)
            return []

        details = self._base_query_api_call(
            operation="RTR_GetFalconScripts",
            query_params={"ids": script_ids},
            error_message="Failed to retrieve Falcon RTR script details",
            default_result=[],
        )

        if self._is_error(details):
            return [details]

        return details

    def get_rtr_falcon_script_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Falcon script IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve Falcon RTR scripts by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve Falcon RTR script details.",
                    operation="RTR_GetFalconScripts",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_GetFalconScripts",
            query_params={"ids": ids},
            error_message="Failed to retrieve Falcon RTR script details",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_rtr_put_file_contents(
        self,
        put_file_id: str | None = Field(
            default=None,
            description="Put-file ID to retrieve contents for.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve RTR put-file content payload for a file ID."""
        if not put_file_id:
            return [
                _format_error_response(
                    "`put_file_id` is required to retrieve put file contents.",
                    operation="RTR_GetPutFileContents",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_GetPutFileContents",
            query_params={"id": put_file_id},
            error_message="Failed to retrieve RTR put file contents",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_rtr_admin_put_file_details_v2(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="RTR put-file IDs to retrieve using v2 endpoint.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve RTR put-file metadata using v2 endpoint."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve RTR put-file details.",
                    operation="RTR_GetPut_FilesV2",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_GetPut_FilesV2",
            query_params={"ids": ids},
            error_message="Failed to retrieve RTR put-file details (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_rtr_admin_put_file_v1(
        self,
        form_data: dict[str, Any] | None = Field(
            default=None,
            description="Form-data payload for `RTR_CreatePut_Files` (for example: `file`, `description`, `name`).",
        ),
    ) -> list[dict[str, Any]]:
        """Create RTR put-file using v1 endpoint."""
        if form_data is None:
            return [
                _format_error_response(
                    "`form_data` is required to create an RTR put file.",
                    operation="RTR_CreatePut_Files",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_CreatePut_Files",
            body_params=form_data,
            error_message="Failed to create RTR put file (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_rtr_admin_put_file_v2(
        self,
        form_data: dict[str, Any] | None = Field(
            default=None,
            description="Form-data payload for `RTR_CreatePut_FilesV2` (for example: `file`, `description`, `name`).",
        ),
    ) -> list[dict[str, Any]]:
        """Create RTR put-file using v2 endpoint."""
        if form_data is None:
            return [
                _format_error_response(
                    "`form_data` is required to create an RTR put file.",
                    operation="RTR_CreatePut_FilesV2",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_CreatePut_FilesV2",
            body_params=form_data,
            error_message="Failed to create RTR put file (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_rtr_admin_put_file(
        self,
        put_file_id: str | None = Field(
            default=None,
            description="RTR put-file ID to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete RTR put-file by ID."""
        if not put_file_id:
            return [
                _format_error_response(
                    "`put_file_id` is required to delete an RTR put file.",
                    operation="RTR_DeletePut_Files",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_DeletePut_Files",
            query_params={"ids": put_file_id},
            error_message="Failed to delete RTR put file",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_rtr_admin_script_details_v2(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="RTR script IDs to retrieve using v2 endpoint.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve RTR script metadata using v2 endpoint."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve RTR script details.",
                    operation="RTR_GetScriptsV2",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_GetScriptsV2",
            query_params={"ids": ids},
            error_message="Failed to retrieve RTR script details (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_rtr_admin_script_v1(
        self,
        form_data: dict[str, Any] | None = Field(
            default=None,
            description="Form-data payload for `RTR_CreateScripts`.",
        ),
    ) -> list[dict[str, Any]]:
        """Create an RTR custom script using v1 endpoint."""
        if form_data is None:
            return [
                _format_error_response(
                    "`form_data` is required to create an RTR script.",
                    operation="RTR_CreateScripts",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_CreateScripts",
            body_params=form_data,
            error_message="Failed to create RTR script (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_rtr_admin_script_v2(
        self,
        form_data: dict[str, Any] | None = Field(
            default=None,
            description="Form-data payload for `RTR_CreateScriptsV2`.",
        ),
    ) -> list[dict[str, Any]]:
        """Create an RTR custom script using v2 endpoint."""
        if form_data is None:
            return [
                _format_error_response(
                    "`form_data` is required to create an RTR script.",
                    operation="RTR_CreateScriptsV2",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_CreateScriptsV2",
            body_params=form_data,
            error_message="Failed to create RTR script (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_rtr_admin_script_v1(
        self,
        form_data: dict[str, Any] | None = Field(
            default=None,
            description="Form-data payload for `RTR_UpdateScripts` including `id`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update an RTR custom script using v1 endpoint."""
        if form_data is None:
            return [
                _format_error_response(
                    "`form_data` is required to update an RTR script.",
                    operation="RTR_UpdateScripts",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_UpdateScripts",
            body_params=form_data,
            error_message="Failed to update RTR script (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_rtr_admin_script_v2(
        self,
        form_data: dict[str, Any] | None = Field(
            default=None,
            description="Form-data payload for `RTR_UpdateScriptsV2` including `id`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update an RTR custom script using v2 endpoint."""
        if form_data is None:
            return [
                _format_error_response(
                    "`form_data` is required to update an RTR script.",
                    operation="RTR_UpdateScriptsV2",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_UpdateScriptsV2",
            body_params=form_data,
            error_message="Failed to update RTR script (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_rtr_admin_script(
        self,
        script_id: str | None = Field(
            default=None,
            description="RTR script ID to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete an RTR custom script by ID."""
        if not script_id:
            return [
                _format_error_response(
                    "`script_id` is required to delete an RTR script.",
                    operation="RTR_DeleteScripts",
                )
            ]

        result = self._base_query_api_call(
            operation="RTR_DeleteScripts",
            query_params={"ids": script_id},
            error_message="Failed to delete RTR script",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
