"""Tests for the Drift Indicators module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.drift_indicators import DriftIndicatorsModule
from tests.modules.utils.test_modules import TestModules


class TestDriftIndicatorsModule(TestModules):
    """Test cases for the Drift Indicators module."""

    def setUp(self):
        self.setup_module(DriftIndicatorsModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_get_drift_indicator_values_by_date",
            "falcon_get_drift_indicator_count",
            "falcon_query_drift_indicator_ids",
            "falcon_get_drift_indicator_details",
            "falcon_search_drift_indicator_entities",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_drift_indicators_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_drift_indicator_values_by_date", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_drift_indicator_entities", READ_ONLY_ANNOTATIONS)

    def test_get_drift_indicator_values_by_date_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"name": "2026-03-18", "buckets": 12}]},
        }

        result = self.module.get_drift_indicator_values_by_date(
            filter="prevented:'true'",
            limit=7,
        )

        self.mock_client.command.assert_called_once_with(
            "GetDriftIndicatorsValuesByDate",
            parameters={"filter": "prevented:'true'", "limit": 7},
        )
        self.assertEqual(result[0]["buckets"], 12)

    def test_get_drift_indicator_count_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"count": 42}]},
        }

        result = self.module.get_drift_indicator_count(filter="cloud_name:'aws'")

        self.mock_client.command.assert_called_once_with(
            "ReadDriftIndicatorsCount",
            parameters={"filter": "cloud_name:'aws'"},
        )
        self.assertEqual(result[0]["count"], 42)

    def test_query_drift_indicator_ids_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["abc123"]},
        }

        result = self.module.query_drift_indicator_ids(
            filter="prevented:'true'",
            limit=1,
            offset=0,
            sort="occurred_at.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "SearchDriftIndicators",
            parameters={
                "filter": "prevented:'true'",
                "limit": 1,
                "offset": 0,
                "sort": "occurred_at.desc",
            },
        )
        self.assertEqual(result, ["abc123"])

    def test_get_drift_indicator_details_validation_and_success(self):
        result = self.module.get_drift_indicator_details(ids=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"agent_id": "aid-1", "severity": "low"}]},
        }

        result = self.module.get_drift_indicator_details(ids=["abc123"])

        self.mock_client.command.assert_called_once_with(
            "ReadDriftIndicatorEntities",
            parameters={"ids": ["abc123"]},
        )
        self.assertEqual(result[0]["agent_id"], "aid-1")

    def test_search_drift_indicator_entities_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"aid": "aid-1", "severity": "medium"}]},
        }

        result = self.module.search_drift_indicator_entities(
            filter="prevented:'true'",
            limit=1,
            offset=0,
            sort="occurred_at.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "SearchAndReadDriftIndicatorEntities",
            parameters={
                "filter": "prevented:'true'",
                "limit": 1,
                "offset": 0,
                "sort": "occurred_at.desc",
            },
        )
        self.assertEqual(result[0]["severity"], "medium")


if __name__ == "__main__":
    unittest.main()
