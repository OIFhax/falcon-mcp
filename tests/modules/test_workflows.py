"""
Tests for the Workflows module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.workflows import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    WorkflowsModule,
)
from tests.modules.utils.test_modules import TestModules


class TestWorkflowsModule(TestModules):
    """Test cases for the Workflows module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(WorkflowsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_workflow_activities",
            "falcon_search_workflow_activities_content",
            "falcon_search_workflow_definitions",
            "falcon_search_workflow_executions",
            "falcon_search_workflow_triggers",
            "falcon_export_workflow_definition",
            "falcon_import_workflow_definition",
            "falcon_update_workflow_definition",
            "falcon_update_workflow_definition_status",
            "falcon_execute_workflow",
            "falcon_execute_workflow_internal",
            "falcon_mock_execute_workflow",
            "falcon_update_workflow_execution_state",
            "falcon_get_workflow_execution_results",
            "falcon_get_workflow_human_input",
            "falcon_update_workflow_human_input",
            "falcon_deprovision_workflow_system_definition",
            "falcon_promote_workflow_system_definition",
            "falcon_provision_workflow_system_definition",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_workflow_activities_fql_guide",
            "falcon_search_workflow_definitions_fql_guide",
            "falcon_search_workflow_executions_fql_guide",
            "falcon_search_workflow_triggers_fql_guide",
            "falcon_workflow_import_guide",
            "falcon_workflow_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_workflow_definitions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_import_workflow_definition", WRITE_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_update_workflow_definition_status",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_update_workflow_execution_state",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_search_workflow_definitions_success(self):
        """Test workflow definition search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "wf-def-1", "name": "My Workflow"}]},
        }

        result = self.module.search_workflow_definitions(
            filter="name:'My Workflow'",
            limit=10,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowDefinitionsCombined",
            parameters={
                "filter": "name:'My Workflow'",
                "limit": 10,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "wf-def-1")

    def test_search_workflow_definitions_empty_filter_returns_guide(self):
        """Test empty filtered search returns FQL helper response."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.search_workflow_definitions(
            filter="name:'DoesNotExist*'",
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_export_workflow_definition_requires_id(self):
        """Test export requires ID."""
        result = self.module.export_workflow_definition(id=None, sanitize=True)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_export_workflow_definition_success(self):
        """Test export workflow definition call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "exported-workflow"}]},
        }

        result = self.module.export_workflow_definition(id="wf-def-1", sanitize=True)

        self.mock_client.command.assert_called_once_with(
            "WorkflowDefinitionsExport",
            parameters={"id": "wf-def-1", "sanitize": True},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "exported-workflow")

    def test_export_workflow_definition_bytes_response(self):
        """Test export workflow definition returns decoded YAML on bytes response."""
        self.mock_client.command.return_value = b"name: exported-workflow\n"

        result = self.module.export_workflow_definition(id="wf-def-1", sanitize=True)

        self.mock_client.command.assert_called_once_with(
            "WorkflowDefinitionsExport",
            parameters={"id": "wf-def-1", "sanitize": True},
        )
        self.assertIsInstance(result, str)
        self.assertIn("name: exported-workflow", result)

    def test_import_workflow_definition_confirm_required(self):
        """Test import requires confirm_execution=true."""
        result = self.module.import_workflow_definition(
            confirm_execution=False,
            data_file_content="name: test",
            name=None,
            validate_only=True,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_import_workflow_definition_requires_content(self):
        """Test import requires YAML content."""
        result = self.module.import_workflow_definition(
            confirm_execution=True,
            data_file_content=None,
            name=None,
            validate_only=True,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_import_workflow_definition_success(self):
        """Test import workflow definition call."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "wf-def-1"}]},
        }

        result = self.module.import_workflow_definition(
            confirm_execution=True,
            data_file_content="name: test-workflow",
            name="test-workflow",
            validate_only=True,
        )

        self.mock_client.command.assert_called_once()
        call = self.mock_client.command.call_args
        self.assertEqual(call[0][0], "WorkflowDefinitionsImport")
        self.assertEqual(call[1]["parameters"], {"name": "test-workflow", "validate_only": True})
        self.assertEqual(call[1]["files"][0][0], "data_file")
        self.assertEqual(call[1]["files"][0][1][0], "workflow.yaml")
        self.assertEqual(call[1]["files"][0][1][2], "application/x-yaml")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "wf-def-1")

    def test_update_workflow_definition_confirm_required(self):
        """Test update requires confirm_execution=true."""
        result = self.module.update_workflow_definition(
            confirm_execution=False,
            body={"name": "updated"},
            validate_only=True,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_workflow_definition_success(self):
        """Test update workflow definition call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "wf-def-1", "name": "updated"}]},
        }

        result = self.module.update_workflow_definition(
            confirm_execution=True,
            body={"name": "updated"},
            validate_only=True,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowDefinitionsUpdate",
            parameters={"validate_only": True},
            body={"name": "updated"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "updated")

    def test_update_workflow_definition_status_success(self):
        """Test workflow definition status action call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "wf-def-1"}]},
        }

        result = self.module.update_workflow_definition_status(
            confirm_execution=True,
            action_name="enable",
            ids=["wf-def-1"],
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowDefinitionsAction",
            parameters={"action_name": "enable"},
            body={"ids": ["wf-def-1"]},
        )
        self.assertEqual(len(result), 1)

    def test_execute_workflow_requires_selector_or_body(self):
        """Test execute workflow validates selector/body requirements."""
        result = self.module.execute_workflow(
            confirm_execution=True,
            body=None,
            execution_cid=None,
            definition_id=None,
            name=None,
            key=None,
            depth=None,
            source_event_url=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_execute_workflow_success(self):
        """Test execute workflow API call."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "wf-exec-1"}]},
        }

        result = self.module.execute_workflow(
            confirm_execution=True,
            body=None,
            execution_cid=["cid-1"],
            definition_id=["wf-def-1"],
            name=None,
            key="request-1",
            depth=1,
            source_event_url="https://example.invalid/event/1",
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowExecute",
            parameters={
                "execution_cid": ["cid-1"],
                "definition_id": ["wf-def-1"],
                "key": "request-1",
                "depth": 1,
                "source_event_url": "https://example.invalid/event/1",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "wf-exec-1")

    def test_mock_execute_workflow_success(self):
        """Test mock execute workflow call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "wf-exec-mock-1"}]},
        }

        result = self.module.mock_execute_workflow(
            confirm_execution=True,
            body=None,
            execution_cid=["cid-1"],
            definition_id="wf-def-1",
            name=None,
            key=None,
            depth=None,
            source_event_url=None,
            validate_only=True,
            skip_validation=None,
            ignore_activity_mock_references=None,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowMockExecute",
            parameters={
                "execution_cid": ["cid-1"],
                "definition_id": "wf-def-1",
                "validate_only": True,
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "wf-exec-mock-1")

    def test_get_workflow_execution_results_validation_and_success(self):
        """Test execution result validation and success path."""
        validation_result = self.module.get_workflow_execution_results(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "wf-exec-1", "status": "complete"}]},
        }
        success_result = self.module.get_workflow_execution_results(ids=["wf-exec-1"])

        self.mock_client.command.assert_called_once_with(
            "WorkflowExecutionResults",
            parameters={"ids": ["wf-exec-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["status"], "complete")

    def test_update_workflow_human_input_success(self):
        """Test workflow human-input update call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "human-input-1", "input": "Approve"}]},
        }

        result = self.module.update_workflow_human_input(
            confirm_execution=True,
            id="human-input-1",
            input="Approve",
            note="approved by unit test",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowUpdateHumanInputV1",
            parameters={"id": "human-input-1"},
            body={"input": "Approve", "note": "approved by unit test"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["input"], "Approve")

    def test_deprovision_workflow_system_definition_validation_and_success(self):
        """Test deprovision validation and success path."""
        validation_result = self.module.deprovision_workflow_system_definition(
            confirm_execution=True,
            body=None,
            definition_id=None,
            template_id=None,
            template_name=None,
            deprovision_all=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"definition_id": "wf-def-1"}]},
        }
        success_result = self.module.deprovision_workflow_system_definition(
            confirm_execution=True,
            body=None,
            definition_id="wf-def-1",
            template_id=None,
            template_name=None,
            deprovision_all=None,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowSystemDefinitionsDeProvision",
            body={"definition_id": "wf-def-1"},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["definition_id"], "wf-def-1")

    def test_promote_and_provision_system_definition_success(self):
        """Test promote and provision system-definition operations."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"status": "ok"}]},
        }
        promote_result = self.module.promote_workflow_system_definition(
            confirm_execution=True,
            body={"template_name": "Sample Template"},
        )
        self.mock_client.command.assert_called_once_with(
            "WorkflowSystemDefinitionsPromote",
            body={"template_name": "Sample Template"},
        )
        self.assertEqual(len(promote_result), 1)

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"status": "ok"}]},
        }
        provision_result = self.module.provision_workflow_system_definition(
            confirm_execution=True,
            body={"template_name": "Sample Template"},
        )
        self.mock_client.command.assert_called_once_with(
            "WorkflowSystemDefinitionsProvision",
            body={"template_name": "Sample Template"},
        )
        self.assertEqual(len(provision_result), 1)


if __name__ == "__main__":
    unittest.main()
