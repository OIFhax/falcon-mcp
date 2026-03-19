"""Integration tests for the Delivery Settings module."""

from typing import Any

import pytest

from falcon_mcp.modules.delivery_settings import DeliverySettingsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDeliverySettingsIntegration(BaseIntegrationTest):
    """Integration tests for Delivery Settings with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = DeliverySettingsModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        if isinstance(result, dict):
            details = result.get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
        return None

    def test_get_delivery_settings_operation_name(self):
        result = self.call_method(self.module.get_delivery_settings)

        self.assert_no_error(result, context="get_delivery_settings")
        self.assert_valid_list_response(result, min_length=0, context="get_delivery_settings")

    def test_create_delivery_settings_invalid_payload(self):
        result = self.call_method(
            self.module.create_delivery_settings,
            confirm_execution=True,
            body={
                "delivery_settings": [
                    {
                        "delivery_type": "invalid-type-for-integration-test",
                        "delivery_cadence": "invalid-cadence-for-integration-test",
                    }
                ]
            },
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required delivery-settings:write scope for write validation",
                context="create_delivery_settings",
            )
        if status_code in (400, 404, 409, 422):
            return

        self.assert_no_error(result, context="create_delivery_settings_invalid_payload")
