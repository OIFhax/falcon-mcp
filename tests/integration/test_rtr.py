"""Integration tests for the Real Time Response (RTR) module."""

from typing import Any

import pytest

from falcon_mcp.modules.rtr import RTRModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestRTRIntegration(BaseIntegrationTest):
    """Integration tests for RTR module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the RTR module with a real client."""
        self.module = RTRModule(falcon_client)

    def _skip_if_scope_missing(self, result: Any, context: str) -> None:
        """Skip test when API credentials are missing required scopes or RTR service data."""
        details = None

        if isinstance(result, dict):
            if "error" in result:
                details = result.get("details")
            elif "results" in result and isinstance(result["results"], list) and result["results"]:
                first = result["results"][0]
                if isinstance(first, dict) and "error" in first:
                    details = first.get("details")
        elif isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                details = first.get("details")

        if not isinstance(details, dict):
            return

        status_code = details.get("status_code")
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for RTR integration test",
                context=context,
            )

        if status_code == 400:
            body = details.get("body", {})
            if isinstance(body, dict):
                errors = body.get("errors", [])
                if isinstance(errors, list) and errors:
                    message = errors[0].get("message", "")
                    if isinstance(message, str) and "could not list active sessions" in message.lower():
                        self.skip_with_warning(
                            "RTR audit data unavailable in this tenant",
                            context=context,
                        )

    def test_search_rtr_sessions_operation_names(self):
        """Validate core RTR operation names by running a minimal search."""
        result = self.call_method(
            self.module.search_rtr_sessions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self._skip_if_scope_missing(result, "search_rtr_sessions")
        self.assert_no_error(result, context="search_rtr_sessions operation name validation")

    def test_search_rtr_admin_scripts_operation_names(self):
        """Validate RTR admin operation names by running a minimal script search."""
        result = self.call_method(
            self.module.search_rtr_admin_scripts,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self._skip_if_scope_missing(result, "search_rtr_admin_scripts")
        self.assert_no_error(result, context="search_rtr_admin_scripts operation name validation")

    def test_search_rtr_falcon_scripts_operation_names(self):
        """Validate Falcon script search operation names by running a minimal search."""
        result = self.call_method(
            self.module.search_rtr_falcon_scripts,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self._skip_if_scope_missing(result, "search_rtr_falcon_scripts")
        self.assert_no_error(result, context="search_rtr_falcon_scripts operation name validation")

    def test_aggregate_rtr_sessions_operation_name(self):
        """Validate RTR aggregate operation name with a minimal aggregate body."""
        result = self.call_method(
            self.module.aggregate_rtr_sessions,
            body=[{"field": "user_id", "type": "terms", "size": 1}],
        )

        self._skip_if_scope_missing(result, "aggregate_rtr_sessions")
        self.assert_no_error(result, context="aggregate_rtr_sessions operation name validation")

    def test_search_rtr_audit_sessions_operation_name(self):
        """Validate RTR audit operation name by running a minimal audit search."""
        result = self.call_method(
            self.module.search_rtr_audit_sessions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
            with_command_info=False,
        )

        self._skip_if_scope_missing(result, "search_rtr_audit_sessions")
        self.assert_no_error(result, context="search_rtr_audit_sessions operation name validation")
