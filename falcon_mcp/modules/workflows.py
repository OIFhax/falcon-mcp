"""
Workflows module for Falcon MCP Server.

This module provides full Falcon Workflows service collection coverage:
search, export/import/update, execute, execution actions/results, human
input actions, and system definition lifecycle operations.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.workflows import (
    SEARCH_WORKFLOW_ACTIVITIES_FQL_DOCUMENTATION,
    SEARCH_WORKFLOW_DEFINITIONS_FQL_DOCUMENTATION,
    SEARCH_WORKFLOW_EXECUTIONS_FQL_DOCUMENTATION,
    SEARCH_WORKFLOW_TRIGGERS_FQL_DOCUMENTATION,
    WORKFLOW_IMPORT_GUIDE,
    WORKFLOW_SAFETY_GUIDE,
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


class WorkflowsModule(BaseModule):
    """Module for Falcon Workflows operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_workflow_activities,
            name="search_workflow_activities",
        )
        self._add_tool(
            server=server,
            method=self.search_workflow_activities_content,
            name="search_workflow_activities_content",
        )
        self._add_tool(
            server=server,
            method=self.search_workflow_definitions,
            name="search_workflow_definitions",
        )
        self._add_tool(
            server=server,
            method=self.search_workflow_executions,
            name="search_workflow_executions",
        )
        self._add_tool(
            server=server,
            method=self.search_workflow_triggers,
            name="search_workflow_triggers",
        )
        self._add_tool(
            server=server,
            method=self.export_workflow_definition,
            name="export_workflow_definition",
        )
        self._add_tool(
            server=server,
            method=self.import_workflow_definition,
            name="import_workflow_definition",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_workflow_definition,
            name="update_workflow_definition",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_workflow_definition_status,
            name="update_workflow_definition_status",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.execute_workflow,
            name="execute_workflow",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.execute_workflow_internal,
            name="execute_workflow_internal",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.mock_execute_workflow,
            name="mock_execute_workflow",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_workflow_execution_state,
            name="update_workflow_execution_state",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_workflow_execution_results,
            name="get_workflow_execution_results",
        )
        self._add_tool(
            server=server,
            method=self.get_workflow_human_input,
            name="get_workflow_human_input",
        )
        self._add_tool(
            server=server,
            method=self.update_workflow_human_input,
            name="update_workflow_human_input",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.deprovision_workflow_system_definition,
            name="deprovision_workflow_system_definition",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.promote_workflow_system_definition,
            name="promote_workflow_system_definition",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.provision_workflow_system_definition,
            name="provision_workflow_system_definition",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_workflow_activities_fql_resource = TextResource(
            uri=AnyUrl("falcon://workflows/activities/fql-guide"),
            name="falcon_search_workflow_activities_fql_guide",
            description="Contains FQL guidance for workflow activity search tools.",
            text=SEARCH_WORKFLOW_ACTIVITIES_FQL_DOCUMENTATION,
        )

        search_workflow_definitions_fql_resource = TextResource(
            uri=AnyUrl("falcon://workflows/definitions/fql-guide"),
            name="falcon_search_workflow_definitions_fql_guide",
            description="Contains FQL guidance for `falcon_search_workflow_definitions`.",
            text=SEARCH_WORKFLOW_DEFINITIONS_FQL_DOCUMENTATION,
        )

        search_workflow_executions_fql_resource = TextResource(
            uri=AnyUrl("falcon://workflows/executions/fql-guide"),
            name="falcon_search_workflow_executions_fql_guide",
            description="Contains FQL guidance for `falcon_search_workflow_executions`.",
            text=SEARCH_WORKFLOW_EXECUTIONS_FQL_DOCUMENTATION,
        )

        search_workflow_triggers_fql_resource = TextResource(
            uri=AnyUrl("falcon://workflows/triggers/fql-guide"),
            name="falcon_search_workflow_triggers_fql_guide",
            description="Contains FQL guidance for `falcon_search_workflow_triggers`.",
            text=SEARCH_WORKFLOW_TRIGGERS_FQL_DOCUMENTATION,
        )

        workflow_import_guide_resource = TextResource(
            uri=AnyUrl("falcon://workflows/import/guide"),
            name="falcon_workflow_import_guide",
            description="Guidance for `falcon_import_workflow_definition`.",
            text=WORKFLOW_IMPORT_GUIDE,
        )

        workflow_safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://workflows/safety-guide"),
            name="falcon_workflow_safety_guide",
            description="Safety and operational guidance for workflow write/execute tools.",
            text=WORKFLOW_SAFETY_GUIDE,
        )

        self._add_resource(server, search_workflow_activities_fql_resource)
        self._add_resource(server, search_workflow_definitions_fql_resource)
        self._add_resource(server, search_workflow_executions_fql_resource)
        self._add_resource(server, search_workflow_triggers_fql_resource)
        self._add_resource(server, workflow_import_guide_resource)
        self._add_resource(server, workflow_safety_guide_resource)

    def search_workflow_activities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for workflow activities. IMPORTANT: use the `falcon://workflows/activities/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of activity records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort activities. Example: `name.desc,time.asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search workflow activities."""
        return self._search_with_fql_guide(
            operation="WorkflowActivitiesCombined",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search workflow activities",
            filter_used=filter,
            fql_guide=SEARCH_WORKFLOW_ACTIVITIES_FQL_DOCUMENTATION,
        )

    def search_workflow_activities_content(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for workflow activity content. IMPORTANT: use the `falcon://workflows/activities/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of activity content records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort activity content. Example: `name.desc,time.asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search workflow activity content records."""
        return self._search_with_fql_guide(
            operation="WorkflowActivitiesContentCombined",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search workflow activities content",
            filter_used=filter,
            fql_guide=SEARCH_WORKFLOW_ACTIVITIES_FQL_DOCUMENTATION,
        )

    def search_workflow_definitions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for workflow definitions. IMPORTANT: use the `falcon://workflows/definitions/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of definition records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort definitions. Example: `name.desc,time.asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search workflow definitions."""
        return self._search_with_fql_guide(
            operation="WorkflowDefinitionsCombined",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search workflow definitions",
            filter_used=filter,
            fql_guide=SEARCH_WORKFLOW_DEFINITIONS_FQL_DOCUMENTATION,
        )

    def search_workflow_executions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for workflow executions. IMPORTANT: use the `falcon://workflows/executions/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of execution records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort executions. Example: `name.desc,time.asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search workflow executions."""
        return self._search_with_fql_guide(
            operation="WorkflowExecutionsCombined",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search workflow executions",
            filter_used=filter,
            fql_guide=SEARCH_WORKFLOW_EXECUTIONS_FQL_DOCUMENTATION,
        )

    def search_workflow_triggers(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for workflow triggers. IMPORTANT: use the `falcon://workflows/triggers/fql-guide` resource when building this filter parameter.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search workflow triggers."""
        return self._search_with_fql_guide(
            operation="WorkflowTriggersCombined",
            search_params={"filter": filter},
            error_message="Failed to search workflow triggers",
            filter_used=filter,
            fql_guide=SEARCH_WORKFLOW_TRIGGERS_FQL_DOCUMENTATION,
        )

    def export_workflow_definition(
        self,
        id: str | None = Field(
            default=None,
            description="Workflow definition ID to export.",
        ),
        sanitize: bool | None = Field(
            default=True,
            description="Whether to sanitize PII from exported workflow definition.",
        ),
    ) -> list[dict[str, Any]] | str:
        """Export a workflow definition by ID."""
        if not id:
            return [
                _format_error_response(
                    "`id` is required to export workflow definitions.",
                    operation="WorkflowDefinitionsExport",
                )
            ]

        prepared_params = prepare_api_parameters(
            {
                "id": id,
                "sanitize": sanitize,
            }
        )

        command_response = self.client.command(
            "WorkflowDefinitionsExport",
            parameters=prepared_params,
        )

        if isinstance(command_response, bytes):
            return command_response.decode("utf-8")

        result = handle_api_response(
            command_response,
            operation="WorkflowDefinitionsExport",
            error_message="Failed to export workflow definition",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def import_workflow_definition(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        data_file_content: str | None = Field(
            default=None,
            description="Workflow definition YAML content to import.",
        ),
        name: str | None = Field(
            default=None,
            description="Optional workflow name override.",
        ),
        validate_only: bool | None = Field(
            default=True,
            description="When true, validates import without saving workflow.",
        ),
    ) -> list[dict[str, Any]]:
        """Import a workflow definition from YAML text."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="WorkflowDefinitionsImport",
                )
            ]

        if not data_file_content:
            return [
                _format_error_response(
                    "`data_file_content` is required to import workflow definitions.",
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
            error_message="Failed to import workflow definition",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_workflow_definition(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Workflow definition update payload body.",
        ),
        validate_only: bool | None = Field(
            default=True,
            description="When true, validates update without saving definition changes.",
        ),
    ) -> list[dict[str, Any]]:
        """Update a workflow definition."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="WorkflowDefinitionsUpdate",
                )
            ]

        if not body:
            return [
                _format_error_response(
                    "`body` is required to update workflow definitions.",
                    operation="WorkflowDefinitionsUpdate",
                )
            ]

        result = self._base_query_api_call(
            operation="WorkflowDefinitionsUpdate",
            query_params={"validate_only": validate_only},
            body_params=body,
            error_message="Failed to update workflow definition",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_workflow_definition_status(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        action_name: Literal["enable", "disable", "cancel"] | None = Field(
            default=None,
            description="Definition action to apply.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Workflow definition IDs to target.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `WorkflowDefinitionsAction`.",
        ),
    ) -> list[dict[str, Any]]:
        """Enable/disable definitions or cancel all in-flight definition executions."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="WorkflowDefinitionsAction",
                )
            ]

        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required for workflow definition action.",
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
            error_message="Failed to apply workflow definition action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def execute_workflow(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional execution body payload.",
        ),
        execution_cid: list[str] | None = Field(
            default=None,
            description="CID list to execute on.",
        ),
        definition_id: list[str] | None = Field(
            default=None,
            description="Workflow definition ID list to execute.",
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
        """Execute an on-demand workflow."""
        return self._execute_workflow_operation(
            operation="WorkflowExecute",
            confirm_execution=confirm_execution,
            body=body,
            execution_cid=execution_cid,
            definition_id=definition_id,
            name=name,
            key=key,
            depth=depth,
            source_event_url=source_event_url,
        )

    def execute_workflow_internal(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional execution body payload.",
        ),
        execution_cid: list[str] | None = Field(
            default=None,
            description="CID list to execute on.",
        ),
        definition_id: list[str] | None = Field(
            default=None,
            description="Workflow definition ID list to execute.",
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
        batch_size: int | None = Field(
            default=None,
            ge=1,
            description="Optional internal execution batch size.",
        ),
        source_event_url: str | None = Field(
            default=None,
            description="Source event URL for execution context.",
        ),
    ) -> list[dict[str, Any]]:
        """Execute an internal on-demand workflow."""
        return self._execute_workflow_operation(
            operation="WorkflowExecuteInternal",
            confirm_execution=confirm_execution,
            body=body,
            execution_cid=execution_cid,
            definition_id=definition_id,
            name=name,
            key=key,
            depth=depth,
            source_event_url=source_event_url,
            batch_size=batch_size,
        )

    def mock_execute_workflow(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Mock execution body containing definition/mocks/on_demand_trigger payloads.",
        ),
        execution_cid: list[str] | None = Field(
            default=None,
            description="CID list to execute on.",
        ),
        definition_id: str | None = Field(
            default=None,
            description="Workflow definition ID to execute.",
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
            default=True,
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
        """Execute a workflow definition with mocks."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="WorkflowMockExecute",
                )
            ]

        request_body = body or {}
        if not request_body and not definition_id and not name:
            return [
                _format_error_response(
                    "Provide `body` or a selector (`definition_id` or `name`) for mock workflow execution.",
                    operation="WorkflowMockExecute",
                )
            ]

        result = self._base_query_api_call(
            operation="WorkflowMockExecute",
            query_params={
                "execution_cid": execution_cid,
                "definition_id": definition_id,
                "name": name,
                "key": key,
                "depth": depth,
                "source_event_url": source_event_url,
                "validate_only": validate_only,
                "skip_validation": skip_validation,
                "ignore_activity_mock_references": ignore_activity_mock_references,
            },
            body_params=request_body,
            error_message="Failed to mock execute workflow",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_workflow_execution_state(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        action_name: Literal["resume", "cancel"] | None = Field(
            default=None,
            description="Execution action to apply.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Workflow execution IDs to target.",
        ),
        action_parameters: list[dict[str, Any]] | None = Field(
            default=None,
            description="Optional action parameter list.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `WorkflowExecutionsAction`.",
        ),
    ) -> list[dict[str, Any]]:
        """Resume or cancel workflow executions."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="WorkflowExecutionsAction",
                )
            ]

        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required for workflow execution action.",
                    operation="WorkflowExecutionsAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="WorkflowExecutionsAction",
                    )
                ]
            request_body = {"ids": ids}
            if action_parameters:
                request_body["action_parameters"] = action_parameters

        result = self._base_query_api_call(
            operation="WorkflowExecutionsAction",
            query_params={"action_name": action_name},
            body_params=request_body,
            error_message="Failed to apply workflow execution action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_workflow_execution_results(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Workflow execution IDs to retrieve results for.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve results for workflow execution IDs."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve workflow execution results.",
                    operation="WorkflowExecutionResults",
                )
            ]

        result = self._base_get_by_ids(
            operation="WorkflowExecutionResults",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def get_workflow_human_input(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Workflow human input IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve workflow human input records by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve workflow human input records.",
                    operation="WorkflowGetHumanInputV1",
                )
            ]

        result = self._base_get_by_ids(
            operation="WorkflowGetHumanInputV1",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def update_workflow_human_input(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        id: str | None = Field(
            default=None,
            description="Human input ID to update.",
        ),
        input: str | None = Field(
            default=None,
            description="Input decision value (for example Approve, Decline, Escalate).",
        ),
        note: str | None = Field(
            default=None,
            description="Optional note to append with input response.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `WorkflowUpdateHumanInputV1`.",
        ),
    ) -> list[dict[str, Any]]:
        """Provide input for a workflow human-input step."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="WorkflowUpdateHumanInputV1",
                )
            ]

        if not id:
            return [
                _format_error_response(
                    "`id` is required to update workflow human input.",
                    operation="WorkflowUpdateHumanInputV1",
                )
            ]

        request_body = body
        if request_body is None:
            if input is None:
                return [
                    _format_error_response(
                        "`input` is required when `body` is not provided.",
                        operation="WorkflowUpdateHumanInputV1",
                    )
                ]
            request_body = {"input": input}
            if note is not None:
                request_body["note"] = note

        result = self._base_query_api_call(
            operation="WorkflowUpdateHumanInputV1",
            query_params={"id": id},
            body_params=request_body,
            error_message="Failed to update workflow human input",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def deprovision_workflow_system_definition(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `WorkflowSystemDefinitionsDeProvision`.",
        ),
        definition_id: str | None = Field(
            default=None,
            description="System workflow definition ID.",
        ),
        template_id: str | None = Field(
            default=None,
            description="System workflow template ID.",
        ),
        template_name: str | None = Field(
            default=None,
            description="System workflow template name.",
        ),
        deprovision_all: bool | None = Field(
            default=None,
            description="Whether to deprovision all system definitions for the target selection.",
        ),
    ) -> list[dict[str, Any]]:
        """Deprovision a system workflow definition."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="WorkflowSystemDefinitionsDeProvision",
                )
            ]

        request_body = body
        if request_body is None:
            request_body = {
                "definition_id": definition_id,
                "template_id": template_id,
                "template_name": template_name,
                "deprovision_all": deprovision_all,
            }
            request_body = prepare_api_parameters(request_body)
            if not request_body:
                return [
                    _format_error_response(
                        "Provide `body` or at least one selector field for deprovision.",
                        operation="WorkflowSystemDefinitionsDeProvision",
                    )
                ]

        result = self._base_query_api_call(
            operation="WorkflowSystemDefinitionsDeProvision",
            body_params=request_body,
            error_message="Failed to deprovision system workflow definition",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def promote_workflow_system_definition(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full body payload for `WorkflowSystemDefinitionsPromote`.",
        ),
    ) -> list[dict[str, Any]]:
        """Promote a system workflow definition template."""
        return self._system_definition_template_operation(
            operation="WorkflowSystemDefinitionsPromote",
            body=body,
            confirm_execution=confirm_execution,
        )

    def provision_workflow_system_definition(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full body payload for `WorkflowSystemDefinitionsProvision`.",
        ),
    ) -> list[dict[str, Any]]:
        """Provision a system workflow definition template."""
        return self._system_definition_template_operation(
            operation="WorkflowSystemDefinitionsProvision",
            body=body,
            confirm_execution=confirm_execution,
        )

    def _search_with_fql_guide(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str,
        filter_used: str | None,
        fql_guide: str,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params=search_params,
            error_message=error_message,
        )

        if self._is_error(result):
            return self._format_fql_error_response([result], filter_used, fql_guide)

        if not result and filter_used:
            return self._format_fql_error_response([], filter_used, fql_guide)

        return result

    def _execute_workflow_operation(
        self,
        operation: str,
        confirm_execution: bool,
        body: dict[str, Any] | None,
        execution_cid: list[str] | None,
        definition_id: list[str] | None,
        name: str | None,
        key: str | None,
        depth: int | None,
        source_event_url: str | None,
        batch_size: int | None = None,
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation=operation,
                )
            ]

        request_body = body or {}
        if not request_body and not definition_id and not name:
            return [
                _format_error_response(
                    "Provide `body` or a selector (`definition_id` or `name`) for workflow execution.",
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
                "batch_size": batch_size,
            },
            body_params=request_body,
            error_message="Failed to execute workflow",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _system_definition_template_operation(
        self,
        operation: str,
        body: dict[str, Any] | None,
        confirm_execution: bool,
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation=operation,
                )
            ]

        if not body:
            return [
                _format_error_response(
                    "`body` is required for this system-definition template operation.",
                    operation=operation,
                )
            ]

        result = self._base_query_api_call(
            operation=operation,
            body_params=body,
            error_message="Failed to process system-definition template operation",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
