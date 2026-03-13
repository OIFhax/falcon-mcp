"""
Tests for the Sensor Update Policies module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.sensor_update_policies import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    SensorUpdatePoliciesModule,
)
from tests.modules.utils.test_modules import TestModules


class TestSensorUpdatePoliciesModule(TestModules):
    """Test cases for the Sensor Update Policies module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(SensorUpdatePoliciesModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_reveal_sensor_uninstall_token",
            "falcon_search_sensor_update_builds",
            "falcon_search_sensor_update_kernels",
            "falcon_search_sensor_update_policy_members",
            "falcon_search_sensor_update_policies",
            "falcon_search_sensor_update_policies_v2",
            "falcon_perform_sensor_update_policies_action",
            "falcon_set_sensor_update_policies_precedence",
            "falcon_get_sensor_update_policy_details",
            "falcon_create_sensor_update_policies",
            "falcon_update_sensor_update_policies",
            "falcon_delete_sensor_update_policies",
            "falcon_get_sensor_update_policy_details_v2",
            "falcon_create_sensor_update_policies_v2",
            "falcon_update_sensor_update_policies_v2",
            "falcon_query_sensor_update_kernel_distinct",
            "falcon_query_sensor_update_policy_member_ids",
            "falcon_query_sensor_update_policy_ids",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_sensor_update_policies_fql_guide",
            "falcon_search_sensor_update_policy_members_fql_guide",
            "falcon_search_sensor_update_kernels_fql_guide",
            "falcon_sensor_update_builds_guide",
            "falcon_sensor_update_policies_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_sensor_update_policies", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_sensor_update_policies", WRITE_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_delete_sensor_update_policies",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_reveal_sensor_uninstall_token",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_search_sensor_update_builds_validation_and_success(self):
        """Test build search validation and success."""
        validation_result = self.module.search_sensor_update_builds(platform=None, stage=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"platform": "windows", "build": "12345"}]},
        }
        success_result = self.module.search_sensor_update_builds(
            platform="windows",
            stage=["prod"],
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedSensorUpdateBuilds",
            parameters={"platform": "windows", "stage": ["prod"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["build"], "12345")

    def test_search_sensor_update_policies_success(self):
        """Test policy search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1", "name": "Default"}]},
        }

        result = self.module.search_sensor_update_policies(
            filter="platform_name:'Windows'",
            limit=10,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedSensorUpdatePolicies",
            parameters={
                "filter": "platform_name:'Windows'",
                "limit": 10,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_search_sensor_update_policies_v2_success(self):
        """Test v2 policy search success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-2"}]},
        }

        result = self.module.search_sensor_update_policies_v2(
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedSensorUpdatePoliciesV2",
            parameters={"limit": 5, "offset": 0},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-2")

    def test_search_sensor_update_policy_members_requires_policy_id(self):
        """Test policy member search requires policy ID."""
        result = self.module.search_sensor_update_policy_members(
            policy_id=None,
            filter=None,
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_query_sensor_update_policy_ids_empty_filter_returns_guide(self):
        """Test empty ID query with filter returns FQL helper response."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_sensor_update_policy_ids(
            filter="name:'NotReal*'",
            limit=100,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_sensor_update_policy_details_validation_and_success(self):
        """Test v1 policy detail validation and success path."""
        validation_result = self.module.get_sensor_update_policy_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        success_result = self.module.get_sensor_update_policy_details(ids=["policy-1"])

        self.mock_client.command.assert_called_once_with(
            "getSensorUpdatePolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_reveal_sensor_uninstall_token_confirm_required(self):
        """Test reveal uninstall token requires confirm_execution=true."""
        result = self.module.reveal_sensor_uninstall_token(
            confirm_execution=False,
            body=None,
            device_id="MAINTENANCE",
            audit_message=None,
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_reveal_sensor_uninstall_token_success(self):
        """Test reveal uninstall token call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"uninstall_token": "masked"}]},
        }

        result = self.module.reveal_sensor_uninstall_token(
            confirm_execution=True,
            body=None,
            device_id="MAINTENANCE",
            audit_message="test",
        )

        self.mock_client.command.assert_called_once_with(
            "revealUninstallToken",
            body={"device_id": "MAINTENANCE", "audit_message": "test"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uninstall_token"], "masked")

    def test_perform_sensor_update_policies_action_success(self):
        """Test policy action success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.perform_sensor_update_policies_action(
            confirm_execution=True,
            action_name="disable",
            ids=["policy-1"],
            group_id=None,
            action_parameters=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "performSensorUpdatePoliciesAction",
            parameters={"action_name": "disable"},
            body={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_set_sensor_update_policies_precedence_success(self):
        """Test policy precedence success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"updated": 1}]},
        }

        result = self.module.set_sensor_update_policies_precedence(
            confirm_execution=True,
            body=None,
            ids=["policy-1", "policy-2"],
            platform_name="Windows",
        )

        self.mock_client.command.assert_called_once_with(
            "setSensorUpdatePoliciesPrecedence",
            body={"ids": ["policy-1", "policy-2"], "platform_name": "Windows"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["updated"], 1)

    def test_create_sensor_update_policies_success(self):
        """Test create v1 policy success."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.create_sensor_update_policies(
            confirm_execution=True,
            body=None,
            name="Policy V1",
            platform_name="Windows",
            description="created via test",
            build="12345",
            settings=None,
        )

        self.mock_client.command.assert_called_once_with(
            "createSensorUpdatePolicies",
            body={
                "resources": [
                    {
                        "name": "Policy V1",
                        "platform_name": "Windows",
                        "settings": {"build": "12345"},
                        "description": "created via test",
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_update_sensor_update_policies_validation_and_success(self):
        """Test update v1 policy validation and success."""
        validation_result = self.module.update_sensor_update_policies(
            confirm_execution=True,
            body=None,
            id="policy-1",
            name=None,
            description=None,
            build=None,
            settings=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }
        success_result = self.module.update_sensor_update_policies(
            confirm_execution=True,
            body=None,
            id="policy-1",
            name=None,
            description="updated",
            build=None,
            settings={"build": "12346"},
        )

        self.mock_client.command.assert_called_once_with(
            "updateSensorUpdatePolicies",
            body={
                "resources": [
                    {
                        "id": "policy-1",
                        "description": "updated",
                        "settings": {"build": "12346"},
                    }
                ]
            },
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-1")

    def test_delete_sensor_update_policies_success(self):
        """Test delete policy success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.delete_sensor_update_policies(
            confirm_execution=True,
            ids=["policy-1"],
        )

        self.mock_client.command.assert_called_once_with(
            "deleteSensorUpdatePolicies",
            parameters={"ids": ["policy-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-1")

    def test_get_sensor_update_policy_details_v2_success(self):
        """Test get v2 policy details success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-v2"}]},
        }

        result = self.module.get_sensor_update_policy_details_v2(ids=["policy-v2"])

        self.mock_client.command.assert_called_once_with(
            "getSensorUpdatePoliciesV2",
            parameters={"ids": ["policy-v2"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-v2")

    def test_create_sensor_update_policies_v2_success(self):
        """Test create v2 policy success."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "policy-v2"}]},
        }

        result = self.module.create_sensor_update_policies_v2(
            confirm_execution=True,
            body=None,
            name="Policy V2",
            platform_name="Windows",
            description="created via test",
            build="12345",
            scheduler=None,
            show_early_adopter_builds=True,
            uninstall_protection="ENABLED",
            variants=None,
            settings=None,
        )

        self.mock_client.command.assert_called_once_with(
            "createSensorUpdatePoliciesV2",
            body={
                "resources": [
                    {
                        "name": "Policy V2",
                        "platform_name": "Windows",
                        "settings": {
                            "build": "12345",
                            "show_early_adopter_builds": True,
                            "uninstall_protection": "ENABLED",
                        },
                        "description": "created via test",
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "policy-v2")

    def test_update_sensor_update_policies_v2_validation_and_success(self):
        """Test update v2 policy validation and success."""
        validation_result = self.module.update_sensor_update_policies_v2(
            confirm_execution=True,
            body=None,
            id="policy-v2",
            name=None,
            description=None,
            build=None,
            scheduler=None,
            show_early_adopter_builds=None,
            uninstall_protection=None,
            variants=None,
            settings=None,
        )
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "policy-v2"}]},
        }
        success_result = self.module.update_sensor_update_policies_v2(
            confirm_execution=True,
            body=None,
            id="policy-v2",
            name=None,
            description="updated",
            build=None,
            scheduler=None,
            show_early_adopter_builds=False,
            uninstall_protection="DISABLED",
            variants=None,
            settings=None,
        )

        self.mock_client.command.assert_called_once_with(
            "updateSensorUpdatePoliciesV2",
            body={
                "resources": [
                    {
                        "id": "policy-v2",
                        "description": "updated",
                        "settings": {
                            "show_early_adopter_builds": False,
                            "uninstall_protection": "DISABLED",
                        },
                    }
                ]
            },
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "policy-v2")

    def test_query_sensor_update_kernel_distinct_success(self):
        """Test distinct kernel query success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "kernel-1"}]},
        }

        result = self.module.query_sensor_update_kernel_distinct(
            distinct_field="id",
            filter="platform:'windows'",
            limit=10,
            offset=0,
        )

        self.mock_client.command.assert_called_once_with(
            "querySensorUpdateKernelsDistinct",
            parameters={
                "distinct-field": "id",
                "filter": "platform:'windows'",
                "limit": 10,
                "offset": 0,
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "kernel-1")

    def test_query_sensor_update_policy_member_ids_requires_policy_id(self):
        """Test policy member ID query requires policy ID."""
        result = self.module.query_sensor_update_policy_member_ids(
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
