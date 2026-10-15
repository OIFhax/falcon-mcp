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

    def test_search_applications_returns_details(self):
        """Validate combined application search returns complete records."""
        result = self.call_method(
            self.module.search_applications,
            filter="name:*'*'",
            limit=5,
        )
        self.assert_no_error(result, context="search_applications")
        self.assert_valid_list_response(result, min_length=0, context="search_applications")
        if self.records(result, context="search_applications"):
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="search_applications",
            )

    def test_search_applications_with_filter(self):
        """Validate an application vendor filter."""
        result = self.call_method(
            self.module.search_applications,
            filter="vendor:'Microsoft Corporation'",
            limit=3,
        )
        self.assert_no_error(result, context="search_applications with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_applications with filter")

    def test_search_applications_with_facet(self):
        """Validate an application host-info facet."""
        result = self.call_method(
            self.module.search_applications,
            filter="name:*'*'",
            facet="host_info",
            limit=3,
        )
        self.assert_no_error(result, context="search_applications with facet")
        self.assert_valid_list_response(result, min_length=0, context="search_applications with facet")

    def test_search_unmanaged_assets_returns_details(self):
        """Validate combined unmanaged-asset search returns complete records."""
        result = self.call_method(self.module.search_unmanaged_assets, limit=5)
        self.assert_no_error(result, context="search_unmanaged_assets")
        self.assert_valid_list_response(result, min_length=0, context="search_unmanaged_assets")
        if self.records(result, context="search_unmanaged_assets"):
            self.assert_search_returns_details(
                result,
                expected_fields=["id"],
                context="search_unmanaged_assets",
            )

    def test_search_unmanaged_assets_with_filter(self):
        """Validate an unmanaged-asset platform filter."""
        result = self.call_method(
            self.module.search_unmanaged_assets,
            filter="platform_name:'Windows'",
            limit=3,
        )
        self.assert_no_error(result, context="search_unmanaged_assets with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_unmanaged_assets with filter")

    def test_search_unmanaged_assets_with_sort(self):
        """Validate unmanaged-asset sorting."""
        result = self.call_method(
            self.module.search_unmanaged_assets,
            sort="last_seen_timestamp.desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_unmanaged_assets with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_unmanaged_assets with sort")

    def test_search_managed_assets_returns_details(self):
        """Validate combined managed-asset search returns complete records."""
        result = self.call_method(self.module.search_managed_assets, limit=5)
        self.assert_no_error(result, context="search_managed_assets")
        self.assert_valid_list_response(result, min_length=0, context="search_managed_assets")
        if self.records(result, context="search_managed_assets"):
            self.assert_search_returns_details(
                result,
                expected_fields=["id"],
                context="search_managed_assets",
            )

    def test_search_managed_assets_with_filter(self):
        """Validate the managed-only encryption-status filter."""
        result = self.call_method(
            self.module.search_managed_assets,
            filter="encryption_status:'Unencrypted'",
            limit=3,
        )
        self.assert_no_error(result, context="search_managed_assets with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_managed_assets with filter")

    def test_search_managed_assets_with_os_security_filter(self):
        """Validate the boolean os_security filter."""
        result = self.call_method(
            self.module.search_managed_assets,
            filter="os_security.credential_guard_status:true",
            limit=3,
        )
        self.assert_no_error(result, context="search_managed_assets os_security filter")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_managed_assets os_security filter",
        )

    def test_operation_names_are_correct(self):
        """Validate that FalconPy operation names are correct.

        If operation names are wrong, the API call will fail with an error.
        """
        # Test combined_applications
        result = self.call_method(self.module.search_applications, filter="name:*'*'", limit=1)
        self.assert_no_error(result, context="combined_applications operation name")

        # Test combined_hosts (unmanaged)
        result = self.call_method(self.module.search_unmanaged_assets, limit=1)
        self.assert_no_error(result, context="combined_hosts operation name")

        # Test combined_hosts (managed)
        result = self.call_method(self.module.search_managed_assets, limit=1)
        self.assert_no_error(result, context="combined_hosts managed operation name")

    # ------------------------------------------------------------------
    # The host.* application filter fields
    # ------------------------------------------------------------------

    def test_application_host_fields_filter(self):
        """`host.hostname` and `host.platform_name` really are filter fields.

        They appear in the applications filter hint and nowhere else in the repo —
        not in the applications guide, whose table has no `host.*` entry at all,
        and `host_info` is a facet rather than a filter field. That made them look
        invented. They are not: both select applications.

        combined_applications rejects an unknown field (see
        test_filter_classification.py), and the bare `hostname` control below shows
        that rejection happening, so the dotted forms coming back clean is the
        fields existing rather than the endpoint being permissive.
        """
        hostname = None
        applications = self.records(
            self.call_method(
                self.module.search_applications,
                filter="name:*'*'",
                facet="host_info",
                limit=20,
            ),
            context="application host fixture",
        )
        for application in applications:
            candidate = (application.get("host") or {}).get("hostname")
            if candidate:
                hostname = candidate
                break
        if not hostname:
            self.skip_with_warning(
                "No application carries a host.hostname",
                context="application host fields",
            )
            return

        self.assert_filter_matches(
            self.module.search_applications,
            f"host.hostname:'{hostname}'",
            predicate=lambda app: (app.get("host") or {}).get("hostname") == hostname,
            predicate_desc=f"application.host.hostname == {hostname!r}",
            note="host.hostname is in the filter hint but absent from the guide.",
            limit=3,
            facet="host_info",
        )

        for value in ("Windows", "Linux", "Mac"):
            self.assert_filter_matches(
                self.module.search_applications,
                f"host.platform_name:'{value}'",
                predicate=lambda app, value=value: (
                    (app.get("host") or {}).get("platform_name") == value
                ),
                predicate_desc=f"application.host.platform_name == {value!r}",
                note="host.platform_name is in the filter hint but absent from the guide.",
                limit=3,
                facet="host_info",
            )

        # Control: the undotted field is rejected, so the clean results above are
        # the dotted fields existing rather than this endpoint accepting anything.
        bare = self.call_method(
            self.module.search_applications, filter=f"hostname:'{hostname}'", limit=1
        )
        assert self.error_dicts(bare), (
            "Bare `hostname` was accepted on search_applications. If unknown fields "
            "no longer 400 here, the host.* results above prove nothing. Got: "
            f"{bare}"
        )
