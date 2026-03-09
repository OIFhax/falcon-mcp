"""Integration tests for the IOA Exclusions module."""

import pytest

from falcon_mcp.modules.ioa_exclusions import IOAExclusionsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIOAExclusionsIntegration(BaseIntegrationTest):
    """Integration tests for IOA Exclusions module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the IOA Exclusions module with a real client."""
        self.module = IOAExclusionsModule(falcon_client)

    def test_operation_names_are_correct(self):
        """Validate operation names by executing a minimal IOA exclusions query."""
        result = self.call_method(
            self.module.search_ioa_exclusions,
            filter=None,
            ifn_regex=None,
            cl_regex=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self.assert_no_error(result, context="operation name validation")

    def test_search_ioa_exclusions_returns_details(self):
        """Test that search_ioa_exclusions returns full details, not only IDs."""
        result = self.call_method(
            self.module.search_ioa_exclusions,
            filter=None,
            ifn_regex=None,
            cl_regex=None,
            limit=5,
            offset=0,
            sort=None,
        )

        self.assert_no_error(result, context="search_ioa_exclusions")
        self.assert_valid_list_response(result, min_length=0, context="search_ioa_exclusions")

        if len(result) > 0:
            self.assert_search_returns_details(
                result,
                expected_fields=["id", "name"],
                context="search_ioa_exclusions",
            )
