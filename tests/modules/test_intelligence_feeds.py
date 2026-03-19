"""Tests for the Intelligence Feeds module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.intelligence_feeds import IntelligenceFeedsModule
from tests.modules.utils.test_modules import TestModules


class TestIntelligenceFeedsModule(TestModules):
    """Test cases for the Intelligence Feeds module."""

    def setUp(self):
        self.setup_module(IntelligenceFeedsModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_list_intelligence_feeds",
            "falcon_query_intelligence_feed_archives",
            "falcon_download_intelligence_feed_archive",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        self.assert_resources_registered(["falcon_intelligence_feeds_usage_guide"])

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_list_intelligence_feeds", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_download_intelligence_feed_archive", READ_ONLY_ANNOTATIONS)

    def test_download_intelligence_feed_archive_validation(self):
        result = self.module.download_intelligence_feed_archive(feed_item_id=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_query_intelligence_feed_archives_validation(self):
        result = self.module.query_intelligence_feed_archives(feed_name=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_download_intelligence_feed_archive_binary_response(self):
        self.mock_client.command.return_value = b"zip-bytes"

        result = self.module.download_intelligence_feed_archive(feed_item_id="item-1")

        self.assertEqual(result[0]["operation"], "DownloadFeedArchive")
        self.assertEqual(result[0]["size_bytes"], 9)


if __name__ == "__main__":
    unittest.main()
