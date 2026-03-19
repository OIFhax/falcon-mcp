"""
Message Center module for Falcon MCP Server.

This module provides case, activity, attachment, and aggregation tools for Message Center.
"""

import base64
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.message_center import (
    MESSAGE_CENTER_SAFETY_GUIDE,
    MESSAGE_CENTER_USAGE_GUIDE,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class MessageCenterModule(BaseModule):
    """Module for Falcon Message Center operations."""

    def register_tools(self, server: FastMCP) -> None:
        self._add_tool(server=server, method=self.aggregate_message_center_cases, name="aggregate_message_center_cases")
        self._add_tool(server=server, method=self.get_message_center_case_activities, name="get_message_center_case_activities")
        self._add_tool(server=server, method=self.add_message_center_case_activity, name="add_message_center_case_activity", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.download_message_center_case_attachment, name="download_message_center_case_attachment")
        self._add_tool(server=server, method=self.add_message_center_case_attachment, name="add_message_center_case_attachment", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.create_message_center_case, name="create_message_center_case", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.get_message_center_cases, name="get_message_center_cases")
        self._add_tool(server=server, method=self.query_message_center_case_activity_ids, name="query_message_center_case_activity_ids")
        self._add_tool(server=server, method=self.query_message_center_case_ids, name="query_message_center_case_ids")

    def register_resources(self, server: FastMCP) -> None:
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://message-center/usage-guide"),
                name="falcon_message_center_usage_guide",
                description="Usage guidance for Message Center workflows.",
                text=MESSAGE_CENTER_USAGE_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://message-center/safety-guide"),
                name="falcon_message_center_safety_guide",
                description="Safety guidance for Message Center write tools.",
                text=MESSAGE_CENTER_SAFETY_GUIDE,
            ),
        )

    def aggregate_message_center_cases(self, body: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        if body is None:
            return [_format_error_response("Provide `body` to aggregate Message Center cases.", operation="AggregateCases")]
        result = self._base_query_api_call("AggregateCases", body_params=body, error_message="Failed to aggregate Message Center cases", default_result=[])
        if self._is_error(result):
            return [result]
        return result

    def get_message_center_case_activities(self, body: dict[str, Any] | None = None, ids: list[str] | None = None) -> list[dict[str, Any]]:
        payload = body or ({"ids": ids} if ids else None)
        if payload is None:
            return [_format_error_response("Provide `body` or `ids` to retrieve Message Center case activities.", operation="GetCaseActivityByIds")]
        result = self._base_query_api_call("GetCaseActivityByIds", body_params=payload, error_message="Failed to retrieve Message Center case activities", default_result=[])
        if self._is_error(result):
            return [result]
        return result

    def add_message_center_case_activity(self, confirm_execution: bool = Field(default=False), body: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self._run_body_write(operation="CaseAddActivity", confirm_execution=confirm_execution, body=body, validation_message="Provide `body` to add a Message Center case activity.", error_message="Failed to add Message Center case activity")

    def download_message_center_case_attachment(self, ids: list[str] | None = Field(default=None, description="Attachment ID to download.")) -> list[dict[str, Any]]:
        if not ids:
            return [_format_error_response("`ids` is required to download a Message Center attachment.", operation="CaseDownloadAttachment")]
        command_response = self.client.command("CaseDownloadAttachment", parameters=prepare_api_parameters({"ids": ids}))
        if isinstance(command_response, (bytes, bytearray)):
            return [{"message": "Attachment content is binary and is not rendered inline by this MCP tool.", "operation": "CaseDownloadAttachment", "size_bytes": len(command_response)}]
        if not isinstance(command_response, dict):
            return [_format_error_response(f"Unexpected response type: {type(command_response).__name__}", operation="CaseDownloadAttachment")]
        body = command_response.get("body")
        if isinstance(body, (bytes, bytearray)):
            return [{"message": "Attachment content is binary and is not rendered inline by this MCP tool.", "operation": "CaseDownloadAttachment", "size_bytes": len(body)}]
        result = handle_api_response(command_response, operation="CaseDownloadAttachment", error_message="Failed to download Message Center attachment", default_result=[])
        if self._is_error(result):
            return [result]
        return result

    def add_message_center_case_attachment(
        self,
        confirm_execution: bool = Field(default=False),
        case_id: str | None = None,
        file_name: str | None = None,
        file_data_base64: str | None = None,
        user_uuid: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [_format_error_response("This operation requires `confirm_execution=true`.", operation="CaseAddAttachment")]
        if not file_name or not file_data_base64 or not case_id:
            return [_format_error_response("Provide `case_id`, `file_name`, and `file_data_base64` to upload a Message Center attachment.", operation="CaseAddAttachment")]
        try:
            file_bytes = base64.b64decode(file_data_base64)
        except ValueError:
            return [_format_error_response("`file_data_base64` must be valid base64-encoded content.", operation="CaseAddAttachment")]
        response = self.client.command(
            "CaseAddAttachment",
            files=[("file", (file_name, file_bytes))],
            data={key: value for key, value in {"case_id": case_id, "user_uuid": user_uuid}.items() if value is not None},
            body=body or {},
        )
        result = handle_api_response(response, operation="CaseAddAttachment", error_message="Failed to add Message Center attachment", default_result=[])
        if self._is_error(result):
            return [result]
        return result

    def create_message_center_case(self, confirm_execution: bool = Field(default=False), body: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self._run_body_write(operation="CreateCaseV2", confirm_execution=confirm_execution, body=body, validation_message="Provide `body` to create a Message Center case.", error_message="Failed to create Message Center case")

    def get_message_center_cases(self, body: dict[str, Any] | None = None, ids: list[str] | None = None) -> list[dict[str, Any]]:
        payload = body or ({"ids": ids} if ids else None)
        if payload is None:
            return [_format_error_response("Provide `body` or `ids` to retrieve Message Center cases.", operation="GetCaseEntitiesByIDs")]
        result = self._base_query_api_call("GetCaseEntitiesByIDs", body_params=payload, error_message="Failed to retrieve Message Center cases", default_result=[])
        if self._is_error(result):
            return [result]
        return result

    def query_message_center_case_activity_ids(self, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        result = self._base_query_api_call(operation="QueryActivityByCaseID", query_params=parameters or {}, error_message="Failed to query Message Center case activity IDs", default_result=[])
        if self._is_error(result):
            return [result]
        return result

    def query_message_center_case_ids(self, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        result = self._base_query_api_call(operation="QueryCasesIdsByFilter", query_params=parameters or {}, error_message="Failed to query Message Center case IDs", default_result=[])
        if self._is_error(result):
            return [result]
        return result

    def _run_body_write(self, operation: str, confirm_execution: bool, body: dict[str, Any] | None, validation_message: str, error_message: str) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [_format_error_response("This operation requires `confirm_execution=true`.", operation=operation)]
        if body is None:
            return [_format_error_response(validation_message, operation=operation)]
        result = self._base_query_api_call(operation, body_params=body, error_message=error_message, default_result=[])
        if self._is_error(result):
            return [result]
        return result
