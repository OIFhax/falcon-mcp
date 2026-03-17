"""
Tests for the Scheduled Reports module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.scheduled_reports import (
    ScheduledReportsModule,
    WRITE_ANNOTATIONS,
)
from tests.modules.utils.test_modules import TestModules


class TestScheduledReportsModule(TestModules):
    """Test cases for the Scheduled Reports module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ScheduledReportsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_scheduled_reports",
            "falcon_query_scheduled_report_ids",
            "falcon_get_scheduled_report_details",
            "falcon_launch_scheduled_report",
            "falcon_search_report_executions",
            "falcon_query_report_execution_ids",
            "falcon_get_report_execution_details",
            "falcon_retry_report_execution",
            "falcon_download_report_execution",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_scheduled_reports_fql_guide",
            "falcon_search_report_executions_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_scheduled_reports", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_launch_scheduled_report", WRITE_ANNOTATIONS)
        self.assert_tool_annotations("falcon_retry_report_execution", WRITE_ANNOTATIONS)

    def test_search_scheduled_reports_success(self):
        """Test scheduled report search and detail retrieval."""
        query_response = {"status_code": 200, "body": {"resources": ["report-id-1"]}}
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "report-id-1", "name": "Weekly Report"}]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_scheduled_reports(
            filter="status:'ACTIVE'",
            limit=10,
            offset=0,
            sort="created_on.desc",
            q=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "scheduled_reports_query",
            parameters={
                "filter": "status:'ACTIVE'",
                "limit": 10,
                "offset": 0,
                "sort": "created_on.desc",
            },
        )
        self.mock_client.command.assert_any_call(
            "scheduled_reports_get",
            parameters={"ids": ["report-id-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "report-id-1")

    def test_query_scheduled_report_ids_empty_filter_returns_guide(self):
        """Test query IDs helper response when filtered results are empty."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_scheduled_report_ids(
            filter="name:'none'",
            limit=100,
            offset=0,
            sort=None,
            q=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_scheduled_report_details_validation_and_success(self):
        """Test scheduled report details validation and success."""
        validation_result = self.module.get_scheduled_report_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "report-id-1"}]},
        }
        success_result = self.module.get_scheduled_report_details(ids=["report-id-1"])

        self.mock_client.command.assert_called_once_with(
            "scheduled_reports_get",
            parameters={"ids": ["report-id-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "report-id-1")

    def test_launch_scheduled_report_confirm_required(self):
        """Test launch operation requires explicit confirmation."""
        result = self.module.launch_scheduled_report(
            confirm_execution=False,
            id="report-id-1",
            body=None,
        )
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_launch_scheduled_report_success(self):
        """Test launch operation success path."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "execution-id-1"}]},
        }

        result = self.module.launch_scheduled_report(
            confirm_execution=True,
            id="report-id-1",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "scheduled_reports_launch",
            body=[{"id": "report-id-1"}],
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "execution-id-1")

    def test_search_report_executions_success(self):
        """Test execution search and detail retrieval."""
        query_response = {"status_code": 200, "body": {"resources": ["exec-id-1"]}}
        get_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-id-1", "status": "DONE"}]},
        }
        self.mock_client.command.side_effect = [query_response, get_response]

        result = self.module.search_report_executions(
            filter="status:'DONE'",
            limit=10,
            offset=0,
            sort="created_on.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "report_executions_query",
            parameters={
                "filter": "status:'DONE'",
                "limit": 10,
                "offset": 0,
                "sort": "created_on.desc",
            },
        )
        self.mock_client.command.assert_any_call(
            "report_executions_get",
            parameters={"ids": ["exec-id-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "exec-id-1")

    def test_retry_report_execution_confirm_required_and_success(self):
        """Test retry operation confirmation and success path."""
        validation_result = self.module.retry_report_execution(
            confirm_execution=False,
            id="exec-id-1",
            body=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "exec-id-1", "status": "PENDING"}]},
        }
        success_result = self.module.retry_report_execution(
            confirm_execution=True,
            id="exec-id-1",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "report_executions_retry",
            body=[{"id": "exec-id-1"}],
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "exec-id-1")

    def test_download_report_execution_csv_format(self):
        """Test download of CSV format execution."""
        self.mock_client.command.return_value = b"@timestamp,text\n1,test\n"

        result = self.module.download_report_execution(id="exec-id-1")

        self.mock_client.command.assert_called_once_with(
            "report_executions_download_get",
            parameters={"ids": "exec-id-1"},
        )
        self.assertIsInstance(result, str)
        self.assertIn("test", result)

    def test_download_report_execution_pdf_format_returns_error(self):
        """Test download of PDF format returns unsupported error."""
        self.mock_client.command.return_value = b"%PDF-1.4\n..."

        result = self.module.download_report_execution(id="exec-id-1")

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("PDF format not supported", result["error"])


if __name__ == "__main__":
    unittest.main()
