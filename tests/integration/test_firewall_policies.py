"""Integration tests for the Firewall Policies module."""

from typing import Any

import pytest

from falcon_mcp.modules.firewall_policies import FirewallPoliciesModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestFirewallPoliciesIntegration(BaseIntegrationTest):
    """Integration tests for Firewall Policies module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Firewall Policies module with a real client."""
        self.module = FirewallPoliciesModule(falcon_client)

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
        """Skip when Firewall Policies scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Firewall Policies integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Firewall Policies service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_policy_id(record: dict[str, Any]) -> str | None:
        """Extract firewall policy ID from a record."""
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

    def _assert_write_result_or_expected_error(self, result: Any, context: str) -> None:
        """Accept expected validation/not-found errors, otherwise require success."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Firewall Policies:write scope",
                context=context,
            )
        if status_code in (400, 404, 422):
            return

        self.assert_no_error(result, context=context)
        self.assert_valid_list_response(result, min_length=0, context=context)

    def test_search_firewall_policies_operation_name(self):
        """Validate policy search operation name."""
        result = self.call_method(
            self.module.search_firewall_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_firewall_policies")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_firewall_policies")
        self.assert_valid_list_response(normalized, min_length=0, context="search_firewall_policies")

    def test_query_firewall_policy_ids_operation_name(self):
        """Validate policy ID query operation name."""
        result = self.call_method(
            self.module.query_firewall_policy_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_firewall_policy_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_firewall_policy_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_firewall_policy_ids")

    def test_get_firewall_policy_details_with_existing_id(self):
        """Validate policy detail retrieval from discovered policy ID."""
        search_result = self.call_method(
            self.module.search_firewall_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(search_result, "get_firewall_policy_details setup")
        search_result = self._normalize_search_result(search_result)

        self.assert_no_error(search_result, context="get_firewall_policy_details setup")
        if not search_result:
            self.skip_with_warning(
                "No firewall policies available to validate detail retrieval",
                context="test_get_firewall_policy_details_with_existing_id",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract firewall policy ID from search results",
                context="test_get_firewall_policy_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_firewall_policy_details,
            ids=[policy_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_firewall_policy_details")

        self.assert_no_error(result, context="get_firewall_policy_details")
        self.assert_valid_list_response(result, min_length=0, context="get_firewall_policy_details")

    def test_search_firewall_policy_members_with_existing_policy(self):
        """Validate combined policy-member search using discovered policy ID."""
        search_result = self.call_method(
            self.module.search_firewall_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "search_firewall_policy_members setup",
        )
        search_result = self._normalize_search_result(search_result)
        self.assert_no_error(search_result, context="search_firewall_policy_members setup")

        if not search_result:
            self.skip_with_warning(
                "No firewall policies available to validate member search",
                context="test_search_firewall_policy_members_with_existing_policy",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract firewall policy ID from search results",
                context="test_search_firewall_policy_members_with_existing_policy",
            )

        result = self.call_method(
            self.module.search_firewall_policy_members,
            policy_id=policy_id,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_firewall_policy_members")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_firewall_policy_members")
        self.assert_valid_list_response(normalized, min_length=0, context="search_firewall_policy_members")

    def test_query_firewall_policy_member_ids_with_existing_policy(self):
        """Validate member ID query using discovered policy ID."""
        search_result = self.call_method(
            self.module.search_firewall_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "query_firewall_policy_member_ids setup",
        )
        search_result = self._normalize_search_result(search_result)
        self.assert_no_error(search_result, context="query_firewall_policy_member_ids setup")

        if not search_result:
            self.skip_with_warning(
                "No firewall policies available to validate member ID query",
                context="test_query_firewall_policy_member_ids_with_existing_policy",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract firewall policy ID from search results",
                context="test_query_firewall_policy_member_ids_with_existing_policy",
            )

        result = self.call_method(
            self.module.query_firewall_policy_member_ids,
            policy_id=policy_id,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_firewall_policy_member_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_firewall_policy_member_ids")
        self.assert_valid_list_response(
            normalized,
            min_length=0,
            context="query_firewall_policy_member_ids",
        )

    def test_write_operations_invalid_payload_expected_error_or_success(self):
        """Validate write operation wiring using invalid payloads/selectors."""
        invalid_policy_id = "0" * 32

        action_result = self.call_method(
            self.module.perform_firewall_policies_action,
            confirm_execution=True,
            action_name="disable",
            ids=[invalid_policy_id],
            group_id=None,
            action_parameters=None,
            body=None,
        )
        self._assert_write_result_or_expected_error(
            action_result,
            context="perform_firewall_policies_action",
        )

        precedence_result = self.call_method(
            self.module.set_firewall_policies_precedence,
            confirm_execution=True,
            body=None,
            ids=[invalid_policy_id],
            platform_name="Windows",
        )
        self._assert_write_result_or_expected_error(
            precedence_result,
            context="set_firewall_policies_precedence",
        )

        delete_result = self.call_method(
            self.module.delete_firewall_policies,
            confirm_execution=True,
            ids=[invalid_policy_id],
        )
        self._assert_write_result_or_expected_error(
            delete_result,
            context="delete_firewall_policies",
        )

        create_result = self.call_method(
            self.module.create_firewall_policies,
            confirm_execution=True,
            body={"resources": [{}]},
            clone_id=None,
            name=None,
            platform_name=None,
            description=None,
            settings=None,
        )
        self._assert_write_result_or_expected_error(
            create_result,
            context="create_firewall_policies",
        )

        update_result = self.call_method(
            self.module.update_firewall_policies,
            confirm_execution=True,
            body={"resources": [{"id": invalid_policy_id}]},
            id=None,
            name=None,
            description=None,
            settings=None,
        )
        self._assert_write_result_or_expected_error(
            update_result,
            context="update_firewall_policies",
        )
