"""
Case Management module for Falcon MCP Server.

This module provides full Falcon Case Management coverage across case files,
notification groups, SLAs, templates, cases, tags, and evidence workflows.
"""

import base64
import binascii
from collections.abc import Callable
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.case_management import (
    CASE_MANAGEMENT_SAFETY_GUIDE,
    CASE_MANAGEMENT_USAGE_GUIDE,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


def tool_spec(
    *,
    operation: str,
    kind: str,
    annotations: ToolAnnotations | None = None,
) -> dict[str, Any]:
    """Build a generated Case Management tool specification."""
    return {
        "tool_name": f"case_management_{operation}",
        "operation": operation,
        "kind": kind,
        "annotations": annotations,
    }


class CaseManagementModule(BaseModule):
    """Module for Falcon Case Management operations."""

    TOOL_SPECS = [
        tool_spec(operation="aggregates_file_details_post_v1", kind="body_read"),
        tool_spec(operation="combined_file_details_get_v1", kind="params_read"),
        tool_spec(operation="entities_file_details_get_v1", kind="params_read"),
        tool_spec(
            operation="entities_file_details_patch_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="entities_files_bulk_download_post_v1", kind="binary_body_read"),
        tool_spec(operation="entities_files_download_get_v1", kind="binary_params_read"),
        tool_spec(
            operation="entities_files_upload_post_v1",
            kind="multipart_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_files_delete_v1",
            kind="params_write",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_retrieve_rtr_file_post_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="queries_file_details_get_v1", kind="params_read"),
        tool_spec(operation="aggregates_notification_groups_post_v1", kind="body_read"),
        tool_spec(operation="aggregates_notification_groups_post_v2", kind="body_read"),
        tool_spec(operation="aggregates_slas_post_v1", kind="body_read"),
        tool_spec(operation="aggregates_templates_post_v1", kind="body_read"),
        tool_spec(operation="entities_fields_get_v1", kind="params_read"),
        tool_spec(operation="entities_notification_groups_get_v1", kind="params_read"),
        tool_spec(
            operation="entities_notification_groups_post_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_notification_groups_patch_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_notification_groups_delete_v1",
            kind="params_write",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="entities_notification_groups_get_v2", kind="params_read"),
        tool_spec(
            operation="entities_notification_groups_post_v2",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_notification_groups_patch_v2",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_notification_groups_delete_v2",
            kind="params_write",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="entities_slas_get_v1", kind="params_read"),
        tool_spec(
            operation="entities_slas_post_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_slas_patch_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_slas_delete_v1",
            kind="params_write",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="entities_template_snapshots_get_v1", kind="params_read"),
        tool_spec(operation="entities_templates_export_get_v1", kind="binary_params_read"),
        tool_spec(
            operation="entities_templates_import_post_v1",
            kind="multipart_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="entities_templates_get_v1", kind="params_read"),
        tool_spec(
            operation="entities_templates_post_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_templates_patch_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_templates_delete_v1",
            kind="params_write",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="queries_fields_get_v1", kind="params_read"),
        tool_spec(operation="queries_notification_groups_get_v1", kind="params_read"),
        tool_spec(operation="queries_notification_groups_get_v2", kind="params_read"),
        tool_spec(operation="queries_slas_get_v1", kind="params_read"),
        tool_spec(operation="queries_template_snapshots_get_v1", kind="params_read"),
        tool_spec(operation="queries_templates_get_v1", kind="params_read"),
        tool_spec(
            operation="entities_alert_evidence_post_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_case_tags_post_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_case_tags_delete_v1",
            kind="params_write",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_cases_put_v2",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="entities_cases_post_v2", kind="body_read"),
        tool_spec(
            operation="entities_cases_patch_v2",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(
            operation="entities_event_evidence_post_v1",
            kind="body_write",
            annotations=WRITE_ANNOTATIONS,
        ),
        tool_spec(operation="queries_cases_get_v1", kind="params_read"),
    ]

    def __init__(self, client):
        super().__init__(client)
        self._build_generated_tools()

    def _build_generated_tools(self) -> None:
        for spec in self.TOOL_SPECS:
            operation = spec["operation"]
            kind = spec["kind"]
            if kind == "params_read":
                method = self._make_params_read_tool(operation)
            elif kind == "body_read":
                method = self._make_body_read_tool(operation)
            elif kind == "params_write":
                method = self._make_params_write_tool(operation)
            elif kind == "body_write":
                method = self._make_body_write_tool(operation)
            elif kind == "binary_params_read":
                method = self._make_binary_params_read_tool(operation)
            elif kind == "binary_body_read":
                method = self._make_binary_body_read_tool(operation)
            elif kind == "multipart_write":
                method = self._make_multipart_write_tool(operation)
            else:
                raise ValueError(f"Unsupported tool kind: {kind}")
            setattr(self, spec["tool_name"], method)

    def register_tools(self, server: FastMCP) -> None:
        for spec in self.TOOL_SPECS:
            self._add_tool(
                server=server,
                method=getattr(self, spec["tool_name"]),
                name=spec["tool_name"],
                annotations=spec["annotations"],
            )

    def register_resources(self, server: FastMCP) -> None:
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://case-management/usage-guide"),
                name="falcon_case_management_usage_guide",
                description="Usage guidance for Falcon Case Management tools.",
                text=CASE_MANAGEMENT_USAGE_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://case-management/safety-guide"),
                name="falcon_case_management_safety_guide",
                description="Safety guidance for Falcon Case Management write tools.",
                text=CASE_MANAGEMENT_SAFETY_GUIDE,
            ),
        )

    def _make_params_read_tool(self, operation: str) -> Callable[..., Any]:
        def tool(
            parameters: dict[str, Any] | None = Field(
                default=None,
                description="Full query parameters payload.",
            ),
        ) -> Any:
            result = self._execute_operation(
                operation=operation,
                parameters=parameters or {},
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_body_read_tool(self, operation: str) -> Callable[..., Any]:
        def tool(
            body: dict[str, Any] | list[dict[str, Any]] | None = Field(
                default=None,
                description="Full request body payload.",
            ),
        ) -> Any:
            if body is None:
                return [
                    _format_error_response(
                        "Provide `body` to execute this Case Management read operation.",
                        operation=operation,
                    )
                ]
            result = self._execute_operation(
                operation=operation,
                body=body,
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_params_write_tool(self, operation: str) -> Callable[..., Any]:
        def tool(
            confirm_execution: bool = Field(default=False),
            parameters: dict[str, Any] | None = Field(
                default=None,
                description="Full query parameters payload.",
            ),
        ) -> Any:
            if not confirm_execution:
                return [
                    _format_error_response(
                        "This operation requires `confirm_execution=true`.",
                        operation=operation,
                    )
                ]
            if parameters is None:
                return [
                    _format_error_response(
                        "Provide `parameters` to execute this Case Management write operation.",
                        operation=operation,
                    )
                ]
            result = self._execute_operation(
                operation=operation,
                parameters=parameters,
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_body_write_tool(self, operation: str) -> Callable[..., Any]:
        def tool(
            confirm_execution: bool = Field(default=False),
            body: dict[str, Any] | list[dict[str, Any]] | None = Field(
                default=None,
                description="Full request body payload.",
            ),
        ) -> Any:
            if not confirm_execution:
                return [
                    _format_error_response(
                        "This operation requires `confirm_execution=true`.",
                        operation=operation,
                    )
                ]
            if body is None:
                return [
                    _format_error_response(
                        "Provide `body` to execute this Case Management write operation.",
                        operation=operation,
                    )
                ]
            result = self._execute_operation(
                operation=operation,
                body=body,
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_binary_params_read_tool(self, operation: str) -> Callable[..., list[dict[str, Any]]]:
        def tool(
            parameters: dict[str, Any] | None = Field(
                default=None,
                description="Full query parameters payload.",
            ),
            include_binary_base64: bool = Field(
                default=False,
                description="When true, include base64-encoded binary content inline when within `max_inline_bytes`.",
            ),
            max_inline_bytes: int = Field(
                default=2_000_000,
                ge=1,
                le=20_000_000,
                description="Maximum binary size allowed for inline base64 output.",
            ),
        ) -> list[dict[str, Any]]:
            return self._run_binary_operation(
                operation=operation,
                parameters=parameters or {},
                include_binary_base64=include_binary_base64,
                max_inline_bytes=max_inline_bytes,
                error_message=f"Failed to execute {operation}",
            )

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_binary_body_read_tool(self, operation: str) -> Callable[..., list[dict[str, Any]]]:
        def tool(
            body: dict[str, Any] | list[dict[str, Any]] | None = Field(
                default=None,
                description="Full request body payload.",
            ),
            include_binary_base64: bool = Field(
                default=False,
                description="When true, include base64-encoded binary content inline when within `max_inline_bytes`.",
            ),
            max_inline_bytes: int = Field(
                default=2_000_000,
                ge=1,
                le=20_000_000,
                description="Maximum binary size allowed for inline base64 output.",
            ),
        ) -> list[dict[str, Any]]:
            if body is None:
                return [
                    _format_error_response(
                        "Provide `body` to execute this Case Management download operation.",
                        operation=operation,
                    )
                ]
            return self._run_binary_operation(
                operation=operation,
                body=body,
                include_binary_base64=include_binary_base64,
                max_inline_bytes=max_inline_bytes,
                error_message=f"Failed to execute {operation}",
            )

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_multipart_write_tool(self, operation: str) -> Callable[..., list[dict[str, Any]]]:
        def tool(
            confirm_execution: bool = Field(default=False),
            file_name: str | None = Field(
                default=None,
                description="Logical file name to send to the Falcon API.",
            ),
            file_data_base64: str | None = Field(
                default=None,
                description="Base64-encoded file contents.",
            ),
            parameters: dict[str, Any] | None = Field(
                default=None,
                description="Additional multipart/query parameters for this operation.",
            ),
        ) -> list[dict[str, Any]]:
            if not confirm_execution:
                return [
                    _format_error_response(
                        "This operation requires `confirm_execution=true`.",
                        operation=operation,
                    )
                ]
            if not file_name or not file_data_base64:
                return [
                    _format_error_response(
                        "Provide `file_name` and `file_data_base64` to execute this Case Management file operation.",
                        operation=operation,
                    )
                ]
            try:
                file_bytes = base64.b64decode(file_data_base64, validate=True)
            except (ValueError, binascii.Error):
                return [
                    _format_error_response(
                        "`file_data_base64` must be valid base64-encoded content.",
                        operation=operation,
                    )
                ]

            call_args: dict[str, Any] = {
                "files": [("file", (file_name, file_bytes))],
            }
            if parameters is not None:
                call_args["parameters"] = prepare_api_parameters(parameters)

            response = self.client.command(operation, **call_args)
            result = handle_api_response(
                response,
                operation=operation,
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool

    def _execute_operation(
        self,
        operation: str,
        *,
        parameters: dict[str, Any] | None = None,
        body: Any = None,
        error_message: str,
        default_result: Any,
    ) -> Any:
        call_args: dict[str, Any] = {}
        if parameters is not None:
            call_args["parameters"] = prepare_api_parameters(parameters)
        if body is not None:
            call_args["body"] = prepare_api_parameters(body) if isinstance(body, dict) else body
        response = self.client.command(operation, **call_args)
        return handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=default_result,
        )

    def _run_binary_operation(
        self,
        operation: str,
        *,
        parameters: dict[str, Any] | None = None,
        body: Any = None,
        include_binary_base64: bool,
        max_inline_bytes: int,
        error_message: str,
    ) -> list[dict[str, Any]]:
        call_args: dict[str, Any] = {}
        if parameters is not None:
            call_args["parameters"] = prepare_api_parameters(parameters)
        if body is not None:
            call_args["body"] = prepare_api_parameters(body) if isinstance(body, dict) else body

        command_response = self.client.command(operation, **call_args)

        if isinstance(command_response, (bytes, bytearray)):
            return self._format_binary_response(
                operation=operation,
                binary_bytes=bytes(command_response),
                include_binary_base64=include_binary_base64,
                max_inline_bytes=max_inline_bytes,
            )

        if not isinstance(command_response, dict):
            return [
                _format_error_response(
                    f"Unexpected response type: {type(command_response).__name__}",
                    operation=operation,
                )
            ]

        response_body = command_response.get("body")
        if isinstance(response_body, (bytes, bytearray)):
            return self._format_binary_response(
                operation=operation,
                binary_bytes=bytes(response_body),
                include_binary_base64=include_binary_base64,
                max_inline_bytes=max_inline_bytes,
                headers=command_response.get("headers", {}),
            )

        result = handle_api_response(
            command_response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        if isinstance(result, list):
            return result
        return [
            {
                "operation": operation,
                "message": "Download completed but the Falcon API did not return inline binary content.",
                "result": result,
            }
        ]

    def _format_binary_response(
        self,
        *,
        operation: str,
        binary_bytes: bytes,
        include_binary_base64: bool,
        max_inline_bytes: int,
        headers: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        metadata: dict[str, Any] = {
            "operation": operation,
            "size_bytes": len(binary_bytes),
        }
        if headers:
            if headers.get("Content-Type"):
                metadata["content_type"] = headers["Content-Type"]
            if headers.get("Content-Disposition"):
                metadata["content_disposition"] = headers["Content-Disposition"]

        if include_binary_base64:
            if len(binary_bytes) > max_inline_bytes:
                return [
                    _format_error_response(
                        "Binary content exceeds `max_inline_bytes`. Increase the limit or set `include_binary_base64=false`.",
                        operation=operation,
                    )
                ]
            metadata["binary_base64"] = base64.b64encode(binary_bytes).decode("ascii")
            metadata["message"] = "Binary content included as base64."
            return [metadata]

        metadata["message"] = "Binary content omitted. Set `include_binary_base64=true` to include inline bytes."
        return [metadata]
