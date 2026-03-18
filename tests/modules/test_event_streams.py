"""Tests for the Event Streams module."""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.event_streams import EventStreamsModule
from tests.modules.utils.test_modules import TestModules


class TestEventStreamsModule(TestModules):
    """Test cases for the Event Streams module."""

    def setUp(self):
        self.setup_module(EventStreamsModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_list_event_streams",
            "falcon_refresh_event_stream_session",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_event_streams_usage_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_list_event_streams", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_refresh_event_stream_session",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_list_event_streams_validation(self):
        result = self.module.list_event_streams(app_id=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.reset_mock()
        result = self.module.list_event_streams(app_id="bad-id")
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_list_event_streams_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "dataFeedURL": "https://firehose.example/v1/0?appId=falconmcp01",
                        "refreshActiveSessionInterval": 1800,
                    }
                ]
            },
        }

        result = self.module.list_event_streams(app_id="FalconMCP01", format="flatjson")

        self.mock_client.command.assert_called_once_with(
            "listAvailableStreamsOAuth2",
            parameters={"appId": "FalconMCP01", "format": "flatjson"},
        )
        self.assertEqual(result[0]["refreshActiveSessionInterval"], 1800)

    def test_refresh_event_stream_session_validation(self):
        result = self.module.refresh_event_stream_session(app_id=None, partition=0)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_refresh_event_stream_session_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "partition": 0,
                        "refreshed": True,
                    }
                ]
            },
        }

        result = self.module.refresh_event_stream_session(app_id="FalconMCP01", partition=0)

        self.mock_client.command.assert_called_once_with(
            "refreshActiveStreamSession",
            appId="FalconMCP01",
            partition=0,
            action_name="refresh_active_stream_session",
        )
        self.assertEqual(result[0]["refreshed"], True)


if __name__ == "__main__":
    unittest.main()
