"""Tests for the Correlation Rules module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.correlation_rules import (
    DESTRUCTIVE_WRITE_ANNOTATIONS,
    WRITE_ANNOTATIONS,
    CorrelationRulesModule,
)
from tests.modules.utils.test_modules import TestModules


class TestCorrelationRulesModule(TestModules):
    """Test cases for the Correlation Rules module."""

    def setUp(self):
        self.setup_module(CorrelationRulesModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_search_correlation_rules_v1",
            "falcon_search_correlation_rules_v2",
            "falcon_query_correlation_rule_ids",
            "falcon_query_correlation_rule_version_ids",
            "falcon_get_correlation_rules",
            "falcon_get_correlation_rule_versions",
            "falcon_get_latest_correlation_rule_versions",
            "falcon_aggregate_correlation_rule_versions",
            "falcon_create_correlation_rule",
            "falcon_update_correlation_rule",
            "falcon_delete_correlation_rules",
            "falcon_export_correlation_rule_versions",
            "falcon_import_correlation_rule",
            "falcon_publish_correlation_rule_version",
            "falcon_delete_correlation_rule_versions",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_correlation_rules_fql_guide",
            "falcon_correlation_rules_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_correlation_rules_v1", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_create_correlation_rule", WRITE_ANNOTATIONS)
        self.assert_tool_annotations("falcon_delete_correlation_rules", DESTRUCTIVE_WRITE_ANNOTATIONS)

    def test_create_correlation_rule_confirm_required(self):
        result = self.module.create_correlation_rule(confirm_execution=False, body={"name": "x"})
        self.assertIn("error", result[0])

    def test_query_correlation_rule_ids_empty_filter_returns_guide(self):
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}
        result = self.module.query_correlation_rule_ids(filter="name:'missing'", q=None, sort=None, offset=0, limit=10)
        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)


if __name__ == "__main__":
    unittest.main()
