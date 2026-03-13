"""
Tests for the Firewall module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.firewall import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    FirewallModule,
)
from tests.modules.utils.test_modules import TestModules


class TestFirewallModule(TestModules):
    """Test cases for the Firewall module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(FirewallModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_firewall_rules",
            "falcon_search_firewall_rule_groups",
            "falcon_search_firewall_policy_rules",
            "falcon_query_firewall_rule_ids",
            "falcon_query_firewall_rule_group_ids",
            "falcon_query_firewall_policy_rule_ids",
            "falcon_get_firewall_rules",
            "falcon_get_firewall_rule_groups",
            "falcon_aggregate_firewall_rules",
            "falcon_aggregate_firewall_rule_groups",
            "falcon_aggregate_firewall_policy_rules",
            "falcon_aggregate_firewall_events",
            "falcon_query_firewall_event_ids",
            "falcon_get_firewall_events",
            "falcon_query_firewall_field_ids",
            "falcon_get_firewall_fields",
            "falcon_query_firewall_platform_ids",
            "falcon_get_firewall_platforms",
            "falcon_get_firewall_policy_containers",
            "falcon_create_firewall_rule_group",
            "falcon_update_firewall_rule_group",
            "falcon_delete_firewall_rule_groups",
            "falcon_validate_firewall_rule_group_create",
            "falcon_validate_firewall_rule_group_update",
            "falcon_update_firewall_policy_container",
            "falcon_update_firewall_policy_container_v1",
            "falcon_query_firewall_network_location_ids",
            "falcon_get_firewall_network_locations",
            "falcon_get_firewall_network_location_details",
            "falcon_create_firewall_network_locations",
            "falcon_upsert_firewall_network_locations",
            "falcon_update_firewall_network_locations",
            "falcon_update_firewall_network_locations_metadata",
            "falcon_update_firewall_network_locations_precedence",
            "falcon_delete_firewall_network_locations",
            "falcon_validate_firewall_filepath_pattern",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_firewall_rules_fql_guide",
            "falcon_search_firewall_events_fql_guide",
            "falcon_search_firewall_network_locations_fql_guide",
            "falcon_firewall_management_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_firewall_rules", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_firewall_rule_group", WRITE_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_delete_firewall_rule_groups",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_delete_firewall_network_locations",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_search_firewall_rules_success(self):
        """Test firewall rule search success."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["rule-1"]},
        }
        detail_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "rule-1", "name": "Rule 1"}]},
        }
        self.mock_client.command.side_effect = [query_response, detail_response]

        result = self.module.search_firewall_rules(
            filter="enabled:true",
            limit=10,
            offset=0,
            sort="modified_on.desc",
            q=None,
            after=None,
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "query_rules",
            parameters={
                "filter": "enabled:true",
                "limit": 10,
                "offset": 0,
                "sort": "modified_on.desc",
            },
        )
        self.mock_client.command.assert_any_call("get_rules", parameters={"ids": ["rule-1"]})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "rule-1")

    def test_query_firewall_rule_ids_empty_filter_returns_guide(self):
        """Test empty query results with filter return FQL helper context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.query_firewall_rule_ids(
            filter="name:'missing*'",
            limit=100,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_firewall_rules_validation_and_success(self):
        """Test get rules validation and success path."""
        validation_result = self.module.get_firewall_rules(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "rule-1"}]},
        }
        success_result = self.module.get_firewall_rules(ids=["rule-1"])

        self.mock_client.command.assert_called_once_with("get_rules", parameters={"ids": ["rule-1"]})
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "rule-1")

    def test_create_firewall_rule_group_confirm_required(self):
        """Test create firewall rule group requires explicit confirmation."""
        result = self.module.create_firewall_rule_group(
            confirm_execution=False,
            body={"name": "group"},
            parameters=None,
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_firewall_rule_group_success(self):
        """Test create firewall rule group success path."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "group-1"}]},
        }

        result = self.module.create_firewall_rule_group(
            confirm_execution=True,
            body={"name": "group-1"},
            parameters={"comment": "integration"},
        )

        self.mock_client.command.assert_called_once_with(
            "create_rule_group",
            parameters={"comment": "integration"},
            body={"name": "group-1"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "group-1")

    def test_delete_firewall_rule_groups_validation_and_success(self):
        """Test delete rule groups validation and success path."""
        validation_result = self.module.delete_firewall_rule_groups(
            confirm_execution=True,
            ids=None,
            comment=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "group-1"}]},
        }
        success_result = self.module.delete_firewall_rule_groups(
            confirm_execution=True,
            ids=["group-1"],
            comment="cleanup",
        )

        self.mock_client.command.assert_called_once_with(
            "delete_rule_groups",
            parameters={"ids": ["group-1"], "comment": "cleanup"},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "group-1")

    def test_aggregate_firewall_rules_requires_body(self):
        """Test aggregate operation requires body."""
        result = self.module.aggregate_firewall_rules(body=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_aggregate_firewall_events_success(self):
        """Test aggregate events sends list body correctly."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"count": 10}]},
        }

        result = self.module.aggregate_firewall_events(
            body=[{"field": "event_type", "type": "terms"}],
        )

        self.mock_client.command.assert_called_once_with(
            "aggregate_events",
            body=[{"field": "event_type", "type": "terms"}],
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["count"], 10)

    def test_query_firewall_network_location_ids_empty_filter_returns_guide(self):
        """Test network location query helper response for empty filtered result."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.query_firewall_network_location_ids(
            filter="name:'none*'",
            limit=100,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_validate_firewall_filepath_pattern_validation_and_success(self):
        """Test filepath validation input checks and success path."""
        validation_result = self.module.validate_firewall_filepath_pattern(filepath_pattern=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"valid": True}]},
        }
        success_result = self.module.validate_firewall_filepath_pattern(
            filepath_pattern="C:\\\\Windows\\\\*",
        )

        self.mock_client.command.assert_called_once_with(
            "validate_filepath_pattern",
            parameters={"filepath_pattern": "C:\\\\Windows\\\\*"},
        )
        self.assertEqual(len(success_result), 1)
        self.assertTrue(success_result[0]["valid"])


if __name__ == "__main__":
    unittest.main()
