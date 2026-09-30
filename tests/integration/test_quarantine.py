"""Integration tests for the Quarantine module."""

from typing import Any

import pytest

from falcon_mcp.modules.quarantine import QuarantineModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestQuarantineIntegration(BaseIntegrationTest):
    """Integration tests for Quarantine module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Quarantine module with a real client."""
        self.module = QuarantineModule(falcon_client)

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
        """Skip when Quarantine scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Quarantine integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Quarantine service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_quarantine_id(record: dict[str, Any]) -> str | None:
        """Extract quarantine file ID from record."""
        for key in ["id", "quarantine_file_id"]:
            value = record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    def test_search_quarantined_files_returns_details(self):
        """Validate two-step quarantine search returns full details."""
        result = self.call_method(self.module.search_quarantined_files, limit=5)
        self.assert_no_error(result, context="search_quarantined_files")
        self.assert_valid_list_response(result, min_length=0, context="search_quarantined_files")
        if self.records(result, context="search_quarantined_files"):
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "sha256", "hostname"],
                context="search_quarantined_files",
            )

    def test_search_quarantined_files_with_sort(self):
        """Validate quarantine sorting."""
        result = self.call_method(
            self.module.search_quarantined_files,
            sort="date_updated|desc",
            limit=3,
        )
        self.assert_no_error(result, context="search_quarantined_files with sort")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_quarantined_files with sort",
        )

    def test_preview_quarantine_actions_with_filter(self):
        """Validate read-only quarantine action counts using state FQL."""
        result = self.call_method(
            self.module.preview_quarantine_actions,
            filter="state:'quarantined'",
        )
        self.assert_no_error(result, context="preview_quarantine_actions")
        self.assert_valid_list_response(result, min_length=0, context="preview_quarantine_actions")
        if result:
            assert isinstance(result[0], dict), "Expected dict payload from preview_quarantine_actions"
            assert "buckets" in result[0], "Expected buckets in preview_quarantine_actions response"

    def test_search_quarantine_files_operation_name(self):
        """Validate quarantine search operation name."""
        result = self.call_method(
            self.module.search_quarantine_files,
            filter=None,
            q=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_quarantine_files")

        if isinstance(result, dict):
            self.assertIn("results", result)
            return

        self.assert_no_error(result, context="search_quarantine_files")
        self.assert_valid_list_response(result, min_length=0, context="search_quarantine_files")

    def test_get_quarantine_action_update_count_operation_name(self):
        """Validate action update count operation name."""
        result = self.call_method(
            self.module.get_quarantine_action_update_count,
            filter="state:'quarantined'",
        )
        self._skip_if_scope_or_service_missing(result, "get_quarantine_action_update_count")

        if isinstance(result, dict):
            self.assertIn("results", result)
            return

        self.assert_no_error(result, context="get_quarantine_action_update_count")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="get_quarantine_action_update_count",
        )

    def test_aggregate_quarantine_files_operation_name(self):
        """Validate quarantine aggregation operation name."""
        result = self.call_method(
            self.module.aggregate_quarantine_files,
            body=[{"field": "state", "name": "state", "type": "terms"}],
        )
        self._skip_if_scope_or_service_missing(result, "aggregate_quarantine_files")

        self.assert_no_error(result, context="aggregate_quarantine_files")
        self.assert_valid_list_response(result, min_length=0, context="aggregate_quarantine_files")

    def test_get_quarantine_file_details_with_existing_id(self):
        """Validate detail retrieval from discovered quarantine ID."""
        search_result = self.call_method(
            self.module.search_quarantine_files,
            filter="state:'quarantined'",
            q=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(search_result, "get_quarantine_file_details setup")

        if isinstance(search_result, dict):
            search_result = search_result.get("results", [])

        self.assert_no_error(search_result, context="get_quarantine_file_details setup")

        if not search_result:
            self.skip_with_warning(
                "No quarantine files available to validate detail retrieval",
                context="test_get_quarantine_file_details_with_existing_id",
            )

        quarantine_id = self._extract_quarantine_id(search_result[0])
        if not quarantine_id:
            self.skip_with_warning(
                "Could not extract quarantine file ID from search results",
                context="test_get_quarantine_file_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_quarantine_file_details,
            ids=[quarantine_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_quarantine_file_details")

        self.assert_no_error(result, context="get_quarantine_file_details")
        self.assert_valid_list_response(result, min_length=0, context="get_quarantine_file_details")

    def test_update_quarantine_files_by_query_safe_operation_name(self):
        """Validate update-by-query operation with impossible selector."""
        result = self.call_method(
            self.module.update_quarantine_files_by_query,
            confirm_execution=True,
            action="release",
            filter="device.hostname:'__falcon_mcp_quarantine_no_match__'",
            q=None,
            comment="falcon-mcp integration test no-op",
            body=None,
        )
        self._skip_if_scope_or_service_missing(result, "update_quarantine_files_by_query")

        self.assert_no_error(result, context="update_quarantine_files_by_query")
        self.assert_valid_list_response(result, min_length=0, context="update_quarantine_files_by_query")

    def test_update_quarantine_files_by_ids_invalid_id_expected_error(self):
        """Validate update-by-IDs operation call using an invalid ID."""
        result = self.call_method(
            self.module.update_quarantine_files_by_ids,
            confirm_execution=True,
            action="release",
            ids=["0" * 32],
            comment="falcon-mcp integration test invalid id",
            body=None,
        )
        self._skip_if_scope_or_service_missing(result, "update_quarantine_files_by_ids")

        if isinstance(result, list) and result and isinstance(result[0], dict):
            details = result[0].get("details", {})
            if isinstance(details, dict):
                status_code = details.get("status_code")
                if status_code in (400, 404):
                    return

        self.assert_no_error(result, context="update_quarantine_files_by_ids")

    def test_operation_names_are_correct(self):
        """Validate quarantine query and detail operation wiring."""
        result = self.call_method(self.module.search_quarantined_files, limit=1)
        self.assert_no_error(
            result,
            context="QueryQuarantineFiles + GetQuarantineFiles operation names",
        )

    # ------------------------------------------------------------------
    # Filter fields and the state vocabulary
    #
    # QueryQuarantineFiles answers an unknown field with an empty HTTP 200 (see
    # test_filter_classification.py), and so does a real field whose value matches
    # nothing — `sha256:'x'` and `zzz_not_a_field:'x'` are the same observation
    # here. A bogus-field control therefore proves nothing on its own, so field
    # existence is established from GetAggregateFiles instead: it returns buckets
    # for a field it knows and a null bucket list for one it does not.
    # ------------------------------------------------------------------

    def _aggregate_buckets(self, field):
        """Terms buckets for `field`, or None when the API does not know the field."""
        response = self.module.client.command(
            "GetAggregateFiles",
            body=[{"field": field, "type": "terms", "name": "probe", "size": 20}],
        )
        assert response.get("status_code") == 200, f"Aggregate on {field!r} failed: {response}"
        resources = (response.get("body") or {}).get("resources") or []
        return resources[0].get("buckets") if resources else None

    def test_aggregate_distinguishes_known_from_unknown_fields(self):
        """The oracle the two tests below rely on actually discriminates.

        A known field returns buckets and an unknown one returns null. Without
        this, `paths` coming back null would be indistinguishable from the
        aggregate simply not supporting nested fields.
        """
        assert self._aggregate_buckets("sha256"), (
            "GetAggregateFiles returned no buckets for sha256, a field that certainly "
            "exists. The field-existence oracle no longer works and the two tests "
            "below prove nothing."
        )
        assert self._aggregate_buckets("zzz_not_a_field") is None, (
            "GetAggregateFiles returned buckets for a field that cannot exist, so it "
            "no longer discriminates known from unknown fields."
        )

    def test_status_is_not_an_alias_for_state(self):
        """`status` is not a filter field, though it is accepted without error.

        The guide and all four quarantine hints used to offer it as an alias. It is
        unknown to the aggregate and matches nothing in a search, while `state`
        does both — and the `state` half runs here against the same records, so
        this is a divergence rather than an empty tenant.
        """
        assert self._aggregate_buckets("state"), (
            "state returned no aggregate buckets. Either `state` stopped being a known "
            "field — the regression this test exists to catch — or the aggregate broke, "
            "or the tenant holds no quarantined files. Check "
            "test_aggregate_distinguishes_known_from_unknown_fields first: if that still "
            "passes, the oracle works and this is about `state` or the tenant."
        )
        assert self._aggregate_buckets("status") is None, (
            "status is now a known field. If it really works as an alias, restore it "
            "in the guide and the four quarantine filter hints."
        )

        matched = self.call_method(
            self.module.search_quarantined_files, filter="state:'quarantined'", limit=2
        )
        self.assert_envelope_ok(matched, context="state:'quarantined'")
        assert self.records(matched, "state:'quarantined'"), (
            "state:'quarantined' matched nothing, so the status comparison below has "
            "no positive control."
        )

        aliased = self.call_method(
            self.module.search_quarantined_files, filter="status:'quarantined'", limit=2
        )
        self.assert_envelope_ok(aliased, context="status:'quarantined'")
        assert not self.records(aliased, "status:'quarantined'"), (
            "status:'quarantined' now returns records while it previously matched "
            "nothing. Update the guide and the four quarantine hints."
        )

    def test_state_vocabulary_matches_the_aggregate(self):
        """Every state the field actually holds is filterable, and the hint lists them.

        The hint offered only quarantined and released.

        Only one direction is checkable: every state the aggregate reports must be
        filterable. The reverse — that each of the six documented values is real —
        cannot be established here, because this endpoint is silent, so a documented
        value the tenant simply has no files in looks exactly like a wrong one. The
        four values beyond quarantined and released rest on the aggregate having
        reported them when the guide was written, not on this assertion.
        """
        buckets = self._aggregate_buckets("state")
        assert buckets, "No state buckets, so there is nothing to check."
        observed = {bucket["label"] for bucket in buckets}
        documented = {"quarantined", "released", "purged", "cleaned", "error", "unknown"}
        assert observed <= documented, (
            f"The state field holds values the guide and hint do not list: "
            f"{sorted(observed - documented)}. Add them."
        )

        for value in sorted(observed):
            self.assert_filter_matches(
                self.module.search_quarantined_files,
                f"state:'{value}'",
                predicate=lambda record, value=value: (
                    record.get("state") == value
                    or any(
                        path.get("state") == value
                        for path in (record.get("paths") or [])
                    )
                ),
                predicate_desc=f"record.state or one of its paths == {value!r}",
                note="Each state the aggregate reports must also be filterable.",
                limit=2,
            )

    def test_paths_filters_only_in_its_dotted_form(self):
        """`paths.path` filters; bare `paths` does not.

        Bare `paths` appeared in all four quarantine hints and nowhere else in the
        repo except the response shape. It is unknown to the aggregate, and a real
        path value that `paths.path` matches returns nothing through `paths`.
        """
        path_buckets = self._aggregate_buckets("paths.path")
        assert path_buckets, "No paths.path buckets to work from."
        assert self._aggregate_buckets("paths.state"), "No paths.state buckets to work from."
        assert self._aggregate_buckets("paths") is None, (
            "Bare `paths` is now a known field. If it filters, put it back in the "
            "guide and the four quarantine hints."
        )

        real_path = path_buckets[0]["label"]

        self.assert_filter_matches(
            self.module.search_quarantined_files,
            f"paths.path:'{real_path}'",
            predicate=lambda record: any(
                entry.get("path") == real_path for entry in record.get("paths") or []
            ),
            predicate_desc=f"record carries the path {real_path!r}",
            note="paths.path is the dotted form the hint now documents.",
            limit=2,
        )

        bare = self.call_method(
            self.module.search_quarantined_files, filter=f"paths:'{real_path}'", limit=2
        )
        self.assert_envelope_ok(bare, context="bare paths")
        assert not self.records(bare, "bare paths"), (
            f"paths:'{real_path}' now returns records. The dotted form matched the "
            "same value on the line above, so if both work the hints can offer either."
        )
