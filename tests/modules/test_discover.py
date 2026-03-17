"""Tests for the Discover module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.discover import DiscoverModule
from tests.modules.utils.test_modules import TestModules


class TestDiscoverModule(TestModules):
    """Test cases for the Discover module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(DiscoverModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_applications",
            "falcon_query_application_ids",
            "falcon_get_application_details",
            "falcon_search_hosts_combined",
            "falcon_query_host_ids",
            "falcon_get_host_details",
            "falcon_search_hosts",
            "falcon_search_unmanaged_assets",
            "falcon_query_account_ids",
            "falcon_get_account_details",
            "falcon_search_accounts",
            "falcon_query_login_ids",
            "falcon_get_login_details",
            "falcon_search_logins",
            "falcon_query_iot_host_ids",
            "falcon_query_iot_host_ids_v2",
            "falcon_get_iot_host_details",
            "falcon_search_iot_hosts",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_applications_fql_guide",
            "falcon_search_unmanaged_assets_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_applications", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_iot_hosts", READ_ONLY_ANNOTATIONS)

    def test_search_applications_success(self):
        """Test search_applications uses combined_applications operation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "app-1", "name": "Chrome"}]},
        }

        result = self.module.search_applications(
            filter="name:'Chrome'",
            facet="host_info",
            limit=25,
            after="cursor",
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "combined_applications",
            parameters={
                "filter": "name:'Chrome'",
                "facet": "host_info",
                "limit": 25,
                "after": "cursor",
                "sort": "name.asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "app-1")

    def test_query_application_ids_success(self):
        """Test query_application_ids uses query_applications operation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["app-1", "app-2"]},
        }

        result = self.module.query_application_ids(
            filter="vendor:'Microsoft Corporation'",
            limit=10,
            offset=5,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "query_applications",
            parameters={
                "filter": "vendor:'Microsoft Corporation'",
                "limit": 10,
                "offset": 5,
                "sort": "name.asc",
            },
        )
        self.assertEqual(result, ["app-1", "app-2"])

    def test_get_application_details_validation_and_success(self):
        """Test get_application_details validates ids and retrieves data."""
        validation_result = self.module.get_application_details(ids=None)
        self.assertEqual(len(validation_result), 1)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "app-1", "name": "Chrome"}]},
        }
        success_result = self.module.get_application_details(ids=["app-1"])

        self.mock_client.command.assert_called_once_with(
            "get_applications",
            parameters={"ids": ["app-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "app-1")

    def test_search_unmanaged_assets_enforces_unmanaged_filter(self):
        """Test unmanaged asset search always enforces entity_type:'unmanaged'."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "host-1", "hostname": "PC-001"}]},
        }

        result = self.module.search_unmanaged_assets(
            filter="platform_name:'Windows'",
            limit=50,
            after="cursor",
            sort="hostname.asc",
            facet="risk_factors",
        )

        self.mock_client.command.assert_called_once_with(
            "combined_hosts",
            parameters={
                "filter": "entity_type:'unmanaged'+platform_name:'Windows'",
                "limit": 50,
                "after": "cursor",
                "sort": "hostname.asc",
                "facet": "risk_factors",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "host-1")

    def test_search_accounts_two_step_flow(self):
        """Test search_accounts runs query + details workflow."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["acct-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "acct-1", "username": "alice"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_accounts(
            filter="username:'alice'",
            limit=10,
            offset=0,
            sort="username|asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "query_accounts",
            parameters={
                "filter": "username:'alice'",
                "limit": 10,
                "offset": 0,
                "sort": "username|asc",
            },
        )
        self.mock_client.command.assert_any_call(
            "get_accounts",
            parameters={"ids": ["acct-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "acct-1")

    def test_search_logins_two_step_flow(self):
        """Test search_logins runs query + details workflow."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["login-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "login-1"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_logins(
            filter="account_name:'alice'",
            limit=5,
            offset=0,
            sort="login_timestamp|desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "query_logins",
            parameters={
                "filter": "account_name:'alice'",
                "limit": 5,
                "offset": 0,
                "sort": "login_timestamp|desc",
            },
        )
        self.mock_client.command.assert_any_call(
            "get_logins",
            parameters={"ids": ["login-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "login-1")

    def test_search_iot_hosts_two_step_flow(self):
        """Test search_iot_hosts runs v2 query + details workflow."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["iot-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "iot-1"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_iot_hosts(
            filter="device_class:'PLC'",
            limit=10,
            after="cursor",
            sort="hostname|asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.mock_client.command.assert_any_call(
            "query_iot_hostsV2",
            parameters={
                "filter": "device_class:'PLC'",
                "limit": 10,
                "after": "cursor",
                "sort": "hostname|asc",
            },
        )
        self.mock_client.command.assert_any_call(
            "get_iot_hosts",
            parameters={"ids": ["iot-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "iot-1")

    def test_query_iot_host_ids_v1_and_v2(self):
        """Test IoT host ID query operation names."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["iot-1", "iot-2"]},
        }
        v1_result = self.module.query_iot_host_ids(
            filter="device_type:'Camera'",
            limit=20,
            offset=10,
            sort="hostname|asc",
        )
        self.mock_client.command.assert_called_once_with(
            "query_iot_hosts",
            parameters={
                "filter": "device_type:'Camera'",
                "limit": 20,
                "offset": 10,
                "sort": "hostname|asc",
            },
        )
        self.assertEqual(v1_result, ["iot-1", "iot-2"])

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["iot-3"]},
        }
        v2_result = self.module.query_iot_host_ids_v2(
            filter="device_type:'Camera'",
            limit=20,
            after="cursor",
            sort="hostname|asc",
        )
        self.mock_client.command.assert_called_once_with(
            "query_iot_hostsV2",
            parameters={
                "filter": "device_type:'Camera'",
                "limit": 20,
                "after": "cursor",
                "sort": "hostname|asc",
            },
        )
        self.assertEqual(v2_result, ["iot-3"])

    def test_get_host_details_validation(self):
        """Test get_host_details requires IDs."""
        result = self.module.get_host_details(ids=None)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
