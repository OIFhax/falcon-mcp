"""Integration tests for the Case Management module."""

from typing import Any

import pytest

from falcon_mcp.modules.case_management import CaseManagementModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCaseManagementIntegration(BaseIntegrationTest):
    """Integration tests for Case Management with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = CaseManagementModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_query_case_management_case_ids(self):
        result = self.call_method(
            self.module.case_management_queries_cases_get_v1,
            parameters={"limit": 1},
        )
        self.assert_no_error(result, context="queries_cases_get_v1")
        self.assert_valid_list_response(result, min_length=0, context="queries_cases_get_v1")

    def test_case_management_fields_round_trip(self):
        ids = self.call_method(
            self.module.case_management_queries_fields_get_v1,
            parameters={"limit": 1},
        )
        self.assert_no_error(ids, context="queries_fields_get_v1 setup")
        self.assert_valid_list_response(ids, min_length=0, context="queries_fields_get_v1 setup")
        if not ids:
            self.skip_with_warning(
                "No Case Management fields available to validate detail retrieval",
                context="entities_fields_get_v1",
            )
        result = self.call_method(
            self.module.case_management_entities_fields_get_v1,
            parameters={"ids": [ids[0]]},
        )
        self.assert_no_error(result, context="entities_fields_get_v1")
        self.assert_valid_list_response(result, min_length=0, context="entities_fields_get_v1")

    def test_case_management_cases_round_trip(self):
        ids = self.call_method(
            self.module.case_management_queries_cases_get_v1,
            parameters={"limit": 1},
        )
        self.assert_no_error(ids, context="queries_cases_get_v1 setup")
        self.assert_valid_list_response(ids, min_length=0, context="queries_cases_get_v1 setup")
        if not ids:
            self.skip_with_warning(
                "No Case Management cases available to validate detail retrieval",
                context="entities_cases_post_v2",
            )
        result = self.call_method(
            self.module.case_management_entities_cases_post_v2,
            body={"ids": [ids[0]]},
        )
        self.assert_no_error(result, context="entities_cases_post_v2")
        self.assert_valid_list_response(result, min_length=0, context="entities_cases_post_v2")

    def test_case_management_invalid_write_payload(self):
        result = self.call_method(
            self.module.case_management_entities_case_tags_post_v1,
            confirm_execution=True,
            body={
                "case_id": "00000000-0000-0000-0000-000000000000",
                "tags": ["falcon-mcp-integration-test"],
            },
        )
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required case-templates:write scope for write validation",
                context="entities_case_tags_post_v1",
            )
        if status_code in (400, 404, 409, 422):
            return
        self.assert_no_error(result, context="entities_case_tags_post_v1 invalid payload")
