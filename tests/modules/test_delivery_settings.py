"""Tests for the Delivery Settings module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.delivery_settings import (
    WRITE_ANNOTATIONS,
    DeliverySettingsModule,
)
from tests.modules.utils.test_modules import TestModules


class TestDeliverySettingsModule(TestModules):
    """Test cases for the Delivery Settings module."""

    def setUp(self):
        self.setup_module(DeliverySettingsModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_get_delivery_settings",
            "falcon_create_delivery_settings",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_delivery_settings_usage_guide",
            "falcon_delivery_settings_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_delivery_settings", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_delivery_settings", WRITE_ANNOTATIONS)

    def test_get_delivery_settings_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"delivery_type": "sample", "delivery_cadence": "daily"}]},
        }

        result = self.module.get_delivery_settings()

        self.mock_client.command.assert_called_once_with("GetDeliverySettings")
        self.assertEqual(result[0]["delivery_type"], "sample")

    def test_create_delivery_settings_confirm_required(self):
        result = self.module.create_delivery_settings(
            confirm_execution=False,
            delivery_type="sample",
            delivery_cadence="daily",
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_delivery_settings_success(self):
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"delivery_type": "sample", "delivery_cadence": "daily"}]},
        }

        result = self.module.create_delivery_settings(
            confirm_execution=True,
            delivery_type="sample",
            delivery_cadence="daily",
        )

        self.mock_client.command.assert_called_once_with(
            "PostDeliverySettings",
            body={
                "delivery_settings": [
                    {
                        "delivery_cadence": "daily",
                        "delivery_type": "sample",
                    }
                ]
            },
        )
        self.assertEqual(result[0]["delivery_cadence"], "daily")


if __name__ == "__main__":
    unittest.main()
