"""
IT Automation module for Falcon MCP Server.

This module provides full Falcon IT Automation service collection coverage:
search/query/get operations across tasks, task groups, scheduled tasks, user
groups, and policies, plus controlled write and execution actions.
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

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)

HIGH_RISK_EXECUTION_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


class ITAutomationModule(BaseModule):
    """Module for Falcon IT Automation operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_it_automation_associated_tasks,
            name="search_it_automation_associated_tasks",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_scheduled_tasks_combined,
            name="search_it_automation_scheduled_tasks_combined",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_task_executions,
            name="search_it_automation_task_executions",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_task_groups_combined,
            name="search_it_automation_task_groups_combined",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_tasks_combined,
            name="search_it_automation_tasks_combined",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_user_group_ids,
            name="search_it_automation_user_group_ids",
        )
        self._add_tool(
            server=server,
            method=self.query_it_automation_policy_ids,
            name="query_it_automation_policy_ids",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_scheduled_task_ids,
            name="search_it_automation_scheduled_task_ids",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_task_execution_ids,
            name="search_it_automation_task_execution_ids",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_task_group_ids,
            name="search_it_automation_task_group_ids",
        )
        self._add_tool(
            server=server,
            method=self.search_it_automation_task_ids,
            name="search_it_automation_task_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_user_groups,
            name="get_it_automation_user_groups",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_policies,
            name="get_it_automation_policies",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_scheduled_tasks,
            name="get_it_automation_scheduled_tasks",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_task_executions,
            name="get_it_automation_task_executions",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_task_groups,
            name="get_it_automation_task_groups",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_tasks,
            name="get_it_automation_tasks",
        )
        self._add_tool(
            server=server,
            method=self.get_it_automation_task_execution_host_status,
            name="get_it_automation_task_execution_host_status",
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
        self._add_tool(
            server=server,
            method=self.create_it_automation_user_group,
            name="create_it_automation_user_group",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_it_automation_user_group,
            name="update_it_automation_user_group",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_it_automation_user_groups,
            name="delete_it_automation_user_groups",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.create_it_automation_policy,
            name="create_it_automation_policy",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_it_automation_policies,
            name="update_it_automation_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_it_automation_policies,
            name="delete_it_automation_policies",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_it_automation_policy_host_groups,
            name="update_it_automation_policy_host_groups",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_it_automation_policies_precedence,
            name="update_it_automation_policies_precedence",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.create_it_automation_scheduled_task,
            name="create_it_automation_scheduled_task",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_it_automation_scheduled_task,
            name="update_it_automation_scheduled_task",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_it_automation_scheduled_tasks,
            name="delete_it_automation_scheduled_tasks",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.create_it_automation_task_group,
            name="create_it_automation_task_group",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_it_automation_task_group,
            name="update_it_automation_task_group",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_it_automation_task_groups,
            name="delete_it_automation_task_groups",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.create_it_automation_task,
            name="create_it_automation_task",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_it_automation_task,
            name="update_it_automation_task",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_it_automation_tasks,
            name="delete_it_automation_tasks",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
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
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.rerun_it_automation_task_execution,
            name="rerun_it_automation_task_execution",
            annotations=HIGH_RISK_EXECUTION_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_task_executions_fql_resource = TextResource(
            uri=AnyUrl("falcon://it-automation/task-executions/fql-guide"),
            name="falcon_search_it_automation_task_executions_fql_guide",
            description="Contains the guide for the `filter` parameter of IT Automation task execution search tools.",
            text=SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_DOCUMENTATION,
        )

        phase3_safety_resource = TextResource(
            uri=AnyUrl("falcon://it-automation/phase3/safety-guide"),
            name="falcon_it_automation_phase3_safety_guide",
            description="Safety and execution guidance for high-impact IT Automation write and execution tools.",
            text=IT_AUTOMATION_PHASE3_SAFETY_GUIDE,
        )

        self._add_resource(server, search_task_executions_fql_resource)
        self._add_resource(server, phase3_safety_resource)

    def _search_with_common_filters(
        self,
        operation: str,
        filter: str | None,
        limit: int,
        offset: int | None,
        sort: str | None,
        error_message: str,
        include_fql_guide: bool = False,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Execute IT Automation search-style operations with filter/limit/offset/sort."""
        result = self._base_search_api_call(
            operation=operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message=error_message,
        )

        if self._is_error(result):
            if filter and include_fql_guide:
                return self._format_fql_error_response(
                    [result],
                    filter,
                    SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_DOCUMENTATION,
                )
            return [result]

        if not result and filter and include_fql_guide:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_DOCUMENTATION,
            )

        return result

    def _get_by_ids_query_operation(
        self,
        operation: str,
        ids: list[str] | None,
        error_text: str,
        error_message: str,
    ) -> list[dict[str, Any]]:
        """Execute GET-by-IDs operations where IDs are passed in query parameters."""
        if not ids:
            return [_format_error_response(error_text, operation=operation)]

        result = self._base_query_api_call(
            operation=operation,
            query_params={"ids": ids},
            error_message=error_message,
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _execute_confirmed_write(
        self,
        operation: str,
        confirm_execution: bool,
        query_params: dict[str, Any] | None,
        body_params: dict[str, Any] | None,
        error_message: str,
        confirmation_text: str,
        default_result: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute write operations that require explicit confirmation."""
        if not confirm_execution:
            return [
                _format_error_response(
                    confirmation_text,
                    operation=operation,
                )
            ]

        result = self._base_query_api_call(
            operation=operation,
            query_params=query_params,
            body_params=body_params,
            error_message=error_message,
            default_result=default_result or [],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_it_automation_associated_tasks(
        self,
        file_id: str | None = Field(
            default=None,
            description="File ID to retrieve associated tasks for.",
        ),
        filter: str | None = Field(
            default=None,
            description="Optional FQL filter for associated task results.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of associated task records to return. [1-1000]",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression for associated task records.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve tasks associated with a file ID."""
        if not file_id:
            return [
                _format_error_response(
                    "`file_id` is required to search associated tasks.",
                    operation="ITAutomationGetAssociatedTasks",
                )
            ]

        result = self._base_search_api_call(
            operation="ITAutomationGetAssociatedTasks",
            search_params={
                "id": file_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search IT Automation associated tasks",
        )

        if self._is_error(result):
            return [result]

        return result

    def search_it_automation_scheduled_tasks_combined(
        self,
        filter: str | None = Field(default=None, description="FQL filter for combined scheduled tasks."),
        limit: int = Field(default=100, ge=1, le=1000, description="Maximum records to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search combined scheduled-task details."""
        return self._search_with_common_filters(
            operation="ITAutomationCombinedScheduledTasks",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation combined scheduled tasks",
        )

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
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="FQL sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search combined task execution records."""
        return self._search_with_common_filters(
            operation="ITAutomationGetTaskExecutionsByQuery",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation task executions",
            include_fql_guide=True,
        )

    def search_it_automation_task_groups_combined(
        self,
        filter: str | None = Field(default=None, description="FQL filter for combined task groups."),
        limit: int = Field(default=100, ge=1, le=1000, description="Maximum records to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search combined task-group details."""
        return self._search_with_common_filters(
            operation="ITAutomationGetTaskGroupsByQuery",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation combined task groups",
        )

    def search_it_automation_tasks_combined(
        self,
        filter: str | None = Field(default=None, description="FQL filter for combined tasks."),
        limit: int = Field(default=100, ge=1, le=1000, description="Maximum records to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search combined task details."""
        return self._search_with_common_filters(
            operation="ITAutomationGetTasksByQuery",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation combined tasks",
        )

    def search_it_automation_user_group_ids(
        self,
        filter: str | None = Field(default=None, description="FQL filter for user-group ID search."),
        limit: int = Field(default=100, ge=1, le=1000, description="Maximum IDs to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search user-group IDs."""
        return self._search_with_common_filters(
            operation="ITAutomationSearchUserGroup",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation user-group IDs",
        )

    def query_it_automation_policy_ids(
        self,
        platform: str | None = Field(
            default=None,
            description="Policy platform. Supported values: `Windows`, `Mac`, `Linux`.",
            examples={"Windows", "Mac", "Linux"},
        ),
        limit: int | None = Field(default=None, ge=1, le=500, description="Maximum IDs to return."),
        offset: int | None = Field(default=None, ge=0, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression for policy IDs."),
    ) -> list[dict[str, Any]]:
        """Query policy IDs by platform."""
        if not platform:
            return [
                _format_error_response(
                    "`platform` is required to query IT Automation policy IDs.",
                    operation="ITAutomationQueryPolicies",
                )
            ]

        result = self._base_query_api_call(
            operation="ITAutomationQueryPolicies",
            query_params={
                "platform": platform,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query IT Automation policy IDs",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_it_automation_scheduled_task_ids(
        self,
        filter: str | None = Field(default=None, description="FQL filter for scheduled-task ID search."),
        limit: int = Field(default=100, ge=1, le=1000, description="Maximum IDs to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search scheduled-task IDs."""
        return self._search_with_common_filters(
            operation="ITAutomationSearchScheduledTasks",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation scheduled-task IDs",
        )

    def search_it_automation_task_execution_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for task execution ID search. IMPORTANT: use the `falcon://it-automation/task-executions/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=1000, description="Maximum IDs to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search task execution IDs."""
        return self._search_with_common_filters(
            operation="ITAutomationSearchTaskExecutions",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation task execution IDs",
            include_fql_guide=True,
        )

    def search_it_automation_task_group_ids(
        self,
        filter: str | None = Field(default=None, description="FQL filter for task-group ID search."),
        limit: int = Field(default=100, ge=1, le=1000, description="Maximum IDs to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search task-group IDs."""
        return self._search_with_common_filters(
            operation="ITAutomationSearchTaskGroups",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation task-group IDs",
        )

    def search_it_automation_task_ids(
        self,
        filter: str | None = Field(default=None, description="FQL filter for task ID search."),
        limit: int = Field(default=100, ge=1, le=1000, description="Maximum IDs to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search task IDs."""
        return self._search_with_common_filters(
            operation="ITAutomationSearchTasks",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to search IT Automation task IDs",
        )

    def get_it_automation_user_groups(
        self,
        ids: list[str] | None = Field(default=None, description="User-group IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve user groups by ID."""
        return self._get_by_ids_query_operation(
            operation="ITAutomationGetUserGroup",
            ids=ids,
            error_text="`ids` is required to retrieve user groups.",
            error_message="Failed to get IT Automation user groups",
        )

    def get_it_automation_policies(
        self,
        ids: list[str] | None = Field(default=None, description="Policy IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve policies by ID."""
        return self._get_by_ids_query_operation(
            operation="ITAutomationGetPolicies",
            ids=ids,
            error_text="`ids` is required to retrieve policies.",
            error_message="Failed to get IT Automation policies",
        )

    def get_it_automation_scheduled_tasks(
        self,
        ids: list[str] | None = Field(default=None, description="Scheduled-task IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve scheduled tasks by ID."""
        return self._get_by_ids_query_operation(
            operation="ITAutomationGetScheduledTasks",
            ids=ids,
            error_text="`ids` is required to retrieve scheduled tasks.",
            error_message="Failed to get IT Automation scheduled tasks",
        )

    def get_it_automation_task_executions(
        self,
        ids: list[str] | None = Field(default=None, description="Task execution IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve task execution records by ID."""
        return self._get_by_ids_query_operation(
            operation="ITAutomationGetTaskExecution",
            ids=ids,
            error_text="`ids` is required to retrieve task executions.",
            error_message="Failed to get IT Automation task executions",
        )

    def get_it_automation_task_groups(
        self,
        ids: list[str] | None = Field(default=None, description="Task-group IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve task groups by ID."""
        return self._get_by_ids_query_operation(
            operation="ITAutomationGetTaskGroups",
            ids=ids,
            error_text="`ids` is required to retrieve task groups.",
            error_message="Failed to get IT Automation task groups",
        )

    def get_it_automation_tasks(
        self,
        ids: list[str] | None = Field(default=None, description="Task IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve tasks by ID."""
        return self._get_by_ids_query_operation(
            operation="ITAutomationGetTasks",
            ids=ids,
            error_text="`ids` is required to retrieve tasks.",
            error_message="Failed to get IT Automation tasks",
        )

    def get_it_automation_task_execution_host_status(
        self,
        ids: list[str] | None = Field(default=None, description="Task execution IDs for host-status retrieval."),
        filter: str | None = Field(default=None, description="Optional FQL filter for host status records."),
        limit: int = Field(default=10, ge=1, le=1000, description="Maximum records to return. [1-1000]"),
        offset: int | None = Field(default=None, description="Result offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
    ) -> list[dict[str, Any]]:
        """Retrieve host-level execution status for task executions."""
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

    def start_it_automation_execution_results_search(
        self,
        task_execution_id: str | None = Field(
            default=None,
            description="Task execution ID to search results for. Required when `body` is not provided.",
        ),
        start: str | None = Field(default=None, description="Optional start timestamp (ISO 8601)."),
        end: str | None = Field(default=None, description="Optional end timestamp (ISO 8601)."),
        filter_expressions: list[str] | None = Field(default=None, description="Optional result filter expressions."),
        group_by_fields: list[str] | None = Field(default=None, description="Optional result grouping fields."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
    ) -> list[dict[str, Any]]:
        """Start asynchronous execution-results search."""
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
        search_id: str | None = Field(default=None, description="Execution-results search job ID."),
    ) -> list[dict[str, Any]]:
        """Get status of asynchronous execution-results search."""
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
        search_id: str | None = Field(default=None, description="Execution-results search job ID."),
        offset: int | None = Field(default=None, description="Result offset."),
        limit: int | None = Field(default=None, ge=1, description="Maximum event results to return."),
        sort: str | None = Field(default=None, description="Sort expression for event results."),
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
            query_params={"id": search_id, "offset": offset, "limit": limit, "sort": sort},
            error_message="Failed to get IT Automation execution results",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_it_automation_user_group(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body."),
    ) -> list[dict[str, Any]]:
        """Create an IT Automation user group."""
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to create a user group.",
                    operation="ITAutomationCreateUserGroup",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationCreateUserGroup",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=body,
            error_message="Failed to create IT Automation user group",
            confirmation_text="Set `confirm_execution=true` to create an IT Automation user group.",
        )

    def update_it_automation_user_group(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        user_group_id: str | None = Field(default=None, description="User-group ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Update body."),
    ) -> list[dict[str, Any]]:
        """Update an IT Automation user group."""
        if not user_group_id:
            return [
                _format_error_response(
                    "`user_group_id` is required to update a user group.",
                    operation="ITAutomationUpdateUserGroup",
                )
            ]
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to update a user group.",
                    operation="ITAutomationUpdateUserGroup",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationUpdateUserGroup",
            confirm_execution=confirm_execution,
            query_params={"id": user_group_id},
            body_params=body,
            error_message="Failed to update IT Automation user group",
            confirmation_text="Set `confirm_execution=true` to update an IT Automation user group.",
        )

    def delete_it_automation_user_groups(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this destructive operation."),
        ids: list[str] | None = Field(default=None, description="User-group IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete IT Automation user groups."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete user groups.",
                    operation="ITAutomationDeleteUserGroup",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationDeleteUserGroup",
            confirm_execution=confirm_execution,
            query_params={"ids": ids},
            body_params=None,
            error_message="Failed to delete IT Automation user groups",
            confirmation_text="Set `confirm_execution=true` to delete IT Automation user groups.",
            default_result=[{"ids": ids, "status": "submitted"}],
        )

    def create_it_automation_policy(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        body: dict[str, Any] | None = Field(default=None, description="Policy creation body."),
    ) -> list[dict[str, Any]]:
        """Create an IT Automation policy."""
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to create a policy.",
                    operation="ITAutomationCreatePolicy",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationCreatePolicy",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=body,
            error_message="Failed to create IT Automation policy",
            confirmation_text="Set `confirm_execution=true` to create an IT Automation policy.",
        )

    def update_it_automation_policies(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        body: dict[str, Any] | None = Field(default=None, description="Policy update body."),
    ) -> list[dict[str, Any]]:
        """Update IT Automation policies."""
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to update policies.",
                    operation="ITAutomationUpdatePolicies",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationUpdatePolicies",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=body,
            error_message="Failed to update IT Automation policies",
            confirmation_text="Set `confirm_execution=true` to update IT Automation policies.",
        )

    def delete_it_automation_policies(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this destructive operation."),
        ids: list[str] | None = Field(default=None, description="Policy IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete IT Automation policies."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete policies.",
                    operation="ITAutomationDeletePolicy",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationDeletePolicy",
            confirm_execution=confirm_execution,
            query_params={"ids": ids},
            body_params=None,
            error_message="Failed to delete IT Automation policies",
            confirmation_text="Set `confirm_execution=true` to delete IT Automation policies.",
            default_result=[{"ids": ids, "status": "submitted"}],
        )

    def update_it_automation_policy_host_groups(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        body: dict[str, Any] | None = Field(default=None, description="Policy host-group action body."),
    ) -> list[dict[str, Any]]:
        """Manage host groups assigned to IT Automation policies."""
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to update policy host groups.",
                    operation="ITAutomationUpdatePolicyHostGroups",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationUpdatePolicyHostGroups",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=body,
            error_message="Failed to update IT Automation policy host groups",
            confirmation_text="Set `confirm_execution=true` to update IT Automation policy host groups.",
        )

    def update_it_automation_policies_precedence(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        platform: str | None = Field(default=None, description="Policy platform (`Windows`, `Linux`, `Mac`)."),
        body: dict[str, Any] | None = Field(default=None, description="Policy precedence body."),
    ) -> list[dict[str, Any]]:
        """Update IT Automation policy precedence for a platform."""
        if not platform:
            return [
                _format_error_response(
                    "`platform` is required to update policy precedence.",
                    operation="ITAutomationUpdatePoliciesPrecedence",
                )
            ]
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to update policy precedence.",
                    operation="ITAutomationUpdatePoliciesPrecedence",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationUpdatePoliciesPrecedence",
            confirm_execution=confirm_execution,
            query_params={"platform": platform},
            body_params=body,
            error_message="Failed to update IT Automation policy precedence",
            confirmation_text="Set `confirm_execution=true` to update IT Automation policy precedence.",
        )

    def create_it_automation_scheduled_task(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        body: dict[str, Any] | None = Field(default=None, description="Scheduled-task creation body."),
    ) -> list[dict[str, Any]]:
        """Create an IT Automation scheduled task."""
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to create a scheduled task.",
                    operation="ITAutomationCreateScheduledTask",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationCreateScheduledTask",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=body,
            error_message="Failed to create IT Automation scheduled task",
            confirmation_text="Set `confirm_execution=true` to create an IT Automation scheduled task.",
        )

    def update_it_automation_scheduled_task(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        scheduled_task_id: str | None = Field(default=None, description="Scheduled-task ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Scheduled-task update body."),
    ) -> list[dict[str, Any]]:
        """Update an IT Automation scheduled task."""
        if not scheduled_task_id:
            return [
                _format_error_response(
                    "`scheduled_task_id` is required to update a scheduled task.",
                    operation="ITAutomationUpdateScheduledTask",
                )
            ]
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to update a scheduled task.",
                    operation="ITAutomationUpdateScheduledTask",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationUpdateScheduledTask",
            confirm_execution=confirm_execution,
            query_params={"id": scheduled_task_id},
            body_params=body,
            error_message="Failed to update IT Automation scheduled task",
            confirmation_text="Set `confirm_execution=true` to update an IT Automation scheduled task.",
        )

    def delete_it_automation_scheduled_tasks(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this destructive operation."),
        ids: list[str] | None = Field(default=None, description="Scheduled-task IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete IT Automation scheduled tasks."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete scheduled tasks.",
                    operation="ITAutomationDeleteScheduledTasks",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationDeleteScheduledTasks",
            confirm_execution=confirm_execution,
            query_params={"ids": ids},
            body_params=None,
            error_message="Failed to delete IT Automation scheduled tasks",
            confirmation_text="Set `confirm_execution=true` to delete IT Automation scheduled tasks.",
            default_result=[{"ids": ids, "status": "submitted"}],
        )

    def create_it_automation_task_group(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        body: dict[str, Any] | None = Field(default=None, description="Task-group creation body."),
    ) -> list[dict[str, Any]]:
        """Create an IT Automation task group."""
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to create a task group.",
                    operation="ITAutomationCreateTaskGroup",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationCreateTaskGroup",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=body,
            error_message="Failed to create IT Automation task group",
            confirmation_text="Set `confirm_execution=true` to create an IT Automation task group.",
        )

    def update_it_automation_task_group(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        task_group_id: str | None = Field(default=None, description="Task-group ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Task-group update body."),
    ) -> list[dict[str, Any]]:
        """Update an IT Automation task group."""
        if not task_group_id:
            return [
                _format_error_response(
                    "`task_group_id` is required to update a task group.",
                    operation="ITAutomationUpdateTaskGroup",
                )
            ]
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to update a task group.",
                    operation="ITAutomationUpdateTaskGroup",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationUpdateTaskGroup",
            confirm_execution=confirm_execution,
            query_params={"id": task_group_id},
            body_params=body,
            error_message="Failed to update IT Automation task group",
            confirmation_text="Set `confirm_execution=true` to update an IT Automation task group.",
        )

    def delete_it_automation_task_groups(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this destructive operation."),
        ids: list[str] | None = Field(default=None, description="Task-group IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete IT Automation task groups."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete task groups.",
                    operation="ITAutomationDeleteTaskGroups",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationDeleteTaskGroups",
            confirm_execution=confirm_execution,
            query_params={"ids": ids},
            body_params=None,
            error_message="Failed to delete IT Automation task groups",
            confirmation_text="Set `confirm_execution=true` to delete IT Automation task groups.",
            default_result=[{"ids": ids, "status": "submitted"}],
        )

    def create_it_automation_task(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        body: dict[str, Any] | None = Field(default=None, description="Task creation body."),
    ) -> list[dict[str, Any]]:
        """Create an IT Automation task."""
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to create a task.",
                    operation="ITAutomationCreateTask",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationCreateTask",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=body,
            error_message="Failed to create IT Automation task",
            confirmation_text="Set `confirm_execution=true` to create an IT Automation task.",
        )

    def update_it_automation_task(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this write operation."),
        task_id: str | None = Field(default=None, description="Task ID to update."),
        body: dict[str, Any] | None = Field(default=None, description="Task update body."),
    ) -> list[dict[str, Any]]:
        """Update an IT Automation task."""
        if not task_id:
            return [
                _format_error_response(
                    "`task_id` is required to update a task.",
                    operation="ITAutomationUpdateTask",
                )
            ]
        if body is None:
            return [
                _format_error_response(
                    "`body` is required to update a task.",
                    operation="ITAutomationUpdateTask",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationUpdateTask",
            confirm_execution=confirm_execution,
            query_params={"id": task_id},
            body_params=body,
            error_message="Failed to update IT Automation task",
            confirmation_text="Set `confirm_execution=true` to update an IT Automation task.",
        )

    def delete_it_automation_tasks(
        self,
        confirm_execution: bool = Field(default=False, description="Must be `true` to execute this destructive operation."),
        ids: list[str] | None = Field(default=None, description="Task IDs to delete."),
    ) -> list[dict[str, Any]]:
        """Delete IT Automation tasks."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete tasks.",
                    operation="ITAutomationDeleteTask",
                )
            ]

        return self._execute_confirmed_write(
            operation="ITAutomationDeleteTask",
            confirm_execution=confirm_execution,
            query_params={"ids": ids},
            body_params=None,
            error_message="Failed to delete IT Automation tasks",
            confirmation_text="Set `confirm_execution=true` to delete IT Automation tasks.",
            default_result=[{"ids": ids, "status": "submitted"}],
        )

    def start_it_automation_task_execution(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this high-impact operation.",
        ),
        task_id: str | None = Field(default=None, description="Task ID to execute. Required when `body` is not provided."),
        target: str | None = Field(default=None, description="Execution target selector. Required when `body` is not provided."),
        arguments: dict[str, str] | None = Field(default=None, description="Execution argument key-value pairs."),
        discover_new_hosts: bool | None = Field(default=None, description="Allow discovery of new hosts during execution."),
        discover_offline_hosts: bool | None = Field(default=None, description="Allow discovery of offline hosts during execution."),
        distribute: bool | None = Field(default=None, description="Distribute execution workload."),
        expiration_interval: str | None = Field(default=None, description="Execution expiration interval."),
        guardrails: dict[str, Any] | None = Field(default=None, description="Execution guardrails object."),
        trigger_condition: list[dict[str, Any]] | None = Field(default=None, description="Optional trigger condition configuration."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
    ) -> list[dict[str, Any]]:
        """Start execution of an existing IT Automation task."""
        request_body = body
        if request_body is None:
            if not task_id or not target:
                return [
                    _format_error_response(
                        "`task_id` and `target` are required when `body` is not provided.",
                        operation="ITAutomationStartTaskExecution",
                    )
                ]

            request_body = {"task_id": task_id, "target": target}
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

        return self._execute_confirmed_write(
            operation="ITAutomationStartTaskExecution",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=request_body,
            error_message="Failed to start IT Automation task execution",
            confirmation_text="Set `confirm_execution=true` to run this high-impact execution action. Review `falcon://it-automation/phase3/safety-guide` first.",
        )

    def run_it_automation_live_query(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this high-impact operation.",
        ),
        target: str | None = Field(default=None, description="Execution target selector. Required when `body` is not provided."),
        osquery: str | None = Field(default=None, description="Raw osquery SQL string for live execution."),
        queries: dict[str, Any] | None = Field(default=None, description="Platform-specific query/script object."),
        output_parser_config: dict[str, Any] | None = Field(default=None, description="Optional output parser configuration."),
        discover_new_hosts: bool | None = Field(default=None, description="Allow discovery of new hosts during execution."),
        discover_offline_hosts: bool | None = Field(default=None, description="Allow discovery of offline hosts during execution."),
        distribute: bool | None = Field(default=None, description="Distribute execution workload."),
        expiration_interval: str | None = Field(default=None, description="Execution expiration interval."),
        guardrails: dict[str, Any] | None = Field(default=None, description="Execution guardrails object."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
    ) -> list[dict[str, Any]]:
        """Run an IT Automation live query execution."""
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

        return self._execute_confirmed_write(
            operation="ITAutomationRunLiveQuery",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=request_body,
            error_message="Failed to run IT Automation live query",
            confirmation_text="Set `confirm_execution=true` to run this high-impact live query action. Review `falcon://it-automation/phase3/safety-guide` first.",
        )

    def cancel_it_automation_task_execution(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this high-impact operation.",
        ),
        task_execution_id: str | None = Field(default=None, description="Task execution ID to cancel."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
    ) -> list[dict[str, Any]]:
        """Cancel an active IT Automation task execution."""
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

        return self._execute_confirmed_write(
            operation="ITAutomationCancelTaskExecution",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=request_body,
            error_message="Failed to cancel IT Automation task execution",
            confirmation_text="Set `confirm_execution=true` to cancel a task execution. Review `falcon://it-automation/phase3/safety-guide` first.",
        )

    def rerun_it_automation_task_execution(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this high-impact operation.",
        ),
        task_execution_id: str | None = Field(default=None, description="Task execution ID to rerun."),
        run_type: str | None = Field(default=None, description="Run type for rerun behavior (for example, `hosts`)."),
        body: dict[str, Any] | None = Field(default=None, description="Full request body override."),
    ) -> list[dict[str, Any]]:
        """Rerun an IT Automation task execution."""
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

        return self._execute_confirmed_write(
            operation="ITAutomationRerunTaskExecution",
            confirm_execution=confirm_execution,
            query_params=None,
            body_params=request_body,
            error_message="Failed to rerun IT Automation task execution",
            confirmation_text="Set `confirm_execution=true` to rerun a task execution. Review `falcon://it-automation/phase3/safety-guide` first.",
        )
