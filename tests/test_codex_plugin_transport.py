"""Exercise the plugin entrypoint over real stdio without contacting Falcon."""

import json
import sys
from datetime import timedelta
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent


async def test_plugin_stdio_roundtrip_from_unrelated_directory(tmp_path):
    """Initialization, discovery, resources, and startup check survive the CLI boundary."""
    consumer = tmp_path / "unrelated project with spaces"
    consumer.mkdir()
    (consumer / ".env").write_text(
        "FALCON_MCP_MODULES=not_a_module\nFALCON_MCP_TRANSPORT=sse\n", encoding="utf-8"
    )
    # Only the HTTP client is stubbed. The credential loader, server, modules,
    # serialization, subprocess streams, and MCP session are real.
    bootstrap = """
import runpy
from unittest.mock import patch
with patch('falcon_mcp.client.APIHarnessV2') as harness:
    harness.return_value.login.return_value = True
    harness.return_value._login_handler.return_value = {'status_code': 201}
    runpy.run_module('falcon_mcp.codex_plugin', run_name='__main__')
"""
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-c", bootstrap],
        cwd=consumer,
        env={
            "PYTHONPATH": str(Path(__file__).resolve().parents[1]),
            "FALCON_MCP_CONFIG_FILE": str(tmp_path / "absent.json"),
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
            "FALCON_BASE_URL": "https://api.us-2.crowdstrike.com",
            "FALCON_MCP_MODULES": "hosts",
            "FALCON_MCP_TRANSPORT": "streamable-http",
        },
    )
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(
            reader, writer, read_timeout_seconds=timedelta(seconds=30)
        ) as session:
            initialized = await session.initialize()
            assert initialized.serverInfo.name == "Falcon MCP Server"
            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            assert {"falcon_startup_check", "falcon_search_hosts"} <= tool_names
            resources = await session.list_resources()
            assert any(
                str(resource.uri).startswith("falcon://hosts/") for resource in resources.resources
            )
            result = await session.call_tool("falcon_startup_check")
            assert not result.isError
            payload = json.loads(
                next(item.text for item in result.content if isinstance(item, TextContent))
            )
            assert payload["connected"] is True
            assert payload["enabled_modules"] == ["hosts"]
            assert "falcon_search_hosts" in payload["declared_tools"]
            assert payload["region"] == "us-2"
