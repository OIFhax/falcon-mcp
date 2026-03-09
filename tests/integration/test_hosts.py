"""Integration tests for the Hosts module."""

from typing import Any

import pytest

from falcon_mcp.modules.hosts import HostsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestHostsIntegration(BaseIntegrationTest):
    """Integration tests for Hosts module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the hosts module with a real client."""
        self.module = HostsModule(falcon_client)

    @staticmethod
    def _get_status_code(result: Any) -> int | None:
        """Extract status code from standardized error responses."""
        if isinstance(result, dict):
            details = result.get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
        if isinstance(result, list) and result and isinstance(result[0], dict):
            details = result[0].get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
        return None

    def _skip_if_scope_missing(self, result: Any, scope: str, context: str) -> None:
        """Skip integration assertions when API credentials are missing a scope."""
        if self._get_status_code(result) == 403:
            self.skip_with_warning(
                f"Missing required scope for {scope} integration test",
                context=context,
            )

    def test_search_hosts_returns_details(self):
        """Validate hosts search returns full host details."""
        result = self.call_method(self.module.search_hosts, limit=5)

        self.assert_no_error(result, context="search_hosts")
        self.assert_valid_list_response(result, min_length=0, context="search_hosts")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["device_id", "hostname"],
                context="search_hosts",
            )

    def test_search_host_groups_returns_details(self):
        """Validate host group search returns full host group details."""
        result = self.call_method(
            self.module.search_host_groups,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "Host Groups:read", "search_host_groups")

        self.assert_no_error(result, context="search_host_groups")
        self.assert_valid_list_response(result, min_length=0, context="search_host_groups")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="search_host_groups",
            )

    def test_search_migrations_returns_details(self):
        """Validate migration search returns full migration details."""
        result = self.call_method(
            self.module.search_migrations,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "Host Migration:read", "search_migrations")

        self.assert_no_error(result, context="search_migrations")
        self.assert_valid_list_response(result, min_length=0, context="search_migrations")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id"],
                context="search_migrations",
            )

    def test_search_host_migrations_returns_details(self):
        """Validate host migration search returns full host migration details."""
        migrations = self.call_method(
            self.module.search_migrations,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(migrations, "Host Migration:read", "search_host_migrations setup")
        self.assert_no_error(migrations, context="search_host_migrations setup")

        if not migrations:
            self.skip_with_warning(
                "No migration jobs available to test host migration search",
                context="search_host_migrations",
            )

        migration_id = self.get_first_id(migrations, id_field="id")
        if not migration_id:
            self.skip_with_warning(
                "Could not extract migration ID from search_migrations results",
                context="search_host_migrations",
            )

        result = self.call_method(
            self.module.search_host_migrations,
            migration_id=migration_id,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "Host Migration:read", "search_host_migrations")

        self.assert_no_error(result, context="search_host_migrations")
        self.assert_valid_list_response(result, min_length=0, context="search_host_migrations")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id"],
                context="search_host_migrations",
            )

    def test_operation_names_are_correct(self):
        """Validate core operation names by executing minimal read queries."""
        hosts_result = self.call_method(self.module.search_hosts, limit=1)
        self.assert_no_error(hosts_result, context="hosts operation names")

        host_groups_result = self.call_method(
            self.module.search_host_groups,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(
            host_groups_result,
            "Host Groups:read",
            "host group operation names",
        )
        self.assert_no_error(host_groups_result, context="host group operation names")

        migrations_result = self.call_method(
            self.module.search_migrations,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(
            migrations_result,
            "Host Migration:read",
            "host migration operation names",
        )
        self.assert_no_error(migrations_result, context="host migration operation names")
