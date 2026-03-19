"""
Contains Intelligence Feeds resources.
"""

INTELLIGENCE_FEEDS_USAGE_GUIDE = """
# Intelligence Feeds Guide

Use `falcon_list_intelligence_feeds` to see the feed types available to the current tenant.

Use `falcon_query_intelligence_feed_archives` to find downloadable feed archives.

Use `falcon_download_intelligence_feed_archive` to request an archive by `feed_item_id`.

## Notes

- Archive downloads are binary zip payloads and are not rendered inline by default.
- Use query tools first so you can select a valid `feed_item_id`.
"""
