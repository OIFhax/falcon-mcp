"""
Fusion playbooks module for Falcon MCP Server.

This module fills the narrow read-only gap between public workflow-definition
APIs and newer Fusion playbook UI routes. It keeps workflow definition export as
the primary path and uses an experimental allowlisted fallback only for
playbook-shaped IDs.
"""

from __future__ import annotations

import re
from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule

PLAYBOOK_ID_PATTERN = re.compile(r"^[a-fA-F0-9]{32,40}$")
FUSION_PLAYBOOK_PATH_PATTERNS = (
    r"/workflow/fusion/playbooks/[a-fA-F0-9]{32,40}",
    r"/workflow/fusion/playbooks/[a-fA-F0-9]{32,40}/export",
)
FUSION_PLAYBOOK_PATH_TEMPLATES = (
    "/workflow/fusion/playbooks/{playbook_id}/export",
    "/workflow/fusion/playbooks/{playbook_id}",
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

FUSION_PLAYBOOKS_GUIDE = """
# Fusion Playbooks Guide

Use `falcon_get_fusion_playbook` to retrieve a Fusion playbook by the ID shown in
the Falcon UI route `/workflow/fusion/playbooks/{id}`.

The tool first tries the public workflow-definition export API for compatibility
with classic workflow definition IDs. If Falcon returns a not-found response, it
then probes a small allowlist of read-only Fusion playbook routes using the same
Falcon OAuth credentials. If those routes return HTML or login content, the route
is treated as UI-only and the tool returns an unsupported-route error instead of
scraping browser cookies.

Fusion playbooks that are visible as workflow definitions can also be imported,
updated, enabled/disabled, executed, or mock-executed through the Fusion playbook
write tools. These write tools delegate to Falcon workflow-definition APIs and do
not add an MCP-level confirmation gate; Falcon credentials and RBAC remain the
authorization boundary.
"""


class FusionPlaybooksModule(BaseModule):
    """Module for read-only Fusion playbook retrieval."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.get_fusion_playbook,
            name="get_fusion_playbook",
        )
        self._add_tool(
            server=server,
            method=self.import_fusion_playbook,
            name="import_fusion_playbook",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_fusion_playbook,
            name="update_fusion_playbook",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_fusion_playbook_status,
            name="update_fusion_playbook_status",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.execute_fusion_playbook,
            name="execute_fusion_playbook",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.mock_execute_fusion_playbook,
            name="mock_execute_fusion_playbook",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://fusion-playbooks/guide"),
                name="falcon_fusion_playbooks_guide",
                description="Guidance for read-only Fusion playbook retrieval.",
                text=FUSION_PLAYBOOKS_GUIDE,
            ),
        )

    def get_fusion_playbook(
        self,
        playbook_id: str | None = Field(
            default=None,
            description="Fusion playbook or workflow definition ID from the Falcon UI.",
        ),
        sanitize: bool = Field(
            default=True,
            description="Whether to sanitize PII when falling back to workflow definition export.",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]] | str:
        """Retrieve a Fusion playbook or compatible workflow definition by ID."""
        if not playbook_id or not PLAYBOOK_ID_PATTERN.fullmatch(playbook_id):
            return [
                _format_error_response(
                    "`playbook_id` must be a 32-40 character hexadecimal Falcon ID.",
                    error_type="validation_error",
                )
            ]

        workflow_response = self.client.command(
            "WorkflowDefinitionsExport",
            parameters={"id": playbook_id, "sanitize": sanitize},
        )
        workflow_payload = self._format_workflow_export_success(playbook_id, workflow_response)
        if workflow_payload is not None:
            return workflow_payload

        if not self._is_not_found(workflow_response):
            return handle_api_response(
                workflow_response,
                operation="WorkflowDefinitionsExport",
                error_message="Failed to export workflow definition",
                default_result=[],
            )

        attempts: list[dict[str, Any]] = []
        for path_template in FUSION_PLAYBOOK_PATH_TEMPLATES:
            path = path_template.format(playbook_id=playbook_id)
            response = self.client.raw_get_allowed(
                "FusionPlaybookReadExperimental",
                path,
                parameters={"sanitize": sanitize},
                allowed_path_patterns=FUSION_PLAYBOOK_PATH_PATTERNS,
            )
            attempts.append(self._summarize_attempt(path, response))

            if self._is_success(response):
                if self._looks_like_ui_html(response):
                    return _format_error_response(
                        "Fusion playbook route appears to require Falcon console UI/session "
                        "authentication and is not compatible with Falcon API credentials.",
                        details={"playbook_id": playbook_id, "path": path, "attempts": attempts},
                        operation="FusionPlaybookReadExperimental",
                        error_type="unsupported_route",
                    )

                return {
                    "id": playbook_id,
                    "source": "fusion_playbook_experimental",
                    "path": path,
                    "content_type": self._content_type(response),
                    "data": response.get("body", {}),
                }

            if self._is_permission_error(response):
                return handle_api_response(
                    response,
                    operation="FusionPlaybookReadExperimental",
                    error_message="Failed to retrieve Fusion playbook",
                    default_result=[],
                )

        return _format_error_response(
            "Fusion playbook was not found via workflow definition export or the "
            "experimental Fusion playbook routes.",
            details={
                "playbook_id": playbook_id,
                "workflow_definition_export": self._summarize_attempt(
                    "WorkflowDefinitionsExport",
                    workflow_response,
                ),
                "fusion_playbook_attempts": attempts,
            },
            operation="FusionPlaybookReadExperimental",
            error_type="unsupported_route",
        )

    def import_fusion_playbook(
        self,
        data_file_content: str | None = Field(
            default=None,
            description="Workflow definition YAML content to import as a Fusion playbook.",
        ),
        name: str | None = Field(
            default=None,
            description="Optional workflow name override.",
        ),
        validate_only: bool | None = Field(
            default=False,
            description="When true, validates import without saving workflow.",
        ),
    ) -> list[dict[str, Any]]:
        """Import a Fusion playbook from workflow-definition YAML text."""
        if not data_file_content:
            return [
                _format_error_response(
                    "`data_file_content` is required to import Fusion playbooks.",
                    operation="WorkflowDefinitionsImport",
                )
            ]

        prepared_params = prepare_api_parameters(
            {
                "name": name,
                "validate_only": validate_only,
            }
        )
        files_payload = [
            ("data_file", ("workflow.yaml", data_file_content, "application/x-yaml"))
        ]

        command_response = self.client.command(
            "WorkflowDefinitionsImport",
            parameters=prepared_params,
            files=files_payload,
        )
        result = handle_api_response(
            command_response,
            operation="WorkflowDefinitionsImport",
            error_message="Failed to import Fusion playbook",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_fusion_playbook(
        self,
        body: dict[str, Any] | None = Field(
            default=None,
            description="Workflow definition update payload body.",
        ),
        validate_only: bool | None = Field(
            default=False,
            description="When true, validates update without saving definition changes.",
        ),
    ) -> list[dict[str, Any]]:
        """Update a Fusion playbook backed by a workflow definition."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required to update Fusion playbooks.",
                    operation="WorkflowDefinitionsUpdate",
                )
            ]

        result = self._base_query_api_call(
            operation="WorkflowDefinitionsUpdate",
            query_params={"validate_only": validate_only},
            body_params=body,
            error_message="Failed to update Fusion playbook",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_fusion_playbook_status(
        self,
        action_name: Literal["enable", "disable", "cancel"] | None = Field(
            default=None,
            description="Definition action to apply.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Fusion playbook or workflow definition IDs to target.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `WorkflowDefinitionsAction`.",
        ),
    ) -> list[dict[str, Any]]:
        """Enable, disable, or cancel in-flight executions for Fusion playbooks."""
        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required for Fusion playbook definition actions.",
                    operation="WorkflowDefinitionsAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="WorkflowDefinitionsAction",
                    )
                ]
            request_body = {"ids": ids}

        result = self._base_query_api_call(
            operation="WorkflowDefinitionsAction",
            query_params={"action_name": action_name},
            body_params=request_body,
            error_message="Failed to apply Fusion playbook definition action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_fusion_playbook(
        self,
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional execution body payload.",
        ),
        execution_cid: list[str] | None = Field(
            default=None,
            description="CID list to execute on.",
        ),
        playbook_id: str | None = Field(
            default=None,
            description="Fusion playbook or workflow definition ID to execute.",
        ),
        name: str | None = Field(
            default=None,
            description="Workflow name to execute.",
        ),
        key: str | None = Field(
            default=None,
            description="Execution deduplication key.",
        ),
        depth: int | None = Field(
            default=None,
            ge=0,
            le=4,
            description="Execution depth control. [0-4]",
        ),
        source_event_url: str | None = Field(
            default=None,
            description="Source event URL for execution context.",
        ),
    ) -> list[dict[str, Any]]:
        """Execute an on-demand Fusion playbook."""
        return self._execute_workflow_operation(
            operation="WorkflowExecute",
            body=body,
            execution_cid=execution_cid,
            definition_id=[playbook_id] if playbook_id else None,
            name=name,
            key=key,
            depth=depth,
            source_event_url=source_event_url,
        )

    def mock_execute_fusion_playbook(
        self,
        body: dict[str, Any] | None = Field(
            default=None,
            description="Mock execution body containing definition/mocks/on_demand_trigger payloads.",
        ),
        execution_cid: list[str] | None = Field(
            default=None,
            description="CID list to execute on.",
        ),
        playbook_id: str | None = Field(
            default=None,
            description="Fusion playbook or workflow definition ID to execute.",
        ),
        name: str | None = Field(
            default=None,
            description="Workflow name to execute.",
        ),
        key: str | None = Field(
            default=None,
            description="Execution deduplication key.",
        ),
        depth: int | None = Field(
            default=None,
            ge=0,
            le=4,
            description="Execution depth control. [0-4]",
        ),
        source_event_url: str | None = Field(
            default=None,
            description="Source event URL for execution context.",
        ),
        validate_only: bool | None = Field(
            default=False,
            description="When true, validates mock execution without running it.",
        ),
        skip_validation: bool | None = Field(
            default=None,
            description="Skip validation of request-body mocks against output schema.",
        ),
        ignore_activity_mock_references: bool | None = Field(
            default=None,
            description="Disable definition-level activity mock references for this request.",
        ),
    ) -> list[dict[str, Any]]:
        """Execute a Fusion playbook definition with mocks."""
        request_body = body or {}
        if not request_body and not playbook_id and not name:
            return [
                _format_error_response(
                    "Provide `body` or a selector (`playbook_id` or `name`) for mock Fusion playbook execution.",
                    operation="WorkflowMockExecute",
                )
            ]

        result = self._base_query_api_call(
            operation="WorkflowMockExecute",
            query_params={
                "execution_cid": execution_cid,
                "definition_id": playbook_id,
                "name": name,
                "key": key,
                "depth": depth,
                "source_event_url": source_event_url,
                "validate_only": validate_only,
                "skip_validation": skip_validation,
                "ignore_activity_mock_references": ignore_activity_mock_references,
            },
            body_params=request_body,
            error_message="Failed to mock execute Fusion playbook",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _format_workflow_export_success(
        self,
        playbook_id: str,
        response: dict[str, Any] | bytes,
    ) -> dict[str, Any] | str | None:
        """Return a normalized workflow export result when the public API succeeds."""
        if isinstance(response, bytes):
            return {
                "id": playbook_id,
                "source": "workflow_definition_export",
                "format": "yaml",
                "content": response.decode("utf-8", errors="replace"),
            }

        status_code = response.get("status_code")
        if status_code is None or status_code >= 300:
            return None

        body = response.get("body", {})
        if isinstance(body, dict) and body.get("resources"):
            return {
                "id": playbook_id,
                "source": "workflow_definition_export",
                "resources": body["resources"],
            }

        return {
            "id": playbook_id,
            "source": "workflow_definition_export",
            "body": body,
        }

    def _is_success(self, response: dict[str, Any]) -> bool:
        status_code = response.get("status_code")
        return isinstance(status_code, int) and 200 <= status_code < 300

    def _is_not_found(self, response: dict[str, Any] | bytes) -> bool:
        return isinstance(response, dict) and response.get("status_code") == 404

    def _is_permission_error(self, response: dict[str, Any]) -> bool:
        return response.get("status_code") in {401, 403}

    def _looks_like_ui_html(self, response: dict[str, Any]) -> bool:
        content_type = self._content_type(response).lower()
        body = response.get("body", {})
        raw = body.get("raw") if isinstance(body, dict) else None
        return "text/html" in content_type or (
            isinstance(raw, str)
            and ("<html" in raw.lower() or "<!doctype html" in raw.lower())
        )

    def _content_type(self, response: dict[str, Any]) -> str:
        headers = response.get("headers", {})
        if not isinstance(headers, dict):
            return ""
        return str(headers.get("Content-Type") or headers.get("content-type") or "")

    def _summarize_attempt(self, path: str, response: dict[str, Any] | bytes) -> dict[str, Any]:
        if isinstance(response, bytes):
            return {
                "path": path,
                "status_code": 200,
                "response_type": "bytes",
            }

        summary: dict[str, Any] = {
            "path": path,
            "status_code": response.get("status_code"),
            "content_type": self._content_type(response),
        }
        errors = response.get("body", {}).get("errors") if isinstance(response.get("body"), dict) else None
        if errors:
            summary["errors"] = errors
        return summary

    def _execute_workflow_operation(
        self,
        *,
        operation: str,
        body: dict[str, Any] | None,
        execution_cid: list[str] | None,
        definition_id: list[str] | None,
        name: str | None,
        key: str | None,
        depth: int | None,
        source_event_url: str | None,
    ) -> list[dict[str, Any]]:
        request_body = body or {}
        if not request_body and not definition_id and not name:
            return [
                _format_error_response(
                    "Provide `body` or a selector (`playbook_id` or `name`) for Fusion playbook execution.",
                    operation=operation,
                )
            ]

        result = self._base_query_api_call(
            operation=operation,
            query_params={
                "execution_cid": execution_cid,
                "definition_id": definition_id,
                "name": name,
                "key": key,
                "depth": depth,
                "source_event_url": source_event_url,
            },
            body_params=request_body,
            error_message="Failed to execute Fusion playbook",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _is_error(self, result: Any) -> bool:
        return isinstance(result, dict) and "error" in result
