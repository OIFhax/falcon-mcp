"""Tests for the IT Automation module."""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.it_automation import ITAutomationModule
from tests.modules.utils.test_modules import TestModules


class TestITAutomationModule(TestModules):
    """Test cases for the IT Automation module."""

    def setUp(self):
        self.setup_module(ITAutomationModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_search_it_automation_associated_tasks",
            "falcon_search_it_automation_scheduled_tasks_combined",
            "falcon_search_it_automation_task_executions",
            "falcon_search_it_automation_task_groups_combined",
            "falcon_search_it_automation_tasks_combined",
            "falcon_search_it_automation_user_group_ids",
            "falcon_query_it_automation_policy_ids",
            "falcon_search_it_automation_scheduled_task_ids",
            "falcon_search_it_automation_task_execution_ids",
            "falcon_search_it_automation_task_group_ids",
            "falcon_search_it_automation_task_ids",
            "falcon_get_it_automation_user_groups",
            "falcon_get_it_automation_policies",
            "falcon_get_it_automation_scheduled_tasks",
            "falcon_get_it_automation_task_executions",
            "falcon_get_it_automation_task_groups",
            "falcon_get_it_automation_tasks",
            "falcon_get_it_automation_task_execution_host_status",
            "falcon_start_it_automation_execution_results_search",
            "falcon_get_it_automation_execution_results_search_status",
            "falcon_get_it_automation_execution_results",
            "falcon_create_it_automation_user_group",
            "falcon_update_it_automation_user_group",
            "falcon_delete_it_automation_user_groups",
            "falcon_create_it_automation_policy",
            "falcon_update_it_automation_policies",
            "falcon_delete_it_automation_policies",
            "falcon_update_it_automation_policy_host_groups",
            "falcon_update_it_automation_policies_precedence",
            "falcon_create_it_automation_scheduled_task",
            "falcon_update_it_automation_scheduled_task",
            "falcon_delete_it_automation_scheduled_tasks",
            "falcon_create_it_automation_task_group",
            "falcon_update_it_automation_task_group",
            "falcon_delete_it_automation_task_groups",
            "falcon_create_it_automation_task",
            "falcon_update_it_automation_task",
            "falcon_delete_it_automation_tasks",
            "falcon_start_it_automation_task_execution",
            "falcon_run_it_automation_live_query",
            "falcon_cancel_it_automation_task_execution",
            "falcon_rerun_it_automation_task_execution",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_search_it_automation_task_executions_fql_guide",
            "falcon_it_automation_phase3_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations(
            "falcon_search_it_automation_task_executions",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_create_it_automation_task",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_it_automation_tasks",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_start_it_automation_task_execution",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_search_associated_tasks_validation_and_success(self):
        validation_result = self.module.search_it_automation_associated_tasks(
            file_id=None,
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "task-1"}]},
        }
        result = self.module.search_it_automation_associated_tasks(
            file_id="file-1",
            filter="name:'Containment*'",
            limit=10,
            offset=0,
            sort="name|asc",
        )

        self.mock_client.command.assert_called_once_with(
            "ITAutomationGetAssociatedTasks",
            parameters={
                "id": "file-1",
                "filter": "name:'Containment*'",
                "limit": 10,
                "offset": 0,
                "sort": "name|asc",
            },
        )
        self.assertEqual(len(result), 1)

    def test_search_operations_wiring(self):
        test_cases = [
            (
                self.module.search_it_automation_scheduled_tasks_combined,
                "ITAutomationCombinedScheduledTasks",
            ),
            (
                self.module.search_it_automation_task_groups_combined,
                "ITAutomationGetTaskGroupsByQuery",
            ),
            (
                self.module.search_it_automation_tasks_combined,
                "ITAutomationGetTasksByQuery",
            ),
            (
                self.module.search_it_automation_user_group_ids,
                "ITAutomationSearchUserGroup",
            ),
            (
                self.module.search_it_automation_scheduled_task_ids,
                "ITAutomationSearchScheduledTasks",
            ),
            (
                self.module.search_it_automation_task_execution_ids,
                "ITAutomationSearchTaskExecutions",
            ),
            (
                self.module.search_it_automation_task_group_ids,
                "ITAutomationSearchTaskGroups",
            ),
            (
                self.module.search_it_automation_task_ids,
                "ITAutomationSearchTasks",
            ),
        ]

        for method, operation in test_cases:
            with self.subTest(operation=operation):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {"resources": ["id-1"]},
                }

                result = method(
                    filter="name:'example'",
                    limit=5,
                    offset=0,
                    sort="name|asc",
                )

                self.mock_client.command.assert_called_once_with(
                    operation,
                    parameters={
                        "filter": "name:'example'",
                        "limit": 5,
                        "offset": 0,
                        "sort": "name|asc",
                    },
                )
                self.assertEqual(result, ["id-1"])

    def test_get_operations_by_ids_wiring(self):
        test_cases = [
            (self.module.get_it_automation_user_groups, "ITAutomationGetUserGroup"),
            (self.module.get_it_automation_policies, "ITAutomationGetPolicies"),
            (self.module.get_it_automation_scheduled_tasks, "ITAutomationGetScheduledTasks"),
            (self.module.get_it_automation_task_executions, "ITAutomationGetTaskExecution"),
            (self.module.get_it_automation_task_groups, "ITAutomationGetTaskGroups"),
            (self.module.get_it_automation_tasks, "ITAutomationGetTasks"),
        ]

        for method, operation in test_cases:
            with self.subTest(operation=operation):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {"resources": [{"id": "id-1"}]},
                }

                result = method(ids=["id-1"])

                self.mock_client.command.assert_called_once_with(
                    operation,
                    parameters={"ids": ["id-1"]},
                )
                self.assertEqual(result[0]["id"], "id-1")

    def test_query_policy_ids_validation_and_success(self):
        validation_result = self.module.query_it_automation_policy_ids(
            platform=None,
            limit=10,
            offset=0,
            sort=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["policy-1"]},
        }
        result = self.module.query_it_automation_policy_ids(
            platform="Windows",
            limit=10,
            offset=0,
            sort="precedence|asc",
        )

        self.mock_client.command.assert_called_once_with(
            "ITAutomationQueryPolicies",
            parameters={
                "platform": "Windows",
                "limit": 10,
                "offset": 0,
                "sort": "precedence|asc",
            },
        )
        self.assertEqual(result, ["policy-1"])

    def test_write_operations_validation(self):
        operations = [
            self.module.create_it_automation_user_group,
            self.module.create_it_automation_policy,
            self.module.create_it_automation_scheduled_task,
            self.module.create_it_automation_task_group,
            self.module.create_it_automation_task,
        ]
        for method in operations:
            with self.subTest(method=method.__name__):
                result = method(confirm_execution=False, body={"name": "test"})
                self.assertIn("error", result[0])

        update_validation = self.module.update_it_automation_task(
            confirm_execution=True,
            task_id=None,
            body={"name": "updated"},
        )
        self.assertIn("error", update_validation[0])

        delete_validation = self.module.delete_it_automation_tasks(
            confirm_execution=True,
            ids=None,
        )
        self.assertIn("error", delete_validation[0])

    def test_selected_write_operation_wiring(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "created-1"}]},
        }
        create_result = self.module.create_it_automation_user_group(
            confirm_execution=True,
            body={"name": "group-a"},
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationCreateUserGroup",
            body={"name": "group-a"},
        )
        self.assertEqual(create_result[0]["id"], "created-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        delete_result = self.module.delete_it_automation_tasks(
            confirm_execution=True,
            ids=["task-1"],
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationDeleteTask",
            parameters={"ids": ["task-1"]},
        )
        self.assertEqual(delete_result[0]["status"], "submitted")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        precedence_result = self.module.update_it_automation_policies_precedence(
            confirm_execution=True,
            platform="Windows",
            body={"ids": ["policy-1"]},
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationUpdatePoliciesPrecedence",
            parameters={"platform": "Windows"},
            body={"ids": ["policy-1"]},
        )
        self.assertEqual(precedence_result[0]["id"], "policy-1")

    def test_execution_controls_wiring(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "exec-1"}]},
        }
        start_result = self.module.start_it_automation_task_execution(
            confirm_execution=True,
            task_id="task-1",
            target="host_group:'abc123'",
            arguments={"foo": "bar"},
            discover_new_hosts=False,
            discover_offline_hosts=False,
            distribute=True,
            expiration_interval="1h",
            guardrails={"run_time_limit_millis": 600000},
            trigger_condition=None,
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationStartTaskExecution",
            body={
                "task_id": "task-1",
                "target": "host_group:'abc123'",
                "arguments": {"foo": "bar"},
                "discover_new_hosts": False,
                "discover_offline_hosts": False,
                "distribute": True,
                "expiration_interval": "1h",
                "guardrails": {"run_time_limit_millis": 600000},
            },
        )
        self.assertEqual(start_result[0]["id"], "exec-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "exec-2"}]},
        }
        live_result = self.module.run_it_automation_live_query(
            confirm_execution=True,
            target="host_group:'abc123'",
            osquery="SELECT * FROM os_version;",
            queries=None,
            output_parser_config=None,
            discover_new_hosts=False,
            discover_offline_hosts=False,
            distribute=True,
            expiration_interval="30m",
            guardrails={"run_time_limit_millis": 300000},
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationRunLiveQuery",
            body={
                "target": "host_group:'abc123'",
                "osquery": "SELECT * FROM os_version;",
                "discover_new_hosts": False,
                "discover_offline_hosts": False,
                "distribute": True,
                "expiration_interval": "30m",
                "guardrails": {"run_time_limit_millis": 300000},
            },
        )
        self.assertEqual(live_result[0]["id"], "exec-2")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-3"}]},
        }
        cancel_result = self.module.cancel_it_automation_task_execution(
            confirm_execution=True,
            task_execution_id="exec-3",
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationCancelTaskExecution",
            body={"task_execution_id": "exec-3"},
        )
        self.assertEqual(cancel_result[0]["id"], "exec-3")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-4"}]},
        }
        rerun_result = self.module.rerun_it_automation_task_execution(
            confirm_execution=True,
            task_execution_id="exec-4",
            run_type="hosts",
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationRerunTaskExecution",
            body={"task_execution_id": "exec-4", "run_type": "hosts"},
        )
        self.assertEqual(rerun_result[0]["id"], "exec-4")

    def test_execution_results_search_workflow(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "job-1"}]},
        }
        start_result = self.module.start_it_automation_execution_results_search(
            task_execution_id="exec-1",
            start="2026-01-01T00:00:00Z",
            end="2026-01-01T01:00:00Z",
            filter_expressions=["status=success"],
            group_by_fields=["hostname"],
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationStartExecutionResultsSearch",
            body={
                "task_execution_id": "exec-1",
                "start": "2026-01-01T00:00:00Z",
                "end": "2026-01-01T01:00:00Z",
                "filter_expressions": ["status=success"],
                "group_by_fields": ["hostname"],
            },
        )
        self.assertEqual(start_result[0]["id"], "job-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "job-1", "is_pending": False}]},
        }
        status_result = self.module.get_it_automation_execution_results_search_status(
            search_id="job-1",
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationGetExecutionResultsSearchStatus",
            parameters={"id": "job-1"},
        )
        self.assertEqual(status_result[0]["id"], "job-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"hostname": "host-a"}]},
        }
        result_records = self.module.get_it_automation_execution_results(
            search_id="job-1",
            offset=0,
            limit=10,
            sort="hostname.asc",
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationGetExecutionResults",
            parameters={"id": "job-1", "offset": 0, "limit": 10, "sort": "hostname.asc"},
        )
        self.assertEqual(result_records[0]["hostname"], "host-a")


if __name__ == "__main__":
    unittest.main()
