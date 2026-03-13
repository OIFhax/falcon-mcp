"""Integration tests for the Firewall module."""

from typing import Any

import pytest

from falcon_mcp.modules.firewall import FirewallModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestFirewallIntegration(BaseIntegrationTest):
    """Integration tests for Firewall module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the firewall module with a real client."""
        self.module = FirewallModule(falcon_client)

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
        """Skip when firewall scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Firewall Management integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Firewall Management service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_id(record: dict[str, Any]) -> str | None:
        """Extract an ID field from a record."""
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
                "Missing required Firewall Management:write scope",
                context=context,
            )
        if status_code in (400, 404, 422, 500):
            return

        self.assert_no_error(result, context=context)
        self.assert_valid_list_response(result, min_length=0, context=context)

    def test_search_firewall_rules_operation_name(self):
        """Validate rule search operation wiring."""
        result = self.call_method(
            self.module.search_firewall_rules,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_firewall_rules")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_firewall_rules")
        self.assert_valid_list_response(normalized, min_length=0, context="search_firewall_rules")

    def test_query_firewall_rule_ids_operation_name(self):
        """Validate rule ID query operation wiring."""
        result = self.call_method(
            self.module.query_firewall_rule_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_firewall_rule_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_firewall_rule_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_firewall_rule_ids")

    def test_get_firewall_rules_with_existing_id(self):
        """Validate get-rule details using discovered rule ID."""
        query_result = self.call_method(
            self.module.query_firewall_rule_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )
        self._skip_if_scope_or_service_missing(query_result, "get_firewall_rules setup")
        query_result = self._normalize_search_result(query_result)

        self.assert_no_error(query_result, context="get_firewall_rules setup")
        if not query_result:
            self.skip_with_warning(
                "No firewall rules available to validate details retrieval",
                context="test_get_firewall_rules_with_existing_id",
            )

        first_rule_id = query_result[0] if isinstance(query_result[0], str) else None
        if not first_rule_id:
            self.skip_with_warning(
                "Could not extract firewall rule ID from query results",
                context="test_get_firewall_rules_with_existing_id",
            )

        result = self.call_method(
            self.module.get_firewall_rules,
            ids=[first_rule_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_firewall_rules")

        self.assert_no_error(result, context="get_firewall_rules")
        self.assert_valid_list_response(result, min_length=0, context="get_firewall_rules")

    def test_platform_query_and_details(self):
        """Validate platform query -> details roundtrip."""
        query_result = self.call_method(
            self.module.query_firewall_platform_ids,
            limit=5,
            offset=0,
        )
        self._skip_if_scope_or_service_missing(query_result, "query_firewall_platform_ids")

        self.assert_no_error(query_result, context="query_firewall_platform_ids")
        self.assert_valid_list_response(query_result, min_length=0, context="query_firewall_platform_ids")

        if not query_result:
            self.skip_with_warning(
                "No firewall platform IDs available to validate details retrieval",
                context="test_platform_query_and_details",
            )

        first_platform_id = query_result[0] if isinstance(query_result[0], str) else None
        if not first_platform_id:
            self.skip_with_warning(
                "Could not extract firewall platform ID from query results",
                context="test_platform_query_and_details",
            )

        details_result = self.call_method(
            self.module.get_firewall_platforms,
            ids=[first_platform_id],
        )
        self._skip_if_scope_or_service_missing(details_result, "get_firewall_platforms")

        self.assert_no_error(details_result, context="get_firewall_platforms")
        self.assert_valid_list_response(details_result, min_length=0, context="get_firewall_platforms")

    def test_query_firewall_network_location_ids_operation_name(self):
        """Validate network location ID query operation wiring."""
        result = self.call_method(
            self.module.query_firewall_network_location_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
            q=None,
            after=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_firewall_network_location_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_firewall_network_location_ids")
        self.assert_valid_list_response(
            normalized,
            min_length=0,
            context="query_firewall_network_location_ids",
        )

    def test_validate_firewall_filepath_pattern_operation_name(self):
        """Validate filepath pattern validation operation wiring."""
        result = self.call_method(
            self.module.validate_firewall_filepath_pattern,
            filepath_pattern="C:\\\\Windows\\\\*",
        )
        self._skip_if_scope_or_service_missing(result, "validate_firewall_filepath_pattern")

        self.assert_no_error(result, context="validate_firewall_filepath_pattern")
        self.assert_valid_list_response(result, min_length=0, context="validate_firewall_filepath_pattern")

    def test_write_operations_invalid_payload_expected_error_or_success(self):
        """Validate write operation wiring with invalid payloads/selectors."""
        invalid_id = "0" * 32

        create_group_result = self.call_method(
            self.module.create_firewall_rule_group,
            confirm_execution=True,
            body={"name": "falcon-mcp-invalid", "platform": "linux"},
            parameters={"comment": "integration invalid payload check"},
        )
        self._assert_write_result_or_expected_error(
            create_group_result,
            context="create_firewall_rule_group",
        )

        update_group_result = self.call_method(
            self.module.update_firewall_rule_group,
            confirm_execution=True,
            body={"id": invalid_id},
            parameters={"comment": "integration invalid payload check"},
        )
        self._assert_write_result_or_expected_error(
            update_group_result,
            context="update_firewall_rule_group",
        )

        delete_group_result = self.call_method(
            self.module.delete_firewall_rule_groups,
            confirm_execution=True,
            ids=[invalid_id],
            comment="integration invalid selector check",
        )
        self._assert_write_result_or_expected_error(
            delete_group_result,
            context="delete_firewall_rule_groups",
        )

        update_policy_result = self.call_method(
            self.module.update_firewall_policy_container,
            confirm_execution=True,
            body={"id": invalid_id},
            parameters=None,
        )
        self._assert_write_result_or_expected_error(
            update_policy_result,
            context="update_firewall_policy_container",
        )

        create_network_result = self.call_method(
            self.module.create_firewall_network_locations,
            confirm_execution=True,
            body={"resources": [{}]},
            parameters=None,
        )
        self._assert_write_result_or_expected_error(
            create_network_result,
            context="create_firewall_network_locations",
        )

        delete_network_result = self.call_method(
            self.module.delete_firewall_network_locations,
            confirm_execution=True,
            ids=[invalid_id],
        )
        self._assert_write_result_or_expected_error(
            delete_network_result,
            context="delete_firewall_network_locations",
        )
