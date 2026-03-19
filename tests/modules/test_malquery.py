"""Tests for the MalQuery module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.malquery import WRITE_ANNOTATIONS, MalQueryModule
from tests.modules.utils.test_modules import TestModules


class TestMalQueryModule(TestModules):
    """Test cases for the MalQuery module."""

    def setUp(self):
        self.setup_module(MalQueryModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_get_malquery_quotas",
            "falcon_fuzzy_search_malquery",
            "falcon_exact_search_malquery",
            "falcon_hunt_malquery",
            "falcon_get_malquery_request",
            "falcon_get_malquery_metadata",
            "falcon_get_malquery_samples_archive",
            "falcon_schedule_malquery_samples_multidownload",
            "falcon_download_malquery_sample",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_malquery_usage_guide",
            "falcon_malquery_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_malquery_quotas", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_exact_search_malquery", WRITE_ANNOTATIONS)

    def test_exact_search_malquery_confirm_required(self):
        result = self.module.exact_search_malquery(confirm_execution=False, patterns=[{"type": "ascii", "value": "abc"}])
        self.assertIn("error", result[0])

    def test_download_malquery_sample_validation(self):
        result = self.module.download_malquery_sample(ids=None)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
