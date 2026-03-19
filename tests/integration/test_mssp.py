"""Integration tests for the MSSP (Flight Control) module."""

from typing import Any

import pytest

from falcon_mcp.modules.mssp import MSSPModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestMSSPIntegration(BaseIntegrationTest):
    """Integration tests for MSSP (Flight Control) with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = MSSPModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_query_mssp_children_operation_name(self):
        result = self.call_method(self.module.query_mssp_children, parameters={"limit": 1})
        self.assert_no_error(result, context="query_mssp_children")
        self.assert_valid_list_response(result, min_length=0, context="query_mssp_children")

    def test_query_mssp_roles_operation_name(self):
        cid_groups = self.call_method(self.module.query_mssp_cid_groups, parameters={"limit": 1})
        self.assert_no_error(cid_groups, context="query_mssp_cid_groups setup")
        self.assert_valid_list_response(cid_groups, min_length=0, context="query_mssp_cid_groups setup")
        if not cid_groups:
            self.skip_with_warning("No CID groups available to validate role query", context="query_mssp_roles")

        cid_group_id = cid_groups[0] if isinstance(cid_groups[0], str) else None
        if not cid_group_id:
            self.skip_with_warning("Could not extract CID group ID for role query validation", context="query_mssp_roles")

        result = self.call_method(self.module.query_mssp_roles, parameters={"cid_group_id": cid_group_id, "limit": 1})
        self.assert_no_error(result, context="query_mssp_roles")
        self.assert_valid_list_response(result, min_length=0, context="query_mssp_roles")

    def test_add_mssp_role_invalid_payload(self):
        result = self.call_method(
            self.module.add_mssp_role,
            confirm_execution=True,
            body={"cid": "invalid"},
        )
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning("Missing required flight-control:write scope for write validation", context="add_mssp_role")
        if status_code in (400, 404, 409, 422):
            return
        self.assert_no_error(result, context="add_mssp_role_invalid_payload")
