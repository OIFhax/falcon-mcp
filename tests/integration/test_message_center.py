"""Integration tests for the Message Center module."""

from typing import Any

import pytest

from falcon_mcp.modules.message_center import MessageCenterModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestMessageCenterIntegration(BaseIntegrationTest):
    """Integration tests for Message Center with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = MessageCenterModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_query_message_center_case_ids_operation_name(self):
        result = self.call_method(self.module.query_message_center_case_ids, parameters={"limit": 1})
        self.assert_no_error(result, context="query_message_center_case_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_message_center_case_ids")

    def test_get_message_center_cases_with_existing_id(self):
        ids = self.call_method(self.module.query_message_center_case_ids, parameters={"limit": 1})
        self.assert_no_error(ids, context="query_message_center_case_ids setup")
        self.assert_valid_list_response(ids, min_length=0, context="query_message_center_case_ids setup")
        if not ids:
            self.skip_with_warning("No Message Center cases available to validate detail retrieval", context="get_message_center_cases")
        result = self.call_method(self.module.get_message_center_cases, ids=[ids[0]])
        self.assert_no_error(result, context="get_message_center_cases")
        self.assert_valid_list_response(result, min_length=0, context="get_message_center_cases")

    def test_create_message_center_case_invalid_payload(self):
        result = self.call_method(
            self.module.create_message_center_case,
            confirm_execution=True,
            body={"title": "", "type": "invalid"},
        )
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning("Missing required message-center:write scope for write validation", context="create_message_center_case")
        if status_code in (400, 404, 409, 422):
            return
        self.assert_no_error(result, context="create_message_center_case_invalid_payload")
