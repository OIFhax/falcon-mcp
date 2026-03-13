"""
Tests for the Quarantine module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.quarantine import QuarantineModule, WRITE_ANNOTATIONS
from tests.modules.utils.test_modules import TestModules


class TestQuarantineModule(TestModules):
    """Test cases for the Quarantine module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(QuarantineModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_quarantine_files",
            "falcon_get_quarantine_file_details",
            "falcon_aggregate_quarantine_files",
            "falcon_get_quarantine_action_update_count",
            "falcon_update_quarantine_files_by_ids",
            "falcon_update_quarantine_files_by_query",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_quarantine_files_fql_guide",
            "falcon_quarantine_aggregation_guide",
            "falcon_quarantine_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_quarantine_files_success(self):
        """Test quarantine search and detail retrieval."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["qf-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "qf-1", "state": "quarantined"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_quarantine_files(
            filter="state:'quarantined'",
            q=None,
            limit=10,
            offset=0,
            sort="date_updated.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "QueryQuarantineFiles")
        self.assertEqual(
            self.mock_client.command.call_args_list[0][1]["parameters"],
            {
                "filter": "state:'quarantined'",
                "limit": 10,
                "offset": 0,
                "sort": "date_updated.desc",
            },
        )
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "GetQuarantineFiles")
        self.assertEqual(
            self.mock_client.command.call_args_list[1][1]["body"],
            {"ids": ["qf-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "qf-1")

    def test_search_quarantine_files_empty_with_filter_returns_guide(self):
        """Test empty results with filter include FQL helper response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_quarantine_files(
            filter="state:'missing'",
            q=None,
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_quarantine_file_details_validation_error(self):
        """Test file detail retrieval requires IDs."""
        result = self.module.get_quarantine_file_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_quarantine_file_details_success(self):
        """Test file detail retrieval by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "qf-1"}]},
        }

        result = self.module.get_quarantine_file_details(ids=["qf-1"])

        self.mock_client.command.assert_called_once_with(
            "GetQuarantineFiles",
            body={"ids": ["qf-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "qf-1")

    def test_aggregate_quarantine_files_validation_error(self):
        """Test aggregation requires body."""
        result = self.module.aggregate_quarantine_files(body=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_aggregate_quarantine_files_success(self):
        """Test aggregation call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "state", "buckets": []}]},
        }

        body = [{"field": "state", "name": "state", "type": "terms"}]
        result = self.module.aggregate_quarantine_files(body=body)

        self.mock_client.command.assert_called_once_with("GetAggregateFiles", body=body)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "state")

    def test_get_quarantine_action_update_count_validation_error(self):
        """Test action update count requires filter."""
        result = self.module.get_quarantine_action_update_count(filter=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_quarantine_action_update_count_success(self):
        """Test action update count call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "affected_files_by_action"}]},
        }

        result = self.module.get_quarantine_action_update_count(
            filter="state:'quarantined'",
        )

        self.mock_client.command.assert_called_once_with(
            "ActionUpdateCount",
            parameters={"filter": "state:'quarantined'"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "affected_files_by_action")

    def test_update_quarantine_files_by_ids_confirm_required(self):
        """Test update-by-IDs requires confirm_execution=true."""
        result = self.module.update_quarantine_files_by_ids(
            confirm_execution=False,
            action="release",
            ids=["qf-1"],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_quarantine_files_by_ids_success(self):
        """Test update-by-IDs write call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.update_quarantine_files_by_ids(
            confirm_execution=True,
            action="release",
            ids=["qf-1"],
            comment="unit-test",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateQuarantinedDetectsByIds",
            body={"action": "release", "ids": ["qf-1"], "comment": "unit-test"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["updated"], 1)

    def test_update_quarantine_files_by_query_confirm_required(self):
        """Test update-by-query requires confirm_execution=true."""
        result = self.module.update_quarantine_files_by_query(
            confirm_execution=False,
            action="release",
            filter="device.hostname:'host01'",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_quarantine_files_by_query_success(self):
        """Test update-by-query write call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"matched": 0}]},
        }

        result = self.module.update_quarantine_files_by_query(
            confirm_execution=True,
            action="release",
            filter="device.hostname:'not-real-host'",
            q=None,
            comment="unit-test",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateQfByQuery",
            body={
                "action": "release",
                "filter": "device.hostname:'not-real-host'",
                "comment": "unit-test",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["matched"], 0)

    def test_search_quarantine_files_has_read_only_annotations(self):
        """Test that search_quarantine_files is read-only annotated."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_quarantine_files", READ_ONLY_ANNOTATIONS)

    def test_update_quarantine_files_by_ids_has_write_annotations(self):
        """Test that update_quarantine_files_by_ids has write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_quarantine_files_by_ids",
            WRITE_ANNOTATIONS,
        )


if __name__ == "__main__":
    unittest.main()
