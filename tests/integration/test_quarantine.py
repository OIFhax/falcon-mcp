"""Integration tests for the Quarantine module."""

from typing import Any

import pytest

from falcon_mcp.modules.quarantine import QuarantineModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestQuarantineIntegration(BaseIntegrationTest):
    """Integration tests for Quarantine module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Quarantine module with a real client."""
        self.module = QuarantineModule(falcon_client)

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
        """Skip when Quarantine scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Quarantine integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Quarantine service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_quarantine_id(record: dict[str, Any]) -> str | None:
        """Extract quarantine file ID from record."""
        for key in ["id", "quarantine_file_id"]:
            value = record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    def test_search_quarantine_files_operation_name(self):
        """Validate quarantine search operation name."""
        result = self.call_method(
            self.module.search_quarantine_files,
            filter=None,
            q=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_quarantine_files")

        if isinstance(result, dict):
            self.assertIn("results", result)
            return

        self.assert_no_error(result, context="search_quarantine_files")
        self.assert_valid_list_response(result, min_length=0, context="search_quarantine_files")

    def test_get_quarantine_action_update_count_operation_name(self):
        """Validate action update count operation name."""
        result = self.call_method(
            self.module.get_quarantine_action_update_count,
            filter="state:'quarantined'",
        )
        self._skip_if_scope_or_service_missing(result, "get_quarantine_action_update_count")

        if isinstance(result, dict):
            self.assertIn("results", result)
            return

        self.assert_no_error(result, context="get_quarantine_action_update_count")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="get_quarantine_action_update_count",
        )

    def test_aggregate_quarantine_files_operation_name(self):
        """Validate quarantine aggregation operation name."""
        result = self.call_method(
            self.module.aggregate_quarantine_files,
            body=[{"field": "state", "name": "state", "type": "terms"}],
        )
        self._skip_if_scope_or_service_missing(result, "aggregate_quarantine_files")

        self.assert_no_error(result, context="aggregate_quarantine_files")
        self.assert_valid_list_response(result, min_length=0, context="aggregate_quarantine_files")

    def test_get_quarantine_file_details_with_existing_id(self):
        """Validate detail retrieval from discovered quarantine ID."""
        search_result = self.call_method(
            self.module.search_quarantine_files,
            filter="state:'quarantined'",
            q=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(search_result, "get_quarantine_file_details setup")

        if isinstance(search_result, dict):
            search_result = search_result.get("results", [])

        self.assert_no_error(search_result, context="get_quarantine_file_details setup")

        if not search_result:
            self.skip_with_warning(
                "No quarantine files available to validate detail retrieval",
                context="test_get_quarantine_file_details_with_existing_id",
            )

        quarantine_id = self._extract_quarantine_id(search_result[0])
        if not quarantine_id:
            self.skip_with_warning(
                "Could not extract quarantine file ID from search results",
                context="test_get_quarantine_file_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_quarantine_file_details,
            ids=[quarantine_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_quarantine_file_details")

        self.assert_no_error(result, context="get_quarantine_file_details")
        self.assert_valid_list_response(result, min_length=0, context="get_quarantine_file_details")

    def test_update_quarantine_files_by_query_safe_operation_name(self):
        """Validate update-by-query operation with impossible selector."""
        result = self.call_method(
            self.module.update_quarantine_files_by_query,
            confirm_execution=True,
            action="release",
            filter="device.hostname:'__falcon_mcp_quarantine_no_match__'",
            q=None,
            comment="falcon-mcp integration test no-op",
            body=None,
        )
        self._skip_if_scope_or_service_missing(result, "update_quarantine_files_by_query")

        self.assert_no_error(result, context="update_quarantine_files_by_query")
        self.assert_valid_list_response(result, min_length=0, context="update_quarantine_files_by_query")

    def test_update_quarantine_files_by_ids_invalid_id_expected_error(self):
        """Validate update-by-IDs operation call using an invalid ID."""
        result = self.call_method(
            self.module.update_quarantine_files_by_ids,
            confirm_execution=True,
            action="release",
            ids=["0" * 32],
            comment="falcon-mcp integration test invalid id",
            body=None,
        )
        self._skip_if_scope_or_service_missing(result, "update_quarantine_files_by_ids")

        if isinstance(result, list) and result and isinstance(result[0], dict):
            details = result[0].get("details", {})
            if isinstance(details, dict):
                status_code = details.get("status_code")
                if status_code in (400, 404):
                    return

        self.assert_no_error(result, context="update_quarantine_files_by_ids")
