"""Integration tests for the Discover module."""

from typing import Any

import pytest

from falcon_mcp.modules.discover import DiscoverModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDiscoverIntegration(BaseIntegrationTest):
    """Integration tests for Discover module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the discover module with a real client."""
        self.module = DiscoverModule(falcon_client)

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
        """Skip when Discover scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Discover integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Discover service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _normalize_search_result(result: Any) -> Any:
        """Normalize search responses that may include FQL helper wrapping."""
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    def test_search_applications_operation_name(self):
        """Validate combined_applications operation wiring."""
        result = self.call_method(
            self.module.search_applications,
            filter="name:*'*'",
            limit=5,
            after=None,
            sort=None,
            facet=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_applications")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_applications")
        self.assert_valid_list_response(normalized, min_length=0, context="search_applications")

    def test_query_application_ids_operation_name(self):
        """Validate query_applications operation wiring."""
        result = self.call_method(
            self.module.query_application_ids,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_application_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_application_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_application_ids")

    def test_get_application_details_with_existing_id(self):
        """Validate get_applications details retrieval with discovered ID."""
        query_result = self.call_method(
            self.module.query_application_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(query_result, "get_application_details setup")
        query_result = self._normalize_search_result(query_result)

        self.assert_no_error(query_result, context="get_application_details setup")
        if not query_result:
            self.skip_with_warning(
                "No applications available to validate detail retrieval",
                context="test_get_application_details_with_existing_id",
            )

        application_id = query_result[0] if isinstance(query_result[0], str) else None
        if not application_id:
            self.skip_with_warning(
                "Could not extract application ID from query results",
                context="test_get_application_details_with_existing_id",
            )

        result = self.call_method(self.module.get_application_details, ids=[application_id])
        self._skip_if_scope_or_service_missing(result, "get_application_details")

        self.assert_no_error(result, context="get_application_details")
        self.assert_valid_list_response(result, min_length=0, context="get_application_details")

    def test_search_unmanaged_assets_operation_name(self):
        """Validate combined_hosts operation wiring for unmanaged host search."""
        result = self.call_method(
            self.module.search_unmanaged_assets,
            filter=None,
            limit=5,
            after=None,
            sort=None,
            facet=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_unmanaged_assets")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_unmanaged_assets")
        self.assert_valid_list_response(normalized, min_length=0, context="search_unmanaged_assets")

    def test_query_account_ids_operation_name(self):
        """Validate query_accounts operation wiring."""
        result = self.call_method(
            self.module.query_account_ids,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_account_ids")

        self.assert_no_error(result, context="query_account_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_account_ids")

    def test_query_login_ids_operation_name(self):
        """Validate query_logins operation wiring."""
        result = self.call_method(
            self.module.query_login_ids,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_login_ids")

        self.assert_no_error(result, context="query_login_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_login_ids")

    def test_query_iot_host_ids_v2_operation_name(self):
        """Validate query_iot_hostsV2 operation wiring."""
        result = self.call_method(
            self.module.query_iot_host_ids_v2,
            filter=None,
            limit=5,
            after=None,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_iot_host_ids_v2")

        self.assert_no_error(result, context="query_iot_host_ids_v2")
        self.assert_valid_list_response(result, min_length=0, context="query_iot_host_ids_v2")
