"""Tests for the Case Management module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.case_management import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    CaseManagementModule,
)
from tests.modules.utils.test_modules import TestModules


class TestCaseManagementModule(TestModules):
    """Test cases for the Case Management module."""

    def setUp(self):
        self.setup_module(CaseManagementModule)

    def test_register_tools(self):
        expected_tools = [f"falcon_{spec['tool_name']}" for spec in CaseManagementModule.TOOL_SPECS]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        self.assert_resources_registered(
            ["falcon_case_management_usage_guide", "falcon_case_management_safety_guide"]
        )

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_case_management_queries_cases_get_v1", READ_ONLY_ANNOTATIONS
        )
        self.assert_tool_annotations(
            "falcon_case_management_entities_cases_patch_v2", WRITE_ANNOTATIONS
        )
        self.assert_tool_annotations(
            "falcon_case_management_entities_files_delete_v1",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_case_management_write_confirm_required(self):
        result = self.module.case_management_entities_cases_patch_v2(
            confirm_execution=False,
            body={"id": "case-id"},
        )
        self.assertIn("error", result[0])

    def test_case_management_body_read_requires_body(self):
        result = self.module.case_management_entities_cases_post_v2(body=None)
        self.assertIn("error", result[0])

    def test_case_management_upload_requires_file_payload(self):
        result = self.module.case_management_entities_files_upload_post_v1(
            confirm_execution=True,
            file_name=None,
            file_data_base64=None,
            parameters={"case_id": "case-id"},
        )
        self.assertIn("error", result[0])

    def test_case_management_upload_rejects_invalid_base64(self):
        result = self.module.case_management_entities_templates_import_post_v1(
            confirm_execution=True,
            file_name="template.json",
            file_data_base64="not-base64",
            parameters={"dry_run": True},
        )
        self.assertIn("error", result[0])

    def test_case_management_binary_download_can_inline_content(self):
        self.mock_client.command.return_value = b"hello"
        result = self.module.case_management_entities_files_download_get_v1(
            parameters={"id": "file-id"},
            include_binary_base64=True,
            max_inline_bytes=10,
        )
        self.assertEqual(result[0]["binary_base64"], "aGVsbG8=")


if __name__ == "__main__":
    unittest.main()
