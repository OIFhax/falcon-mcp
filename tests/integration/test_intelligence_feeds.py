"""Integration tests for the Intelligence Feeds module."""

from typing import Any

import pytest

from falcon_mcp.modules.intelligence_feeds import IntelligenceFeedsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestIntelligenceFeedsIntegration(BaseIntegrationTest):
    """Integration tests for Intelligence Feeds with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = IntelligenceFeedsModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_list_intelligence_feeds_operation_name(self):
        result = self.call_method(self.module.list_intelligence_feeds)

        self.assert_no_error(result, context="list_intelligence_feeds")
        self.assert_valid_list_response(result, min_length=0, context="list_intelligence_feeds")

    def test_query_intelligence_feed_archives_operation_name(self):
        feeds = self.call_method(self.module.list_intelligence_feeds)
        self.assert_no_error(feeds, context="list_intelligence_feeds setup")
        self.assert_valid_list_response(feeds, min_length=1, context="list_intelligence_feeds setup")

        feed_name = feeds[0].get("name") if isinstance(feeds[0], dict) else None
        if not isinstance(feed_name, str) or not feed_name:
            self.skip_with_warning(
                "No usable feed name returned for archive query validation",
                context="query_intelligence_feed_archives",
            )

        result = self.call_method(
            self.module.query_intelligence_feed_archives,
            feed_name=feed_name,
        )

        self.assert_no_error(result, context="query_intelligence_feed_archives")
        self.assert_valid_list_response(result, min_length=0, context="query_intelligence_feed_archives")

    def test_download_intelligence_feed_archive_invalid_id(self):
        result = self.call_method(
            self.module.download_intelligence_feed_archive,
            feed_item_id="00000000000000000000000000000000",
        )

        status_code = self._extract_status_code(result)
        if status_code in (400, 404, 422):
            return

        self.assert_no_error(result, context="download_intelligence_feed_archive")
