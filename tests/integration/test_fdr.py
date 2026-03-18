"""Integration tests for the FDR module."""

import pytest

from falcon_mcp.modules.fdr import FDRModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestFDRIntegration(BaseIntegrationTest):
    """Integration tests for FDR module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the FDR module with a real client."""
        self.module = FDRModule(falcon_client)

    def test_get_fdr_combined_schema_operation_name(self):
        """Validate combined schema operation name."""
        result = self.call_method(self.module.get_fdr_combined_schema)

        self.assert_no_error(result, context="get_fdr_combined_schema operation name")
        self.assert_valid_list_response(result, min_length=1, context="get_fdr_combined_schema")

    def test_search_fdr_event_schemas_returns_details(self):
        """Validate two-step event schema search flow."""
        result = self.call_method(
            self.module.search_fdr_event_schemas,
            filter="name:'EmailFileWritten'",
            limit=3,
            offset=0,
            sort="name.asc",
        )

        self.assert_no_error(result, context="search_fdr_event_schemas")
        self.assert_valid_list_response(result, min_length=1, context="search_fdr_event_schemas")
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "platform"],
            context="search_fdr_event_schemas",
        )

    def test_search_fdr_field_schemas_returns_details(self):
        """Validate two-step field schema search flow."""
        result = self.call_method(
            self.module.search_fdr_field_schemas,
            filter="name:'AzureFirewallRuleType'",
            limit=3,
            offset=0,
            sort="name.asc",
        )

        self.assert_no_error(result, context="search_fdr_field_schemas")
        self.assert_valid_list_response(result, min_length=1, context="search_fdr_field_schemas")
        self.assert_search_returns_details(
            result,
            expected_fields=["id", "name", "type"],
            context="search_fdr_field_schemas",
        )
