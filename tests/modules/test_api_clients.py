"""
Tests for the API Clients module.
"""

from unittest.mock import patch

from falcon_mcp.modules.api_clients import APIClientsModule, WRITE_ANNOTATIONS
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from tests.modules.utils.test_modules import TestModules


class TestAPIClientsModule(TestModules):
    """Test cases for the API Clients module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(APIClientsModule)
        self.mock_client.client_id = "client-id"
        self.mock_client.client_secret = "client-secret"
        self.mock_client.base_url = "https://api.example.com"
        self.mock_client.debug = False
        self.mock_client.get_user_agent.return_value = "falcon-mcp/test"

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_get_accessible_api_client_scopes",
            "falcon_list_api_client_ids",
            "falcon_get_api_clients",
            "falcon_find_api_clients",
            "falcon_update_api_client_scopes",
            "falcon_copy_api_client_scopes_to_matching_clients",
        ]
        self.assert_tools_registered(expected_tools)
        self.assert_tool_annotations(
            "falcon_get_api_clients",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_update_api_client_scopes",
            WRITE_ANNOTATIONS,
        )

    def test_register_resources(self):
        """Test registering resources with the server."""
        self.assert_resources_registered(["falcon_api_clients_usage_guide"])

    @patch("falcon_mcp.modules.api_clients.APIClients")
    def test_list_api_client_ids_success(self, mock_service_class):
        """Test API client ID listing."""
        service = mock_service_class.return_value
        service.get_all_api_client_ids_for_customer.return_value = {
            "status_code": 200,
            "body": {"resources": ["client-1", "client-2"]},
        }

        result = self.module.list_api_client_ids(
            member_cid="child-cid",
            limit=25,
            offset=10,
            sort="name|asc",
        )

        mock_service_class.assert_called_once()
        self.assertEqual(mock_service_class.call_args.kwargs["member_cid"], "child-cid")
        service.get_all_api_client_ids_for_customer.assert_called_once_with(
            parameters={"limit": 25, "offset": 10, "sort": "name|asc"}
        )
        self.assertEqual(result, ["client-1", "client-2"])

    @patch("falcon_mcp.modules.api_clients.APIClients")
    def test_get_api_clients_sanitizes_secret_fields(self, mock_service_class):
        """Test API client retrieval redacts secret-like fields."""
        service = mock_service_class.return_value
        service.get_api_clients.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": "client-1",
                        "name": "Intezer API",
                        "client_secret": "should-not-leak",
                        "scopes": ["api-client-mgmt:read"],
                    }
                ]
            },
        }

        result = self.module.get_api_clients(ids=["client-1"])

        service.get_api_clients.assert_called_once_with(ids=["client-1"])
        self.assertEqual(result[0]["client_secret"], "<redacted>")

    def test_update_api_client_scopes_confirm_required(self):
        """Test scope updates require explicit confirmation."""
        result = self.module.update_api_client_scopes(
            id="client-1",
            scopes=["api-client-mgmt:read"],
            confirm_execution=False,
        )

        self.assertIn("error", result)
        self.mock_client.get_user_agent.assert_not_called()

    @patch("falcon_mcp.modules.api_clients.APIClients")
    def test_update_api_client_scopes_success(self, mock_service_class):
        """Test direct API client scope update."""
        service = mock_service_class.return_value
        service.update_api_client.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "client-1", "scopes": ["api-client-mgmt:read"]}]},
        }

        result = self.module.update_api_client_scopes(
            id="client-1",
            scopes=["api-client-mgmt:read"],
            name="Intezer API",
            description="Managed by Falcon MCP",
            confirm_execution=True,
        )

        service.update_api_client.assert_called_once_with(
            parameters={"ids": "client-1"},
            body={
                "name": "Intezer API",
                "description": "Managed by Falcon MCP",
                "scopes": ["api-client-mgmt:read"],
            },
        )
        self.assertEqual(result[0]["id"], "client-1")

    @patch("falcon_mcp.modules.api_clients.APIClients")
    def test_copy_scopes_filtered_apply_uses_target_scope_list(self, mock_service_class):
        """Test filtered apply removes scopes unavailable in a child CID before update."""
        service = mock_service_class.return_value
        service.get_api_clients.side_effect = [
            {
                "status_code": 200,
                "body": {
                    "resources": [
                        {
                            "id": "source-client",
                            "name": "Intezer XDR",
                            "scopes": ["api-client-mgmt:read", "mssp:read"],
                        }
                    ]
                },
            },
            {
                "status_code": 200,
                "body": {
                    "resources": [
                        {
                            "id": "target-client",
                            "name": "Intezer API",
                            "description": "Existing client",
                            "scopes": [],
                        }
                    ]
                },
            },
        ]
        service.get_accessible_scopes.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "api-client-mgmt:read"}]},
        }
        service.get_all_api_client_ids_for_customer.return_value = {
            "status_code": 200,
            "body": {"resources": ["target-client"]},
        }
        service.update_api_client.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "target-client"}]},
        }

        result = self.module.copy_api_client_scopes_to_matching_clients(
            source_client_id="source-client",
            target_name_contains="Intezer",
            source_member_cid=None,
            target_member_cids=["child-cid"],
            max_clients_per_cid=1000,
            exclude_source_client=True,
            filter_unavailable_scopes=True,
            confirm_execution=True,
        )

        service.update_api_client.assert_called_once_with(
            parameters={"ids": "target-client"},
            body={
                "name": "Intezer API",
                "description": "Existing client",
                "scopes": ["api-client-mgmt:read"],
            },
        )
        target = result["processed"][0]["targets"][0]
        self.assertTrue(target["updated"])
        self.assertEqual(target["new_scope_count"], 1)
        self.assertEqual(target["unavailable_source_scopes"], ["mssp:read"])

    @patch("falcon_mcp.modules.api_clients.APIClients")
    def test_handle_response_adds_required_scope_hint(self, mock_service_class):
        """Test API client 403 responses include the required scope hint."""
        service = mock_service_class.return_value
        service.get_api_clients.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "access denied"}]},
        }

        result = self.module.get_api_clients(ids=["client-1"])

        self.assertIn("error", result)
        self.assertEqual(result["required_scopes"], ["api-client-mgmt:read"])
