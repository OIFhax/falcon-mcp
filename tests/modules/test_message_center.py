"""Tests for the Message Center module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.message_center import WRITE_ANNOTATIONS, MessageCenterModule
from tests.modules.utils.test_modules import TestModules


class TestMessageCenterModule(TestModules):
    """Test cases for the Message Center module."""

    def setUp(self):
        self.setup_module(MessageCenterModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_aggregate_message_center_cases",
            "falcon_get_message_center_case_activities",
            "falcon_add_message_center_case_activity",
            "falcon_download_message_center_case_attachment",
            "falcon_add_message_center_case_attachment",
            "falcon_create_message_center_case",
            "falcon_get_message_center_cases",
            "falcon_query_message_center_case_activity_ids",
            "falcon_query_message_center_case_ids",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        self.assert_resources_registered(["falcon_message_center_usage_guide", "falcon_message_center_safety_guide"])

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_query_message_center_case_ids", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_message_center_case", WRITE_ANNOTATIONS)

    def test_create_message_center_case_confirm_required(self):
        result = self.module.create_message_center_case(confirm_execution=False, body={"title": "x"})
        self.assertIn("error", result[0])

    def test_download_message_center_case_attachment_validation(self):
        result = self.module.download_message_center_case_attachment(ids=None)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
