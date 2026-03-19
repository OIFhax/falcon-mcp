"""Tests for the Device Content module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.device_content import DeviceContentModule
from tests.modules.utils.test_modules import TestModules


class TestDeviceContentModule(TestModules):
    """Test cases for the Device Content module."""

    def setUp(self):
        self.setup_module(DeviceContentModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_search_device_content_states",
            "falcon_query_device_content_state_ids",
            "falcon_get_device_content_states",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        self.assert_resources_registered(["falcon_device_content_fql_guide"])

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_device_content_states", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_device_content_states", READ_ONLY_ANNOTATIONS)

    def test_query_device_content_state_ids_empty_filter_returns_guide(self):
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_device_content_state_ids(
            filter="state:'not-real'",
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)

    def test_get_device_content_states_validation(self):
        result = self.module.get_device_content_states(ids=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_search_device_content_states_success(self):
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["state-1"]}},
            {"status_code": 200, "body": {"resources": [{"id": "state-1", "state": "ready"}]}},
        ]

        result = self.module.search_device_content_states(limit=1)

        self.assertEqual(result[0]["id"], "state-1")


if __name__ == "__main__":
    unittest.main()
