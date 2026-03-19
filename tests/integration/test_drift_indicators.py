"""Integration tests for the Drift Indicators module."""

import pytest

from falcon_mcp.modules.drift_indicators import DriftIndicatorsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDriftIndicatorsIntegration(BaseIntegrationTest):
    """Integration tests for Drift Indicators module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Drift Indicators module with a real client."""
        self.module = DriftIndicatorsModule(falcon_client)

    def test_get_drift_indicator_values_by_date_operation_name(self):
        """Validate GetDriftIndicatorsValuesByDate operation name."""
        result = self.call_method(
            self.module.get_drift_indicator_values_by_date,
            limit=3,
        )

        self.assert_no_error(result, context="get_drift_indicator_values_by_date")
        self.assert_valid_list_response(result, min_length=1, context="get_drift_indicator_values_by_date")

    def test_query_and_get_drift_indicator_entities(self):
        """Validate SearchDriftIndicators + ReadDriftIndicatorEntities workflow."""
        ids = self.call_method(
            self.module.query_drift_indicator_ids,
            limit=1,
            offset=0,
            sort="occurred_at.desc",
        )

        self.assert_no_error(ids, context="query_drift_indicator_ids")
        assert isinstance(ids, list), f"Expected list of IDs, got {type(ids)}"
        assert ids, "Expected at least one drift indicator ID"

        details = self.call_method(
            self.module.get_drift_indicator_details,
            ids=[ids[0]],
        )

        self.assert_no_error(details, context="get_drift_indicator_details")
        self.assert_valid_list_response(details, min_length=1, context="get_drift_indicator_details")
        self.assert_search_returns_details(
            details,
            expected_fields=["aid", "agent_id", "computer_name"],
            context="get_drift_indicator_details",
        )

    def test_search_drift_indicator_entities_operation_name(self):
        """Validate combined drift indicator search operation name."""
        result = self.call_method(
            self.module.search_drift_indicator_entities,
            filter=None,
            limit=1,
            offset=0,
            sort="occurred_at.desc",
        )

        self.assert_no_error(result, context="search_drift_indicator_entities")
        self.assert_valid_list_response(result, min_length=0, context="search_drift_indicator_entities")
