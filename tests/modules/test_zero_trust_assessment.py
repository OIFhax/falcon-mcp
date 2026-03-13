"""
Tests for the Zero Trust Assessment module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.zero_trust_assessment import ZeroTrustAssessmentModule
from tests.modules.utils.test_modules import TestModules


class TestZeroTrustAssessmentModule(TestModules):
    """Test cases for the Zero Trust Assessment module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ZeroTrustAssessmentModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_zta_assessments_by_score",
            "falcon_search_zta_combined_assessments",
            "falcon_get_zta_assessment_details",
            "falcon_get_zta_audit_report",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_zta_assessments_fql_guide",
            "falcon_search_zta_combined_assessments_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_zta_assessments_by_score_validation_error(self):
        """Test that score search requires a filter."""
        result = self.module.search_zta_assessments_by_score(
            filter=None,
            limit=100,
            after=None,
            sort=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_search_zta_assessments_by_score_success(self):
        """Test score search dispatches operation and returns resources."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"aid": "aid-1", "score": 92},
                    {"aid": "aid-2", "score": 88},
                ]
            },
        }

        result = self.module.search_zta_assessments_by_score(
            filter="score:>=80",
            limit=20,
            after="next-token",
            sort="score|desc",
        )

        self.mock_client.command.assert_called_once_with(
            "getAssessmentsByScoreV1",
            parameters={
                "filter": "score:>=80",
                "limit": 20,
                "after": "next-token",
                "sort": "score|desc",
            },
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["aid"], "aid-1")

    def test_search_zta_assessments_by_score_error_returns_fql_guide(self):
        """Test search errors include an FQL helper response."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"code": 400, "message": "invalid filter"}]},
        }

        result = self.module.search_zta_assessments_by_score(
            filter="score:'high'",
            limit=10,
            after=None,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertEqual(result["filter_used"], "score:'high'")

    def test_get_zta_assessment_details_validation_error(self):
        """Test detail lookup requires IDs."""
        result = self.module.get_zta_assessment_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_zta_assessment_details_success(self):
        """Test detail lookup by AID."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"aid": "aid-1", "score": 77}]},
        }

        result = self.module.get_zta_assessment_details(ids=["aid-1"])

        self.mock_client.command.assert_called_once_with(
            "getAssessmentV1",
            parameters={"ids": ["aid-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["aid"], "aid-1")

    def test_search_zta_combined_assessments_validation_error(self):
        """Test combined search requires a filter."""
        result = self.module.search_zta_combined_assessments(
            filter=None,
            facet=None,
            limit=100,
            after=None,
            sort=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_search_zta_combined_assessments_success(self):
        """Test combined search dispatches operation and returns resources."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "finding-1", "aid": "aid-1"}]},
        }

        result = self.module.search_zta_combined_assessments(
            filter="updated_timestamp:>'now-7d'",
            facet=["host"],
            limit=10,
            after="token-1",
            sort="updated_timestamp.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "getCombinedAssessmentsQuery",
            parameters={
                "filter": "updated_timestamp:>'now-7d'",
                "facet": ["host"],
                "limit": 10,
                "after": "token-1",
                "sort": "updated_timestamp.desc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["aid"], "aid-1")

    def test_search_zta_combined_assessments_error_returns_fql_guide(self):
        """Test combined search errors include an FQL helper response."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"code": 400, "message": "invalid filter"}]},
        }

        result = self.module.search_zta_combined_assessments(
            filter="badfilter",
            facet=None,
            limit=10,
            after=None,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertEqual(result["filter_used"], "badfilter")

    def test_get_zta_audit_report_success(self):
        """Test audit report retrieval."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cid": "abc123", "num_aids": 42}]},
        }

        result = self.module.get_zta_audit_report()

        self.mock_client.command.assert_called_once_with("getAuditV1")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cid"], "abc123")

    def test_search_zta_assessments_has_read_only_annotations(self):
        """Test that score search is registered as read-only."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_search_zta_assessments_by_score",
            READ_ONLY_ANNOTATIONS,
        )


if __name__ == "__main__":
    unittest.main()
