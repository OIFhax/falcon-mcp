"""Integration tests for the Spotlight module."""

from typing import Any

import pytest

from falcon_mcp.modules.spotlight import SpotlightModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestSpotlightIntegration(BaseIntegrationTest):
    """Integration tests for Spotlight module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the spotlight module with a real client."""
        self.module = SpotlightModule(falcon_client)

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
        """Skip when Spotlight scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Spotlight integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Spotlight service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _normalize_search_result(result: Any) -> Any:
        """Normalize search responses that may include FQL helper wrapping."""
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    def test_search_vulnerabilities_operation_name(self):
        """Validate combined vulnerability search operation name."""
        result = self.call_method(
            self.module.search_vulnerabilities,
            filter="status:'open'",
            limit=5,
            offset=0,
            sort=None,
            after=None,
            facet=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_vulnerabilities")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_vulnerabilities")
        self.assert_valid_list_response(normalized, min_length=0, context="search_vulnerabilities")

    def test_query_vulnerability_ids_operation_name(self):
        """Validate vulnerability ID query operation name."""
        result = self.call_method(
            self.module.query_vulnerability_ids,
            filter="status:'open'",
            limit=5,
            offset=0,
            sort=None,
            after=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_vulnerability_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_vulnerability_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_vulnerability_ids")

    def test_get_vulnerability_details_with_existing_id(self):
        """Validate vulnerability detail retrieval using discovered vulnerability ID."""
        query_result = self.call_method(
            self.module.query_vulnerability_ids,
            filter="status:'open'",
            limit=1,
            offset=0,
            sort=None,
            after=None,
        )
        self._skip_if_scope_or_service_missing(query_result, "get_vulnerability_details setup")
        query_result = self._normalize_search_result(query_result)

        self.assert_no_error(query_result, context="get_vulnerability_details setup")
        if not query_result:
            self.skip_with_warning(
                "No vulnerabilities available to validate detail retrieval",
                context="test_get_vulnerability_details_with_existing_id",
            )

        vulnerability_id = query_result[0] if isinstance(query_result[0], str) else None
        if not vulnerability_id:
            self.skip_with_warning(
                "Could not extract vulnerability ID from query results",
                context="test_get_vulnerability_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_vulnerability_details,
            ids=[vulnerability_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_vulnerability_details")

        self.assert_no_error(result, context="get_vulnerability_details")
        self.assert_valid_list_response(result, min_length=0, context="get_vulnerability_details")

    def test_get_remediation_details_expected_error_or_success(self):
        """Validate remediation operation wiring with invalid remediation ID."""
        invalid_remediation_id = "0" * 32

        remediation_v1_result = self.call_method(
            self.module.get_remediation_details,
            ids=[invalid_remediation_id],
        )
        status_code_v1 = self._extract_status_code(remediation_v1_result)
        if status_code_v1 == 403:
            self.skip_with_warning(
                "Missing required API scope for Spotlight remediation retrieval",
                context="get_remediation_details",
            )
        if status_code_v1 not in (None, 400, 404, 422):
            self.assert_no_error(remediation_v1_result, context="get_remediation_details")
            self.assert_valid_list_response(
                remediation_v1_result,
                min_length=0,
                context="get_remediation_details",
            )

        remediation_v2_result = self.call_method(
            self.module.get_remediation_details_v2,
            ids=[invalid_remediation_id],
        )
        status_code_v2 = self._extract_status_code(remediation_v2_result)
        if status_code_v2 == 403:
            self.skip_with_warning(
                "Missing required API scope for Spotlight remediation retrieval",
                context="get_remediation_details_v2",
            )
        if status_code_v2 not in (None, 400, 404, 422):
            self.assert_no_error(remediation_v2_result, context="get_remediation_details_v2")
            self.assert_valid_list_response(
                remediation_v2_result,
                min_length=0,
                context="get_remediation_details_v2",
            )
