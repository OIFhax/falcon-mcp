"""Integration tests for the API Integrations module."""

from typing import Any

import pytest

from falcon_mcp.modules.api_integrations import APIIntegrationsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestAPIIntegrationsIntegration(BaseIntegrationTest):
    """Integration tests for API Integrations with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = APIIntegrationsModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_search_api_integration_plugin_configs_operation_name(self):
        result = self.call_method(
            self.module.search_api_integration_plugin_configs,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self.assert_no_error(result, context="search_api_integration_plugin_configs")
        self.assert_valid_list_response(result, min_length=0, context="search_api_integration_plugin_configs")

    def test_execute_api_integration_command_invalid_payload(self):
        result = self.call_method(
            self.module.execute_api_integration_command,
            confirm_execution=True,
            body={"resources": [{"id": "invalid.plugin", "operation_id": "invalid-operation"}]},
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required api-integrations:write scope for write validation",
                context="execute_api_integration_command",
            )
        if status_code in (400, 404, 409, 422):
            return

        self.assert_no_error(result, context="execute_api_integration_command_invalid_payload")
