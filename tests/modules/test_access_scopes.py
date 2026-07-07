"""
Tests for the Access Scopes module.
"""

from unittest.mock import patch

from falcon_mcp.modules.access_scopes import AccessScopesModule
from tests.modules.utils.test_modules import TestModules


class TestAccessScopesModule(TestModules):
    """Test cases for the Access Scopes module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(AccessScopesModule)
        self.mock_client.client_id = "client-id"
        self.mock_client.client_secret = "client-secret"
        self.mock_client.base_url = "https://api.example.com"
        self.mock_client.debug = False
        self.mock_client.get_user_agent.return_value = "falcon-mcp/test"

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_query_access_scopes",
            "falcon_list_access_scopes",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        self.assert_resources_registered(["falcon_access_scopes_fql_guide"])

    @patch("falcon_mcp.modules.access_scopes.AccessScopes")
    def test_query_access_scopes_success(self, mock_service_class):
        """Test querying access-scope IDs."""
        service = mock_service_class.return_value
        service.query_access_scopes_external.return_value = {
            "status_code": 200,
            "body": {"resources": ["access-scope-id"]},
        }

        result = self.module.query_access_scopes(
            filter="name:'API Clients'",
            member_cid="child-cid",
            limit=25,
            offset=10,
            sort="name|asc",
        )

        mock_service_class.assert_called_once()
        self.assertEqual(mock_service_class.call_args.kwargs["member_cid"], "child-cid")
        service.query_access_scopes_external.assert_called_once_with(
            parameters={
                "filter": "name:'API Clients'",
                "limit": 25,
                "offset": 10,
                "sort": "name|asc",
            }
        )
        self.assertEqual(result, ["access-scope-id"])

    @patch("falcon_mcp.modules.access_scopes.AccessScopes")
    def test_list_access_scopes_success(self, mock_service_class):
        """Test listing access scopes by ID."""
        service = mock_service_class.return_value
        service.list_access_scopes_external.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "access-scope-id", "name": "API Clients"}]},
        }

        result = self.module.list_access_scopes(ids=["access-scope-id"])

        service.list_access_scopes_external.assert_called_once_with(ids=["access-scope-id"])
        self.assertEqual(result[0]["name"], "API Clients")

    def test_list_access_scopes_validation_error(self):
        """Test access-scope listing requires IDs."""
        result = self.module.list_access_scopes(ids=[])

        self.assertIn("error", result)
        self.mock_client.get_user_agent.assert_not_called()

    @patch("falcon_mcp.modules.access_scopes.AccessScopes")
    def test_forbidden_response_adds_required_scope_hint(self, mock_service_class):
        """Test access-scope 403 responses include the required scope hint."""
        service = mock_service_class.return_value
        service.query_access_scopes_external.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "access denied"}]},
        }

        result = self.module.query_access_scopes()

        self.assertIn("error", result)
        self.assertEqual(result["required_scopes"], ["access-scope:read"])
