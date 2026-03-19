"""Tests for the API Integrations module."""

import unittest

from falcon_mcp.modules.api_integrations import (
    WRITE_ANNOTATIONS,
    APIIntegrationsModule,
)
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from tests.modules.utils.test_modules import TestModules


class TestAPIIntegrationsModule(TestModules):
    """Test cases for the API Integrations module."""

    def setUp(self):
        self.setup_module(APIIntegrationsModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_search_api_integration_plugin_configs",
            "falcon_execute_api_integration_command",
            "falcon_execute_api_integration_command_proxy",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_api_integrations_fql_guide",
            "falcon_api_integrations_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_api_integration_plugin_configs", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_execute_api_integration_command", WRITE_ANNOTATIONS)

    def test_execute_api_integration_command_confirm_required(self):
        result = self.module.execute_api_integration_command(confirm_execution=False)
        self.assertIn("error", result[0])

    def test_execute_api_integration_command_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"status": "queued"}]},
        }

        result = self.module.execute_api_integration_command(
            confirm_execution=True,
            plugin_id="plugin.operation",
            operation_id="op-id",
            description="integration test",
        )

        self.mock_client.command.assert_called_once_with(
            "ExecuteCommand",
            body={
                "resources": [
                    {
                        "id": "plugin.operation",
                        "operation_id": "op-id",
                        "request": {"description": "integration test"},
                    }
                ]
            },
        )
        self.assertEqual(result[0]["status"], "queued")


if __name__ == "__main__":
    unittest.main()
