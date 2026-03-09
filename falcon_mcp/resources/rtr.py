"""
Contains Real Time Response (RTR) resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_RTR_SESSIONS_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "aid",
        "String",
        "Falcon agent ID for the host tied to the RTR session.",
    ),
    (
        "date_created",
        "Timestamp",
        "Session creation time.",
    ),
    (
        "date_deleted",
        "Timestamp",
        "Session deletion time, when present.",
    ),
    (
        "date_updated",
        "Timestamp",
        "Last session update time.",
    ),
    (
        "session_id",
        "String",
        "RTR session identifier.",
    ),
    (
        "user_id",
        "String",
        "User identifier that created the session. Supports `@me` in filters.",
    ),
]

SEARCH_RTR_SESSIONS_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("date_created", "Sort by session creation time"),
    ("date_updated", "Sort by last update time"),
    ("date_deleted", "Sort by deletion time"),
    ("session_id", "Sort by session ID"),
    ("user_id", "Sort by user ID"),
]

SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION = f"""
# RTR Session Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_rtr_sessions`.

## Filter Fields

{generate_md_table(SEARCH_RTR_SESSIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_RTR_SESSIONS_FQL_SORT_FIELDS)}

## Examples

- Sessions created by the current user:
  - `filter="user_id:'@me'"`
- Sessions for a specific host:
  - `filter="aid:'1234567890abcdef1234567890abcdef'"`
- Most recent sessions first:
  - `sort="date_created.desc"`

## Notes

- Start with broad filters and narrow gradually.
- Validate filters in a test environment before production use.
"""
