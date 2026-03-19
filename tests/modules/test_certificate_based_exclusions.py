"""
Tests for the Certificate Based Exclusions module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.certificate_based_exclusions import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    CertificateBasedExclusionsModule,
)
from tests.modules.utils.test_modules import TestModules


class TestCertificateBasedExclusionsModule(TestModules):
    """Test cases for the Certificate Based Exclusions module."""

    def setUp(self):
        self.setup_module(CertificateBasedExclusionsModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_search_certificate_based_exclusions",
            "falcon_query_certificate_based_exclusion_ids",
            "falcon_get_certificate_based_exclusion_details",
            "falcon_get_certificate_signing_info",
            "falcon_create_certificate_based_exclusions",
            "falcon_update_certificate_based_exclusions",
            "falcon_delete_certificate_based_exclusions",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_search_certificate_based_exclusions_fql_guide",
            "falcon_certificate_based_exclusions_certificates_guide",
            "falcon_certificate_based_exclusions_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_search_certificate_based_exclusions",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_create_certificate_based_exclusions",
            WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_delete_certificate_based_exclusions",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_query_certificate_based_exclusion_ids_empty_filter_returns_guide(self):
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}
        result = self.module.query_certificate_based_exclusion_ids(
            filter="name:'NotReal*'",
            limit=10,
            offset=0,
            sort=None,
        )
        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)

    def test_get_certificate_based_exclusion_details_validation(self):
        result = self.module.get_certificate_based_exclusion_details(ids=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_certificate_signing_info_validation(self):
        result = self.module.get_certificate_signing_info(sha256=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_certificate_based_exclusions_confirm_required(self):
        result = self.module.create_certificate_based_exclusions(
            confirm_execution=False,
            body=None,
            name="test",
        )
        self.assertIn("error", result[0])

    def test_delete_certificate_based_exclusions_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"deleted": 1}]},
        }
        result = self.module.delete_certificate_based_exclusions(
            confirm_execution=True,
            ids=["id-1"],
            comment="cleanup",
        )
        self.mock_client.command.assert_called_once_with(
            "cb_exclusions_delete_v1",
            parameters={"ids": ["id-1"], "comment": "cleanup"},
        )
        self.assertEqual(result[0]["deleted"], 1)


if __name__ == "__main__":
    unittest.main()
