"""Tests for the Detections module."""

import unittest

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
        self.assertEqual(second_call[1]["parameters"], {"include_hidden": True})
        self.assertEqual(second_call[1]["body"], {"composite_ids": ["composite-1", "composite-2"]})

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["composite_id"], "composite-1")

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
            parameters={"include_hidden": False},
            body={"composite_ids": ["composite-1"]},
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


if __name__ == "__main__":
    unittest.main()
