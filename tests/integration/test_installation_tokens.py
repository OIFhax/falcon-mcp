"""Integration tests for the Installation Tokens module."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest

from falcon_mcp.modules.installation_tokens import InstallationTokensModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestInstallationTokensIntegration(BaseIntegrationTest):
    """Integration tests for Installation Tokens module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Installation Tokens module with a real client."""
        self.module = InstallationTokensModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        """Extract status code from standardized error responses."""
        if isinstance(result, dict):
            details = result.get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
            nested_results = result.get("results")
            if isinstance(nested_results, list) and nested_results:
                first = nested_results[0]
                if isinstance(first, dict):
                    nested_details = first.get("details", {})
                    if isinstance(nested_details, dict):
                        return nested_details.get("status_code")

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")

        return None

    def _skip_if_scope_or_service_missing(self, result: Any, context: str) -> None:
        """Skip when Installation Tokens scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Installation Tokens integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Installation Tokens service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_token_id(record: dict[str, Any]) -> str | None:
        """Extract token ID from token record."""
        value = record.get("id")
        if isinstance(value, str) and value:
            return value
        return None

    @staticmethod
    def _extract_audit_event_id(record: dict[str, Any]) -> str | None:
        """Extract audit event ID from event record."""
        value = record.get("id")
        if isinstance(value, str) and value:
            return value
        return None

    def test_search_installation_tokens_operation_name(self):
        """Validate installation token search operation name."""
        result = self.call_method(
            self.module.search_installation_tokens,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_installation_tokens")

        if isinstance(result, dict):
            self.assertIn("results", result)
            return

        self.assert_no_error(result, context="search_installation_tokens")
        self.assert_valid_list_response(result, min_length=0, context="search_installation_tokens")

    def test_get_installation_token_customer_settings_operation_name(self):
        """Validate customer settings read operation name."""
        result = self.call_method(self.module.get_installation_token_customer_settings)
        self._skip_if_scope_or_service_missing(result, "get_installation_token_customer_settings")

        self.assert_no_error(result, context="get_installation_token_customer_settings")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="get_installation_token_customer_settings",
        )

    def test_search_installation_token_audit_events_operation_name(self):
        """Validate audit event search operation name."""
        result = self.call_method(
            self.module.search_installation_token_audit_events,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_installation_token_audit_events")

        if isinstance(result, dict):
            self.assertIn("results", result)
            return

        self.assert_no_error(result, context="search_installation_token_audit_events")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_installation_token_audit_events",
        )

    def test_get_installation_token_audit_event_details_with_existing_id(self):
        """Validate audit event detail retrieval from discovered ID."""
        search_result = self.call_method(
            self.module.search_installation_token_audit_events,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "get_installation_token_audit_event_details setup",
        )

        if isinstance(search_result, dict):
            search_result = search_result.get("results", [])

        self.assert_no_error(search_result, context="get_installation_token_audit_event_details setup")

        if not search_result:
            self.skip_with_warning(
                "No installation token audit events available to validate detail retrieval",
                context="test_get_installation_token_audit_event_details_with_existing_id",
            )

        event_id = self._extract_audit_event_id(search_result[0])
        if not event_id:
            self.skip_with_warning(
                "Could not extract installation token audit event ID from search results",
                context="test_get_installation_token_audit_event_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_installation_token_audit_event_details,
            ids=[event_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_installation_token_audit_event_details")

        self.assert_no_error(result, context="get_installation_token_audit_event_details")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="get_installation_token_audit_event_details",
        )

    def test_create_update_delete_installation_token_round_trip(self):
        """Validate create/update/delete token workflow with safe cleanup."""
        label = f"falcon-mcp-integration-{uuid4().hex[:10]}"
        expires_timestamp = (
            datetime.now(timezone.utc) + timedelta(days=30)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        created_token_id: str | None = None
        try:
            create_result = self.call_method(
                self.module.create_installation_token,
                confirm_execution=True,
                label=label,
                expires_timestamp=expires_timestamp,
                type=None,
                body=None,
            )
            self._skip_if_scope_or_service_missing(create_result, "create_installation_token")
            self.assert_no_error(create_result, context="create_installation_token")
            self.assert_valid_list_response(create_result, min_length=1, context="create_installation_token")

            created_token_id = self._extract_token_id(create_result[0])
            if not created_token_id:
                self.skip_with_warning(
                    "Could not extract token ID from create response",
                    context="test_create_update_delete_installation_token_round_trip",
                )

            update_result = self.call_method(
                self.module.update_installation_tokens,
                confirm_execution=True,
                ids=[created_token_id],
                label=f"{label}-updated",
                expires_timestamp=None,
                revoked=None,
                body=None,
                parameters=None,
            )
            self._skip_if_scope_or_service_missing(update_result, "update_installation_tokens")
            self.assert_no_error(update_result, context="update_installation_tokens")
            self.assert_valid_list_response(update_result, min_length=0, context="update_installation_tokens")
        finally:
            if created_token_id:
                delete_result = self.call_method(
                    self.module.delete_installation_tokens,
                    confirm_execution=True,
                    ids=[created_token_id],
                )
                self._skip_if_scope_or_service_missing(delete_result, "delete_installation_tokens")
                self.assert_no_error(delete_result, context="delete_installation_tokens")
