"""
Tests for the Fusion Playbooks module.
"""

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.fusion_playbooks import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    FUSION_PLAYBOOK_PATH_PATTERNS,
    FusionPlaybooksModule,
    WRITE_ANNOTATIONS,
)
from tests.modules.utils.test_modules import TestModules


class TestFusionPlaybooksModule(TestModules):
    """Test cases for the Fusion Playbooks module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(FusionPlaybooksModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        self.assert_tools_registered(
            [
                "falcon_get_fusion_playbook",
                "falcon_import_fusion_playbook",
                "falcon_update_fusion_playbook",
                "falcon_update_fusion_playbook_status",
                "falcon_execute_fusion_playbook",
                "falcon_mock_execute_fusion_playbook",
            ]
        )

    def test_register_resources(self):
        """Test registering resources with the server."""
        self.assert_resources_registered(["falcon_fusion_playbooks_guide"])

    def test_tool_annotations(self):
        """Test Fusion playbook tools declare read/write intent."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_get_fusion_playbook", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_import_fusion_playbook", WRITE_ANNOTATIONS)
        self.assert_tool_annotations("falcon_update_fusion_playbook", WRITE_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_update_fusion_playbook_status",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations("falcon_execute_fusion_playbook", WRITE_ANNOTATIONS)
        self.assert_tool_annotations("falcon_mock_execute_fusion_playbook", WRITE_ANNOTATIONS)

    def test_get_fusion_playbook_public_workflow_export_success(self):
        """Test workflow definition export remains the primary retrieval path."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "wf-def-1", "name": "Workflow"}]},
        }

        result = self.module.get_fusion_playbook(playbook_id="a" * 32, sanitize=True)

        self.mock_client.command.assert_called_once_with(
            "WorkflowDefinitionsExport",
            parameters={"id": "a" * 32, "sanitize": True},
        )
        self.mock_client.raw_get_allowed.assert_not_called()
        self.assertEqual(result["source"], "workflow_definition_export")
        self.assertEqual(result["resources"][0]["name"], "Workflow")

    def test_get_fusion_playbook_fallback_success_after_workflow_404(self):
        """Test Fusion playbook fallback is used after workflow definition 404."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "definition not found"}]},
        }
        self.mock_client.raw_get_allowed.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"id": "a" * 32, "name": "Fusion Playbook"},
        }

        result = self.module.get_fusion_playbook(playbook_id="a" * 32, sanitize=False)

        self.mock_client.raw_get_allowed.assert_called_once_with(
            "FusionPlaybookReadExperimental",
            f"/workflow/fusion/playbooks/{'a' * 32}/export",
            parameters={"sanitize": False},
            allowed_path_patterns=FUSION_PLAYBOOK_PATH_PATTERNS,
        )
        self.assertEqual(result["source"], "fusion_playbook_experimental")
        self.assertEqual(result["data"]["name"], "Fusion Playbook")

    def test_get_fusion_playbook_all_fallback_routes_missing(self):
        """Test a clear error when public and fallback routes miss."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "definition not found"}]},
        }
        self.mock_client.raw_get_allowed.return_value = {
            "status_code": 404,
            "headers": {"Content-Type": "application/json"},
            "body": {"errors": [{"message": "playbook not found"}]},
        }

        result = self.module.get_fusion_playbook(playbook_id="b" * 32, sanitize=True)

        self.assertIn("error", result)
        self.assertEqual(result["error_type"], "unsupported_route")
        self.assertEqual(self.mock_client.raw_get_allowed.call_count, 2)
        self.assertEqual(
            len(result["details"]["fusion_playbook_attempts"]),
            2,
        )

    def test_get_fusion_playbook_rejects_invalid_id(self):
        """Test invalid playbook IDs are rejected before network calls."""
        result = self.module.get_fusion_playbook(playbook_id="../bad", sanitize=True)

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()
        self.mock_client.raw_get_allowed.assert_not_called()

    def test_get_fusion_playbook_html_route_is_unsupported(self):
        """Test UI HTML responses are not treated as API-compatible playbooks."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "definition not found"}]},
        }
        self.mock_client.raw_get_allowed.return_value = {
            "status_code": 200,
            "headers": {"Content-Type": "text/html"},
            "body": {"raw": "<!doctype html><html><body>login</body></html>"},
        }

        result = self.module.get_fusion_playbook(playbook_id="c" * 32, sanitize=True)

        self.assertIn("error", result)
        self.assertEqual(result["error_type"], "unsupported_route")
        self.assertIn("UI/session", result["error"])

    def test_import_fusion_playbook_requires_content(self):
        """Test import requires YAML content."""
        result = self.module.import_fusion_playbook(
            data_file_content=None,
            name=None,
            validate_only=False,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_import_fusion_playbook_has_no_confirm_gate(self):
        """Test import delegates to workflow import without confirm_execution."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "wf-def-1"}]},
        }

        result = self.module.import_fusion_playbook(
            data_file_content="name: test-playbook",
            name="test-playbook",
            validate_only=False,
        )

        self.mock_client.command.assert_called_once()
        call = self.mock_client.command.call_args
        self.assertEqual(call[0][0], "WorkflowDefinitionsImport")
        self.assertEqual(call[1]["parameters"], {"name": "test-playbook", "validate_only": False})
        self.assertEqual(call[1]["files"][0][0], "data_file")
        self.assertEqual(call[1]["files"][0][1][0], "workflow.yaml")
        self.assertEqual(call[1]["files"][0][1][2], "application/x-yaml")
        self.assertEqual(result[0]["id"], "wf-def-1")

    def test_update_fusion_playbook_has_no_confirm_gate(self):
        """Test update delegates to workflow update without confirm_execution."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "wf-def-1", "name": "updated"}]},
        }

        result = self.module.update_fusion_playbook(
            body={"id": "wf-def-1", "name": "updated"},
            validate_only=False,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowDefinitionsUpdate",
            parameters={"validate_only": False},
            body={"id": "wf-def-1", "name": "updated"},
        )
        self.assertEqual(result[0]["name"], "updated")

    def test_update_fusion_playbook_requires_body(self):
        """Test update requires a body payload."""
        result = self.module.update_fusion_playbook(body=None, validate_only=False)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_fusion_playbook_status_has_no_confirm_gate(self):
        """Test status action delegates without confirm_execution."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "wf-def-1"}]},
        }

        result = self.module.update_fusion_playbook_status(
            action_name="disable",
            ids=["wf-def-1"],
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowDefinitionsAction",
            parameters={"action_name": "disable"},
            body={"ids": ["wf-def-1"]},
        )
        self.assertEqual(result[0]["id"], "wf-def-1")

    def test_update_fusion_playbook_status_requires_selector(self):
        """Test status action requires ids or an explicit body."""
        result = self.module.update_fusion_playbook_status(
            action_name="disable",
            ids=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_execute_fusion_playbook_has_no_confirm_gate(self):
        """Test execution delegates without confirm_execution."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-1"}]},
        }

        result = self.module.execute_fusion_playbook(
            body=None,
            execution_cid=None,
            playbook_id="wf-def-1",
            name=None,
            key=None,
            depth=None,
            source_event_url=None,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowExecute",
            parameters={"definition_id": ["wf-def-1"]},
        )
        self.assertEqual(result[0]["id"], "exec-1")

    def test_execute_fusion_playbook_requires_body_or_selector(self):
        """Test execution requires a body or selector."""
        result = self.module.execute_fusion_playbook(
            body=None,
            execution_cid=None,
            playbook_id=None,
            name=None,
            key=None,
            depth=None,
            source_event_url=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_mock_execute_fusion_playbook_has_no_confirm_gate(self):
        """Test mock execution delegates without confirm_execution."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "mock-1"}]},
        }

        result = self.module.mock_execute_fusion_playbook(
            body={},
            execution_cid=None,
            playbook_id="wf-def-1",
            name=None,
            key=None,
            depth=None,
            source_event_url=None,
            validate_only=False,
            skip_validation=None,
            ignore_activity_mock_references=None,
        )

        self.mock_client.command.assert_called_once_with(
            "WorkflowMockExecute",
            parameters={"definition_id": "wf-def-1", "validate_only": False},
        )
        self.assertEqual(result[0]["id"], "mock-1")

    def test_mock_execute_fusion_playbook_requires_body_or_selector(self):
        """Test mock execution requires a body or selector."""
        result = self.module.mock_execute_fusion_playbook(
            body=None,
            execution_cid=None,
            playbook_id=None,
            name=None,
            key=None,
            depth=None,
            source_event_url=None,
            validate_only=False,
            skip_validation=None,
            ignore_activity_mock_references=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()
