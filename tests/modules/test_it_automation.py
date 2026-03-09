"""
Tests for the IT Automation module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.it_automation import ITAutomationModule
from tests.modules.utils.test_modules import TestModules


class TestITAutomationModule(TestModules):
    """Test cases for the IT Automation module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ITAutomationModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_it_automation_task_executions",
            "falcon_get_it_automation_task_executions",
            "falcon_get_it_automation_task_execution_host_status",
            "falcon_start_it_automation_task_execution",
            "falcon_run_it_automation_live_query",
            "falcon_cancel_it_automation_task_execution",
            "falcon_rerun_it_automation_task_execution",
            "falcon_start_it_automation_execution_results_search",
            "falcon_get_it_automation_execution_results_search_status",
            "falcon_get_it_automation_execution_results",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_it_automation_task_executions_fql_guide",
            "falcon_it_automation_phase3_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations(
            "falcon_search_it_automation_task_executions", READ_ONLY_ANNOTATIONS
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
        self.assert_tool_annotations(
            "falcon_cancel_it_automation_task_execution",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_search_task_executions_success(self):
        """Test searching task executions with parameters."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-1", "status": "running"}]},
        }

        result = self.module.search_it_automation_task_executions(
            filter="status:'running'",
            limit=25,
            offset=10,
            sort="start_time.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "ITAutomationGetTaskExecutionsByQuery",
            parameters={
                "filter": "status:'running'",
                "limit": 25,
                "offset": 10,
                "sort": "start_time.desc",
            },
        )
        self.assertEqual(len(result), 1)

    def test_search_task_executions_empty_filter_response(self):
        """Test empty filtered search returns FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_it_automation_task_executions(
            filter="task_name:'DoesNotExist*'",
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_task_executions_validation_and_success(self):
        """Test get task executions validation and success path."""
        validation_result = self.module.get_it_automation_task_executions(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-1"}]},
        }
        success_result = self.module.get_it_automation_task_executions(ids=["exec-1"])

        self.mock_client.command.assert_called_once_with(
            "ITAutomationGetTaskExecution",
            parameters={"ids": ["exec-1"]},
        )
        self.assertEqual(len(success_result), 1)

    def test_get_task_execution_host_status_success(self):
        """Test host status retrieval success path."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"task_execution_id": "exec-1", "status": "running"}]},
        }

        result = self.module.get_it_automation_task_execution_host_status(
            ids=["exec-1"],
            filter="status:'running'",
            limit=20,
            offset=5,
            sort="start_time.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "ITAutomationGetTaskExecutionHostStatus",
            parameters={
                "ids": ["exec-1"],
                "filter": "status:'running'",
                "limit": 20,
                "offset": 5,
                "sort": "start_time.desc",
            },
        )
        self.assertEqual(len(result), 1)

    def test_start_task_execution_gating_validation_and_success(self):
        """Test start task execution gating, validation, and success path."""
        no_confirm_result = self.module.start_it_automation_task_execution(
            confirm_execution=False,
            task_id="task-1",
            target="host_group:'abc123'",
            arguments=None,
            discover_new_hosts=None,
            discover_offline_hosts=None,
            distribute=None,
            expiration_interval=None,
            guardrails=None,
            trigger_condition=None,
            body=None,
        )
        self.assertIn("error", no_confirm_result[0])
        self.mock_client.command.assert_not_called()

        missing_fields_result = self.module.start_it_automation_task_execution(
            confirm_execution=True,
            task_id=None,
            target=None,
            arguments=None,
            discover_new_hosts=None,
            discover_offline_hosts=None,
            distribute=None,
            expiration_interval=None,
            guardrails=None,
            trigger_condition=None,
            body=None,
        )
        self.assertIn("error", missing_fields_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "exec-1"}]},
        }
        success_result = self.module.start_it_automation_task_execution(
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
        self.assertEqual(len(success_result), 1)

    def test_run_live_query_gating_validation_and_success(self):
        """Test live query gating, validation, and success path."""
        no_confirm_result = self.module.run_it_automation_live_query(
            confirm_execution=False,
            target="host_group:'abc123'",
            osquery="SELECT * FROM os_version;",
            queries=None,
            output_parser_config=None,
            discover_new_hosts=None,
            discover_offline_hosts=None,
            distribute=None,
            expiration_interval=None,
            guardrails=None,
            body=None,
        )
        self.assertIn("error", no_confirm_result[0])
        self.mock_client.command.assert_not_called()

        missing_payload_result = self.module.run_it_automation_live_query(
            confirm_execution=True,
            target="host_group:'abc123'",
            osquery=None,
            queries=None,
            output_parser_config=None,
            discover_new_hosts=None,
            discover_offline_hosts=None,
            distribute=None,
            expiration_interval=None,
            guardrails=None,
            body=None,
        )
        self.assertIn("error", missing_payload_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "exec-2"}]},
        }
        success_result = self.module.run_it_automation_live_query(
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
        self.assertEqual(len(success_result), 1)

    def test_cancel_and_rerun_execution_success(self):
        """Test cancel and rerun execution operations."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-1"}]},
        }
        cancel_result = self.module.cancel_it_automation_task_execution(
            confirm_execution=True,
            task_execution_id="exec-1",
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationCancelTaskExecution",
            body={"task_execution_id": "exec-1"},
        )
        self.assertEqual(len(cancel_result), 1)

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-2"}]},
        }
        rerun_result = self.module.rerun_it_automation_task_execution(
            confirm_execution=True,
            task_execution_id="exec-2",
            run_type="hosts",
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationRerunTaskExecution",
            body={"task_execution_id": "exec-2", "run_type": "hosts"},
        )
        self.assertEqual(len(rerun_result), 1)

    def test_execution_results_search_and_retrieval_success(self):
        """Test execution results search lifecycle helper methods."""
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
        self.assertEqual(len(start_result), 1)

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "job-1", "is_pending": False}]},
        }
        status_result = self.module.get_it_automation_execution_results_search_status(
            search_id="job-1"
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationGetExecutionResultsSearchStatus",
            parameters={"id": "job-1"},
        )
        self.assertEqual(len(status_result), 1)

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"hostname": "host-1"}]},
        }
        results = self.module.get_it_automation_execution_results(
            search_id="job-1",
            offset=0,
            limit=100,
            sort="hostname.asc",
        )
        self.mock_client.command.assert_called_once_with(
            "ITAutomationGetExecutionResults",
            parameters={"id": "job-1", "offset": 0, "limit": 100, "sort": "hostname.asc"},
        )
        self.assertEqual(len(results), 1)

    def test_run_live_query_permission_error(self):
        """Test permission error handling for live query execution."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.run_it_automation_live_query(
            confirm_execution=True,
            target="host_group:'abc123'",
            osquery="SELECT * FROM os_version;",
            queries=None,
            output_parser_config=None,
            discover_new_hosts=None,
            discover_offline_hosts=None,
            distribute=None,
            expiration_interval=None,
            guardrails=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
