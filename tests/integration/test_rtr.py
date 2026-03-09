"""Integration tests for the Real Time Response (RTR) module."""

import pytest

from falcon_mcp.modules.rtr import RTRModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestRTRIntegration(BaseIntegrationTest):
    """Integration tests for RTR module with real API calls.

    Validates:
    - Correct FalconPy operation names (RTR_ListAllSessions, RTR_ListSessions)
    - Two-step search pattern returns full details, not just IDs
    """

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the RTR module with a real client."""
        self.module = RTRModule(falcon_client)

    def test_operation_names_are_correct(self):
        """Validate operation names by executing a minimal RTR session query."""
        result = self.call_method(
            self.module.search_rtr_sessions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self.assert_no_error(result, context="RTR operation name validation")

    def test_search_rtr_sessions_returns_details(self):
        """Test that search_rtr_sessions returns full details, not only session IDs."""
        result = self.call_method(
            self.module.search_rtr_sessions,
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )

        self.assert_no_error(result, context="search_rtr_sessions")
        self.assert_valid_list_response(result, min_length=0, context="search_rtr_sessions")

        if len(result) > 0:
            first = result[0]
            assert isinstance(first, dict), (
                f"Expected dict items (session details), got {type(first)}"
            )
            assert any(field in first for field in ["session_id", "id", "aid"]), (
                f"Expected session detail fields in first result. Available fields: {list(first.keys())}"
            )

    def test_search_rtr_sessions_with_user_filter(self):
        """Test RTR session search with user-scoped FQL filter."""
        result = self.call_method(
            self.module.search_rtr_sessions,
            filter="user_id:'@me'",
            limit=3,
            offset=0,
            sort="date_created.desc",
        )

        self.assert_no_error(result, context="search_rtr_sessions with filter")
        if isinstance(result, list):
            self.assert_valid_list_response(
                result, min_length=0, context="search_rtr_sessions with filter"
            )
