"""
Tests for the Installation Tokens module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.installation_tokens import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    InstallationTokensModule,
    WRITE_ANNOTATIONS,
)
from tests.modules.utils.test_modules import TestModules


class TestInstallationTokensModule(TestModules):
    """Test cases for the Installation Tokens module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(InstallationTokensModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_installation_tokens",
            "falcon_get_installation_token_details",
            "falcon_create_installation_token",
            "falcon_update_installation_tokens",
            "falcon_delete_installation_tokens",
            "falcon_search_installation_token_audit_events",
            "falcon_get_installation_token_audit_event_details",
            "falcon_get_installation_token_customer_settings",
            "falcon_update_installation_token_customer_settings",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_installation_tokens_fql_guide",
            "falcon_search_installation_token_audit_fql_guide",
            "falcon_installation_tokens_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_installation_tokens_success(self):
        """Test token search and detail retrieval."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["token-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "token-1", "status": "valid"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_installation_tokens(
            filter="status:'valid'",
            limit=10,
            offset=0,
            sort="created_timestamp|desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "tokens_query")
        self.assertEqual(
            self.mock_client.command.call_args_list[0][1]["parameters"],
            {
                "filter": "status:'valid'",
                "limit": 10,
                "offset": 0,
                "sort": "created_timestamp|desc",
            },
        )
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "tokens_read")
        self.assertEqual(
            self.mock_client.command.call_args_list[1][1]["parameters"],
            {"ids": ["token-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "token-1")

    def test_get_installation_token_details_validation_error(self):
        """Test token detail retrieval requires IDs."""
        result = self.module.get_installation_token_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_installation_token_confirm_required(self):
        """Test token creation requires confirm_execution=true."""
        result = self.module.create_installation_token(
            confirm_execution=False,
            label="token-label",
            expires_timestamp="2026-12-01T00:00:00Z",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_installation_token_success(self):
        """Test token creation call."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "token-1", "status": "valid"}]},
        }

        result = self.module.create_installation_token(
            confirm_execution=True,
            label="token-label",
            expires_timestamp="2026-12-01T00:00:00Z",
            type=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "tokens_create",
            body={
                "label": "token-label",
                "expires_timestamp": "2026-12-01T00:00:00Z",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "token-1")

    def test_update_installation_tokens_confirm_required(self):
        """Test token update requires confirm_execution=true."""
        result = self.module.update_installation_tokens(
            confirm_execution=False,
            ids=["token-1"],
            label="new-label",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_installation_tokens_success(self):
        """Test token update call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "token-1", "label": "new-label"}]},
        }

        result = self.module.update_installation_tokens(
            confirm_execution=True,
            ids=["token-1"],
            label="new-label",
            expires_timestamp=None,
            revoked=None,
            body=None,
            parameters=None,
        )

        self.mock_client.command.assert_called_once_with(
            "tokens_update",
            parameters={"ids": ["token-1"]},
            body={"label": "new-label"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "new-label")

    def test_delete_installation_tokens_confirm_required(self):
        """Test token delete requires confirm_execution=true."""
        result = self.module.delete_installation_tokens(
            confirm_execution=False,
            ids=["token-1"],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_installation_tokens_success(self):
        """Test token delete call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "token-1"}]},
        }

        result = self.module.delete_installation_tokens(
            confirm_execution=True,
            ids=["token-1"],
        )

        self.mock_client.command.assert_called_once_with(
            "tokens_delete",
            parameters={"ids": ["token-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "token-1")

    def test_search_installation_token_audit_events_success(self):
        """Test audit event search and detail retrieval."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["event-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "event-1", "action": "token_create"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_installation_token_audit_events(
            filter="action:'token_create'",
            limit=10,
            offset=0,
            sort="timestamp|desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "audit_events_query")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "audit_events_read")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "event-1")

    def test_get_installation_token_audit_event_details_validation_error(self):
        """Test audit detail retrieval requires IDs."""
        result = self.module.get_installation_token_audit_event_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_installation_token_customer_settings_success(self):
        """Test customer settings read call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"tokens_required": True, "max_active_tokens": 25}]},
        }

        result = self.module.get_installation_token_customer_settings()

        self.mock_client.command.assert_called_once_with("customer_settings_read")
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["tokens_required"])

    def test_update_installation_token_customer_settings_confirm_required(self):
        """Test customer settings update requires confirm_execution=true."""
        result = self.module.update_installation_token_customer_settings(
            confirm_execution=False,
            max_active_tokens=10,
            tokens_required=True,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_installation_token_customer_settings_success(self):
        """Test customer settings update call."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"tokens_required": True, "max_active_tokens": 50}]},
        }

        result = self.module.update_installation_token_customer_settings(
            confirm_execution=True,
            max_active_tokens=50,
            tokens_required=True,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "customer_settings_update",
            body={"max_active_tokens": 50, "tokens_required": True},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["max_active_tokens"], 50)

    def test_search_installation_tokens_has_read_only_annotations(self):
        """Test that search_installation_tokens is read-only annotated."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_installation_tokens", READ_ONLY_ANNOTATIONS)

    def test_create_installation_token_has_write_annotations(self):
        """Test that create_installation_token has write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_create_installation_token", WRITE_ANNOTATIONS)

    def test_delete_installation_tokens_has_destructive_annotations(self):
        """Test that delete_installation_tokens has destructive write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_delete_installation_tokens",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )


if __name__ == "__main__":
    unittest.main()
