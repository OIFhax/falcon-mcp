"""Integration tests for the Correlation Rules module."""

from typing import Any

import pytest

from falcon_mcp.modules.correlation_rules import CorrelationRulesModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCorrelationRulesIntegration(BaseIntegrationTest):
    """Integration tests for Correlation Rules with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CorrelationRulesModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_search_correlation_rules_v2_operation_name(self):
        result = self.call_method(
            self.module.search_correlation_rules_v2,
            filter=None,
            q=None,
            sort=None,
            offset=0,
            limit=1,
        )
        self.assert_no_error(result, context="search_correlation_rules_v2")
        self.assert_valid_list_response(result, min_length=0, context="search_correlation_rules_v2")

    def test_get_latest_correlation_rule_versions_with_existing_rule(self):
        ids = self.call_method(
            self.module.query_correlation_rule_ids,
            filter=None,
            q=None,
            sort=None,
            offset=0,
            limit=1,
        )
        self.assert_no_error(ids, context="query_correlation_rule_ids")
        self.assert_valid_list_response(ids, min_length=0, context="query_correlation_rule_ids")
        if not ids:
            self.skip_with_warning(
                "No correlation rules available to validate latest version lookup",
                context="get_latest_correlation_rule_versions",
            )
        result = self.call_method(self.module.get_latest_correlation_rule_versions, rule_ids=[ids[0]])
        self.assert_no_error(result, context="get_latest_correlation_rule_versions")
        self.assert_valid_list_response(result, min_length=0, context="get_latest_correlation_rule_versions")

    def test_publish_correlation_rule_version_invalid_id(self):
        result = self.call_method(
            self.module.publish_correlation_rule_version,
            confirm_execution=True,
            id="00000000000000000000000000000000",
        )
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required correlation-rules:write scope for write validation",
                context="publish_correlation_rule_version",
            )
        if status_code in (400, 404, 409, 422):
            return
        self.assert_no_error(result, context="publish_correlation_rule_version_invalid_id")
