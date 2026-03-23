"""Tests for the Quick Scan module."""

import asyncio
import unittest

from mcp.server.fastmcp import FastMCP

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.quick_scan import (
    WRITE_ANNOTATIONS,
    QuickScanModule,
)
from tests.modules.utils.test_modules import TestModules


class TestQuickScanModule(TestModules):
    """Test cases for the Quick Scan module."""

    def setUp(self):
        self.setup_module(QuickScanModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_search_quick_scans",
            "falcon_query_quick_scan_ids",
            "falcon_get_quick_scans",
            "falcon_aggregate_quick_scans",
            "falcon_scan_quick_samples",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_quick_scan_fql_guide",
            "falcon_quick_scan_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_quick_scans", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_scan_quick_samples", WRITE_ANNOTATIONS)

    def test_query_quick_scan_ids_empty_filter_returns_guide(self):
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}
        result = self.module.query_quick_scan_ids(filter="name:'not-real'", limit=10, offset=0, sort=None)
        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)

    def test_aggregate_quick_scans_validation(self):
        result = self.module.aggregate_quick_scans(body=None)
        self.assertIn("error", result[0])

    def test_aggregate_quick_scans_schema_has_typed_sub_aggregates_items(self):
        server = FastMCP("test")
        self.module.register_tools(server)

        async def get_input_schema():
            tools = await server.list_tools()
            for tool in tools:
                if tool.name == "falcon_aggregate_quick_scans":
                    return tool.inputSchema
            self.fail("falcon_aggregate_quick_scans was not registered")

        input_schema = asyncio.run(get_input_schema())
        sub_aggregates_schema = input_schema["properties"]["sub_aggregates"]
        array_schema = next(
            schema for schema in sub_aggregates_schema["anyOf"] if schema.get("type") == "array"
        )

        self.assertIn("items", array_schema)
        self.assertEqual(
            array_schema["items"],
            {"additionalProperties": True, "type": "object"},
        )

    def test_scan_quick_samples_confirm_required(self):
        result = self.module.scan_quick_samples(confirm_execution=False, samples=["0" * 64])
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
