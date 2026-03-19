"""Integration tests for the Sensor Visibility Exclusions module."""

from typing import Any

import pytest

from falcon_mcp.modules.sensor_visibility_exclusions import SensorVisibilityExclusionsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestSensorVisibilityExclusionsIntegration(BaseIntegrationTest):
    """Integration tests for Sensor Visibility Exclusions module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the module with a real client."""
        self.module = SensorVisibilityExclusionsModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
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
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Sensor Visibility Exclusions integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Sensor Visibility Exclusions service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _normalize_search_result(result: Any) -> Any:
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    @staticmethod
    def _extract_exclusion_id(record: dict[str, Any]) -> str | None:
        value = record.get("id")
        if isinstance(value, str) and value:
            return value
        return None

    def test_search_sensor_visibility_exclusions_operation_name(self):
        result = self.call_method(
            self.module.search_sensor_visibility_exclusions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_sensor_visibility_exclusions")
        normalized = self._normalize_search_result(result)
        self.assert_no_error(normalized, context="search_sensor_visibility_exclusions")
        self.assert_valid_list_response(normalized, min_length=0, context="search_sensor_visibility_exclusions")

    def test_query_sensor_visibility_exclusion_ids_operation_name(self):
        result = self.call_method(
            self.module.query_sensor_visibility_exclusion_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_sensor_visibility_exclusion_ids")
        normalized = self._normalize_search_result(result)
        self.assert_no_error(normalized, context="query_sensor_visibility_exclusion_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_sensor_visibility_exclusion_ids")

    def test_get_sensor_visibility_exclusion_details_with_existing_id(self):
        search_result = self.call_method(
            self.module.search_sensor_visibility_exclusions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(search_result, "get_sensor_visibility_exclusion_details setup")
        search_result = self._normalize_search_result(search_result)
        self.assert_no_error(search_result, context="get_sensor_visibility_exclusion_details setup")
        if not search_result:
            self.skip_with_warning(
                "No sensor visibility exclusions available to validate detail retrieval",
                context="test_get_sensor_visibility_exclusion_details_with_existing_id",
            )
        exclusion_id = self._extract_exclusion_id(search_result[0])
        if not exclusion_id:
            self.skip_with_warning(
                "Could not extract sensor visibility exclusion ID from search results",
                context="test_get_sensor_visibility_exclusion_details_with_existing_id",
            )
        result = self.call_method(
            self.module.get_sensor_visibility_exclusion_details,
            ids=[exclusion_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_sensor_visibility_exclusion_details")
        self.assert_no_error(result, context="get_sensor_visibility_exclusion_details")
        self.assert_valid_list_response(result, min_length=0, context="get_sensor_visibility_exclusion_details")

    def test_update_sensor_visibility_exclusions_invalid_id_expected_error(self):
        result = self.call_method(
            self.module.update_sensor_visibility_exclusions,
            confirm_execution=True,
            id="00000000000000000000000000000000",
            comment="falcon-mcp integration probe",
            groups=["all"],
            is_descendant_process=False,
            value="\\\\__falcon_mcp_probe__\\\\never-run.invalid",
            body=None,
        )
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required sensor-visibility-exclusions:write scope for update operation",
                context="update_sensor_visibility_exclusions",
            )
        if status_code in (400, 404, 422):
            return
        self.assert_no_error(result, context="update_sensor_visibility_exclusions")
        self.assert_valid_list_response(result, min_length=0, context="update_sensor_visibility_exclusions")

    def test_delete_sensor_visibility_exclusions_invalid_id_expected_error(self):
        result = self.call_method(
            self.module.delete_sensor_visibility_exclusions,
            confirm_execution=True,
            ids=["00000000000000000000000000000000"],
            comment="falcon-mcp integration probe",
        )
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required sensor-visibility-exclusions:write scope for delete operation",
                context="delete_sensor_visibility_exclusions",
            )
        if status_code in (400, 404, 422):
            return
        self.assert_no_error(result, context="delete_sensor_visibility_exclusions")
        self.assert_valid_list_response(result, min_length=0, context="delete_sensor_visibility_exclusions")
