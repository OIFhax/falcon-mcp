"""Tests for the ThreatGraph module."""

import inspect
import unittest
from typing import get_args

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

    def test_get_threatgraph_ran_on_indicator_types_are_constrained(self):
        annotation = (
            inspect.signature(self.module.get_threatgraph_ran_on).parameters["type"].annotation
        )
        union_args = get_args(annotation)
        literal_args = next(args for args in union_args if get_args(args))

        self.assertEqual(
            set(get_args(literal_args)),
            {"domain", "ipv4", "ipv6", "md5", "sha1", "sha256"},
        )

    def test_get_threatgraph_ran_on_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "vertex-1"}]},
        }

        result = self.module.get_threatgraph_ran_on(
            type="ipv4",
            value="192.0.2.1",
            limit=10,
            offset=0,
            nano=False,
        )

        self.mock_client.command.assert_called_once_with(
            "combined_ran_on_get",
            parameters={
                "type": "ipv4",
                "value": "192.0.2.1",
                "limit": 10,
                "offset": 0,
                "nano": False,
            },
        )
        self.assertEqual(result, [{"id": "vertex-1"}])

    def test_get_threatgraph_ran_on_404_is_empty_result(self):
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"message": "resource not found"}]},
        }

        result = self.module.get_threatgraph_ran_on(
            type="domain",
            value="example.invalid",
        )

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
