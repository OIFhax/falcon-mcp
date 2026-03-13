"""
Tests for the Firewall Policies module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.firewall_policies import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    FirewallPoliciesModule,
)
from tests.modules.utils.test_modules import TestModules


class TestFirewallPoliciesModule(TestModules):
    """Test cases for the Firewall Policies module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(FirewallPoliciesModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_firewall_policy_members",
            "falcon_search_firewall_policies",
            "falcon_perform_firewall_policies_action",
            "falcon_set_firewall_policies_precedence",
            "falcon_get_firewall_policy_details",
            "falcon_create_firewall_policies",
            "falcon_update_firewall_policies",
            "falcon_delete_firewall_policies",
            "falcon_query_firewall_policy_member_ids",
            "falcon_query_firewall_policy_ids",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_firewall_policies_fql_guide",
            "falcon_search_firewall_policy_members_fql_guide",
            "falcon_firewall_policies_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_firewall_policies", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_firewall_policies", WRITE_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_delete_firewall_policies",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_perform_firewall_policies_action",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_search_firewall_policies_success(self):
        """Test firewall policy search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1", "name": "Default"}]},
        }

        result = self.module.search_firewall_policies(
            filter="platform_name:'Windows'",
            limit=10,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedFirewallPolicies",
            parameters={
                "filter": "platform_name:'Windows'",
                "limit": 10,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_search_firewall_policy_members_requires_policy_id(self):
        """Test policy member search requires policy ID."""
        result = self.module.search_firewall_policy_members(
            policy_id=None,
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_query_firewall_policy_ids_empty_filter_returns_guide(self):
        """Test empty ID query with filter returns FQL helper response."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_firewall_policy_ids(
            filter="name:'NotReal*'",
            limit=100,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_firewall_policy_details_validation_and_success(self):
        """Test policy detail validation and success path."""
        validation_result = self.module.get_firewall_policy_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        success_result = self.module.get_firewall_policy_details(ids=["policy-1"])

        self.mock_client.command.assert_called_once_with(
            "getFirewallPolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_create_firewall_policies_confirm_required(self):
        """Test create requires confirm_execution=true."""
        result = self.module.create_firewall_policies(
            confirm_execution=False,
            body=None,
            clone_id=None,
            name="Policy",
            platform_name="Windows",
            description=None,
            settings={"policy": {}},
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_firewall_policies_success(self):
        """Test create firewall policy success."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.create_firewall_policies(
            confirm_execution=True,
            body=None,
            clone_id="template-policy-id",
            name="Policy",
            platform_name="Windows",
            description="created via test",
            settings={"policy": {"enabled": True}},
        )

        self.mock_client.command.assert_called_once_with(
            "createFirewallPolicies",
            parameters={"clone_id": "template-policy-id"},
            body={
                "resources": [
                    {
                        "name": "Policy",
                        "platform_name": "Windows",
                        "description": "created via test",
                        "settings": {"policy": {"enabled": True}},
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_update_firewall_policies_validation_and_success(self):
        """Test update validation and success path."""
        validation_result = self.module.update_firewall_policies(
            confirm_execution=True,
            body=None,
            id="policy-1",
            name=None,
            description=None,
            settings=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        success_result = self.module.update_firewall_policies(
            confirm_execution=True,
            body=None,
            id="policy-1",
            name=None,
            description="updated",
            settings={"policy": {"enabled": False}},
        )

        self.mock_client.command.assert_called_once_with(
            "updateFirewallPolicies",
            body={
                "resources": [
                    {
                        "id": "policy-1",
                        "description": "updated",
                        "settings": {"policy": {"enabled": False}},
                    }
                ]
            },
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_delete_firewall_policies_success(self):
        """Test delete policy success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.delete_firewall_policies(
            confirm_execution=True,
            ids=["policy-1"],
        )

        self.mock_client.command.assert_called_once_with(
            "deleteFirewallPolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_perform_firewall_policies_action_success(self):
        """Test policy action success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.perform_firewall_policies_action(
            confirm_execution=True,
            action_name="disable",
            ids=["policy-1"],
            group_id=None,
            action_parameters=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "performFirewallPoliciesAction",
            parameters={"action_name": "disable"},
            body={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_set_firewall_policies_precedence_success(self):
        """Test precedence update success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.set_firewall_policies_precedence(
            confirm_execution=True,
            body=None,
            ids=["policy-1", "policy-2"],
            platform_name="Windows",
        )

        self.mock_client.command.assert_called_once_with(
            "setFirewallPoliciesPrecedence",
            body={"ids": ["policy-1", "policy-2"], "platform_name": "Windows"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["updated"], 1)

    def test_query_firewall_policy_member_ids_requires_policy_id(self):
        """Test policy member ID query requires policy ID."""
        result = self.module.query_firewall_policy_member_ids(
            policy_id=None,
            filter=None,
            limit=100,
            offset=0,
            sort=None,
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
