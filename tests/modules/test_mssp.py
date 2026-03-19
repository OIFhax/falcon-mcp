"""Tests for the MSSP (Flight Control) module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.mssp import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    MSSPModule,
)
from tests.modules.utils.test_modules import TestModules


class TestMSSPModule(TestModules):
    """Test cases for the MSSP module."""

    def setUp(self):
        self.setup_module(MSSPModule)

    def test_register_tools(self):
        self.module.register_tools(self.mock_server)
        self.assertGreaterEqual(len(self.module.tools), 35)
        self.assertIn("falcon_query_mssp_children", self.module.tools)
        self.assertIn("falcon_add_mssp_role", self.module.tools)
        self.assertIn("falcon_delete_mssp_user_groups", self.module.tools)

    def test_register_resources(self):
        self.assert_resources_registered(["falcon_mssp_usage_guide", "falcon_mssp_safety_guide"])

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_query_mssp_children", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_add_mssp_role", WRITE_ANNOTATIONS)
        self.assert_tool_annotations("falcon_delete_mssp_user_groups", DESTRUCTIVE_WRITE_ANNOTATIONS)

    def test_add_mssp_role_confirm_required(self):
        result = self.module.add_mssp_role(confirm_execution=False, body={"cid": "x"})
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
