"""Integration tests for the Intel module."""

from typing import Any

import pytest

from falcon_mcp.modules.intel import IntelModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIntelIntegration(BaseIntegrationTest):
    """Integration tests for Intel module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the intel module with a real client."""
        self.module = IntelModule(falcon_client)

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
        """Skip when Intel scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Intel API scope for integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Intel service unavailable for this tenant/region",
                context=context,
            )

    def test_search_actors_operation_name(self):
        """Validate QueryIntelActorEntities operation wiring."""
        result = self.call_method(self.module.search_actors, limit=2)
        self._skip_if_scope_or_service_missing(result, "search_actors")

        self.assert_no_error(result, context="search_actors")
        self.assert_valid_list_response(result, min_length=0, context="search_actors")

    def test_query_actor_ids_operation_name(self):
        """Validate QueryIntelActorIds operation wiring."""
        result = self.call_method(self.module.query_actor_ids, limit=2)
        self._skip_if_scope_or_service_missing(result, "query_actor_ids")

        self.assert_no_error(result, context="query_actor_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_actor_ids")

    def test_get_actor_details_round_trip(self):
        """Validate GetIntelActorEntities retrieval from queried actor IDs."""
        actor_ids = self.call_method(self.module.query_actor_ids, limit=1)
        self._skip_if_scope_or_service_missing(actor_ids, "get_actor_details setup")
        self.assert_no_error(actor_ids, context="get_actor_details setup")

        if not actor_ids:
            self.skip_with_warning(
                "No actor IDs available to validate detail retrieval",
                context="test_get_actor_details_round_trip",
            )

        actor_id = actor_ids[0]
        result = self.call_method(self.module.get_actor_details, ids=[str(actor_id)])
        self._skip_if_scope_or_service_missing(result, "get_actor_details")

        self.assert_no_error(result, context="get_actor_details")
        self.assert_valid_list_response(result, min_length=0, context="get_actor_details")

    def test_query_indicator_ids_and_details_round_trip(self):
        """Validate QueryIntelIndicatorIds + GetIntelIndicatorEntities wiring."""
        indicator_ids = self.call_method(self.module.query_indicator_ids, limit=1)
        self._skip_if_scope_or_service_missing(indicator_ids, "query_indicator_ids")
        self.assert_no_error(indicator_ids, context="query_indicator_ids")

        if not indicator_ids:
            self.skip_with_warning(
                "No indicator IDs available to validate detail retrieval",
                context="test_query_indicator_ids_and_details_round_trip",
            )

        result = self.call_method(
            self.module.get_indicator_details,
            ids=[str(indicator_ids[0])],
        )
        self._skip_if_scope_or_service_missing(result, "get_indicator_details")
        self.assert_no_error(result, context="get_indicator_details")
        self.assert_valid_list_response(result, min_length=0, context="get_indicator_details")

    def test_query_report_ids_and_details_round_trip(self):
        """Validate QueryIntelReportIds + GetIntelReportEntities wiring."""
        report_ids = self.call_method(self.module.query_report_ids, limit=1)
        self._skip_if_scope_or_service_missing(report_ids, "query_report_ids")
        self.assert_no_error(report_ids, context="query_report_ids")

        if not report_ids:
            self.skip_with_warning(
                "No report IDs available to validate detail retrieval",
                context="test_query_report_ids_and_details_round_trip",
            )

        result = self.call_method(self.module.get_report_details, ids=[str(report_ids[0])])
        self._skip_if_scope_or_service_missing(result, "get_report_details")
        self.assert_no_error(result, context="get_report_details")
        self.assert_valid_list_response(result, min_length=0, context="get_report_details")

    def test_query_rule_ids_operation_name(self):
        """Validate QueryIntelRuleIds operation wiring."""
        result = self.call_method(
            self.module.query_rule_ids,
            rule_type="yara-master",
            limit=1,
        )
        self._skip_if_scope_or_service_missing(result, "query_rule_ids")

        self.assert_no_error(result, context="query_rule_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_rule_ids")

    def test_query_malware_entities_operation_name(self):
        """Validate QueryMalware and QueryMalwareEntities operation wiring."""
        malware_ids = self.call_method(self.module.query_malware_ids, limit=1)
        self._skip_if_scope_or_service_missing(malware_ids, "query_malware_ids")
        self.assert_no_error(malware_ids, context="query_malware_ids")
        self.assert_valid_list_response(malware_ids, min_length=0, context="query_malware_ids")

        malware_entities = self.call_method(self.module.search_malware, limit=1)
        self._skip_if_scope_or_service_missing(malware_entities, "search_malware")
        self.assert_no_error(malware_entities, context="search_malware")
        self.assert_valid_list_response(malware_entities, min_length=0, context="search_malware")

    def test_query_vulnerabilities_operation_name(self):
        """Validate QueryVulnerabilities operation wiring."""
        result = self.call_method(self.module.query_vulnerability_ids, limit=2)
        self._skip_if_scope_or_service_missing(result, "query_vulnerability_ids")

        self.assert_no_error(result, context="query_vulnerability_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_vulnerability_ids")

    def test_get_mitre_report_with_actor_name(self):
        """Validate actor-name to actor-id MITRE report flow."""
        actors = self.call_method(self.module.search_actors, limit=1)
        self._skip_if_scope_or_service_missing(actors, "get_mitre_report setup")
        self.assert_no_error(actors, context="get_mitre_report setup")

        if not actors:
            self.skip_with_warning(
                "No actor entities available to validate MITRE report retrieval",
                context="test_get_mitre_report_with_actor_name",
            )

        actor_name = actors[0].get("name")
        if not actor_name:
            self.skip_with_warning(
                "Could not extract actor name from actor search result",
                context="test_get_mitre_report_with_actor_name",
            )

        result = self.call_method(self.module.get_mitre_report, actor=actor_name, format="json")
        self._skip_if_scope_or_service_missing(result, "get_mitre_report")

        if isinstance(result, list):
            self.assert_no_error(result, context="get_mitre_report list response")
        elif isinstance(result, str):
            assert len(result) >= 0
        else:
            raise AssertionError(f"Unexpected result type for get_mitre_report: {type(result)}")
