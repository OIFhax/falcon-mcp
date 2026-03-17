"""Tests for the Incidents module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.incidents import IncidentsModule, WRITE_ANNOTATIONS
from tests.modules.utils.test_modules import TestModules


class TestIncidentsModule(TestModules):
    """Test cases for the Incidents module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IncidentsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_show_crowd_score",
            "falcon_search_incidents",
            "falcon_query_incident_ids",
            "falcon_get_incident_details",
            "falcon_search_behaviors",
            "falcon_query_behavior_ids",
            "falcon_get_behavior_details",
            "falcon_perform_incident_action",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_show_crowd_score_fql_guide",
            "falcon_search_incidents_fql_guide",
            "falcon_search_behaviors_fql_guide",
            "falcon_incident_actions_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_incidents", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_perform_incident_action", WRITE_ANNOTATIONS)

    def test_show_crowd_score(self):
        """Test querying crowd score with successful response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "score1", "score": 50, "adjusted_score": 60},
                    {"id": "score2", "score": 70, "adjusted_score": 80},
                ]
            },
        }

        result = self.module.show_crowd_score(
            filter="score:>40",
            limit=100,
            offset=0,
            sort="score.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "CrowdScore",
            parameters={
                "filter": "score:>40",
                "limit": 100,
                "offset": 0,
                "sort": "score.desc",
            },
        )
        self.assertEqual(result["average_score"], 60)
        self.assertEqual(result["average_adjusted_score"], 70)
        self.assertEqual(len(result["scores"]), 2)

    def test_query_incident_ids_success(self):
        """Test querying incident IDs uses QueryIncidents operation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["inc-1", "inc-2"]},
        }

        result = self.module.query_incident_ids(
            filter="state:'open'",
            limit=2,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "QueryIncidents",
            parameters={
                "filter": "state:'open'",
                "limit": 2,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(result, ["inc-1", "inc-2"])

    def test_search_incidents_success(self):
        """Test searching incidents runs query + details flow."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["inc-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"incident_id": "inc-1"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_incidents(
            filter="state:'open'",
            limit=10,
            offset=0,
            sort="name.asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "GetIncidents",
            body={"ids": ["inc-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["incident_id"], "inc-1")

    def test_query_behavior_ids_success(self):
        """Test querying behavior IDs uses QueryBehaviors operation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["beh-1", "beh-2"]},
        }

        result = self.module.query_behavior_ids(
            filter="tactic:'Persistence'",
            limit=2,
            offset=0,
            sort="timestamp.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "QueryBehaviors",
            parameters={
                "filter": "tactic:'Persistence'",
                "limit": 2,
                "offset": 0,
                "sort": "timestamp.desc",
            },
        )
        self.assertEqual(result, ["beh-1", "beh-2"])

    def test_search_behaviors_success(self):
        """Test searching behaviors runs query + details flow."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["beh-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"behavior_id": "beh-1"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_behaviors(
            filter="tactic:'Persistence'",
            limit=10,
            offset=0,
            sort="timestamp.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "GetBehaviors",
            body={"ids": ["beh-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["behavior_id"], "beh-1")

    def test_perform_incident_action_requires_confirmation(self):
        """Test perform_incident_action requires confirm_execution=true."""
        result = self.module.perform_incident_action(
            confirm_execution=False,
            ids=["inc-1"],
            update_status=30,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_perform_incident_action_requires_ids_without_body(self):
        """Test perform_incident_action requires ids when body is not provided."""
        result = self.module.perform_incident_action(
            confirm_execution=True,
            ids=None,
            update_status=30,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_perform_incident_action_requires_action_parameters(self):
        """Test perform_incident_action requires at least one action."""
        result = self.module.perform_incident_action(
            confirm_execution=True,
            ids=["inc-1"],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_perform_incident_action_success_with_convenience_fields(self):
        """Test perform_incident_action builds action parameters from convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "inc-1", "updated": True}]},
        }

        result = self.module.perform_incident_action(
            confirm_execution=True,
            ids=["inc-1"],
            update_status=30,
            add_comment="triaging",
            update_detects=True,
            overwrite_detects=False,
        )

        self.mock_client.command.assert_called_once_with(
            "PerformIncidentAction",
            parameters={"update_detects": True, "overwrite_detects": False},
            body={
                "ids": ["inc-1"],
                "action_parameters": [
                    {"name": "add_comment", "value": "triaging"},
                    {"name": "update_status", "value": "30"},
                ],
            },
        )
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["updated"])

    def test_perform_incident_action_body_override(self):
        """Test perform_incident_action accepts full body override."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "inc-1", "updated": True}]},
        }

        custom_body = {
            "ids": ["inc-1"],
            "action_parameters": [{"name": "add_tag", "value": "investigating"}],
        }
        result = self.module.perform_incident_action(
            confirm_execution=True,
            body=custom_body,
            update_detects=None,
            overwrite_detects=None,
        )

        self.mock_client.command.assert_called_once_with(
            "PerformIncidentAction",
            parameters={},
            body=custom_body,
        )
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["updated"])


if __name__ == "__main__":
    unittest.main()
