"""Regression tests for issue #325.

Assert that tools/list responses omit outputSchema. The unconditional
emission inflated per-tool payload and caused context-budget-constrained
clients (VS Code Copilot) to silently drop tools.
"""

import unittest
from unittest.mock import MagicMock, patch

from mcp.shared.memory import create_connected_server_and_client_session

from falcon_mcp.modules.generated_falconpy import FALCONPY_1_6_6_SERVICE_COLLECTIONS
from falcon_mcp.server import FalconMCPServer


class TestToolsListOutputSchema(unittest.IsolatedAsyncioTestCase):
    """In-process tools/list assertions for issue #325."""

    def setUp(self):
        patcher = patch("falcon_mcp.server.FalconClient")
        self.mock_client_cls = patcher.start()
        self.addCleanup(patcher.stop)

        mock_client = MagicMock()
        mock_client.authenticate.return_value = True
        mock_client.is_authenticated.return_value = True
        self.mock_client_cls.return_value = mock_client

        self.mcp_server = FalconMCPServer()

    async def test_every_tool_omits_output_schema(self):
        """No tool returned by tools/list may declare outputSchema.

        outputSchema is intended for post-call structured output validation
        per MCP 2025-11-25, not tool selection. Including it in tools/list
        doubles per-tool payload for typed return values and pushes the
        full catalogue past VS Code Copilot's context budget.
        """
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            tools = (await session.list_tools()).tools

        self.assertGreater(len(tools), 0, "FalconMCPServer registered no tools")

        offenders = [t.name for t in tools if t.outputSchema is not None]
        self.assertFalse(
            offenders,
            "Tools must not declare outputSchema in tools/list (issue #325). "
            "Offending tools:\n"
            + "\n".join(f"  - {name}" for name in sorted(offenders)),
        )

    async def test_every_tool_still_has_input_schema(self):
        """Disabling structured output must not affect inputSchema emission."""
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            tools = (await session.list_tools()).tools

        missing = [t.name for t in tools if not t.inputSchema]
        self.assertFalse(
            missing,
            "Tools missing inputSchema (regression of issue #325 fix):\n"
            + "\n".join(f"  - {name}" for name in sorted(missing)),
        )

    async def test_falconpy_1_6_6_tool_input_schemas_have_array_items(self):
        async with create_connected_server_and_client_session(
            self.mcp_server.server
        ) as session:
            tools = (await session.list_tools()).tools

        prefixes = tuple(f"falcon_{key}_" for key in FALCONPY_1_6_6_SERVICE_COLLECTIONS)
        for prefix in prefixes:
            self.assertTrue(any(tool.name.startswith(prefix) for tool in tools), prefix)

        def check_array_items(value, path):
            if isinstance(value, dict):
                if value.get("type") == "array":
                    self.assertIn("items", value, path)
                for key, nested in value.items():
                    check_array_items(nested, f"{path}.{key}")
            elif isinstance(value, list):
                for index, nested in enumerate(value):
                    check_array_items(nested, f"{path}[{index}]")

        for tool in tools:
            if tool.name.startswith(prefixes):
                check_array_items(tool.inputSchema, tool.name)


if __name__ == "__main__":
    unittest.main()
