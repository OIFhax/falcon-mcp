"""Integration tests for the Device Content module."""

import pytest

from falcon_mcp.modules.device_content import DeviceContentModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDeviceContentIntegration(BaseIntegrationTest):
    """Integration tests for Device Content with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = DeviceContentModule(falcon_client)

    @staticmethod
    def _normalize_search_result(result):
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    def test_query_device_content_state_ids_operation_name(self):
        result = self.call_method(
            self.module.query_device_content_state_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        result = self._normalize_search_result(result)
        self.assert_no_error(result, context="query_device_content_state_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_device_content_state_ids")

    def test_search_device_content_states_operation_name(self):
        result = self.call_method(
            self.module.search_device_content_states,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        result = self._normalize_search_result(result)
        self.assert_no_error(result, context="search_device_content_states")
        self.assert_valid_list_response(result, min_length=0, context="search_device_content_states")
