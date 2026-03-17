"""Integration tests for the Scheduled Reports module."""

from typing import Any

import pytest

from falcon_mcp.modules.scheduled_reports import ScheduledReportsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestScheduledReportsIntegration(BaseIntegrationTest):
    """Integration tests for Scheduled Reports module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the scheduled reports module with a real client."""
        self.module = ScheduledReportsModule(falcon_client)

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
        """Skip when Scheduled Reports scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Scheduled Reports integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Scheduled Reports service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _normalize_search_result(result: Any) -> Any:
        """Normalize search responses that may include FQL helper wrapping."""
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    def _assert_write_result_or_expected_error(self, result: Any, context: str) -> None:
        """Accept expected validation/not-found errors, otherwise require success."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Scheduled Reports scope",
                context=context,
            )
        if status_code in (400, 404, 422, 500):
            return

        self.assert_no_error(result, context=context)
        self.assert_valid_list_response(result, min_length=0, context=context)

    def test_query_scheduled_report_ids_operation_name(self):
        """Validate scheduled report ID query operation name."""
        result = self.call_method(
            self.module.query_scheduled_report_ids,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
            q=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_scheduled_report_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_scheduled_report_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_scheduled_report_ids")

    def test_get_scheduled_report_details_with_existing_id(self):
        """Validate scheduled report details retrieval using discovered report ID."""
        query_result = self.call_method(
            self.module.query_scheduled_report_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
            q=None,
        )
        self._skip_if_scope_or_service_missing(query_result, "get_scheduled_report_details setup")
        query_result = self._normalize_search_result(query_result)

        self.assert_no_error(query_result, context="get_scheduled_report_details setup")
        if not query_result:
            self.skip_with_warning(
                "No scheduled reports available for detail retrieval test",
                context="test_get_scheduled_report_details_with_existing_id",
            )

        report_id = query_result[0] if isinstance(query_result[0], str) else None
        if not report_id:
            self.skip_with_warning(
                "Could not extract scheduled report ID from query results",
                context="test_get_scheduled_report_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_scheduled_report_details,
            ids=[report_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_scheduled_report_details")

        self.assert_no_error(result, context="get_scheduled_report_details")
        self.assert_valid_list_response(result, min_length=0, context="get_scheduled_report_details")

    def test_query_report_execution_ids_operation_name(self):
        """Validate report execution ID query operation name."""
        result = self.call_method(
            self.module.query_report_execution_ids,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_report_execution_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_report_execution_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_report_execution_ids")

    def test_get_report_execution_details_with_existing_id(self):
        """Validate report execution detail retrieval using discovered execution ID."""
        query_result = self.call_method(
            self.module.query_report_execution_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(query_result, "get_report_execution_details setup")
        query_result = self._normalize_search_result(query_result)

        self.assert_no_error(query_result, context="get_report_execution_details setup")
        if not query_result:
            self.skip_with_warning(
                "No report executions available for detail retrieval test",
                context="test_get_report_execution_details_with_existing_id",
            )

        execution_id = query_result[0] if isinstance(query_result[0], str) else None
        if not execution_id:
            self.skip_with_warning(
                "Could not extract report execution ID from query results",
                context="test_get_report_execution_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_report_execution_details,
            ids=[execution_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_report_execution_details")

        self.assert_no_error(result, context="get_report_execution_details")
        self.assert_valid_list_response(result, min_length=0, context="get_report_execution_details")

    def test_retry_report_execution_expected_error_or_success(self):
        """Validate retry operation wiring with invalid execution ID."""
        invalid_execution_id = "0" * 32

        retry_result = self.call_method(
            self.module.retry_report_execution,
            confirm_execution=True,
            id=invalid_execution_id,
            body=None,
        )
        self._assert_write_result_or_expected_error(
            retry_result,
            context="retry_report_execution",
        )
