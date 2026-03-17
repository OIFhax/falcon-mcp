"""Integration tests for the Incidents module."""

from typing import Any

import pytest

from falcon_mcp.modules.incidents import IncidentsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIncidentsIntegration(BaseIntegrationTest):
    """Integration tests for Incidents module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the incidents module with a real client."""
        self.module = IncidentsModule(falcon_client)

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
        """Skip test when Incidents scope/service is unavailable in tenant/region."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Incidents integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Incidents service unavailable for this tenant/region",
                context=context,
            )

    def _assert_write_result_or_expected_error(self, result: Any, context: str) -> None:
        """Allow expected validation/not-found errors for write endpoint wiring."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Incidents:write scope",
                context=context,
            )
        if status_code in (400, 404, 422, 500):
            return

        self.assert_no_error(result, context=context)
        self.assert_valid_list_response(result, min_length=0, context=context)

    def test_show_crowd_score_operation_name(self):
        """Validate CrowdScore operation wiring."""
        result = self.call_method(self.module.show_crowd_score, limit=5)
        self._skip_if_scope_or_service_missing(result, "show_crowd_score")

        self.assert_no_error(result, context="show_crowd_score")
        assert isinstance(result, dict), "Expected dict response from show_crowd_score"
        assert "average_score" in result, "Expected average_score in response"
        assert "scores" in result, "Expected scores in response"

    def test_query_incident_ids_operation_name(self):
        """Validate QueryIncidents operation wiring."""
        result = self.call_method(
            self.module.query_incident_ids,
            filter=None,
            limit=3,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_incident_ids")

        self.assert_no_error(result, context="query_incident_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_incident_ids")

    def test_search_incidents_returns_details(self):
        """Validate two-step incident search flow."""
        result = self.call_method(self.module.search_incidents, limit=3)
        self._skip_if_scope_or_service_missing(result, "search_incidents")

        self.assert_no_error(result, context="search_incidents")
        self.assert_valid_list_response(result, min_length=0, context="search_incidents")
        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["incident_id"],
                context="search_incidents",
            )

    def test_get_incident_details_with_existing_id(self):
        """Validate GetIncidents details retrieval with discovered incident ID."""
        query_result = self.call_method(
            self.module.query_incident_ids,
            limit=1,
        )
        self._skip_if_scope_or_service_missing(query_result, "get_incident_details setup")

        self.assert_no_error(query_result, context="get_incident_details setup")
        if not query_result:
            self.skip_with_warning(
                "No incidents available to validate detail retrieval",
                context="test_get_incident_details_with_existing_id",
            )

        incident_id = query_result[0] if isinstance(query_result[0], str) else None
        if not incident_id:
            self.skip_with_warning(
                "Could not extract incident ID from query results",
                context="test_get_incident_details_with_existing_id",
            )

        result = self.call_method(self.module.get_incident_details, ids=[incident_id])
        self._skip_if_scope_or_service_missing(result, "get_incident_details")

        self.assert_no_error(result, context="get_incident_details")
        self.assert_valid_list_response(result, min_length=0, context="get_incident_details")

    def test_query_behavior_ids_operation_name(self):
        """Validate QueryBehaviors operation wiring."""
        result = self.call_method(
            self.module.query_behavior_ids,
            filter=None,
            limit=3,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_behavior_ids")

        self.assert_no_error(result, context="query_behavior_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_behavior_ids")

    def test_search_behaviors_returns_details(self):
        """Validate two-step behavior search flow."""
        result = self.call_method(self.module.search_behaviors, limit=3)
        self._skip_if_scope_or_service_missing(result, "search_behaviors")

        self.assert_no_error(result, context="search_behaviors")
        self.assert_valid_list_response(result, min_length=0, context="search_behaviors")
        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["behavior_id"],
                context="search_behaviors",
            )

    def test_get_behavior_details_with_existing_id(self):
        """Validate GetBehaviors details retrieval with discovered behavior ID."""
        query_result = self.call_method(
            self.module.query_behavior_ids,
            limit=1,
        )
        self._skip_if_scope_or_service_missing(query_result, "get_behavior_details setup")

        self.assert_no_error(query_result, context="get_behavior_details setup")
        if not query_result:
            self.skip_with_warning(
                "No behaviors available to validate detail retrieval",
                context="test_get_behavior_details_with_existing_id",
            )

        behavior_id = query_result[0] if isinstance(query_result[0], str) else None
        if not behavior_id:
            self.skip_with_warning(
                "Could not extract behavior ID from query results",
                context="test_get_behavior_details_with_existing_id",
            )

        result = self.call_method(self.module.get_behavior_details, ids=[behavior_id])
        self._skip_if_scope_or_service_missing(result, "get_behavior_details")

        self.assert_no_error(result, context="get_behavior_details")
        self.assert_valid_list_response(result, min_length=0, context="get_behavior_details")

    def test_perform_incident_action_expected_error_or_success(self):
        """Validate PerformIncidentAction wiring with invalid incident ID."""
        invalid_incident_id = "0" * 32
        result = self.call_method(
            self.module.perform_incident_action,
            confirm_execution=True,
            ids=[invalid_incident_id],
            update_status=30,
            add_comment="falcon-mcp integration test",
            update_detects=False,
            overwrite_detects=False,
        )
        self._assert_write_result_or_expected_error(
            result,
            context="perform_incident_action",
        )
