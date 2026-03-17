"""
Tests for the Spotlight module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.spotlight import SpotlightModule
from tests.modules.utils.test_modules import TestModules


class TestSpotlightModule(TestModules):
    """Test cases for the Spotlight module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(SpotlightModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_vulnerabilities",
            "falcon_query_vulnerability_ids",
            "falcon_get_vulnerability_details",
            "falcon_get_remediation_details",
            "falcon_get_remediation_details_v2",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_vulnerabilities_fql_guide",
            "falcon_spotlight_remediations_usage_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_vulnerabilities", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_remediation_details_v2", READ_ONLY_ANNOTATIONS)

    def test_search_vulnerabilities_success(self):
        """Test vulnerability combined search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "vuln-1", "status": "open"}]},
        }

        result = self.module.search_vulnerabilities(
            filter="status:'open'",
            limit=10,
            offset=0,
            sort="created_timestamp|desc",
            after=None,
            facet="cve",
        )

        self.mock_client.command.assert_called_once_with(
            "combinedQueryVulnerabilities",
            parameters={
                "filter": "status:'open'",
                "limit": 10,
                "offset": 0,
                "sort": "created_timestamp|desc",
                "facet": "cve",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "vuln-1")

    def test_query_vulnerability_ids_empty_filter_returns_guide(self):
        """Test ID query with empty filtered result returns FQL helper response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.query_vulnerability_ids(
            filter="status:'none'",
            limit=100,
            offset=0,
            sort=None,
            after=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_vulnerability_details_validation_and_success(self):
        """Test vulnerability details validation and success path."""
        validation_result = self.module.get_vulnerability_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "vuln-1"}]},
        }
        success_result = self.module.get_vulnerability_details(ids=["vuln-1"])

        self.mock_client.command.assert_called_once_with(
            "getVulnerabilities",
            parameters={"ids": ["vuln-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "vuln-1")

    def test_get_remediation_details_validation_and_success(self):
        """Test remediation details validation and success path."""
        validation_result = self.module.get_remediation_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rem-1"}]},
        }
        success_result = self.module.get_remediation_details(ids=["rem-1"])

        self.mock_client.command.assert_called_once_with(
            "getRemediations",
            parameters={"ids": ["rem-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "rem-1")

    def test_get_remediation_details_v2_success(self):
        """Test remediation details v2 success path."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rem-2"}]},
        }

        result = self.module.get_remediation_details_v2(ids=["rem-2"])

        self.mock_client.command.assert_called_once_with(
            "getRemediationsV2",
            parameters={"ids": ["rem-2"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "rem-2")


if __name__ == "__main__":
    unittest.main()
