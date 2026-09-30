"""Integration tests for the Hosts module."""

from typing import Any

import pytest

from falcon_mcp.modules.hosts import GROUPING_PREFIX, HostsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest

# Deliberately synthetic so a tag leaked by a crashed run is obvious and cannot
# collide with a real one. Passed to the tool unprefixed to exercise normalization.
PROBE_TAG = "falcon-mcp-probe"
QUALIFIED_PROBE_TAG = f"{GROUPING_PREFIX}{PROBE_TAG}"


@pytest.mark.integration
class TestHostsIntegration(BaseIntegrationTest):
    """Integration tests for Hosts module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the hosts module with a real client."""
        self.module = HostsModule(falcon_client)

    @staticmethod
    def _get_status_code(result: Any) -> int | None:
        """Extract status code from standardized error responses."""
        if isinstance(result, dict):
            details = result.get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
        if isinstance(result, list) and result and isinstance(result[0], dict):
            details = result[0].get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
        return None

    def _skip_if_scope_missing(self, result: Any, scope: str, context: str) -> None:
        """Skip integration assertions when API credentials are missing a scope."""
        if self._get_status_code(result) == 403:
            self.skip_with_warning(
                f"Missing required scope for {scope} integration test",
                context=context,
            )

    def test_search_hosts_returns_details(self):
        """Validate hosts search returns full host details."""
        result = self.call_method(self.module.search_hosts, limit=5)

        self.assert_no_error(result, context="search_hosts")
        self.assert_valid_list_response(result, min_length=0, context="search_hosts")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["device_id", "hostname"],
                context="search_hosts",
            )

    def test_search_hosts_with_filter(self):
        """Validate host search accepts a platform FQL filter."""
        result = self.call_method(
            self.module.search_hosts,
            filter="platform_name:'Windows'",
            limit=3,
        )
        self.assert_no_error(result, context="search_hosts with filter")
        self.assert_valid_list_response(result, min_length=0, context="search_hosts with filter")

    def test_search_hosts_with_sort(self):
        """Validate host search accepts a sort expression."""
        result = self.call_method(
            self.module.search_hosts,
            sort="last_seen.desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_hosts with sort")
        self.assert_valid_list_response(result, min_length=0, context="search_hosts with sort")

    def test_get_host_details_with_valid_id(self):
        """Retrieve a host by an ID found through search."""
        search_result = self.skip_unless_tenant_has(
            self.call_method(self.module.search_hosts, limit=1),
            "hosts",
            context="test_get_host_details_with_valid_id",
        )
        device_id = self.get_first_id(search_result, id_field="device_id")
        if not device_id:
            self.skip_with_warning(
                "Could not extract device ID from search results",
                context="test_get_host_details_with_valid_id",
            )

        result = self.call_method(self.module.get_host_details, ids=[device_id])
        self.assert_no_error(result, context="get_host_details")
        self.assert_valid_list_response(result, min_length=1, context="get_host_details")
        self.assert_search_returns_details(
            result,
            expected_fields=["device_id", "hostname"],
            context="get_host_details",
        )

    def test_search_host_groups_returns_details(self):
        """Validate host group search returns full host group details."""
        result = self.call_method(
            self.module.search_host_groups,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "Host Groups:read", "search_host_groups")

        self.assert_no_error(result, context="search_host_groups")
        self.assert_valid_list_response(result, min_length=0, context="search_host_groups")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="search_host_groups",
            )

    def test_search_migrations_returns_details(self):
        """Validate migration search returns full migration details."""
        result = self.call_method(
            self.module.search_migrations,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "Host Migration:read", "search_migrations")

        self.assert_no_error(result, context="search_migrations")
        self.assert_valid_list_response(result, min_length=0, context="search_migrations")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["migration_id"],
                context="search_migrations",
            )

    def test_search_host_migrations_returns_details(self):
        """Validate host migration search returns full host migration details."""
        migrations = self.call_method(
            self.module.search_migrations,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(migrations, "Host Migration:read", "search_host_migrations setup")
        self.assert_no_error(migrations, context="search_host_migrations setup")

        if not migrations:
            self.skip_with_warning(
                "No migration jobs available to test host migration search",
                context="search_host_migrations",
            )

        migration_id = self.get_first_id(migrations, id_field="migration_id")
        if not migration_id:
            self.skip_with_warning(
                "Could not extract migration ID from search_migrations results",
                context="search_host_migrations",
            )

        result = self.call_method(
            self.module.search_host_migrations,
            migration_id=migration_id,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "Host Migration:read", "search_host_migrations")

        self.assert_no_error(result, context="search_host_migrations")
        self.assert_valid_list_response(result, min_length=0, context="search_host_migrations")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["host_migration_id"],
                context="search_host_migrations",
            )

    def test_manage_host_grouping_tags_round_trip(self):
        """Add and remove a Falcon Grouping Tag on a real host.

        This is the only test that can catch a wrong request body. `FalconClient`
        uses APIHarnessV2, so the body must use the Uber-class model
        ({"action", "device_ids", "tags"}) rather than the action_name/ids keyword
        names of FalconPy's Hosts.update_device_tags(). A mocked test would assert
        whatever shape we chose to send and pass regardless.

        Also validates two behaviours the tool's design assumes: bare tags are sent
        fully qualified, and a duplicate add is a no-op (which is what justifies
        annotating the tool idempotentHint=True).

        Skips gracefully if Hosts:write scope is not available.
        """
        search_result = self.call_method(self.module.search_hosts, limit=1)
        device_id = self.get_first_id(search_result, id_field="device_id")
        if not device_id:
            self.skip_with_warning(
                "No hosts available to test manage_host_grouping_tags",
                context="test_manage_host_grouping_tags_round_trip",
            )
            return

        add_result = self.call_method(
            self.module.manage_host_grouping_tags,
            ids=[device_id],
            action="add",
            tags=[PROBE_TAG],
        )

        # Skip on 401/403 — the caller lacks Hosts:write
        if isinstance(add_result, list) and add_result and isinstance(add_result[0], dict):
            error = add_result[0]
            if "error" in error:
                details = error.get("details", {})
                status_code = details.get("status_code", 0) if isinstance(details, dict) else 0
                if status_code in (401, 403):
                    self.skip_with_warning(
                        f"Insufficient scope for manage_host_grouping_tags "
                        f"(Hosts:write required): {add_result}",
                        context="test_manage_host_grouping_tags_round_trip",
                    )
                    return
                pytest.fail(f"manage_host_grouping_tags add failed unexpectedly: {add_result}")

        try:
            # The bare tag we sent should come back fully qualified.
            updated = self.call_method(self.module.get_host_details, ids=[device_id])
            self.assert_no_error(updated, context="read-back after tag add")
            assert updated, f"get_host_details returned empty after tag add for {device_id}"
            tags = updated[0].get("tags") or []
            assert QUALIFIED_PROBE_TAG in tags, (
                f"Expected {QUALIFIED_PROBE_TAG!r} in tags after add, got: {tags}"
            )

            # Adding again must be a no-op — the tool documents add/remove as
            # idempotent and is annotated idempotentHint=True on that basis.
            repeat_result = self.call_method(
                self.module.manage_host_grouping_tags,
                ids=[device_id],
                action="add",
                tags=[PROBE_TAG],
            )
            self.assert_no_error(repeat_result, context="duplicate tag add")
            after_repeat = self.call_method(self.module.get_host_details, ids=[device_id])
            repeat_tags = after_repeat[0].get("tags") or []
            assert repeat_tags.count(QUALIFIED_PROBE_TAG) == 1, (
                f"Duplicate add should be a no-op, got: {repeat_tags}"
            )

            # Not asserting that search_hosts finds the host by tags:'<qualified
            # tag>' here. The filter form is correct, but it reads a separate
            # search index from the entity read-back above, so a write-then-search
            # assertion is timing-dependent in a way the round-trip is not.
        finally:
            remove_result = self.call_method(
                self.module.manage_host_grouping_tags,
                ids=[device_id],
                action="remove",
                tags=[PROBE_TAG],
            )
            self.assert_no_error(remove_result, context="manage_host_grouping_tags remove")

        after_remove = self.call_method(self.module.get_host_details, ids=[device_id])
        self.assert_no_error(after_remove, context="read-back after tag remove")
        assert after_remove, f"get_host_details returned empty after tag remove for {device_id}"
        remaining_tags = after_remove[0].get("tags") or []
        assert QUALIFIED_PROBE_TAG not in remaining_tags, (
            f"Expected {QUALIFIED_PROBE_TAG!r} to be removed, still present: {remaining_tags}"
        )

    def test_manage_host_grouping_tags_rejects_sensor_tag(self):
        """Sensor grouping tags are rejected locally, before any API call."""
        result = self.call_method(
            self.module.manage_host_grouping_tags,
            ids=["does-not-need-to-exist"],
            action="add",
            tags=["SensorGroupingTags/Production"],
        )

        assert isinstance(result, list) and result, f"Expected an error list, got: {result}"
        assert "error" in result[0], f"Expected sensor tag rejection, got: {result}"

    def test_manage_host_grouping_tags_rejects_miscased_sensor_tag(self):
        """A miscased sensor prefix is rejected rather than written as a junk tag.

        Guards the case-insensitive prefix check against regression. If the check
        goes back to matching exactly, this input is prefixed into the real tag
        'FalconGroupingTags/sensorgroupingtags/Production', which the API accepts
        with updated=true — so the regression shows up as a stray tag on a live
        host, not as a failure. No cleanup needed while the check holds, because
        nothing is sent.
        """
        result = self.call_method(
            self.module.manage_host_grouping_tags,
            ids=["does-not-need-to-exist"],
            action="add",
            tags=["sensorgroupingtags/Production"],
        )

        assert isinstance(result, list) and result, f"Expected an error list, got: {result}"
        assert "error" in result[0], (
            f"Miscased sensor prefix must be rejected, not prefixed into a junk tag: {result}"
        )

    def test_operation_names_are_correct(self):
        """Validate core operation names by executing minimal read queries."""
        hosts_result = self.call_method(self.module.search_hosts, limit=1)
        self.assert_no_error(hosts_result, context="hosts operation names")

        host_groups_result = self.call_method(
            self.module.search_host_groups,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(
            host_groups_result,
            "Host Groups:read",
            "host group operation names",
        )
        self.assert_no_error(host_groups_result, context="host group operation names")

        migrations_result = self.call_method(
            self.module.search_migrations,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(
            migrations_result,
            "Host Migration:read",
            "host migration operation names",
        )
        self.assert_no_error(migrations_result, context="host migration operation names")

    def test_product_type_desc_vocabulary(self):
        """Every product type the guide and hint list matches its own hosts.

        Mobile is included: it is a fourth value the tenant holds, and the closed
        three-value list read as the whole vocabulary, so a search for mobile
        devices had no spelling that worked.
        """
        for value in ("Workstation", "Server", "Domain Controller", "Mobile"):
            self.assert_filter_matches(
                self.module.search_hosts,
                f"product_type_desc:'{value}'",
                predicate=lambda host, value=value: host.get("product_type_desc") == value,
                predicate_desc=f"host.product_type_desc == {value!r}",
                note="Each product type in the guide must match its own hosts.",
                limit=3,
            )

    def test_last_seen_accepts_relative_dates(self):
        """`last_seen:>'now-7d'` is honored, not parsed as garbage and dropped.

        The hint has always used this form while the guide never mentioned it. A
        dropped clause would still return hosts that all carry a `last_seen`, so
        the predicate alone cannot tell the two apart — `assert_filter_narrows`
        additionally requires the filtered total to come in under the unfiltered
        one, which is what a clause the API ignored cannot do.
        """
        self.assert_filter_narrows(
            self.module.search_hosts,
            "last_seen:>'now-7d'",
            predicate=lambda host: bool(host.get("last_seen")),
            predicate_desc="host carries a last_seen timestamp",
            note="Relative dates are documented for last_seen in the guide and the hint.",
            limit=5,
        )

    def test_relative_date_garbage_is_rejected(self):
        """A malformed relative expression 400s rather than being silently dropped.

        This is what licenses reading the narrowing above as the API honoring the
        expression: the parser is strict about this operand, so `now-7d` reaching
        it and returning a smaller set is the expression being understood.
        """
        result = self.call_method(
            self.module.search_hosts, filter="last_seen:>'zzz-garbage'", limit=1
        )
        assert self.error_dicts(result), (
            "last_seen:>'zzz-garbage' was accepted. If unparseable date operands are "
            "now silently ignored, the relative-date test above no longer proves the "
            f"expression was honored. Got: {result}"
        )
