"""Tests for the ThreatGraph module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.threatgraph import ThreatGraphModule
from tests.modules.utils.test_modules import TestModules


class TestThreatGraphModule(TestModules):
    """Test cases for the ThreatGraph module."""

    def setUp(self):
        self.setup_module(ThreatGraphModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_get_threatgraph_edge_types",
            "falcon_get_threatgraph_edges",
            "falcon_get_threatgraph_ran_on",
            "falcon_get_threatgraph_summary",
            "falcon_get_threatgraph_vertices_v1",
            "falcon_get_threatgraph_vertices_v2",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        self.assert_resources_registered(["falcon_threatgraph_usage_guide"])

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_threatgraph_edge_types", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_threatgraph_vertices_v2", READ_ONLY_ANNOTATIONS)

    def test_get_threatgraph_edges_validation(self):
        result = self.module.get_threatgraph_edges(ids=None, edge_type=None)
        self.assertIn("error", result[0])

    def test_get_threatgraph_ran_on_validation(self):
        result = self.module.get_threatgraph_ran_on(type=None, value=None)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
