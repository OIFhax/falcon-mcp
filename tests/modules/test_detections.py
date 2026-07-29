"""Tests for the Detections module."""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.detections import DetectionsModule, WRITE_ANNOTATIONS
from tests.modules.utils.test_modules import TestModules


class TestDetectionsModule(TestModules):
    """Test cases for the Detections module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DetectionsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_detections",
            "falcon_search_detections_combined",
            "falcon_query_detection_ids_v1",
            "falcon_query_detection_ids_v2",
            "falcon_get_detection_details",
            "falcon_get_detection_details_v1",
            "falcon_get_detection_details_v2",
            "falcon_aggregate_detections_v1",
            "falcon_aggregate_detections_v2",
            "falcon_update_detections_v1",
            "falcon_update_detections_v2",
            "falcon_update_detections_v3",
            "falcon_update_detections",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_detections_fql_guide",
            "falcon_detections_aggregation_guide",
            "falcon_detections_update_actions_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_detections", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_update_detections_v3", WRITE_ANNOTATIONS)

    def test_search_detections_success(self):
        """Test search_detections runs query + details flow with v2 operations."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["composite-1", "composite-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"composite_id": "composite-1"},
                    {"composite_id": "composite-2"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_detections(
            filter="status:'new'",
            limit=10,
            offset=0,
            q=None,
            sort="severity.desc",
            include_hidden=True,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "GetQueriesAlertsV2")
        self.assertEqual(first_call[1]["parameters"]["filter"], "status:'new'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.assertTrue(first_call[1]["parameters"]["include_hidden"])

        self.assertEqual(second_call[0][0], "PostEntitiesAlertsV2")
        self.assertEqual(
            second_call[1]["body"],
            {
                "composite_ids": ["composite-1", "composite-2"],
                "include_hidden": True,
            },
        )

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["composite_id"], "composite-1")

    def test_search_detections_batches_large_detail_requests(self):
        """Detection hydration must stay below the Falcon request-body limit."""
        detection_ids = [f"composite-{index}" for index in range(501)]
        query_response = {
            "status_code": 200,
            "body": {"resources": detection_ids},
        }
        first_details = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"composite_id": detection_id} for detection_id in detection_ids[:500]
                ]
            },
        }
        second_details = {
            "status_code": 200,
            "body": {"resources": [{"composite_id": detection_ids[500]}]},
        }
        self.mock_client.command.side_effect = [query_response, first_details, second_details]

        result = self.module.search_detections(limit=501, include_hidden=True)

        self.assertEqual(self.mock_client.command.call_count, 3)
        first_body = self.mock_client.command.call_args_list[1].kwargs["body"]
        second_body = self.mock_client.command.call_args_list[2].kwargs["body"]
        self.assertEqual(len(first_body["composite_ids"]), 500)
        self.assertEqual(second_body["composite_ids"], ["composite-500"])
        self.assertEqual(
            [item["composite_id"] for item in result["results"]],
            detection_ids,
        )

    def test_query_detection_ids_v2_error_returns_fql_guide(self):
        """Test v2 ID query returns FQL guide wrapping on API error."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.query_detection_ids_v2(filter="bad filter")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])

    def test_query_detection_ids_v1_success(self):
        """Test v1 ID query operation name and parameter mapping."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["det-1", "det-2"]},
        }

        result = self.module.query_detection_ids_v1(
            filter="status:'new'",
            limit=2,
            offset=0,
            q="host",
            sort="created_timestamp|desc",
        )

        self.mock_client.command.assert_called_once_with(
            "GetQueriesAlertsV1",
            parameters={
                "filter": "status:'new'",
                "limit": 2,
                "offset": 0,
                "q": "host",
                "sort": "created_timestamp|desc",
            },
        )
        self.assertEqual(result, ["det-1", "det-2"])

    def test_search_detections_combined_success(self):
        """Test PostCombinedAlertsV1 wiring."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"composite_id": "composite-1"}]},
        }

        result = self.module.search_detections_combined(
            filter="severity_name:'High'",
            limit=50,
            after="next-cursor",
            sort="created_timestamp|desc",
        )

        self.mock_client.command.assert_called_once_with(
            "PostCombinedAlertsV1",
            body={
                "filter": "severity_name:'High'",
                "limit": 50,
                "after": "next-cursor",
                "sort": "created_timestamp|desc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["composite_id"], "composite-1")

    def test_get_detection_details_validation_and_success(self):
        """Test get_detection_details aliases to v2 validation and success path."""
        validation_result = self.module.get_detection_details(ids=None, include_hidden=True)
        self.assertEqual(len(validation_result), 1)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"composite_id": "composite-1"}]},
        }
        success_result = self.module.get_detection_details(
            ids=["composite-1"],
            include_hidden=False,
        )

        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            body={"composite_ids": ["composite-1"], "include_hidden": False},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["composite_id"], "composite-1")

    def test_get_detection_details_v1_success(self):
        """Test PostEntitiesAlertsV1 details retrieval."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "det-legacy-1"}]},
        }

        result = self.module.get_detection_details_v1(ids=["det-legacy-1"])

        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV1",
            body={"ids": ["det-legacy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "det-legacy-1")

    def test_aggregate_detections_v2_validation_and_success(self):
        """Test v2 aggregation validates body and passes include_hidden query param."""
        validation_result = self.module.aggregate_detections_v2(body=None, include_hidden=True)
        self.assertEqual(len(validation_result), 1)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "severity_name", "buckets": []}]},
        }

        payload = [{"type": "terms", "field": "severity_name", "size": 10}]
        result = self.module.aggregate_detections_v2(body=payload, include_hidden=False)

        self.mock_client.command.assert_called_once_with(
            "PostAggregatesAlertsV2",
            parameters={"include_hidden": False},
            body=payload,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "severity_name")

    def test_update_detections_requires_confirmation(self):
        """Test update operations require confirm_execution=true."""
        result = self.module.update_detections_v3(
            confirm_execution=False,
            composite_ids=["composite-1"],
            update_status="in_progress",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_detections_v3_builds_action_parameters(self):
        """Test v3 update body generation from convenience action fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": True}]},
        }

        result = self.module.update_detections_v3(
            confirm_execution=True,
            composite_ids=["composite-1"],
            update_status="in_progress",
            append_comment="Triaging",
            include_hidden=True,
        )

        self.mock_client.command.assert_called_once_with(
            "PatchEntitiesAlertsV3",
            parameters={"include_hidden": True},
            body={
                "composite_ids": ["composite-1"],
                "action_parameters": [
                    {"name": "update_status", "value": "in_progress"},
                    {"name": "append_comment", "value": "Triaging"},
                ],
            },
        )
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["updated"])

    def test_update_detections_v2_accepts_full_body_override(self):
        """Test v2 update supports full body override and bypasses action field building."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": True}]},
        }

        custom_body = {
            "ids": ["det-legacy-1"],
            "action_parameters": [{"name": "add_tag", "value": "manual-review"}],
        }
        result = self.module.update_detections_v2(
            confirm_execution=True,
            ids=None,
            body=custom_body,
        )

        self.mock_client.command.assert_called_once_with(
            "PatchEntitiesAlertsV2",
            body=custom_body,
        )
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["updated"])

    def test_update_detections_requires_action(self):
        """Test update returns validation error when no action is provided."""
        result = self.module.update_detections_v1(
            confirm_execution=True,
            ids=["det-legacy-1"],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_detections_has_write_annotations(self):
        """Verify falcon_update_detections has correct non-read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_detections",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_update_detections_status(self):
        """Test updating detection status."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        result = self.module.update_detections(
            ids=["id1"],
            status="in_progress",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_called_once_with(
            "PatchEntitiesAlertsV3",
            body={
                "composite_ids": ["id1"],
                "action_parameters": [{"name": "update_status", "value": "in_progress"}],
            },
        )
        self.assertEqual(result, [])

    def test_update_detections_assign_uuid(self):
        """Test assigning detection to a user by UUID."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_uuid", "value": "00000000-0000-0000-0000-000000000000"},
            call_body["action_parameters"],
        )

    def test_update_detections_assign_user_id(self):
        """Test assigning detection to a user by email."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_user_id", "value": "analyst@example.com"},
            call_body["action_parameters"],
        )

    def test_update_detections_no_params_returns_error(self):
        """Test that providing no update params returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_show_in_ui_false(self):
        """Test hiding a detection from UI.

        show_in_ui must be sent as the string "false" — live-validated 2026-06-10:
        JSON boolean False returns 400 "failed to read and parse request";
        string "false" returns 200 and the read-back field is Python False.
        """
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=False,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "show_in_ui", "value": "false"},
            call_body["action_parameters"],
        )

    def test_update_detections_unassign(self):
        """Test unassigning a detection from the current user."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "unassign", "value": "true"},
            call_body["action_parameters"],
        )

    def test_update_detections_unassign_false_only_returns_error(self):
        """Test that unassign=False as the only argument hits the no-param guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=False,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_api_error_returns_error_dict(self):
        """Test that a non-200 API response produces an error dict."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad request"}]},
        }

        result = self.module.update_detections(
            ids=["id1"],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_called_once()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_uuid_and_name_returns_error(self):
        """Test that assign_to_uuid + assign_to_name also triggers the guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_user_id_and_name_returns_error(self):
        """Test that assign_to_user_id + assign_to_name also triggers the guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_assign_user_id_and_unassign_returns_error(self):
        """Test that assign_to_user_id + unassign=True triggers the conflict guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_assign_name_and_unassign_returns_error(self):
        """Test that assign_to_name + unassign=True triggers the conflict guard."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_invalid_status_returns_error(self):
        """Test that an invalid status value returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status="true_positive",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("status", result["error"])

    def test_update_detections_empty_ids_returns_error(self):
        """Test that passing an empty ids list returns an error without calling API."""
        result = self.module.update_detections(
            ids=[],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_show_in_ui_true(self):
        """Test showing a detection in the UI sends the string 'true'."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=True,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "show_in_ui", "value": "true"},
            call_body["action_parameters"],
        )

    def test_update_detections_assign_name(self):
        """Test assigning detection to a user by full name."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name="Jane Smith",
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "assign_to_name", "value": "Jane Smith"},
            call_body["action_parameters"],
        )

    def test_update_detections_append_comment(self):
        """Test appending a comment sends the correct action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="Investigating now",
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "append_comment", "value": "Investigating now"},
            call_body["action_parameters"],
        )

    def test_update_detections_add_tags_resolution(self):
        """Test add_tags with a resolution tag emits an add_tag action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["true_positive"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "add_tag", "value": "true_positive"},
            call_body["action_parameters"],
        )

    def test_update_detections_add_tags_arbitrary(self):
        """Test that arbitrary (non-resolution) tags are accepted and emitted."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["custom_tag", "testing"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "add_tag", "value": "custom_tag"},
            call_body["action_parameters"],
        )
        self.assertIn(
            {"name": "add_tag", "value": "testing"},
            call_body["action_parameters"],
        )

    def test_update_detections_remove_tags(self):
        """Test remove_tags emits a remove_tag action_parameter per tag."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=["false_positive"],
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "remove_tag", "value": "false_positive"},
            call_body["action_parameters"],
        )

    def test_update_detections_remove_tags_by_prefix(self):
        """Test remove_tags_by_prefix emits the remove_tags_by_prefix action_parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix="fc/",
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        self.assertIn(
            {"name": "remove_tags_by_prefix", "value": "fc/"},
            call_body["action_parameters"],
        )

    def test_update_detections_empty_tag_returns_error(self):
        """Test that an empty/whitespace tag returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["   "],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_empty_remove_tag_returns_error(self):
        """Test that an empty/whitespace value in remove_tags returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=["   "],
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_empty_prefix_returns_error(self):
        """Test that an empty/whitespace remove_tags_by_prefix returns an error without calling API."""
        for prefix in ("", "   "):
            result = self.module.update_detections(
                ids=["id1"],
                status=None,
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=None,
                add_tags=None,
                remove_tags=None,
                remove_tags_by_prefix=prefix,
            )

            self.mock_client.command.assert_not_called()
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)

    def test_update_detections_two_assign_params_returns_error(self):
        """Test that providing multiple assign_to_* params returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id="analyst@example.com",
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("assign_to_uuid", result["error"])

    def test_update_detections_assign_and_unassign_returns_error(self):
        """Test that combining any assign_to_* with unassign=True returns an error."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid="00000000-0000-0000-0000-000000000000",
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=True,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("unassign", result["error"])

    def test_update_detections_empty_comment_returns_error(self):
        """Test that an empty comment string returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="",
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("append_comment", result["error"])

    def test_update_detections_whitespace_only_comment_returns_error(self):
        """Test that a whitespace-only comment string returns an error without calling API."""
        result = self.module.update_detections(
            ids=["id1"],
            status=None,
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment="   ",
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.mock_client.command.assert_not_called()
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)

    def test_update_detections_add_tags_combined_with_status(self):
        """Test combining add_tags with a status update in one call."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["true_positive"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        param_names = [p["name"] for p in call_body["action_parameters"]]
        self.assertIn("update_status", param_names)
        self.assertIn("add_tag", param_names)

    def test_update_detections_close_without_resolution_tag_returns_hint(self):
        """Test that closing without a resolution tag wraps success with a hint.

        Covers both add_tags=None and add_tags=[] (explicit empty list) — both must
        trigger the hint since neither carries a resolution tag.
        """
        mock_response = {"status_code": 200, "body": {"resources": []}}

        for add_tags in (None, []):
            self.mock_client.command.reset_mock()
            self.mock_client.command.return_value = mock_response

            result = self.module.update_detections(
                ids=["id1"],
                status="closed",
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=None,
                add_tags=add_tags,
                remove_tags=None,
                remove_tags_by_prefix=None,
            )

            self.mock_client.command.assert_called_once()
            self.assertIsInstance(result, dict)
            self.assertIn("hint", result)
            self.assertIn("resolution", result["hint"].lower())
            self.assertEqual(result["result"], [])

    def test_update_detections_close_with_resolution_tag_no_hint(self):
        """Test that closing with any resolution tag returns the plain success shape."""
        mock_response = {"status_code": 200, "body": {"resources": []}}

        for tag in ("true_positive", "false_positive", "ignored"):
            self.mock_client.command.return_value = mock_response
            result = self.module.update_detections(
                ids=["id1"],
                status="closed",
                assign_to_uuid=None,
                assign_to_user_id=None,
                assign_to_name=None,
                unassign=None,
                append_comment=None,
                show_in_ui=None,
                add_tags=[tag],
                remove_tags=None,
                remove_tags_by_prefix=None,
            )

            self.assertEqual(result, [], msg=f"hint must not fire for resolution tag {tag!r}")

    def test_update_detections_close_with_mixed_tags_no_hint(self):
        """Test that a resolution tag mixed with a custom tag still suppresses the hint."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        result = self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["true_positive", "my_custom_tag"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertEqual(result, [])

    def test_update_detections_close_with_non_resolution_tag_returns_hint(self):
        """Test that closing with only a non-resolution tag still emits the hint."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        result = self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=["MY_CUSTOM_TAG"],
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("hint", result)
        self.assertEqual(result["result"], [])

    def test_update_detections_close_api_error_no_hint(self):
        """Test that an API error while closing is returned as-is, not hint-wrapped."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad request"}]},
        }

        result = self.module.update_detections(
            ids=["id1"],
            status="closed",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=None,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertNotIn("hint", result)

    def test_update_detections_unassign_false_is_noop(self):
        """Test that unassign=False does not add the action parameter."""
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        self.module.update_detections(
            ids=["id1"],
            status="new",
            assign_to_uuid=None,
            assign_to_user_id=None,
            assign_to_name=None,
            unassign=False,
            append_comment=None,
            show_in_ui=None,
            add_tags=None,
            remove_tags=None,
            remove_tags_by_prefix=None,
        )

        call_body = self.mock_client.command.call_args[1]["body"]
        param_names = [p["name"] for p in call_body["action_parameters"]]
        self.assertNotIn("unassign", param_names)


if __name__ == "__main__":
    unittest.main()
