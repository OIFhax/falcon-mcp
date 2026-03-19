"""Integration tests for the MalQuery module."""

from typing import Any

import pytest

from falcon_mcp.modules.malquery import MalQueryModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestMalQueryIntegration(BaseIntegrationTest):
    """Integration tests for MalQuery with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = MalQueryModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_get_malquery_quotas_operation_name(self):
        result = self.call_method(self.module.get_malquery_quotas)
        self.assert_no_error(result, context="get_malquery_quotas")
        self.assert_valid_list_response(result, min_length=0, context="get_malquery_quotas")

    def test_get_malquery_metadata_invalid_hash(self):
        result = self.call_method(self.module.get_malquery_metadata, ids=["0" * 64])
        status_code = self._extract_status_code(result)
        if status_code in (400, 404, 422):
            return
        self.assert_no_error(result, context="get_malquery_metadata_invalid_hash")

    def test_exact_search_malquery_invalid_payload(self):
        result = self.call_method(
            self.module.exact_search_malquery,
            confirm_execution=True,
            body={"patterns": [{"type": "ascii", "value": ""}]},
        )
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required malquery:write scope for write validation",
                context="exact_search_malquery",
            )
        if status_code in (400, 404, 409, 422):
            return
        self.assert_no_error(result, context="exact_search_malquery_invalid_payload")
