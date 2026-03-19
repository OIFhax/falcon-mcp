"""
Tests for the Sensor Visibility Exclusions module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.sensor_visibility_exclusions import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    SensorVisibilityExclusionsModule,
)
from tests.modules.utils.test_modules import TestModules


class TestSensorVisibilityExclusionsModule(TestModules):
    """Test cases for the Sensor Visibility Exclusions module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(SensorVisibilityExclusionsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_sensor_visibility_exclusions",
            "falcon_query_sensor_visibility_exclusion_ids",
            "falcon_get_sensor_visibility_exclusion_details",
            "falcon_create_sensor_visibility_exclusions",
            "falcon_update_sensor_visibility_exclusions",
            "falcon_delete_sensor_visibility_exclusions",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_sensor_visibility_exclusions_fql_guide",
            "falcon_sensor_visibility_exclusions_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_search_sensor_visibility_exclusions",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_create_sensor_visibility_exclusions",
            WRITE_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_delete_sensor_visibility_exclusions",
            DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def test_search_sensor_visibility_exclusions_success(self):
        """Test sensor visibility exclusion search success."""
        result_details = [{"id": "id-1", "value": "test"}]
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"resources": ["id-1"]}},
            {"status_code": 200, "body": {"resources": result_details}},
        ]

        result = self.module.search_sensor_visibility_exclusions(
            filter="applied_globally:true",
            limit=10,
            offset=0,
            sort="value.asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(result, result_details)

    def test_query_sensor_visibility_exclusion_ids_empty_filter_returns_guide(self):
        """Test empty ID query with filter returns FQL helper response."""
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_sensor_visibility_exclusion_ids(
            filter="value:'NotReal*'",
            limit=100,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_get_sensor_visibility_exclusion_details_validation_and_success(self):
        """Test detail validation and success."""
        validation_result = self.module.get_sensor_visibility_exclusion_details(ids=None)
        self.assertIn("error", validation_result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "id-1"}]},
        }
        success_result = self.module.get_sensor_visibility_exclusion_details(ids=["id-1"])

        self.mock_client.command.assert_called_once_with(
            "getSensorVisibilityExclusionsV1",
            parameters={"ids": ["id-1"]},
        )
        self.assertEqual(len(success_result), 1)
        self.assertEqual(success_result[0]["id"], "id-1")

    def test_create_sensor_visibility_exclusions_confirm_required(self):
        """Test create requires confirm_execution=true."""
        result = self.module.create_sensor_visibility_exclusions(
            confirm_execution=False,
            comment=None,
            groups=None,
            value="test",
            body=None,
        )
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_sensor_visibility_exclusions_requires_update_fields(self):
        """Test update requires ID and at least one update field."""
        result = self.module.update_sensor_visibility_exclusions(
            confirm_execution=True,
            id="id-1",
            comment=None,
            groups=None,
            is_descendant_process=None,
            value=None,
            body=None,
        )
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_sensor_visibility_exclusions_success(self):
        """Test delete success path."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"deleted": 1}]},
        }

        result = self.module.delete_sensor_visibility_exclusions(
            confirm_execution=True,
            ids=["id-1"],
            comment="cleanup",
        )

        self.mock_client.command.assert_called_once_with(
            "deleteSensorVisibilityExclusionsV1",
            parameters={"ids": ["id-1"], "comment": "cleanup"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["deleted"], 1)


if __name__ == "__main__":
    unittest.main()
