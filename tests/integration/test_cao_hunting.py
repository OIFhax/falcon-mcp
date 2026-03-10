"""Integration tests for the CAO Hunting module."""

from typing import Any

import pytest

from falcon_mcp.modules.cao_hunting import CAOHuntingModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCAOHuntingIntegration(BaseIntegrationTest):
    """Integration tests for CAO Hunting module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the CAO Hunting module with a real client."""
        self.module = CAOHuntingModule(falcon_client)

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
        """Skip when CAO Hunting scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for CAO Hunting integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "CAO Hunting service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_query_id(query_record: dict[str, Any]) -> str | None:
        """Extract intelligence query ID from detail record."""
        for key in ["id", "query_id"]:
            value = query_record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    def test_search_hunting_guides_operation_name(self):
        """Validate search operation names for hunting guides."""
        result = self.call_method(
            self.module.search_hunting_guides,
            filter=None,
            q=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_hunting_guides")

        self.assert_no_error(result, context="search_hunting_guides")
        self.assert_valid_list_response(result, min_length=0, context="search_hunting_guides")

    def test_search_intelligence_queries_operation_name(self):
        """Validate search operation names for intelligence queries."""
        result = self.call_method(
            self.module.search_intelligence_queries,
            filter=None,
            q=None,
            limit=1,
            offset=0,
            sort=None,
            include_translated_content=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_intelligence_queries")

        self.assert_no_error(result, context="search_intelligence_queries")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_intelligence_queries",
        )

    def test_get_intelligence_query_details_with_existing_id(self):
        """Validate detail retrieval from a discovered intelligence query ID."""
        search_result = self.call_method(
            self.module.search_intelligence_queries,
            filter=None,
            q=None,
            limit=1,
            offset=0,
            sort=None,
            include_translated_content=None,
        )
        self._skip_if_scope_or_service_missing(search_result, "get_intelligence_query_details setup")
        self.assert_no_error(search_result, context="get_intelligence_query_details setup")

        if not search_result:
            self.skip_with_warning(
                "No CAO intelligence queries available to validate detail retrieval",
                context="test_get_intelligence_query_details_with_existing_id",
            )

        query_id = self._extract_query_id(search_result[0])
        if not query_id:
            self.skip_with_warning(
                "Could not extract intelligence query ID from search results",
                context="test_get_intelligence_query_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_intelligence_query_details,
            ids=[query_id],
            include_translated_content=None,
        )
        self._skip_if_scope_or_service_missing(result, "get_intelligence_query_details")

        self.assert_no_error(result, context="get_intelligence_query_details")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="get_intelligence_query_details",
        )

