"""
Tests for the CAO Hunting module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.cao_hunting import CAOHuntingModule
from tests.modules.utils.test_modules import TestModules


class TestCAOHuntingModule(TestModules):
    """Test cases for the CAO Hunting module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(CAOHuntingModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_hunting_guides",
            "falcon_get_hunting_guide_details",
            "falcon_search_intelligence_queries",
            "falcon_get_intelligence_query_details",
            "falcon_aggregate_hunting_guides",
            "falcon_aggregate_intelligence_queries",
            "falcon_create_hunting_archive_export",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_hunting_guides_fql_guide",
            "falcon_search_intelligence_queries_fql_guide",
            "falcon_cao_hunting_archive_export_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_hunting_guides_success(self):
        """Test searching hunting guides and fetching full details."""
        search_response = {
            "status_code": 200,
            "body": {"resources": ["guide-id-1", "guide-id-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "guide-id-1", "name": "Guide One"},
                    {"id": "guide-id-2", "name": "Guide Two"},
                ]
            },
        }
        self.mock_client.command.side_effect = [search_response, details_response]

        result = self.module.search_hunting_guides(
            filter="language:'cql'",
            q=None,
            limit=10,
            offset=0,
            sort="name|asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "SearchHuntingGuides")
        self.assertEqual(first_call[1]["parameters"]["filter"], "language:'cql'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "name|asc")

        self.assertEqual(second_call[0][0], "GetHuntingGuides")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["guide-id-1", "guide-id-2"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "guide-id-1")

    def test_search_hunting_guides_empty_with_filter_returns_guide(self):
        """Test empty guide results include FQL helper response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_hunting_guides(
            filter="language:'none'",
            q=None,
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_hunting_guide_details_validation_error(self):
        """Test get_hunting_guide_details requires ids."""
        result = self.module.get_hunting_guide_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_search_intelligence_queries_success(self):
        """Test searching intelligence queries and fetching full details."""
        search_response = {
            "status_code": 200,
            "body": {"resources": ["query-id-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "query-id-1", "language": "cql"}]},
        }
        self.mock_client.command.side_effect = [search_response, details_response]

        result = self.module.search_intelligence_queries(
            filter="language:'cql'",
            q=None,
            limit=5,
            offset=0,
            sort="updated_at.desc",
            include_translated_content=["SPL"],
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "GetIntelligenceQueries")
        self.assertEqual(second_call[1]["parameters"]["include_translated_content"], ["SPL"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "query-id-1")

    def test_get_intelligence_query_details_validation_error(self):
        """Test get_intelligence_query_details requires ids."""
        result = self.module.get_intelligence_query_details(
            ids=None,
            include_translated_content=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_aggregate_hunting_guides_validation_error(self):
        """Test aggregate_hunting_guides requires body."""
        result = self.module.aggregate_hunting_guides(body=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_aggregate_hunting_guides_success(self):
        """Test hunting guide aggregation call."""
        body = [{"field": "language", "name": "language", "type": "terms"}]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"field": "language", "count": 12}]},
        }

        result = self.module.aggregate_hunting_guides(body=body)

        self.mock_client.command.assert_called_once_with(
            "AggregateHuntingGuides",
            body=body,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["field"], "language")

    def test_aggregate_intelligence_queries_success(self):
        """Test intelligence query aggregation call."""
        body = [{"field": "language", "name": "language", "type": "terms"}]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"field": "language", "count": 7}]},
        }

        result = self.module.aggregate_intelligence_queries(body=body)

        self.mock_client.command.assert_called_once_with(
            "AggregateIntelligenceQueries",
            body=body,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["count"], 7)

    def test_create_hunting_archive_export_requires_language(self):
        """Test archive export requires language."""
        result = self.module.create_hunting_archive_export(
            language=None,
            filter=None,
            archive_type="zip",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_hunting_archive_export_success(self):
        """Test archive export request parameters."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"archive_id": "archive-1"}]},
        }

        result = self.module.create_hunting_archive_export(
            language="cql",
            filter="tags:'ransomware'",
            archive_type="zip",
        )

        self.mock_client.command.assert_called_once_with(
            "GetArchiveExport",
            parameters={
                "language": "cql",
                "filter": "tags:'ransomware'",
                "archive_type": "zip",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["archive_id"], "archive-1")

    def test_search_hunting_guides_has_read_only_annotations(self):
        """Test that search_hunting_guides is registered with read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_hunting_guides", READ_ONLY_ANNOTATIONS)


if __name__ == "__main__":
    unittest.main()

