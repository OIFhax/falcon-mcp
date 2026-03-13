"""
Tests for the Device Control Policies module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.device_control_policies import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    DeviceControlPoliciesModule,
)
from tests.modules.utils.test_modules import TestModules


class TestDeviceControlPoliciesModule(TestModules):
    """Test cases for the Device Control Policies module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DeviceControlPoliciesModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_device_control_policy_members",
            "falcon_search_device_control_policies",
            "falcon_get_default_device_control_policies",
            "falcon_update_default_device_control_policies",
            "falcon_perform_device_control_policies_action",
            "falcon_update_device_control_policies_classes",
            "falcon_get_default_device_control_settings",
            "falcon_update_default_device_control_settings",
            "falcon_set_device_control_policies_precedence",
            "falcon_get_device_control_policy_details",
            "falcon_create_device_control_policies",
            "falcon_update_device_control_policies",
            "falcon_delete_device_control_policies",
            "falcon_get_device_control_policy_details_v2",
            "falcon_create_device_control_policies_v2",
            "falcon_update_device_control_policies_v2",
            "falcon_query_device_control_policy_member_ids",
            "falcon_query_device_control_policy_ids",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_device_control_policies_fql_guide",
            "falcon_search_device_control_policy_members_fql_guide",
            "falcon_device_control_defaults_guide",
            "falcon_device_control_policies_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_device_control_policies", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_device_control_policies", WRITE_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_delete_device_control_policies",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_perform_device_control_policies_action",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_search_device_control_policies_success(self):
        """Test policy search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1", "name": "Default"}]},
        }

        result = self.module.search_device_control_policies(
            filter="platform_name:'Windows'",
            limit=10,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedDeviceControlPolicies",
            parameters={
                "filter": "platform_name:'Windows'",
                "limit": 10,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_search_device_control_policy_members_requires_policy_id(self):
        """Test policy member search requires policy ID."""
        result = self.module.search_device_control_policy_members(
            policy_id=None,
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_default_device_control_policies_and_settings_success(self):
        """Test default policy/settings read operations."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "default"}]},
        }
        policy_result = self.module.get_default_device_control_policies()
        self.mock_client.command.assert_called_once_with("getDefaultDeviceControlPolicies")
        self.assertEqual(len(policy_result), 1)

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "settings-default"}]},
        }
        settings_result = self.module.get_default_device_control_settings()
        self.mock_client.command.assert_called_once_with("getDefaultDeviceControlSettings")
        self.assertEqual(len(settings_result), 1)

    def test_update_default_device_control_policies_validation_and_success(self):
        """Test default policy update validation and success."""
        validation_result = self.module.update_default_device_control_policies(
            confirm_execution=True,
            body=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }
        success_result = self.module.update_default_device_control_policies(
            confirm_execution=True,
            body={"resources": [{"id": "default", "enabled": True}]},
        )
        self.mock_client.command.assert_called_once_with(
            "updateDefaultDeviceControlPolicies",
            body={"resources": [{"id": "default", "enabled": True}]},
        )
        self.assertEqual(len(success_result), 1)

    def test_update_device_control_policies_classes_success(self):
        """Test classes patch operation success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.update_device_control_policies_classes(
            confirm_execution=True,
            body={"resources": [{"id": "class-1", "action": "ALLOW"}]},
        )

        self.mock_client.command.assert_called_once_with(
            "patchDeviceControlPoliciesClassesV1",
            body={"resources": [{"id": "class-1", "action": "ALLOW"}]},
        )
        self.assertEqual(len(result), 1)

    def test_update_default_device_control_settings_success(self):
        """Test default settings update operation success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.update_default_device_control_settings(
            confirm_execution=True,
            body={"settings": {"usb_storage": {"enabled": True}}},
        )

        self.mock_client.command.assert_called_once_with(
            "updateDefaultDeviceControlSettings",
            body={"settings": {"usb_storage": {"enabled": True}}},
        )
        self.assertEqual(len(result), 1)

    def test_perform_device_control_policies_action_success(self):
        """Test policy action success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.perform_device_control_policies_action(
            confirm_execution=True,
            action_name="disable",
            ids=["policy-1"],
            group_id=None,
            action_parameters=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "performDeviceControlPoliciesAction",
            parameters={"action_name": "disable"},
            body={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_set_device_control_policies_precedence_success(self):
        """Test precedence update success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.set_device_control_policies_precedence(
            confirm_execution=True,
            body=None,
            ids=["policy-1", "policy-2"],
            platform_name="Windows",
        )

        self.mock_client.command.assert_called_once_with(
            "setDeviceControlPoliciesPrecedence",
            body={"ids": ["policy-1", "policy-2"], "platform_name": "Windows"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["updated"], 1)

    def test_get_device_control_policy_details_validation_and_success(self):
        """Test v1 policy detail validation and success path."""
        validation_result = self.module.get_device_control_policy_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        success_result = self.module.get_device_control_policy_details(ids=["policy-1"])

        self.mock_client.command.assert_called_once_with(
            "getDeviceControlPolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_create_device_control_policies_success(self):
        """Test create v1 policy success."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.create_device_control_policies(
            confirm_execution=True,
            body=None,
            name="Policy V1",
            platform_name="Windows",
            description="created via test",
            settings={"usb_storage": {"enabled": True}},
        )

        self.mock_client.command.assert_called_once_with(
            "createDeviceControlPolicies",
            body={
                "resources": [
                    {
                        "name": "Policy V1",
                        "platform_name": "Windows",
                        "description": "created via test",
                        "settings": {"usb_storage": {"enabled": True}},
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_update_device_control_policies_validation_and_success(self):
        """Test update v1 policy validation and success."""
        validation_result = self.module.update_device_control_policies(
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
        success_result = self.module.update_device_control_policies(
            confirm_execution=True,
            body=None,
            id="policy-1",
            name=None,
            description="updated",
            settings={"usb_storage": {"enabled": False}},
        )

        self.mock_client.command.assert_called_once_with(
            "updateDeviceControlPolicies",
            body={
                "resources": [
                    {
                        "id": "policy-1",
                        "description": "updated",
                        "settings": {"usb_storage": {"enabled": False}},
                    }
                ]
            },
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_delete_device_control_policies_success(self):
        """Test delete policy success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.delete_device_control_policies(
            confirm_execution=True,
            ids=["policy-1"],
        )

        self.mock_client.command.assert_called_once_with(
            "deleteDeviceControlPolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_get_device_control_policy_details_v2_success(self):
        """Test get v2 policy details success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-v2"}]},
        }

        result = self.module.get_device_control_policy_details_v2(ids=["policy-v2"])

        self.mock_client.command.assert_called_once_with(
            "getDeviceControlPoliciesV2",
            parameters={"ids": ["policy-v2"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-v2")

    def test_create_device_control_policies_v2_success(self):
        """Test create v2 policy success."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "policy-v2"}]},
        }

        result = self.module.create_device_control_policies_v2(
            confirm_execution=True,
            body=None,
            name="Policy V2",
            platform_name="Windows",
            description="created via test",
            settings={"usb_storage": {"enabled": True}},
        )

        self.mock_client.command.assert_called_once_with(
            "postDeviceControlPoliciesV2",
            body={
                "resources": [
                    {
                        "name": "Policy V2",
                        "platform_name": "Windows",
                        "description": "created via test",
                        "settings": {"usb_storage": {"enabled": True}},
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-v2")

    def test_update_device_control_policies_v2_success(self):
        """Test update v2 policy success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-v2"}]},
        }

        result = self.module.update_device_control_policies_v2(
            confirm_execution=True,
            body=None,
            id="policy-v2",
            name=None,
            description="updated",
            settings={"usb_storage": {"enabled": False}},
        )

        self.mock_client.command.assert_called_once_with(
            "patchDeviceControlPoliciesV2",
            body={
                "resources": [
                    {
                        "id": "policy-v2",
                        "description": "updated",
                        "settings": {"usb_storage": {"enabled": False}},
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-v2")

    def test_query_device_control_policy_ids_empty_filter_returns_guide(self):
        """Test empty ID query with filter returns FQL helper response."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_device_control_policy_ids(
            filter="name:'NotReal*'",
            limit=100,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_query_device_control_policy_member_ids_requires_policy_id(self):
        """Test policy member ID query requires policy ID."""
        result = self.module.query_device_control_policy_member_ids(
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
