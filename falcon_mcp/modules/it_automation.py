"""
IT Automation module for Falcon MCP Server.

This module provides Phase 3 IT Automation execution tools (high-impact
execution controls, task execution lifecycle, and execution result retrieval).
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.it_automation import (
    IT_AUTOMATION_PHASE3_SAFETY_GUIDE,
    SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_DOCUMENTATION,
)

HIGH_RISK_EXECUTION_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)

HIGH_RISK_IDEMPOTENT_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)


class ITAutomationModule(BaseModule):
    """Module for Phase 3 IT Automation execution operations via FalconPy."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_it_automation_task_executions,
            name="search_it_automation_task_executions",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_task_executions,
            name="get_it_automation_task_executions",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_task_execution_host_status,
            name="get_it_automation_task_execution_host_status",
        )
        self._add_tool(
            server=server,
            method=self.start_it_automation_task_execution,
            name="start_it_automation_task_execution",
            annotations=HIGH_RISK_EXECUTION_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.run_it_automation_live_query,
            name="run_it_automation_live_query",
            annotations=HIGH_RISK_EXECUTION_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.cancel_it_automation_task_execution,
            name="cancel_it_automation_task_execution",
            annotations=HIGH_RISK_IDEMPOTENT_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.rerun_it_automation_task_execution,
            name="rerun_it_automation_task_execution",
            annotations=HIGH_RISK_EXECUTION_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.start_it_automation_execution_results_search,
            name="start_it_automation_execution_results_search",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_execution_results_search_status,
            name="get_it_automation_execution_results_search_status",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_execution_results,
            name="get_it_automation_execution_results",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_task_executions_fql_resource = TextResource(
            uri=AnyUrl("falcon://it-automation/task-executions/fql-guide"),
            name="falcon_search_it_automation_task_executions_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_it_automation_task_executions` tool.",
            text=SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_DOCUMENTATION,
        )

        phase3_safety_resource = TextResource(
            uri=AnyUrl("falcon://it-automation/phase3/safety-guide"),
            name="falcon_it_automation_phase3_safety_guide",
            description="Safety and execution guidance for high-impact IT Automation Phase 3 tools.",
            text=IT_AUTOMATION_PHASE3_SAFETY_GUIDE,
        )

        self._add_resource(server, search_task_executions_fql_resource)
        self._add_resource(server, phase3_safety_resource)

    def search_it_automation_task_executions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for IT Automation task execution search. IMPORTANT: use the `falcon://it-automation/task-executions/fql-guide` resource when building this filter parameter.",
            examples={"status:'running'", "task_name:'Containment*'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=1000,
            description="Maximum number of task execution records to return. [1-1000]",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for task executions (for example, `start_time.desc` or `status|asc`).",
            examples={"start_time.desc", "status|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search IT Automation task executions and return full records."""
        result = self._base_search_api_call(
            operation="ITAutomationGetTaskExecutionsByQuery",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search IT Automation task executions",
        )

        if self._is_error(result):
            if filter:
                return self._format_fql_error_response(
                    [result], filter, SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_DOCUMENTATION
                )
            return [result]

        if not result and filter:
            return self._format_fql_error_response(
                [], filter, SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_DOCUMENTATION
            )

        return result

    def get_it_automation_task_executions(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Task execution IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve task execution records by IDs."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve task executions.",
                    operation="ITAutomationGetTaskExecution",
                )
            ]

        result = self._base_query_api_call(
            operation="ITAutomationGetTaskExecution",
            query_params={"ids": ids},
            error_message="Failed to get IT Automation task executions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_it_automation_task_execution_host_status(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Task execution IDs to fetch host execution status for.",
        ),
        filter: str | None = Field(
            default=None,
            description="Optional FQL filter for host execution status records.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=1000,
            description="Maximum number of host execution status records to return. [1-1000]",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for host execution status records.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve host-level task execution status records."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve task execution host status.",
                    operation="ITAutomationGetTaskExecutionHostStatus",
                )
            ]

        result = self._base_query_api_call(
            operation="ITAutomationGetTaskExecutionHostStatus",
            query_params={
                "ids": ids,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to get IT Automation task execution host status",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def start_it_automation_task_execution(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this high-impact operation.",
        ),
        task_id: str | None = Field(
            default=None,
            description="Task ID to execute. Required when `body` is not provided.",
        ),
        target: str | None = Field(
            default=None,
            description="Execution target selector. Required when `body` is not provided.",
        ),
        arguments: dict[str, str] | None = Field(
            default=None,
            description="Execution argument key-value pairs.",
        ),
        discover_new_hosts: bool | None = Field(
            default=None,
            description="Allow discovery of new hosts during execution.",
        ),
        discover_offline_hosts: bool | None = Field(
            default=None,
            description="Allow discovery of offline hosts during execution.",
        ),
        distribute: bool | None = Field(
            default=None,
            description="Distribute execution workload.",
        ),
        expiration_interval: str | None = Field(
            default=None,
            description="Execution expiration interval.",
        ),
        guardrails: dict[str, Any] | None = Field(
            default=None,
            description="Execution guardrails object.",
        ),
        trigger_condition: list[dict[str, Any]] | None = Field(
            default=None,
            description="Optional trigger condition configuration.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Start execution of an existing IT Automation task."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "Set `confirm_execution=true` to run this high-impact execution action. Review `falcon://it-automation/phase3/safety-guide` first.",
                    operation="ITAutomationStartTaskExecution",
                )
            ]

        request_body = body
        if request_body is None:
            if not task_id or not target:
                return [
                    _format_error_response(
                        "`task_id` and `target` are required when `body` is not provided.",
                        operation="ITAutomationStartTaskExecution",
                    )
                ]

            request_body = {
                "task_id": task_id,
                "target": target,
            }
            optional_values = {
                "arguments": arguments,
                "discover_new_hosts": discover_new_hosts,
                "discover_offline_hosts": discover_offline_hosts,
                "distribute": distribute,
                "expiration_interval": expiration_interval,
                "guardrails": guardrails,
                "trigger_condition": trigger_condition,
            }
            for key, value_ in optional_values.items():
                if value_ is not None:
                    request_body[key] = value_

        result = self._base_query_api_call(
            operation="ITAutomationStartTaskExecution",
            body_params=request_body,
            error_message="Failed to start IT Automation task execution",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def run_it_automation_live_query(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this high-impact operation.",
        ),
        target: str | None = Field(
            default=None,
            description="Execution target selector. Required when `body` is not provided.",
        ),
        osquery: str | None = Field(
            default=None,
            description="Raw osquery SQL string for live execution.",
        ),
        queries: dict[str, Any] | None = Field(
            default=None,
            description="Platform-specific query/script object. Use this when not sending `osquery`.",
        ),
        output_parser_config: dict[str, Any] | None = Field(
            default=None,
            description="Optional output parser configuration.",
        ),
        discover_new_hosts: bool | None = Field(
            default=None,
            description="Allow discovery of new hosts during execution.",
        ),
        discover_offline_hosts: bool | None = Field(
            default=None,
            description="Allow discovery of offline hosts during execution.",
        ),
        distribute: bool | None = Field(
            default=None,
            description="Distribute execution workload.",
        ),
        expiration_interval: str | None = Field(
            default=None,
            description="Execution expiration interval.",
        ),
        guardrails: dict[str, Any] | None = Field(
            default=None,
            description="Execution guardrails object.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Run an IT Automation live query execution."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "Set `confirm_execution=true` to run this high-impact live query action. Review `falcon://it-automation/phase3/safety-guide` first.",
                    operation="ITAutomationRunLiveQuery",
                )
            ]

        request_body = body
        if request_body is None:
            if not target:
                return [
                    _format_error_response(
                        "`target` is required when `body` is not provided.",
                        operation="ITAutomationRunLiveQuery",
                    )
                ]
            if not osquery and not queries:
                return [
                    _format_error_response(
                        "Provide either `osquery` or `queries` when `body` is not provided.",
                        operation="ITAutomationRunLiveQuery",
                    )
                ]

            request_body = {"target": target}
            optional_values = {
                "osquery": osquery,
                "queries": queries,
                "output_parser_config": output_parser_config,
                "discover_new_hosts": discover_new_hosts,
                "discover_offline_hosts": discover_offline_hosts,
                "distribute": distribute,
                "expiration_interval": expiration_interval,
                "guardrails": guardrails,
            }
            for key, value_ in optional_values.items():
                if value_ is not None:
                    request_body[key] = value_

        result = self._base_query_api_call(
            operation="ITAutomationRunLiveQuery",
            body_params=request_body,
            error_message="Failed to run IT Automation live query",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def cancel_it_automation_task_execution(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this high-impact operation.",
        ),
        task_execution_id: str | None = Field(
            default=None,
            description="Task execution ID to cancel. Required when `body` is not provided.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Cancel an active IT Automation task execution."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "Set `confirm_execution=true` to cancel a task execution. Review `falcon://it-automation/phase3/safety-guide` first.",
                    operation="ITAutomationCancelTaskExecution",
                )
            ]

        request_body = body
        if request_body is None:
            if not task_execution_id:
                return [
                    _format_error_response(
                        "`task_execution_id` is required when `body` is not provided.",
                        operation="ITAutomationCancelTaskExecution",
                    )
                ]
            request_body = {"task_execution_id": task_execution_id}

        result = self._base_query_api_call(
            operation="ITAutomationCancelTaskExecution",
            body_params=request_body,
            error_message="Failed to cancel IT Automation task execution",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def rerun_it_automation_task_execution(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this high-impact operation.",
        ),
        task_execution_id: str | None = Field(
            default=None,
            description="Task execution ID to rerun. Required when `body` is not provided.",
        ),
        run_type: str | None = Field(
            default=None,
            description="Run type for rerun behavior (for example, `hosts`).",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Rerun an IT Automation task execution."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "Set `confirm_execution=true` to rerun a task execution. Review `falcon://it-automation/phase3/safety-guide` first.",
                    operation="ITAutomationRerunTaskExecution",
                )
            ]

        request_body = body
        if request_body is None:
            if not task_execution_id:
                return [
                    _format_error_response(
                        "`task_execution_id` is required when `body` is not provided.",
                        operation="ITAutomationRerunTaskExecution",
                    )
                ]
            request_body = {"task_execution_id": task_execution_id}
            if run_type:
                request_body["run_type"] = run_type

        result = self._base_query_api_call(
            operation="ITAutomationRerunTaskExecution",
            body_params=request_body,
            error_message="Failed to rerun IT Automation task execution",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def start_it_automation_execution_results_search(
        self,
        task_execution_id: str | None = Field(
            default=None,
            description="Task execution ID to search results for. Required when `body` is not provided.",
        ),
        start: str | None = Field(
            default=None,
            description="Optional start timestamp (ISO 8601) for result search window.",
        ),
        end: str | None = Field(
            default=None,
            description="Optional end timestamp (ISO 8601) for result search window.",
        ),
        filter_expressions: list[str] | None = Field(
            default=None,
            description="Optional result filter expressions.",
        ),
        group_by_fields: list[str] | None = Field(
            default=None,
            description="Optional grouping fields for aggregation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Start asynchronous task execution results search."""
        request_body = body
        if request_body is None:
            if not task_execution_id:
                return [
                    _format_error_response(
                        "`task_execution_id` is required when `body` is not provided.",
                        operation="ITAutomationStartExecutionResultsSearch",
                    )
                ]

            request_body = {"task_execution_id": task_execution_id}
            optional_values = {
                "start": start,
                "end": end,
                "filter_expressions": filter_expressions,
                "group_by_fields": group_by_fields,
            }
            for key, value_ in optional_values.items():
                if value_ is not None:
                    request_body[key] = value_

        result = self._base_query_api_call(
            operation="ITAutomationStartExecutionResultsSearch",
            body_params=request_body,
            error_message="Failed to start IT Automation execution results search",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_it_automation_execution_results_search_status(
        self,
        search_id: str | None = Field(
            default=None,
            description="Execution results search job ID returned from `falcon_start_it_automation_execution_results_search`.",
        ),
    ) -> list[dict[str, Any]]:
        """Get asynchronous execution results search status."""
        if not search_id:
            return [
                _format_error_response(
                    "`search_id` is required to retrieve execution results search status.",
                    operation="ITAutomationGetExecutionResultsSearchStatus",
                )
            ]

        result = self._base_query_api_call(
            operation="ITAutomationGetExecutionResultsSearchStatus",
            query_params={"id": search_id},
            error_message="Failed to get IT Automation execution results search status",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_it_automation_execution_results(
        self,
        search_id: str | None = Field(
            default=None,
            description="Execution results search job ID returned from `falcon_start_it_automation_execution_results_search`.",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return records.",
        ),
        limit: int | None = Field(
            default=None,
            ge=1,
            description="Maximum number of event results to return.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression for event results fields (for example, `hostname.asc`).",
        ),
    ) -> list[dict[str, Any]]:
        """Get asynchronous execution results by search job ID."""
        if not search_id:
            return [
                _format_error_response(
                    "`search_id` is required to retrieve execution results.",
                    operation="ITAutomationGetExecutionResults",
                )
            ]

        result = self._base_query_api_call(
            operation="ITAutomationGetExecutionResults",
            query_params={
                "id": search_id,
                "offset": offset,
                "limit": limit,
                "sort": sort,
            },
            error_message="Failed to get IT Automation execution results",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
