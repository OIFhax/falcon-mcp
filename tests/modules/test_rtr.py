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
            "falcon_search_rtr_admin_scripts",
            "falcon_search_rtr_admin_put_files",
            "falcon_execute_rtr_admin_command",
            "falcon_execute_rtr_admin_batch_command",
            "falcon_check_rtr_admin_command_status",
            "falcon_delete_rtr_session",
            "falcon_delete_rtr_queued_session",
            "falcon_search_rtr_audit_sessions",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_rtr_sessions_fql_guide",
            "falcon_search_rtr_admin_fql_guide",
            "falcon_search_rtr_audit_sessions_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_rtr_sessions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_rtr_admin_scripts", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_rtr_audit_sessions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_execute_rtr_command",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_execute_rtr_admin_command",
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

    def test_search_rtr_admin_scripts_success(self):
        """Test searching RTR admin scripts and fetching full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["script-id-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "script-id-1", "name": "triage-script"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_rtr_admin_scripts(
            filter="name:'triage*'",
            limit=10,
            offset=0,
            sort="created_at.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "RTR_ListScripts")
        self.assertEqual(first_call[1]["parameters"]["filter"], "name:'triage*'")
        self.assertEqual(second_call[0][0], "RTR_GetScripts")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["script-id-1"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "script-id-1")

    def test_search_rtr_admin_put_files_success(self):
        """Test searching RTR admin put-files and fetching full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["put-file-id-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "put-file-id-1", "name": "payload.bin"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_rtr_admin_put_files(
            filter="name:'payload*'",
            limit=10,
            offset=0,
            sort="created_at.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "RTR_ListPut_Files")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "RTR_GetPut_Files")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "put-file-id-1")

    def test_execute_rtr_admin_command_success(self):
        """Test executing an RTR admin command."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"cloud_request_id": "admin-request-1"}]},
        }

        result = self.module.execute_rtr_admin_command(
            base_command="runscript",
            command_string="runscript -CloudFile='triage-script'",
            session_id="session-id-1",
            device_id=None,
            sequence_id=1,
            persist=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_ExecuteAdminCommand",
            body={
                "base_command": "runscript",
                "command_string": "runscript -CloudFile='triage-script'",
                "session_id": "session-id-1",
                "id": 1,
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cloud_request_id"], "admin-request-1")

    def test_execute_rtr_admin_batch_command_success(self):
        """Test executing an RTR admin batch command."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"cloud_request_id": "batch-request-1"}]},
        }

        result = self.module.execute_rtr_admin_batch_command(
            base_command="runscript",
            batch_id="batch-1",
            command_string="runscript -CloudFile='triage-script'",
            optional_hosts=["aid-1", "aid-2"],
            persist_all=True,
            timeout=120,
            timeout_duration="120s",
            host_timeout_duration="90s",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "BatchAdminCmd",
            parameters={
                "timeout": 120,
                "timeout_duration": "120s",
                "host_timeout_duration": "90s",
            },
            body={
                "base_command": "runscript",
                "batch_id": "batch-1",
                "command_string": "runscript -CloudFile='triage-script'",
                "optional_hosts": ["aid-1", "aid-2"],
                "persist_all": True,
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cloud_request_id"], "batch-request-1")

    def test_check_rtr_admin_command_status_success(self):
        """Test checking RTR admin command status."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "admin-request-1", "complete": True}]},
        }

        result = self.module.check_rtr_admin_command_status(
            cloud_request_id="admin-request-1",
            sequence_id=0,
        )

        self.mock_client.command.assert_called_once_with(
            "RTR_CheckAdminCommandStatus",
            parameters={"cloud_request_id": "admin-request-1", "sequence_id": 0},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cloud_request_id"], "admin-request-1")

    def test_search_rtr_audit_sessions_success(self):
        """Test searching RTR audit sessions."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "audit-session-1"}]},
        }

        result = self.module.search_rtr_audit_sessions(
            filter="user_id:'@me'",
            limit=5,
            offset=0,
            sort="created_at.desc",
            with_command_info=True,
        )

        self.mock_client.command.assert_called_once_with(
            "RTRAuditSessions",
            parameters={
                "filter": "user_id:'@me'",
                "limit": 5,
                "offset": 0,
                "sort": "created_at.desc",
                "with_command_info": True,
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["session_id"], "audit-session-1")

    def test_search_rtr_audit_sessions_empty_with_filter(self):
        """Test empty RTR audit search with filter returns FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_rtr_audit_sessions(
            filter="session_id:'does-not-exist'",
            limit=10,
            offset=None,
            sort=None,
            with_command_info=False,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_delete_rtr_session_validation(self):
        """Test delete_rtr_session validation."""
        result = self.module.delete_rtr_session(session_id=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_execute_rtr_admin_batch_command_validation(self):
        """Test execute_rtr_admin_batch_command validation for missing required fields."""
        result = self.module.execute_rtr_admin_batch_command(
            base_command=None,
            batch_id=None,
            command_string=None,
            optional_hosts=None,
            persist_all=None,
            timeout=None,
            timeout_duration=None,
            host_timeout_duration=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_execute_rtr_admin_command_permission_error(self):
        """Test execute_rtr_admin_command with 403 error returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.execute_rtr_admin_command(
            base_command="runscript",
            command_string="runscript -CloudFile='triage-script'",
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
