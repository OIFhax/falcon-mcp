"""Integration tests for the Response Policies module."""

from typing import Any

import pytest

from falcon_mcp.modules.response_policies import ResponsePoliciesModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestResponsePoliciesIntegration(BaseIntegrationTest):
    """Integration tests for Response Policies module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Response Policies module with a real client."""
        self.module = ResponsePoliciesModule(falcon_client)

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
        """Skip when Response Policies scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Response Policies integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Response Policies service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_policy_id(record: dict[str, Any]) -> str | None:
        """Extract response policy ID from a record."""
        value = record.get("id")
        if isinstance(value, str) and value:
            return value
        return None

    @staticmethod
    def _normalize_search_result(result: Any) -> Any:
        """Normalize search responses that may include FQL helper wrapping."""
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    def test_search_response_policies_operation_name(self):
        """Validate response policy search operation name."""
        result = self.call_method(
            self.module.search_response_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_response_policies")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_response_policies")
        self.assert_valid_list_response(normalized, min_length=0, context="search_response_policies")

    def test_query_response_policy_ids_operation_name(self):
        """Validate response policy ID query operation name."""
        result = self.call_method(
            self.module.query_response_policy_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_response_policy_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_response_policy_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_response_policy_ids")

    def test_get_response_policy_details_with_existing_id(self):
        """Validate policy detail retrieval from discovered policy ID."""
        search_result = self.call_method(
            self.module.search_response_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(search_result, "get_response_policy_details setup")
        search_result = self._normalize_search_result(search_result)

        self.assert_no_error(search_result, context="get_response_policy_details setup")
        if not search_result:
            self.skip_with_warning(
                "No response policies available to validate detail retrieval",
                context="test_get_response_policy_details_with_existing_id",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract response policy ID from search results",
                context="test_get_response_policy_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_response_policy_details,
            ids=[policy_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_response_policy_details")

        self.assert_no_error(result, context="get_response_policy_details")
        self.assert_valid_list_response(result, min_length=0, context="get_response_policy_details")

    def test_search_response_policy_members_with_existing_policy(self):
        """Validate combined policy-member search using a discovered policy ID."""
        search_result = self.call_method(
            self.module.search_response_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "search_response_policy_members setup",
        )
        search_result = self._normalize_search_result(search_result)
        self.assert_no_error(search_result, context="search_response_policy_members setup")

        if not search_result:
            self.skip_with_warning(
                "No response policies available to validate member search",
                context="test_search_response_policy_members_with_existing_policy",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract response policy ID from search results",
                context="test_search_response_policy_members_with_existing_policy",
            )

        result = self.call_method(
            self.module.search_response_policy_members,
            policy_id=policy_id,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_response_policy_members")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_response_policy_members")
        self.assert_valid_list_response(normalized, min_length=0, context="search_response_policy_members")

    def test_query_response_policy_member_ids_with_existing_policy(self):
        """Validate member ID query using a discovered policy ID."""
        search_result = self.call_method(
            self.module.search_response_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "query_response_policy_member_ids setup",
        )
        search_result = self._normalize_search_result(search_result)
        self.assert_no_error(search_result, context="query_response_policy_member_ids setup")

        if not search_result:
            self.skip_with_warning(
                "No response policies available to validate member ID query",
                context="test_query_response_policy_member_ids_with_existing_policy",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract response policy ID from search results",
                context="test_query_response_policy_member_ids_with_existing_policy",
            )

        result = self.call_method(
            self.module.query_response_policy_member_ids,
            policy_id=policy_id,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_response_policy_member_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_response_policy_member_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_response_policy_member_ids")

    def test_perform_response_policies_action_invalid_id_expected_error(self):
        """Validate action operation wiring using invalid policy ID selector."""
        result = self.call_method(
            self.module.perform_response_policies_action,
            confirm_execution=True,
            action_name="disable",
            ids=["00000000000000000000000000000000"],
            group_id=None,
            action_parameters=None,
            body=None,
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Response Policies:write scope for action operation",
                context="perform_response_policies_action",
            )
        if status_code in (400, 404, 422):
            return

        self.assert_no_error(result, context="perform_response_policies_action")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="perform_response_policies_action",
        )

    def test_set_response_policies_precedence_invalid_ids_expected_error(self):
        """Validate precedence operation wiring using invalid policy IDs."""
        result = self.call_method(
            self.module.set_response_policies_precedence,
            confirm_execution=True,
            body=None,
            ids=["00000000000000000000000000000000"],
            platform_name="Windows",
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Response Policies:write scope for precedence operation",
                context="set_response_policies_precedence",
            )
        if status_code in (400, 404, 422):
            return

        self.assert_no_error(result, context="set_response_policies_precedence")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="set_response_policies_precedence",
        )
