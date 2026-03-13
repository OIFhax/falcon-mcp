"""
Tests for the Prevention Policies module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.prevention_policies import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    PreventionPoliciesModule,
)
from tests.modules.utils.test_modules import TestModules


class TestPreventionPoliciesModule(TestModules):
    """Test cases for the Prevention Policies module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(PreventionPoliciesModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_prevention_policies",
            "falcon_search_prevention_policy_members",
            "falcon_query_prevention_policy_ids",
            "falcon_query_prevention_policy_member_ids",
            "falcon_get_prevention_policy_details",
            "falcon_create_prevention_policies",
            "falcon_update_prevention_policies",
            "falcon_delete_prevention_policies",
            "falcon_perform_prevention_policies_action",
            "falcon_set_prevention_policies_precedence",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_prevention_policies_fql_guide",
            "falcon_search_prevention_policy_members_fql_guide",
            "falcon_prevention_policies_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_prevention_policies", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_prevention_policies", WRITE_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_delete_prevention_policies",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_perform_prevention_policies_action",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_search_prevention_policies_success(self):
        """Test prevention policy search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1", "name": "Default"}]},
        }

        result = self.module.search_prevention_policies(
            filter="platform_name:'Windows'",
            limit=10,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedPreventionPolicies",
            parameters={
                "filter": "platform_name:'Windows'",
                "limit": 10,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_search_prevention_policy_members_requires_policy_id(self):
        """Test policy member search requires policy ID."""
        result = self.module.search_prevention_policy_members(
            policy_id=None,
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_search_prevention_policy_members_success(self):
        """Test prevention policy member search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"device_id": "device-1", "hostname": "host1"}]},
        }

        result = self.module.search_prevention_policy_members(
            policy_id="policy-1",
            filter="hostname:'host1'",
            limit=10,
            offset=0,
            sort="hostname.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedPreventionPolicyMembers",
            parameters={
                "id": "policy-1",
                "filter": "hostname:'host1'",
                "limit": 10,
                "offset": 0,
                "sort": "hostname.asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["hostname"], "host1")

    def test_query_prevention_policy_ids_empty_filter_returns_guide(self):
        """Test empty ID query with filter returns FQL helper response."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_prevention_policy_ids(
            filter="name:'NotReal*'",
            limit=100,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_prevention_policy_details_validation_and_success(self):
        """Test policy detail validation and success path."""
        validation_result = self.module.get_prevention_policy_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        success_result = self.module.get_prevention_policy_details(ids=["policy-1"])

        self.mock_client.command.assert_called_once_with(
            "getPreventionPolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_create_prevention_policies_confirm_required(self):
        """Test create requires confirm_execution=true."""
        result = self.module.create_prevention_policies(
            confirm_execution=False,
            body=None,
            clone_id=None,
            description=None,
            name="New Policy",
            platform_name="Windows",
            settings=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_prevention_policies_success(self):
        """Test create prevention policies success."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.create_prevention_policies(
            confirm_execution=True,
            body=None,
            clone_id=None,
            description="created via test",
            name="New Policy",
            platform_name="Windows",
            settings=[{"id": "setting-1", "value": {"enabled": True}}],
        )

        self.mock_client.command.assert_called_once_with(
            "createPreventionPolicies",
            body={
                "resources": [
                    {
                        "name": "New Policy",
                        "platform_name": "Windows",
                        "description": "created via test",
                        "settings": [{"id": "setting-1", "value": {"enabled": True}}],
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_update_prevention_policies_validation_and_success(self):
        """Test update validation and success path."""
        validation_result = self.module.update_prevention_policies(
            confirm_execution=True,
            body=None,
            id="policy-1",
            description=None,
            name=None,
            settings=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        success_result = self.module.update_prevention_policies(
            confirm_execution=True,
            body=None,
            id="policy-1",
            description="updated",
            name=None,
            settings=None,
        )

        self.mock_client.command.assert_called_once_with(
            "updatePreventionPolicies",
            body={"resources": [{"id": "policy-1", "description": "updated"}]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_delete_prevention_policies_confirm_required(self):
        """Test delete requires confirm_execution=true."""
        result = self.module.delete_prevention_policies(
            confirm_execution=False,
            ids=["policy-1"],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_prevention_policies_success(self):
        """Test delete prevention policies success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.delete_prevention_policies(
            confirm_execution=True,
            ids=["policy-1"],
        )

        self.mock_client.command.assert_called_once_with(
            "deletePreventionPolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_perform_prevention_policies_action_success(self):
        """Test perform prevention policy action success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.perform_prevention_policies_action(
            confirm_execution=True,
            action_name="disable",
            ids=["policy-1"],
            group_id=None,
            action_parameters=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "performPreventionPoliciesAction",
            parameters={"action_name": "disable"},
            body={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_set_prevention_policies_precedence_success(self):
        """Test set prevention policy precedence success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.set_prevention_policies_precedence(
            confirm_execution=True,
            body=None,
            ids=["policy-1", "policy-2"],
            platform_name="Windows",
        )

        self.mock_client.command.assert_called_once_with(
            "setPreventionPoliciesPrecedence",
            body={"ids": ["policy-1", "policy-2"], "platform_name": "Windows"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["updated"], 1)


if __name__ == "__main__":
    unittest.main()
