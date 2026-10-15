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
            sort=None,
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

    def test_operation_names_are_correct(self):
        """Validate operation names by executing a minimal read query."""
        result = self.call_method(
            self.module.search_firewall_rules,
            filter=None,
            limit=1,
            sort=None,
            after=None,
        )
        self.assert_no_error(result, context="operation name validation")

    def test_search_firewall_rules_returns_details(self):
        """Test that search_firewall_rules returns full details, not only IDs."""
        result = self.call_method(
            self.module.search_firewall_rules,
            filter=None,
            limit=5,
            sort=None,
            after=None,
        )

        self.assert_no_error(result, context="search_firewall_rules")
        self.assert_valid_list_response(result, min_length=0, context="search_firewall_rules")

        records = self.records(result, context="search_firewall_rules")
        if len(records) > 0:
            self.assert_search_returns_details(
                records,
                expected_fields=["id", "platform_ids"],
                context="search_firewall_rules",
            )

    def test_search_firewall_rules_with_filter(self):
        """Test firewall rule search with an FQL filter."""
        result = self.call_method(
            self.module.search_firewall_rules,
            filter="enabled:true",
            limit=3,
            sort="modified_on.desc",
            after=None,
        )

        self.assert_no_error(result, context="search_firewall_rules with filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_firewall_rules with filter"
        )

    def test_search_firewall_rule_groups_returns_details(self):
        """Test that search_firewall_rule_groups returns full details."""
        result = self.call_method(
            self.module.search_firewall_rule_groups,
            filter=None,
            limit=5,
            sort=None,
            after=None,
        )

        self.assert_no_error(result, context="search_firewall_rule_groups")
        self.assert_valid_list_response(
            result, min_length=0, context="search_firewall_rule_groups"
        )

        records = self.records(result, context="search_firewall_rule_groups")
        if len(records) > 0:
            self.assert_search_returns_details(
                records,
                expected_fields=["id", "platform"],
                context="search_firewall_rule_groups",
            )

    def test_search_firewall_rule_groups_with_filter(self):
        """Test firewall rule group search with an FQL filter."""
        result = self.call_method(
            self.module.search_firewall_rule_groups,
            filter="enabled:true",
            limit=3,
            sort="modified_on.desc",
            after=None,
        )

        self.assert_no_error(result, context="search_firewall_rule_groups with filter")
        self.assert_valid_list_response(
            result, min_length=0, context="search_firewall_rule_groups with filter"
        )

    def test_search_firewall_policy_rules(self):
        """Test searching policy rules using a discovered policy container ID.

        The ID has to come from a rule group's `policy_ids`, not from the group's
        own `id`: passing a rule group ID gets "policy container not found", which
        the test then read as "no policy matches" and skipped on — so it never
        exercised the endpoint.

        Every attached policy is tried until one returns rules, because a policy
        container can legitimately hold none. Asserting rows off the first policy
        found fails on a healthy tenant. Note the meta is not a usable signal here:
        an empty page still reports a large `pagination.total` (the tenant-wide rule
        count, not this policy's), so only the returned rows say anything.
        """
        groups = self.skip_unless_tenant_has(
            self.call_method(self.module.search_firewall_rule_groups, limit=20),
            "firewall rule groups",
            context="test_search_firewall_policy_rules",
        )

        policy_ids = [pid for group in groups for pid in group.get("policy_ids") or []]
        if not policy_ids:
            self.skip_with_warning(
                "No rule group is attached to a policy container",
                context="test_search_firewall_policy_rules",
            )
            return

        for policy_id in dict.fromkeys(policy_ids):
            result = self.call_method(
                self.module.search_firewall_policy_rules,
                policy_id=policy_id,
                limit=3,
            )
            self.assert_no_error(result, context=f"policy rules for {policy_id}")
            rules = self.records(result, context=f"policy rules for {policy_id}")
            if rules:
                self.assert_search_returns_details(
                    rules,
                    expected_fields=["id", "name"],
                    context="search_firewall_policy_rules",
                )
                return

        self.skip_with_warning(
            f"None of the {len(set(policy_ids))} attached policy containers holds a "
            "rule, so the hydration path is unexercised",
            context="test_search_firewall_policy_rules",
        )


    # ------------------------------------------------------------------
    # The platform field, which is real on exactly one of the three tools
    # ------------------------------------------------------------------

    def test_platform_filters_rule_groups(self):
        """`platform` selects rule groups, for each of the three values.

        query_rule_groups checks field names but not values (see
        test_filter_classification.py), so each value is established by rows and
        confirmed against the record's own platform.
        """
        for value in ("windows", "mac", "linux"):
            self.assert_filter_matches(
                self.module.search_firewall_rule_groups,
                f"platform:'{value}'",
                predicate=lambda group, value=value: group.get("platform") == value,
                predicate_desc=f"group.platform == {value!r}",
                note="Every platform value in the guide must match its own rule groups.",
                limit=3,
            )

    def test_platform_is_not_a_field_on_rules(self):
        """`platform` is an unknown property on query_rules, not an empty result.

        It was in the rules guide, the rules filter hint and the tool's own filter
        example. The rule-group test above runs against the same tenant and does
        match rows, so this is the field being absent here rather than an absence
        of Windows rules.
        """
        result = self.call_method(
            self.module.search_firewall_rules, filter="platform:'windows'", limit=1
        )
        errors = self.error_dicts(result)
        assert errors, (
            f"platform:'windows' was accepted on search_firewall_rules. If the field "
            f"now exists, restore it in the guide and the hint. Got: {result}"
        )
        assert "platform" in str(errors[0]), (
            f"Expected the 400 to name platform as the unknown property, got: {errors[0]}"
        )

        # Control: a field that does exist here is accepted, so the rejection above
        # is about `platform` and not about filtering being broken on this endpoint.
        self.assert_filter_matches(
            self.module.search_firewall_rules,
            "enabled:true",
            predicate=lambda rule: rule.get("enabled") is True,
            predicate_desc="rule.enabled is True",
            note="enabled is the control proving filters work on query_rules.",
            limit=3,
        )

    def test_platform_sort_per_tool(self):
        """Where `platform` is accepted as a sort field, tool by tool.

        Sort validity is a separate surface from filter validity — a sort field the
        endpoint does not know may 400 or may be silently ignored, and neither can
        be inferred from `platform` being absent as a *filter* field. The guide
        renders one shared sort table for all three tools, so this records what each
        one actually does with it.
        """
        outcomes: dict[str, str] = {}
        probes = {
            "rule_groups": (self.module.search_firewall_rule_groups, {}),
            "rules": (self.module.search_firewall_rules, {}),
        }
        for label, (method, kwargs) in probes.items():
            result = self.call_method(method, sort="platform|asc", limit=2, **kwargs)
            outcomes[label] = "error" if self.error_dicts(result) else "accepted"

        assert outcomes["rule_groups"] == "accepted", (
            "platform|asc was rejected on search_firewall_rule_groups, the one tool "
            "where platform is a real property. If sort no longer takes it, drop the "
            f"row from the guide's sort table. Got: {outcomes}"
        )
        assert outcomes["rules"] == "error", (
            "platform|asc was accepted on search_firewall_rules, where platform is not "
            "a property. If the endpoint tolerates it, the guide's shared sort table is "
            f"fine as-is and this assertion should be relaxed. Got: {outcomes}"
        )

    def test_policy_rules_filter_requires_the_policy_id_clause(self):
        """Any filter on query_policy_rules must carry `rule_group.policy_ids`.

        Passing `policy_id` is not enough: a filter that omits the clause fails
        with "Query missing required filter field", which is why the hint now leads
        with it. The unfiltered call is the control — it succeeds, so the failure
        is the filter's shape rather than the policy being unusable.
        """
        groups = self.skip_unless_tenant_has(
            self.call_method(self.module.search_firewall_rule_groups, limit=20),
            "firewall rule groups",
            context="policy rules filter shape",
        )
        policy_id = next(
            (pid for group in groups for pid in group.get("policy_ids") or []), None
        )
        if not policy_id:
            self.skip_with_warning(
                "No rule group is attached to a policy",
                context="policy rules filter shape",
            )
            return

        unfiltered = self.call_method(
            self.module.search_firewall_policy_rules, policy_id=policy_id, limit=1
        )
        assert not self.error_dicts(unfiltered), (
            f"The unfiltered policy-rules call failed, so nothing below is "
            f"attributable to the filter: {unfiltered}"
        )

        without_clause = self.call_method(
            self.module.search_firewall_policy_rules,
            policy_id=policy_id,
            filter="enabled:true",
            limit=1,
        )
        errors = self.error_dicts(without_clause)
        assert errors, (
            "A filter without rule_group.policy_ids was accepted. If the endpoint no "
            f"longer requires the clause, drop it from the hint. Got: {without_clause}"
        )
        assert "rule_group.policy_ids" in str(errors[0]), (
            f"Expected the 400 to name the missing required filter field, got: {errors[0]}"
        )

        with_clause = self.call_method(
            self.module.search_firewall_policy_rules,
            policy_id=policy_id,
            filter=f"rule_group.policy_ids:'{policy_id}'",
            limit=1,
        )
        assert not self.error_dicts(with_clause), (
            f"The documented filter shape was rejected: {with_clause}"
        )

    def test_platform_is_not_a_field_on_policy_rules(self):
        """`platform` is unknown on query_policy_rules too, even with the required clause.

        Asserted with `rule_group.policy_ids` present so the rejection is about
        `platform` and not about the missing-clause error the test above covers.
        """
        groups = self.skip_unless_tenant_has(
            self.call_method(self.module.search_firewall_rule_groups, limit=20),
            "firewall rule groups",
            context="policy rules platform",
        )
        policy_id = next(
            (pid for group in groups for pid in group.get("policy_ids") or []), None
        )
        if not policy_id:
            self.skip_with_warning(
                "No rule group is attached to a policy",
                context="policy rules platform",
            )
            return

        result = self.call_method(
            self.module.search_firewall_policy_rules,
            policy_id=policy_id,
            filter=f"rule_group.policy_ids:'{policy_id}'+platform:'windows'",
            limit=1,
        )
        errors = self.error_dicts(result)
        assert errors and "platform" in str(errors[0]), (
            "platform:'windows' was accepted on search_firewall_policy_rules alongside "
            f"the required clause. If the field now exists, restore it. Got: {result}"
        )
