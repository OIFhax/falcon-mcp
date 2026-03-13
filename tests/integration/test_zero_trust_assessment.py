"""Integration tests for the Zero Trust Assessment module."""

from typing import Any

import pytest

from falcon_mcp.modules.zero_trust_assessment import ZeroTrustAssessmentModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestZeroTrustAssessmentIntegration(BaseIntegrationTest):
    """Integration tests for Zero Trust Assessment module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Zero Trust Assessment module with a real client."""
        self.module = ZeroTrustAssessmentModule(falcon_client)

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
        """Skip when ZTA scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Zero Trust Assessment integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Zero Trust Assessment service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_aid(record: dict[str, Any]) -> str | None:
        """Extract an AID value from a ZTA result record."""
        for key in ["aid", "id"]:
            value = record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    def test_get_zta_audit_report_operation_name(self):
        """Validate Zero Trust audit report operation name."""
        result = self.call_method(self.module.get_zta_audit_report)
        self._skip_if_scope_or_service_missing(result, "get_zta_audit_report")

        self.assert_no_error(result, context="get_zta_audit_report")
        self.assert_valid_list_response(result, min_length=0, context="get_zta_audit_report")

    def test_search_zta_assessments_by_score_operation_name(self):
        """Validate score-based ZTA search operation."""
        result = self.call_method(
            self.module.search_zta_assessments_by_score,
            filter="score:>=0",
            limit=5,
            after=None,
            sort="score|desc",
        )
        self._skip_if_scope_or_service_missing(result, "search_zta_assessments_by_score")

        self.assert_no_error(result, context="search_zta_assessments_by_score")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_zta_assessments_by_score",
        )

    def test_search_zta_combined_assessments_operation_name(self):
        """Validate combined-assessment ZTA search operation."""
        result = self.call_method(
            self.module.search_zta_combined_assessments,
            filter="updated_timestamp:>'2020-01-01T00:00:00Z'",
            facet=["host"],
            limit=5,
            after=None,
            sort="updated_timestamp.desc",
        )
        self._skip_if_scope_or_service_missing(result, "search_zta_combined_assessments")

        self.assert_no_error(result, context="search_zta_combined_assessments")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_zta_combined_assessments",
        )

    def test_get_zta_assessment_details_with_existing_aid(self):
        """Validate detail retrieval from a discovered ZTA AID."""
        search_result = self.call_method(
            self.module.search_zta_assessments_by_score,
            filter="score:>=0",
            limit=1,
            after=None,
            sort="score|desc",
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "get_zta_assessment_details setup",
        )
        self.assert_no_error(search_result, context="get_zta_assessment_details setup")

        if not search_result:
            search_result = self.call_method(
                self.module.search_zta_combined_assessments,
                filter="updated_timestamp:>'2020-01-01T00:00:00Z'",
                facet=None,
                limit=1,
                after=None,
                sort="updated_timestamp.desc",
            )
            self._skip_if_scope_or_service_missing(
                search_result,
                "get_zta_assessment_details setup fallback",
            )
            self.assert_no_error(
                search_result,
                context="get_zta_assessment_details setup fallback",
            )

        if not search_result:
            self.skip_with_warning(
                "No Zero Trust assessments available to validate detail retrieval",
                context="test_get_zta_assessment_details_with_existing_aid",
            )

        aid = self._extract_aid(search_result[0])
        if not aid:
            self.skip_with_warning(
                "Could not extract AID from Zero Trust assessment search results",
                context="test_get_zta_assessment_details_with_existing_aid",
            )

        result = self.call_method(
            self.module.get_zta_assessment_details,
            ids=[aid],
        )
        self._skip_if_scope_or_service_missing(result, "get_zta_assessment_details")

        self.assert_no_error(result, context="get_zta_assessment_details")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="get_zta_assessment_details",
        )
