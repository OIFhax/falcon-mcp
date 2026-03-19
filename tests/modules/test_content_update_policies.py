"""
Tests for the Content Update Policies module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.content_update_policies import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    ContentUpdatePoliciesModule,
)
from tests.modules.utils.test_modules import TestModules


class TestContentUpdatePoliciesModule(TestModules):
    """Test cases for the Content Update Policies module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ContentUpdatePoliciesModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_content_update_policies",
            "falcon_search_content_update_policy_members",
            "falcon_query_content_update_policy_ids",
            "falcon_query_content_update_policy_member_ids",
            "falcon_query_content_update_pinnable_versions",
            "falcon_get_content_update_policy_details",
            "falcon_create_content_update_policies",
            "falcon_update_content_update_policies",
            "falcon_delete_content_update_policies",
            "falcon_perform_content_update_policies_action",
            "falcon_set_content_update_policies_precedence",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_content_update_policies_fql_guide",
            "falcon_search_content_update_policy_members_fql_guide",
            "falcon_content_update_policies_pinnable_versions_guide",
            "falcon_content_update_policies_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations(
            "falcon_search_content_update_policies",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_create_content_update_policies",
            WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_delete_content_update_policies",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_search_content_update_policies_success(self):
        """Test content update policy search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1", "name": "Default"}]},
        }

        result = self.module.search_content_update_policies(
            filter="name:'platform_default'",
            limit=10,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedContentUpdatePolicies",
            parameters={
                "filter": "name:'platform_default'",
                "limit": 10,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_search_content_update_policy_members_requires_policy_id(self):
        """Test content update policy member search requires policy ID."""
        result = self.module.search_content_update_policy_members(
            policy_id=None,
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_query_content_update_policy_ids_empty_filter_returns_guide(self):
        """Test empty ID query with filter returns FQL helper response."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_content_update_policy_ids(
            filter="name:'NotReal*'",
            limit=100,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_query_content_update_pinnable_versions_validation_and_success(self):
        """Test pinnable content version validation and success."""
        validation_result = self.module.query_content_update_pinnable_versions(
            category=None,
            sort="deployed_timestamp.desc",
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["2026.03.16.0832"]},
        }
        success_result = self.module.query_content_update_pinnable_versions(
            category="rapid_response_al_bl_listing",
            sort="deployed_timestamp.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "queryPinnableContentVersions",
            parameters={
                "category": "rapid_response_al_bl_listing",
                "sort": "deployed_timestamp.desc",
            },
        )
        self.assertEqual(success_result, ["2026.03.16.0832"])

    def test_get_content_update_policy_details_validation_and_success(self):
        """Test content update policy detail validation and success."""
        validation_result = self.module.get_content_update_policy_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        success_result = self.module.get_content_update_policy_details(ids=["policy-1"])

        self.mock_client.command.assert_called_once_with(
            "getContentUpdatePolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_create_content_update_policies_confirm_required(self):
        """Test create requires confirm_execution=true."""
        result = self.module.create_content_update_policies(
            confirm_execution=False,
            body=None,
            clone_id=None,
            description=None,
            name="test",
            platform_name="Windows",
            settings=None,
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_content_update_policies_success(self):
        """Test create content update policy success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.create_content_update_policies(
            confirm_execution=True,
            body=None,
            clone_id=None,
            description="test",
            name="new-policy",
            platform_name="Windows",
            settings=[{"id": "toggle", "value": True}],
        )

        self.mock_client.command.assert_called_once_with(
            "createContentUpdatePolicies",
            body={
                "resources": [
                    {
                        "name": "new-policy",
                        "platform_name": "Windows",
                        "description": "test",
                        "settings": [{"id": "toggle", "value": True}],
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_update_content_update_policies_requires_update_fields(self):
        """Test update requires ID and at least one update field."""
        result = self.module.update_content_update_policies(
            confirm_execution=True,
            body=None,
            id="policy-1",
            description=None,
            name=None,
            settings=None,
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_perform_content_update_policies_action_success(self):
        """Test content update policy action success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.perform_content_update_policies_action(
            confirm_execution=True,
            action_name="disable",
            ids=["policy-1"],
            group_id=None,
            action_parameters=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "performContentUpdatePoliciesAction",
            parameters={"action_name": "disable"},
            body={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_set_content_update_policies_precedence_success(self):
        """Test content update policy precedence success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.set_content_update_policies_precedence(
            confirm_execution=True,
            body=None,
            ids=["policy-1", "policy-2"],
        )

        self.mock_client.command.assert_called_once_with(
            "setContentUpdatePoliciesPrecedence",
            body={"ids": ["policy-1", "policy-2"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["updated"], 1)


if __name__ == "__main__":
    unittest.main()
