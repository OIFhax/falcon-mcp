"""Integration tests for the Event Streams module."""

from typing import Any

import pytest

from falcon_mcp.modules.event_streams import EventStreamsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest

TEST_APP_ID = "FalconMCPIT01"


@pytest.mark.integration
class TestEventStreamsIntegration(BaseIntegrationTest):
    """Integration tests for Event Streams module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Event Streams module with a real client."""
        self.module = EventStreamsModule(falcon_client)

    def _skip_if_scope_missing(self, result: Any, context: str) -> None:
        """Skip test when credentials are missing required scopes."""
        details = None

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                details = first.get("details")
        elif isinstance(result, dict) and "error" in result:
            details = result.get("details")

        if not isinstance(details, dict):
            return

        if details.get("status_code") == 403:
            self.skip_with_warning(
                "Missing required API scope for Event Streams integration test",
                context=context,
            )

    def test_list_event_streams_operation_name(self):
        """Validate Event Streams discovery operation name."""
        result = self.call_method(
            self.module.list_event_streams,
            app_id=TEST_APP_ID,
            format="json",
        )

        self._skip_if_scope_missing(result, "list_event_streams")
        self.assert_no_error(result, context="list_event_streams operation name validation")

    def test_list_event_streams_response_shape(self):
        """Validate stream discovery response shape."""
        result = self.call_method(
            self.module.list_event_streams,
            app_id=TEST_APP_ID,
            format="json",
        )

        self._skip_if_scope_missing(result, "list_event_streams response shape")
        self.assert_no_error(result, context="list_event_streams response shape")
        self.assert_valid_list_response(result, min_length=1, context="list_event_streams response shape")
        self.assert_search_returns_details(
            result,
            expected_fields=[
                "dataFeedURL",
                "sessionToken",
                "refreshActiveSessionURL",
                "refreshActiveSessionInterval",
            ],
            context="list_event_streams response shape",
        )

    def test_refresh_event_stream_session_operation_name(self):
        """Validate refresh operation name against a known environment state."""
        result = self.call_method(
            self.module.refresh_event_stream_session,
            app_id=TEST_APP_ID,
            partition=0,
        )

        self._skip_if_scope_missing(result, "refresh_event_stream_session")

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                details = first.get("details", {})
                if details.get("status_code") == 404:
                    body = details.get("body", {})
                    errors = body.get("errors", []) if isinstance(body, dict) else []
                    if errors and "no active stream session found" in errors[0].get("message", "").lower():
                        self.skip_with_warning(
                            "No active Event Streams consumer session found for refresh validation",
                            context="refresh_event_stream_session",
                        )

        self.assert_no_error(result, context="refresh_event_stream_session operation name validation")
