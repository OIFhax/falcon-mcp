"""Integration tests for the IT Automation module."""

from typing import Any

import pytest

from falcon_mcp.modules.it_automation import ITAutomationModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestITAutomationIntegration(BaseIntegrationTest):
    """Integration tests for IT Automation module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = ITAutomationModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, dict):
            details = result.get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
            nested_results = result.get("results")
            if isinstance(nested_results, list) and nested_results:
                first = nested_results[0]
                if isinstance(first, dict):
                    nested_details = first.get("details", {})
                    if isinstance(nested_details, dict):
                        return nested_details.get("status_code")

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")

        return None

    def _skip_if_scope_missing(self, result: Any, context: str) -> None:
        if self._extract_status_code(result) == 403:
            self.skip_with_warning(
                "Missing required API scope for IT Automation integration test",
                context=context,
            )

    @staticmethod
    def _extract_first_id(result: Any) -> str | None:
        if not isinstance(result, list) or not result:
            return None
        first = result[0]
        if isinstance(first, dict):
            value = first.get("id")
            if isinstance(value, str) and value:
                return value
        if isinstance(first, str) and first:
            return first
        return None

    def test_search_operations_operation_names(self):
        search_cases = [
            (
                "task_executions_combined",
                self.module.search_it_automation_task_executions,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
            (
                "task_executions_ids",
                self.module.search_it_automation_task_execution_ids,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
            (
                "tasks_combined",
                self.module.search_it_automation_tasks_combined,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
            (
                "task_ids",
                self.module.search_it_automation_task_ids,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
            (
                "task_groups_combined",
                self.module.search_it_automation_task_groups_combined,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
            (
                "task_group_ids",
                self.module.search_it_automation_task_group_ids,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
            (
                "scheduled_combined",
                self.module.search_it_automation_scheduled_tasks_combined,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
            (
                "scheduled_ids",
                self.module.search_it_automation_scheduled_task_ids,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
            (
                "user_group_ids",
                self.module.search_it_automation_user_group_ids,
                {"filter": None, "limit": 1, "offset": 0, "sort": None},
            ),
        ]

        for context, method, kwargs in search_cases:
            result = self.call_method(method, **kwargs)
            self._skip_if_scope_missing(result, context)
            self.assert_no_error(result, context=context)
            self.assert_valid_list_response(result, min_length=0, context=context)

    def test_query_policy_ids_operation_name(self):
        result = self.call_method(
            self.module.query_it_automation_policy_ids,
            platform="Windows",
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "query_policy_ids")
        self.assert_no_error(result, context="query_policy_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_policy_ids")

    def test_get_task_execution_and_host_status_with_existing_id(self):
        search_result = self.call_method(
            self.module.search_it_automation_task_execution_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(search_result, "get_task_execution setup")
        self.assert_no_error(search_result, context="get_task_execution setup")

        execution_id = self._extract_first_id(search_result)
        if not execution_id:
            self.skip_with_warning(
                "No IT Automation task execution IDs available",
                context="test_get_task_execution_and_host_status_with_existing_id",
            )

        detail_result = self.call_method(
            self.module.get_it_automation_task_executions,
            ids=[execution_id],
        )
        self._skip_if_scope_missing(detail_result, "get_task_executions")
        self.assert_no_error(detail_result, context="get_task_executions")
        self.assert_valid_list_response(detail_result, min_length=0, context="get_task_executions")

        host_status_result = self.call_method(
            self.module.get_it_automation_task_execution_host_status,
            ids=[execution_id],
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(host_status_result, "get_task_execution_host_status")
        self.assert_no_error(host_status_result, context="get_task_execution_host_status")
        self.assert_valid_list_response(
            host_status_result,
            min_length=0,
            context="get_task_execution_host_status",
        )

    def test_execution_results_search_flow_with_existing_execution(self):
        search_result = self.call_method(
            self.module.search_it_automation_task_execution_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(search_result, "execution results setup")
        self.assert_no_error(search_result, context="execution results setup")

        execution_id = self._extract_first_id(search_result)
        if not execution_id:
            self.skip_with_warning(
                "No IT Automation task execution IDs available for result search validation",
                context="test_execution_results_search_flow_with_existing_execution",
            )

        start_result = self.call_method(
            self.module.start_it_automation_execution_results_search,
            task_execution_id=execution_id,
            start=None,
            end=None,
            filter_expressions=None,
            group_by_fields=None,
            body=None,
        )
        self._skip_if_scope_missing(start_result, "start_execution_results_search")
        self.assert_no_error(start_result, context="start_execution_results_search")
        self.assert_valid_list_response(
            start_result,
            min_length=0,
            context="start_execution_results_search",
        )

        search_job_id = self._extract_first_id(start_result)
        if not search_job_id:
            return

        status_result = self.call_method(
            self.module.get_it_automation_execution_results_search_status,
            search_id=search_job_id,
        )
        self._skip_if_scope_missing(status_result, "get_execution_results_search_status")
        self.assert_no_error(status_result, context="get_execution_results_search_status")
        self.assert_valid_list_response(
            status_result,
            min_length=0,
            context="get_execution_results_search_status",
        )

        results = self.call_method(
            self.module.get_it_automation_execution_results,
            search_id=search_job_id,
            offset=0,
            limit=10,
            sort=None,
        )
        self._skip_if_scope_missing(results, "get_execution_results")
        self.assert_no_error(results, context="get_execution_results")
        self.assert_valid_list_response(results, min_length=0, context="get_execution_results")

    def test_write_operation_names_with_invalid_payloads(self):
        write_cases = [
            (
                "create_user_group",
                self.module.create_it_automation_user_group,
                {"confirm_execution": True, "body": {}},
            ),
            (
                "update_user_group",
                self.module.update_it_automation_user_group,
                {"confirm_execution": True, "user_group_id": "00000000", "body": {}},
            ),
            (
                "delete_user_group",
                self.module.delete_it_automation_user_groups,
                {"confirm_execution": True, "ids": ["00000000"]},
            ),
            (
                "create_policy",
                self.module.create_it_automation_policy,
                {"confirm_execution": True, "body": {}},
            ),
            (
                "update_policy_host_groups",
                self.module.update_it_automation_policy_host_groups,
                {"confirm_execution": True, "body": {}},
            ),
            (
                "start_task_execution",
                self.module.start_it_automation_task_execution,
                {
                    "confirm_execution": True,
                    "task_id": "00000000",
                    "target": "aid:'00000000000000000000000000000000'",
                    "arguments": None,
                    "discover_new_hosts": None,
                    "discover_offline_hosts": None,
                    "distribute": None,
                    "expiration_interval": None,
                    "guardrails": None,
                    "trigger_condition": None,
                    "body": None,
                },
            ),
            (
                "run_live_query",
                self.module.run_it_automation_live_query,
                {
                    "confirm_execution": True,
                    "target": "aid:'00000000000000000000000000000000'",
                    "osquery": "SELECT 1;",
                    "queries": None,
                    "output_parser_config": None,
                    "discover_new_hosts": None,
                    "discover_offline_hosts": None,
                    "distribute": None,
                    "expiration_interval": None,
                    "guardrails": None,
                    "body": None,
                },
            ),
            (
                "cancel_execution",
                self.module.cancel_it_automation_task_execution,
                {"confirm_execution": True, "task_execution_id": "00000000", "body": None},
            ),
            (
                "rerun_execution",
                self.module.rerun_it_automation_task_execution,
                {
                    "confirm_execution": True,
                    "task_execution_id": "00000000",
                    "run_type": "hosts",
                    "body": None,
                },
            ),
        ]

        for context, method, kwargs in write_cases:
            result = self.call_method(method, **kwargs)
            status_code = self._extract_status_code(result)

            if status_code == 403:
                self.skip_with_warning(
                    "Missing required IT Automation:write scope for write-operation test",
                    context=context,
                )
            if status_code in (400, 404, 422, 500):
                continue

            self.assert_no_error(result, context=context)
            self.assert_valid_list_response(result, min_length=0, context=context)
