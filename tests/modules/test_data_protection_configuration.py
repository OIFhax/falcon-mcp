"""
Tests for the Data Protection Configuration module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.data_protection_configuration import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    DataProtectionConfigurationModule,
)
from tests.modules.utils.test_modules import TestModules


class TestDataProtectionConfigurationModule(TestModules):
    """Test cases for the Data Protection Configuration module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DataProtectionConfigurationModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_query_data_protection_resources",
            "falcon_get_data_protection_resources",
            "falcon_create_data_protection_resource",
            "falcon_update_data_protection_resource",
            "falcon_delete_data_protection_resources",
            "falcon_query_data_protection_policy_ids",
            "falcon_get_data_protection_policies",
            "falcon_create_data_protection_policy",
            "falcon_update_data_protection_policy",
            "falcon_delete_data_protection_policies",
            "falcon_set_data_protection_policy_precedence",
            "falcon_query_data_protection_classification_ids",
            "falcon_get_data_protection_classifications",
            "falcon_create_data_protection_classification",
            "falcon_update_data_protection_classifications",
            "falcon_delete_data_protection_classifications",
            "falcon_query_data_protection_content_pattern_ids",
            "falcon_get_data_protection_content_patterns",
            "falcon_create_data_protection_content_pattern",
            "falcon_update_data_protection_content_pattern",
            "falcon_delete_data_protection_content_patterns",
            "falcon_query_data_protection_cloud_application_ids",
            "falcon_get_data_protection_cloud_applications",
            "falcon_create_data_protection_cloud_application",
            "falcon_update_data_protection_cloud_application",
            "falcon_delete_data_protection_cloud_applications",
            "falcon_query_data_protection_enterprise_account_ids",
            "falcon_get_data_protection_enterprise_accounts",
            "falcon_create_data_protection_enterprise_account",
            "falcon_update_data_protection_enterprise_account",
            "falcon_delete_data_protection_enterprise_accounts",
            "falcon_query_data_protection_file_type_ids",
            "falcon_get_data_protection_file_types",
            "falcon_query_data_protection_sensitivity_label_ids",
            "falcon_get_data_protection_sensitivity_labels",
            "falcon_create_data_protection_sensitivity_label",
            "falcon_delete_data_protection_sensitivity_labels",
            "falcon_query_data_protection_local_application_group_ids",
            "falcon_get_data_protection_local_application_groups",
            "falcon_create_data_protection_local_application_group",
            "falcon_update_data_protection_local_application_group",
            "falcon_delete_data_protection_local_application_groups",
            "falcon_query_data_protection_local_application_ids",
            "falcon_get_data_protection_local_applications",
            "falcon_create_data_protection_local_application",
            "falcon_update_data_protection_local_application",
            "falcon_delete_data_protection_local_applications",
            "falcon_query_data_protection_web_location_ids",
            "falcon_get_data_protection_web_locations",
            "falcon_create_data_protection_web_location",
            "falcon_update_data_protection_web_location",
            "falcon_delete_data_protection_web_locations",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_data_protection_configuration_guide",
            "falcon_data_protection_configuration_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_query_data_protection_resources", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_data_protection_policy", WRITE_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_create_data_protection_cloud_application",
            WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_delete_data_protection_policies",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_delete_data_protection_web_locations",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_query_policy_ids_success(self):
        """Test Data Protection policy ID query."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["policy-1"]},
        }

        result = self.module.query_data_protection_policy_ids(
            platform_name="win",
            filter="name:'*production*'",
            limit=50,
            offset=0,
            sort="precedence.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "queries_policy_get_v2",
            parameters={
                "platform_name": "win",
                "filter": "name:'*production*'",
                "limit": 50,
                "offset": 0,
                "sort": "precedence.asc",
            },
        )
        self.assertEqual(result, ["policy-1"])

    def test_get_data_protection_resources_requires_ids(self):
        """Test generic get requires IDs."""
        result = self.module.get_data_protection_resources(
            resource_type="classification",
            ids=None,
            parameters=None,
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_policy_confirm_required(self):
        """Test policy creation requires confirm_execution=true."""
        result = self.module.create_data_protection_policy(
            confirm_execution=False,
            platform_name="win",
            body=None,
            name="Windows DLP Policy",
            description="test",
            policy_properties={"enable_content_inspection": True},
            precedence=1,
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_policy_success(self):
        """Test policy creation body construction."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "policy-1"}]},
        }

        result = self.module.create_data_protection_policy(
            confirm_execution=True,
            platform_name="win",
            body=None,
            name="Windows DLP Policy",
            description="created via test",
            policy_properties={
                "enable_content_inspection": True,
                "enable_network_inspection": True,
                "min_confidence_level": "medium",
            },
            precedence=1,
        )

        self.mock_client.command.assert_called_once_with(
            "entities_policy_post_v2",
            parameters={"platform_name": "win"},
            body={
                "resources": [
                    {
                        "name": "Windows DLP Policy",
                        "description": "created via test",
                        "policy_properties": {
                            "enable_content_inspection": True,
                            "enable_network_inspection": True,
                            "min_confidence_level": "medium",
                        },
                        "precedence": 1,
                    }
                ]
            },
        )
        self.assertEqual(result[0]["id"], "policy-1")

    def test_create_content_pattern_success(self):
        """Test content pattern creation maps to documented operation."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "pattern-1"}]},
        }

        result = self.module.create_data_protection_content_pattern(
            confirm_execution=True,
            body=None,
            name="SSN Pattern",
            category="pii",
            description="test pattern",
            example="123-45-6789",
            min_match_threshold=3,
            regexes=[r"\b\d{3}-\d{2}-\d{4}\b"],
            region="us",
        )

        self.mock_client.command.assert_called_once_with(
            "entities_content_pattern_create",
            body={
                "name": "SSN Pattern",
                "category": "pii",
                "description": "test pattern",
                "example": "123-45-6789",
                "min_match_threshold": 3,
                "regexes": [r"\b\d{3}-\d{2}-\d{4}\b"],
                "region": "us",
            },
        )
        self.assertEqual(result[0]["id"], "pattern-1")

    def test_delete_file_type_unsupported(self):
        """Test unsupported write resource types produce a clear error."""
        with self.assertRaises(ValueError):
            self.module.delete_data_protection_resources(
                confirm_execution=True,
                resource_type="file_type",
                ids=["file-type-1"],
                parameters=None,
            )

    def test_full_configuration_query_helpers(self):
        """Test read helpers for all non-policy Data Protection resource families."""
        query_expectations = [
            (
                self.module.query_data_protection_cloud_application_ids,
                "queries_cloud_application_get_v2",
                {},
            ),
            (
                self.module.query_data_protection_enterprise_account_ids,
                "queries_enterprise_account_get_v2",
                {},
            ),
            (
                self.module.query_data_protection_file_type_ids,
                "queries_file_type_get_v2",
                {},
            ),
            (
                self.module.query_data_protection_sensitivity_label_ids,
                "queries_sensitivity_label_get_v2",
                {},
            ),
            (
                self.module.query_data_protection_local_application_group_ids,
                "queries_local_application_group_get",
                {},
            ),
            (
                self.module.query_data_protection_local_application_ids,
                "queries_local_application_get",
                {},
            ),
            (
                self.module.query_data_protection_web_location_ids,
                "queries_web_location_get_v2",
                {"type": "custom"},
            ),
        ]

        for helper, operation, kwargs in query_expectations:
            with self.subTest(operation=operation):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = {
                    "status_code": 200,
                    "body": {"resources": ["id-1"]},
                }
                result = helper(
                    filter="name:'*example*'",
                    limit=10,
                    offset=0,
                    sort="name.asc",
                    **kwargs,
                )
                expected_parameters = {
                    "filter": "name:'*example*'",
                    "limit": 10,
                    "offset": 0,
                    "sort": "name.asc",
                }
                expected_parameters.update({k: v for k, v in kwargs.items() if v is not None})
                self.mock_client.command.assert_called_once_with(
                    operation,
                    parameters=expected_parameters,
                )
                self.assertEqual(result, ["id-1"])

    def test_full_configuration_write_helpers(self):
        """Test write helpers for the remaining Data Protection resource families."""
        create_expectations = [
            (
                self.module.create_data_protection_cloud_application,
                "entities_cloud_application_create",
            ),
            (
                self.module.create_data_protection_enterprise_account,
                "entities_enterprise_account_create",
            ),
            (
                self.module.create_data_protection_sensitivity_label,
                "entities_sensitivity_label_create_v2",
            ),
            (
                self.module.create_data_protection_local_application_group,
                "entities_local_application_group_create",
            ),
            (
                self.module.create_data_protection_local_application,
                "entities_local_application_create",
            ),
            (
                self.module.create_data_protection_web_location,
                "entities_web_location_create_v2",
            ),
        ]

        for helper, operation in create_expectations:
            with self.subTest(operation=operation):
                self.mock_client.command.reset_mock()
                self.mock_client.command.return_value = {
                    "status_code": 201,
                    "body": {"resources": [{"id": "created-1"}]},
                }
                result = helper(confirm_execution=True, body={"name": "Example"})
                self.mock_client.command.assert_called_once_with(
                    operation,
                    body={"name": "Example"},
                )
                self.assertEqual(result[0]["id"], "created-1")

    def test_patch_helper_requires_id(self):
        """Test resource patch helpers require IDs before attempting writes."""
        result = self.module.update_data_protection_web_location(
            confirm_execution=True,
            id=None,
            body={"name": "Example"},
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
