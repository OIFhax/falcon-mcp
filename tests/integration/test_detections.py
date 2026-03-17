"""Integration tests for the Detections module."""

from typing import Any

import pytest

from falcon_mcp.modules.detections import DetectionsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDetectionsIntegration(BaseIntegrationTest):
    """Integration tests for Detections module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the detections module with a real client."""
        self.module = DetectionsModule(falcon_client)

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
        """Skip when detections scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Detections integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Detections service unavailable for this tenant/region",
                context=context,
            )

    def _assert_write_result_or_expected_error(self, result: Any, context: str) -> None:
        """Allow expected validation/not-found errors for write endpoint wiring."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Alerts:write scope",
                context=context,
            )
        if status_code in (400, 404, 422, 500):
            return

        self.assert_no_error(result, context=context)
        self.assert_valid_list_response(result, min_length=0, context=context)

    @staticmethod
    def _normalize_search_result(result: Any) -> Any:
        """Normalize search responses that may include FQL helper wrapping."""
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    def test_search_detections_two_step_operation_names(self):
        """Validate two-step search flow (query IDs + details)."""
        result = self.call_method(
            self.module.search_detections,
            filter=None,
            limit=3,
            offset=0,
            q=None,
            sort=None,
            include_hidden=True,
        )
        self._skip_if_scope_or_service_missing(result, "search_detections")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_detections")
        self.assert_valid_list_response(normalized, min_length=0, context="search_detections")

    def test_query_detection_ids_v1_operation_name(self):
        """Validate GetQueriesAlertsV1 operation wiring."""
        result = self.call_method(
            self.module.query_detection_ids_v1,
            filter=None,
            limit=3,
            offset=0,
            q=None,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_detection_ids_v1")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_detection_ids_v1")
        self.assert_valid_list_response(normalized, min_length=0, context="query_detection_ids_v1")

    def test_query_detection_ids_v2_operation_name(self):
        """Validate GetQueriesAlertsV2 operation wiring."""
        result = self.call_method(
            self.module.query_detection_ids_v2,
            filter=None,
            limit=3,
            offset=0,
            q=None,
            sort=None,
            include_hidden=True,
        )
        self._skip_if_scope_or_service_missing(result, "query_detection_ids_v2")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_detection_ids_v2")
        self.assert_valid_list_response(normalized, min_length=0, context="query_detection_ids_v2")

    def test_get_detection_details_v2_with_existing_id(self):
        """Validate PostEntitiesAlertsV2 details retrieval with discovered ID."""
        query_result = self.call_method(
            self.module.query_detection_ids_v2,
            filter=None,
            limit=1,
            offset=0,
            q=None,
            sort=None,
            include_hidden=True,
        )
        self._skip_if_scope_or_service_missing(query_result, "get_detection_details_v2 setup")
        query_result = self._normalize_search_result(query_result)

        self.assert_no_error(query_result, context="get_detection_details_v2 setup")
        if not query_result:
            self.skip_with_warning(
                "No detections available to validate details retrieval",
                context="test_get_detection_details_v2_with_existing_id",
            )

        detection_id = query_result[0] if isinstance(query_result[0], str) else None
        if not detection_id:
            self.skip_with_warning(
                "Could not extract detection ID from query results",
                context="test_get_detection_details_v2_with_existing_id",
            )

        result = self.call_method(
            self.module.get_detection_details_v2,
            composite_ids=[detection_id],
            include_hidden=True,
        )
        self._skip_if_scope_or_service_missing(result, "get_detection_details_v2")

        self.assert_no_error(result, context="get_detection_details_v2")
        self.assert_valid_list_response(result, min_length=0, context="get_detection_details_v2")

    def test_search_detections_combined_operation_name(self):
        """Validate PostCombinedAlertsV1 operation wiring."""
        result = self.call_method(
            self.module.search_detections_combined,
            filter=None,
            limit=3,
            after=None,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_detections_combined")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_detections_combined")
        self.assert_valid_list_response(normalized, min_length=0, context="search_detections_combined")

    def test_aggregate_detections_v2_operation_name(self):
        """Validate PostAggregatesAlertsV2 operation wiring."""
        aggregate_payload = [{"type": "terms", "field": "severity_name", "size": 5}]
        result = self.call_method(
            self.module.aggregate_detections_v2,
            body=aggregate_payload,
            include_hidden=True,
        )
        self._skip_if_scope_or_service_missing(result, "aggregate_detections_v2")

        self.assert_no_error(result, context="aggregate_detections_v2")
        self.assert_valid_list_response(result, min_length=0, context="aggregate_detections_v2")

    def test_update_detections_v2_expected_error_or_success(self):
        """Validate PatchEntitiesAlertsV2 operation wiring with invalid ID."""
        invalid_detection_id = "0" * 32
        result = self.call_method(
            self.module.update_detections_v2,
            confirm_execution=True,
            ids=[invalid_detection_id],
            update_status="in_progress",
            append_comment="falcon-mcp integration test",
        )
        self._assert_write_result_or_expected_error(
            result,
            context="update_detections_v2",
        )

    def test_update_detections_v3_expected_error_or_success(self):
        """Validate PatchEntitiesAlertsV3 operation wiring with invalid composite ID."""
        invalid_composite_id = "d615:ind:" + ("0" * 32)
        result = self.call_method(
            self.module.update_detections_v3,
            confirm_execution=True,
            composite_ids=[invalid_composite_id],
            update_status="in_progress",
            append_comment="falcon-mcp integration test",
            include_hidden=True,
        )
        self._assert_write_result_or_expected_error(
            result,
            context="update_detections_v3",
        )
