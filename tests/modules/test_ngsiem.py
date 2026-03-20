"""
Tests for the NGSIEM module.
"""

import unittest
from unittest.mock import AsyncMock, patch

import asyncio

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.ngsiem import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    NGSIEMModule,
    WRITE_ANNOTATIONS,
)
from tests.modules.utils.test_modules import TestModules


class TestNGSIEMModule(TestModules):
    """Test cases for the NGSIEM module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(NGSIEMModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_ngsiem",
            "falcon_start_ngsiem_search",
            "falcon_get_ngsiem_search_status",
            "falcon_stop_ngsiem_search",
            "falcon_get_ngsiem_dashboard_template",
            "falcon_create_ngsiem_dashboard_from_template",
            "falcon_update_ngsiem_dashboard_from_template",
            "falcon_delete_ngsiem_dashboard",
            "falcon_list_ngsiem_dashboards",
            "falcon_upload_ngsiem_lookup",
            "falcon_get_ngsiem_lookup",
            "falcon_get_ngsiem_lookup_from_package",
            "falcon_get_ngsiem_lookup_from_namespace_package",
            "falcon_get_ngsiem_lookup_file",
            "falcon_create_ngsiem_lookup_file",
            "falcon_update_ngsiem_lookup_file",
            "falcon_delete_ngsiem_lookup_file",
            "falcon_list_ngsiem_lookup_files",
            "falcon_get_ngsiem_parser_template",
            "falcon_create_ngsiem_parser_from_template",
            "falcon_get_ngsiem_parser",
            "falcon_create_ngsiem_parser",
            "falcon_update_ngsiem_parser",
            "falcon_delete_ngsiem_parser",
            "falcon_list_ngsiem_parsers",
            "falcon_get_ngsiem_saved_query_template",
            "falcon_create_ngsiem_saved_query",
            "falcon_update_ngsiem_saved_query_from_template",
            "falcon_delete_ngsiem_saved_query",
            "falcon_list_ngsiem_saved_queries",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_ngsiem_repository_guide",
            "falcon_ngsiem_search_guide",
            "falcon_ngsiem_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_ngsiem", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_start_ngsiem_search", WRITE_ANNOTATIONS)
        self.assert_tool_annotations("falcon_stop_ngsiem_search", DESTRUCTIVE_WRITE_ANNOTATIONS)

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_success(self, mock_sleep):
        """Test search that completes on first poll returns events list."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-123"},
        }
        poll_response = {
            "status_code": 200,
            "body": {"done": True, "events": [{"aid": "agent-1"}]},
        }
        self.mock_client.command.side_effect = [start_response, poll_response]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="*",
                start="2025-01-01T00:00:00Z",
                repository="search-all",
                end=None,
            )
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][1]["operation"], "StartSearchV1")
        self.assertEqual(
            self.mock_client.command.call_args_list[1][1]["operation"],
            "GetSearchStatusV1",
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["aid"], "agent-1")

    @patch("falcon_mcp.modules.ngsiem.TIMEOUT_SECONDS", 10)
    @patch("falcon_mcp.modules.ngsiem.POLL_INTERVAL_SECONDS", 5)
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_timeout(self, mock_sleep):
        """Test timeout path calls StopSearchV1."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-timeout"},
        }
        poll_not_done = {
            "status_code": 200,
            "body": {"done": False},
        }
        stop_response = {
            "status_code": 200,
            "body": {},
        }
        self.mock_client.command.side_effect = [
            start_response,
            poll_not_done,
            poll_not_done,
            stop_response,
        ]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="*",
                start="2025-01-01T00:00:00Z",
                repository="search-all",
                end=None,
            )
        )

        stop_call = self.mock_client.command.call_args_list[-1]
        self.assertEqual(stop_call[1]["operation"], "StopSearchV1")
        self.assertEqual(stop_call[1]["id"], "job-timeout")
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("timed out", result["error"])

    def test_start_ngsiem_search_confirm_required(self):
        """Test start search requires confirmation."""
        result = self.module.start_ngsiem_search(
            confirm_execution=False,
            query_string="*",
            start="2025-01-01T00:00:00Z",
            repository="search-all",
            end=None,
            body=None,
        )

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_start_ngsiem_search_blocks_improvised_query(self):
        """Test natural-language NGSIEM queries are rejected before API execution."""
        result = self.module.start_ngsiem_search(
            confirm_execution=True,
            query_string="show me failed logins from the last hour",
            start="2025-01-01T00:00:00Z",
            repository="search-all",
            end=None,
            body=None,
        )

        self.assertEqual(result["error_type"], "malformed_query")
        self.assertIn("explicit CQL", result["error"])
        self.mock_client.command.assert_not_called()

    def test_start_ngsiem_search_success(self):
        """Test start search operation response shape."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"id": "job-1"},
        }

        result = self.module.start_ngsiem_search(
            confirm_execution=True,
            query_string="*",
            start="2025-01-01T00:00:00Z",
            repository="search-all",
            end=None,
            body=None,
        )

        self.mock_client.command.assert_called_once()
        first_call = self.mock_client.command.call_args
        self.assertEqual(first_call[1]["operation"], "StartSearchV1")
        self.assertEqual(first_call[1]["repository"], "search-all")
        self.assertEqual(first_call[1]["body"]["queryString"], "*")
        self.assertEqual(result["id"], "job-1")

    def test_search_ngsiem_blocks_improvised_query(self):
        """Test convenience NGSIEM search also rejects improvised queries."""
        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="find suspicious activity for this user",
                start="2025-01-01T00:00:00Z",
                repository="search-all",
                end=None,
            )
        )

        self.assertEqual(result["error_type"], "malformed_query")
        self.mock_client.command.assert_not_called()

    def test_get_ngsiem_search_status_validation_and_success(self):
        """Test status validation and success path."""
        validation_result = self.module.get_ngsiem_search_status(repository="search-all", search_id=None)
        self.assertIn("error", validation_result)
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"done": True, "events": []},
        }
        success_result = self.module.get_ngsiem_search_status(
            repository="search-all",
            search_id="job-1",
        )

        self.mock_client.command.assert_called_once_with(
            operation="GetSearchStatusV1",
            repository="search-all",
            search_id="job-1",
        )
        self.assertTrue(success_result["done"])

    def test_stop_ngsiem_search_confirm_required_and_success(self):
        """Test stop search confirmation and success."""
        validation_result = self.module.stop_ngsiem_search(
            confirm_execution=False,
            repository="search-all",
            search_id="job-1",
        )
        self.assertIn("error", validation_result)
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"stopped": True},
        }
        success_result = self.module.stop_ngsiem_search(
            confirm_execution=True,
            repository="search-all",
            search_id="job-1",
        )

        self.mock_client.command.assert_called_once_with(
            operation="StopSearchV1",
            repository="search-all",
            id="job-1",
        )
        self.assertTrue(success_result["stopped"])

    def test_create_dashboard_from_template_confirm_required(self):
        """Test dashboard create operation requires confirmation."""
        result = self.module.create_ngsiem_dashboard_from_template(
            confirm_execution=False,
            body={"resources": [{}]},
        )

        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_list_ngsiem_dashboards_success(self):
        """Test dashboard list operation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "db-1"}]},
        }

        result = self.module.list_ngsiem_dashboards()

        self.mock_client.command.assert_called_once_with(operation="ListDashboards")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "db-1")

    def test_delete_saved_query_validation(self):
        """Test delete saved query requires id."""
        result = self.module.delete_ngsiem_saved_query(
            confirm_execution=True,
            id=None,
        )
        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
