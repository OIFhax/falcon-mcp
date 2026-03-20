"""Tests for the Real Time Response (RTR) module."""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.rtr import RTRModule
from tests.modules.utils.test_modules import TestModules


class TestRTRModule(TestModules):
    """Test cases for the RTR module."""

    def setUp(self):
        self.setup_module(RTRModule)

    def test_register_tools(self):
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
            "falcon_aggregate_rtr_sessions",
            "falcon_search_rtr_queued_sessions",
            "falcon_pulse_rtr_session",
            "falcon_execute_rtr_active_responder_command",
            "falcon_check_rtr_active_responder_command_status",
            "falcon_batch_init_rtr_sessions",
            "falcon_batch_refresh_rtr_sessions",
            "falcon_execute_rtr_batch_command",
            "falcon_execute_rtr_batch_active_responder_command",
            "falcon_execute_rtr_batch_get_command",
            "falcon_check_rtr_batch_get_command_status",
            "falcon_get_rtr_extracted_file_contents",
            "falcon_list_rtr_files_v1",
            "falcon_list_rtr_files_v2",
            "falcon_delete_rtr_file_v1",
            "falcon_delete_rtr_file_v2",
            "falcon_search_rtr_falcon_scripts",
            "falcon_get_rtr_falcon_script_details",
            "falcon_get_rtr_put_file_contents",
            "falcon_get_rtr_admin_put_file_details_v2",
            "falcon_create_rtr_admin_put_file_v1",
            "falcon_create_rtr_admin_put_file_v2",
            "falcon_delete_rtr_admin_put_file",
            "falcon_get_rtr_admin_script_details_v2",
            "falcon_create_rtr_admin_script_v1",
            "falcon_create_rtr_admin_script_v2",
            "falcon_update_rtr_admin_script_v1",
            "falcon_update_rtr_admin_script_v2",
            "falcon_delete_rtr_admin_script",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_search_rtr_sessions_fql_guide",
            "falcon_search_rtr_admin_fql_guide",
            "falcon_search_rtr_audit_sessions_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_rtr_sessions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_execute_rtr_batch_command",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_delete_rtr_file_v2",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_aggregate_rtr_sessions_validation_and_success(self):
        validation = self.module.aggregate_rtr_sessions(body=None)
        self.assertIn("error", validation[0])
        self.mock_client.command.assert_not_called()

        body = [{"field": "user_id", "type": "terms", "size": 10}]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"user_id": "me", "count": 2}]},
        }
        result = self.module.aggregate_rtr_sessions(body=body)

        self.mock_client.command.assert_called_once_with("RTR_AggregateSessions", body=body)
        self.assertEqual(result, [{"user_id": "me", "count": 2}])

    def test_batch_init_sessions_success(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"batch_id": "batch-1"}]},
        }

        result = self.module.batch_init_rtr_sessions(
            host_ids=["aid-1", "aid-2"],
            existing_batch_id=None,
            queue_offline=True,
            timeout=120,
            timeout_duration="120s",
            host_timeout_duration="90s",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "BatchInitSessions",
            parameters={"timeout": 120, "timeout_duration": "120s", "host_timeout_duration": "90s"},
            body={"host_ids": ["aid-1", "aid-2"], "queue_offline": True},
        )
        self.assertEqual(result[0]["batch_id"], "batch-1")

    def test_init_rtr_session_adds_low_confidence_fallback_on_backend_5xx(self):
        self.mock_client.command.side_effect = [
            {
                "status_code": 503,
                "body": {"errors": [{"message": "Service unavailable"}]},
            },
            {
                "status_code": 200,
                "body": {"resources": ["session-1"]},
            },
            {
                "status_code": 200,
                "body": {"resources": [{"session_id": "session-1", "aid": "aid-1"}]},
            },
        ]

        result = self.module.init_rtr_session(
            device_id="aid-1",
            origin=None,
            queue_offline=False,
            timeout=120,
            timeout_duration="120s",
            body=None,
        )

        self.assertEqual(result[0]["error_type"], "falcon_backend_5xx")
        self.assertEqual(result[0]["confidence"], "low")
        self.assertEqual(result[0]["fallback"]["strategy"], "search_existing_rtr_sessions")
        self.assertEqual(result[0]["fallback"]["entries"][0]["device_id"], "aid-1")
        self.assertEqual(
            result[0]["fallback"]["entries"][0]["results"][0]["session_id"],
            "session-1",
        )
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "RTR_InitSession")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "RTR_ListAllSessions")
        self.assertEqual(self.mock_client.command.call_args_list[2][0][0], "RTR_ListSessions")

    def test_execute_rtr_batch_command_success(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"cloud_request_id": "req-1"}]},
        }

        result = self.module.execute_rtr_batch_command(
            base_command="ls",
            batch_id="batch-1",
            command_string="ls C:\\\\Windows",
            optional_hosts=["aid-1"],
            timeout=90,
            timeout_duration="90s",
            host_timeout_duration="60s",
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "BatchCmd",
            parameters={"timeout": 90, "timeout_duration": "90s", "host_timeout_duration": "60s"},
            body={
                "base_command": "ls",
                "batch_id": "batch-1",
                "command_string": "ls C:\\\\Windows",
                "optional_hosts": ["aid-1"],
            },
        )
        self.assertEqual(result[0]["cloud_request_id"], "req-1")

    def test_check_rtr_batch_get_command_status_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"batch_get_cmd_req_id": "job-1", "complete": True}]},
        }

        result = self.module.check_rtr_batch_get_command_status(
            batch_get_cmd_req_id="job-1",
            timeout=60,
            timeout_duration="60s",
        )

        self.mock_client.command.assert_called_once_with(
            "BatchGetCmdStatus",
            parameters={
                "batch_get_cmd_req_id": "job-1",
                "timeout": 60,
                "timeout_duration": "60s",
            },
        )
        self.assertEqual(result[0]["batch_get_cmd_req_id"], "job-1")

    def test_search_queued_and_pulse_session_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "session-1"}]},
        }
        queued_result = self.module.search_rtr_queued_sessions(session_ids=["session-1"])
        self.mock_client.command.assert_called_once_with(
            "RTR_ListQueuedSessions",
            body={"ids": ["session-1"]},
        )
        self.assertEqual(queued_result[0]["session_id"], "session-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"session_id": "session-1", "pulsed": True}]},
        }
        pulse_result = self.module.pulse_rtr_session(device_id="aid-1", body=None)
        self.mock_client.command.assert_called_once_with(
            "RTR_PulseSession",
            body={"device_id": "aid-1"},
        )
        self.assertEqual(pulse_result[0]["pulsed"], True)

    def test_active_responder_command_and_status_success(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"cloud_request_id": "req-1"}]},
        }
        command_result = self.module.execute_rtr_active_responder_command(
            base_command="runscript",
            command_string="runscript -Raw=whoami",
            session_id="session-1",
            device_id=None,
            sequence_id=1,
            persist=False,
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_ExecuteActiveResponderCommand",
            body={
                "base_command": "runscript",
                "command_string": "runscript -Raw=whoami",
                "session_id": "session-1",
                "id": 1,
                "persist": False,
            },
        )
        self.assertEqual(command_result[0]["cloud_request_id"], "req-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cloud_request_id": "req-1", "complete": True}]},
        }
        status_result = self.module.check_rtr_active_responder_command_status(
            cloud_request_id="req-1",
            sequence_id=1,
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_CheckActiveResponderCommandStatus",
            parameters={"cloud_request_id": "req-1", "sequence_id": 1},
        )
        self.assertEqual(status_result[0]["complete"], True)

    def test_batch_refresh_active_responder_and_get_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"batch_id": "batch-1"}]},
        }
        refresh_result = self.module.batch_refresh_rtr_sessions(
            batch_id="batch-1",
            hosts_to_remove=["aid-2"],
            timeout=120,
            timeout_duration="120s",
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "BatchRefreshSessions",
            parameters={"timeout": 120, "timeout_duration": "120s"},
            body={"batch_id": "batch-1", "hosts_to_remove": ["aid-2"]},
        )
        self.assertEqual(refresh_result[0]["batch_id"], "batch-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"cloud_request_id": "req-2"}]},
        }
        active_responder_result = self.module.execute_rtr_batch_active_responder_command(
            base_command="runscript",
            batch_id="batch-1",
            command_string="runscript -Raw=hostname",
            optional_hosts=["aid-1"],
            timeout=60,
            timeout_duration="60s",
            host_timeout_duration="45s",
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "BatchActiveResponderCmd",
            parameters={"timeout": 60, "timeout_duration": "60s", "host_timeout_duration": "45s"},
            body={
                "base_command": "runscript",
                "batch_id": "batch-1",
                "command_string": "runscript -Raw=hostname",
                "optional_hosts": ["aid-1"],
            },
        )
        self.assertEqual(active_responder_result[0]["cloud_request_id"], "req-2")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"batch_get_cmd_req_id": "get-1"}]},
        }
        get_result = self.module.execute_rtr_batch_get_command(
            batch_id="batch-1",
            file_path="C:\\\\Windows\\\\Temp\\\\test.txt",
            optional_hosts=["aid-1"],
            timeout=120,
            timeout_duration="120s",
            host_timeout_duration="90s",
            body=None,
        )
        self.mock_client.command.assert_called_once_with(
            "BatchGetCmd",
            parameters={"timeout": 120, "timeout_duration": "120s", "host_timeout_duration": "90s"},
            body={
                "batch_id": "batch-1",
                "file_path": "C:\\\\Windows\\\\Temp\\\\test.txt",
                "optional_hosts": ["aid-1"],
            },
        )
        self.assertEqual(get_result[0]["batch_get_cmd_req_id"], "get-1")

    def test_get_extracted_and_file_v1_operations_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "abc"}]},
        }
        extracted = self.module.get_rtr_extracted_file_contents(
            session_id="session-1",
            sha256="abc",
            filename="artifact.zip",
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_GetExtractedFileContents",
            parameters={"session_id": "session-1", "sha256": "abc", "filename": "artifact.zip"},
        )
        self.assertEqual(extracted[0]["sha256"], "abc")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "file-v1"}]},
        }
        list_result = self.module.list_rtr_files_v1(session_id="session-1")
        self.mock_client.command.assert_called_once_with(
            "RTR_ListFiles",
            parameters={"session_id": "session-1"},
        )
        self.assertEqual(list_result[0]["id"], "file-v1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"deleted": True}]},
        }
        delete_result = self.module.delete_rtr_file_v1(
            session_id="session-1",
            file_id="file-v1",
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_DeleteFile",
            parameters={"session_id": "session-1", "ids": "file-v1"},
        )
        self.assertEqual(delete_result[0]["deleted"], True)

    def test_list_and_delete_rtr_files_v2_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "file-1"}]},
        }
        list_result = self.module.list_rtr_files_v2(session_id="session-1")
        self.mock_client.command.assert_called_once_with(
            "RTR_ListFilesV2",
            parameters={"session_id": "session-1"},
        )
        self.assertEqual(list_result[0]["id"], "file-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"deleted": True}]},
        }
        delete_result = self.module.delete_rtr_file_v2(
            session_id="session-1",
            file_id="file-1",
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_DeleteFileV2",
            parameters={"session_id": "session-1", "ids": "file-1"},
        )
        self.assertEqual(delete_result[0]["deleted"], True)

    def test_search_rtr_falcon_scripts_success(self):
        query_response = {"status_code": 200, "body": {"resources": ["falcon-script-1"]}}
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "falcon-script-1", "name": "cleanup"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_rtr_falcon_scripts(
            filter="name:'cleanup*'",
            limit=5,
            offset=0,
            sort="name|asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "RTR_ListFalconScripts")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "RTR_GetFalconScripts")
        self.assertEqual(result[0]["id"], "falcon-script-1")

    def test_get_falcon_script_details_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "falcon-script-2"}]},
        }
        result = self.module.get_rtr_falcon_script_details(ids=["falcon-script-2"])
        self.mock_client.command.assert_called_once_with(
            "RTR_GetFalconScripts",
            parameters={"ids": ["falcon-script-2"]},
        )
        self.assertEqual(result[0]["id"], "falcon-script-2")

    def test_get_put_file_contents_and_v2_details_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "put-1"}]},
        }
        put_contents = self.module.get_rtr_put_file_contents(put_file_id="put-1")
        self.mock_client.command.assert_called_once_with(
            "RTR_GetPutFileContents",
            parameters={"id": "put-1"},
        )
        self.assertEqual(put_contents[0]["id"], "put-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "put-2"}]},
        }
        details_v2 = self.module.get_rtr_admin_put_file_details_v2(ids=["put-2"])
        self.mock_client.command.assert_called_once_with(
            "RTR_GetPut_FilesV2",
            parameters={"ids": ["put-2"]},
        )
        self.assertEqual(details_v2[0]["id"], "put-2")

    def test_create_and_delete_rtr_put_file_operations(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "put-3"}]},
        }
        create_v1 = self.module.create_rtr_admin_put_file_v1(
            form_data={"name": "put-v1", "description": "desc"},
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_CreatePut_Files",
            body={"name": "put-v1", "description": "desc"},
        )
        self.assertEqual(create_v1[0]["id"], "put-3")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "put-4"}]},
        }
        create_v2 = self.module.create_rtr_admin_put_file_v2(
            form_data={"name": "put-v2", "description": "desc"},
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_CreatePut_FilesV2",
            body={"name": "put-v2", "description": "desc"},
        )
        self.assertEqual(create_v2[0]["id"], "put-4")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"deleted": True}]},
        }
        delete_result = self.module.delete_rtr_admin_put_file(put_file_id="put-4")
        self.mock_client.command.assert_called_once_with(
            "RTR_DeletePut_Files",
            parameters={"ids": "put-4"},
        )
        self.assertEqual(delete_result[0]["deleted"], True)

    def test_create_update_delete_rtr_script_operations(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "script-1"}]},
        }
        create_result = self.module.create_rtr_admin_script_v2(
            form_data={"name": "test-script", "description": "desc", "permission_type": "private"},
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_CreateScriptsV2",
            body={"name": "test-script", "description": "desc", "permission_type": "private"},
        )
        self.assertEqual(create_result[0]["id"], "script-1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "script-1", "updated": True}]},
        }
        update_result = self.module.update_rtr_admin_script_v2(
            form_data={"id": "script-1", "description": "new desc"},
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_UpdateScriptsV2",
            body={"id": "script-1", "description": "new desc"},
        )
        self.assertEqual(update_result[0]["updated"], True)

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"deleted": True}]},
        }
        delete_result = self.module.delete_rtr_admin_script(script_id="script-1")
        self.mock_client.command.assert_called_once_with(
            "RTR_DeleteScripts",
            parameters={"ids": "script-1"},
        )
        self.assertEqual(delete_result[0]["deleted"], True)

    def test_get_and_update_rtr_script_v1_operations(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "script-v1"}]},
        }
        details = self.module.get_rtr_admin_script_details_v2(ids=["script-v1"])
        self.mock_client.command.assert_called_once_with(
            "RTR_GetScriptsV2",
            parameters={"ids": ["script-v1"]},
        )
        self.assertEqual(details[0]["id"], "script-v1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "script-v1"}]},
        }
        create_v1 = self.module.create_rtr_admin_script_v1(
            form_data={"name": "script-v1", "description": "desc"},
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_CreateScripts",
            body={"name": "script-v1", "description": "desc"},
        )
        self.assertEqual(create_v1[0]["id"], "script-v1")

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "script-v1", "updated": True}]},
        }
        update_v1 = self.module.update_rtr_admin_script_v1(
            form_data={"id": "script-v1", "description": "updated"},
        )
        self.mock_client.command.assert_called_once_with(
            "RTR_UpdateScripts",
            body={"id": "script-v1", "description": "updated"},
        )
        self.assertEqual(update_v1[0]["updated"], True)


if __name__ == "__main__":
    unittest.main()
