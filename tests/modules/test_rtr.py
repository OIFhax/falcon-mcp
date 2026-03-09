"""
Tests for the Real Time Response (RTR) module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.rtr import RTRModule
from tests.modules.utils.test_modules import TestModules


class TestRTRModule(TestModules):
    """Test cases for the RTR module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(RTRModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_rtr_sessions",
            "falcon_init_rtr_session",
            "falcon_execute_rtr_command",
            "falcon_check_rtr_command_status",
            "falcon_delete_rtr_session",
            "falcon_delete_rtr_queued_session",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_rtr_sessions_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_rtr_sessions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_check_rtr_command_status", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_init_rtr_session",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_rtr_session",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_search_rtr_sessions_success(self):
        """Test searching RTR sessions and fetching full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["session-id-1", "session-id-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"session_id": "session-id-1", "aid": "aid-1"},
                    {"session_id": "session-id-2", "aid": "aid-2"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_rtr_sessions(
            filter="user_id:'@me'",
            limit=10,
            offset=0,
            sort="date_created.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListAllSessions")
        self.assertEqual(first_call[1]["parameters"]["filter"], "user_id:'@me'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "date_created.desc")

        self.assertEqual(second_call[0][0], "RTR_ListSessions")
        self.assertEqual(second_call[1]["body"]["ids"], ["session-id-1", "session-id-2"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["session_id"], "session-id-1")

    def test_search_rtr_sessions_empty_with_filter(self):
        """Test empty RTR session search with filter returns FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_rtr_sessions(
            filter="user_id:'does-not-exist'",
            limit=10,
            offset=None,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_search_rtr_sessions_error_without_filter(self):
        """Test RTR session search errors without filter return list-wrapped error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad request"}]},
        }

        result = self.module.search_rtr_sessions(
            filter=None,
            limit=10,
            offset=None,
            sort=None,
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_init_rtr_session_success(self):
        """Test initializing an RTR session with convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {
                "resources": [{"session_id": "session-id-1", "aid": "aid-1"}]
            },
        }

        result = self.module.init_rtr_session(
            device_id="aid-1",
            origin="mcp-tests",
            queue_offline=True,
            timeout=60,
            timeout_duration="60s",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_InitSession",
            parameters={"timeout": 60, "timeout_duration": "60s"},
            body={"device_id": "aid-1", "origin": "mcp-tests", "queue_offline": True},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["session_id"], "session-id-1")

    def test_init_rtr_session_validation(self):
        """Test init_rtr_session validation when device_id is missing."""
        result = self.module.init_rtr_session(
            device_id=None,
            origin=None,
            queue_offline=None,
            timeout=None,
            timeout_duration=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_execute_rtr_command_success(self):
        """Test executing an RTR read-only command."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {
                "resources": [{"cloud_request_id": "cloud-request-1", "session_id": "session-id-1"}]
            },
        }

        result = self.module.execute_rtr_command(
            base_command="ls",
            command_string="ls C:\\\\Windows",
            session_id="session-id-1",
            device_id=None,
            sequence_id=0,
            persist=False,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_ExecuteCommand",
            body={
                "base_command": "ls",
                "command_string": "ls C:\\\\Windows",
                "session_id": "session-id-1",
                "id": 0,
                "persist": False,
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cloud_request_id"], "cloud-request-1")

    def test_execute_rtr_command_validation_missing_fields(self):
        """Test execute_rtr_command validation for missing command fields."""
        result = self.module.execute_rtr_command(
            base_command=None,
            command_string=None,
            session_id="session-id-1",
            device_id=None,
            sequence_id=None,
            persist=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_execute_rtr_command_validation_missing_target(self):
        """Test execute_rtr_command validation for missing session/device target."""
        result = self.module.execute_rtr_command(
            base_command="ls",
            command_string="ls /",
            session_id=None,
            device_id=None,
            sequence_id=None,
            persist=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_check_rtr_command_status_success(self):
        """Test checking RTR command status."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "cloud-request-1", "complete": True}]},
        }

        result = self.module.check_rtr_command_status(
            cloud_request_id="cloud-request-1",
            sequence_id=0,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_CheckCommandStatus",
            parameters={"cloud_request_id": "cloud-request-1", "sequence_id": 0},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cloud_request_id"], "cloud-request-1")

    def test_check_rtr_command_status_validation(self):
        """Test check_rtr_command_status validation."""
        result = self.module.check_rtr_command_status(
            cloud_request_id=None,
            sequence_id=0,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_rtr_session_success(self):
        """Test deleting an RTR session."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "session-id-1"}]},
        }

        result = self.module.delete_rtr_session(session_id="session-id-1")

        self.mock_client.command.assert_called_once_with(
            "RTR_DeleteSession",
            parameters={"session_id": "session-id-1"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["session_id"], "session-id-1")

    def test_delete_rtr_session_validation(self):
        """Test delete_rtr_session validation."""
        result = self.module.delete_rtr_session(session_id=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_rtr_queued_session_success(self):
        """Test deleting a queued RTR session."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "session-id-1", "cloud_request_id": "request-1"}]},
        }

        result = self.module.delete_rtr_queued_session(
            session_id="session-id-1",
            cloud_request_id="request-1",
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_DeleteQueuedSession",
            parameters={"session_id": "session-id-1", "cloud_request_id": "request-1"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cloud_request_id"], "request-1")

    def test_delete_rtr_queued_session_validation(self):
        """Test delete_rtr_queued_session validation."""
        result = self.module.delete_rtr_queued_session(
            session_id="session-id-1",
            cloud_request_id=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_execute_rtr_command_permission_error(self):
        """Test execute_rtr_command with 403 permission error returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.execute_rtr_command(
            base_command="ls",
            command_string="ls /",
            session_id="session-id-1",
            device_id=None,
            sequence_id=None,
            persist=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
