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

SEARCH_RTR_ADMIN_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "created_at",
        "Timestamp",
        "Entity creation time for scripts or put-files.",
    ),
    (
        "description",
        "String",
        "Description text for scripts or put-files.",
    ),
    (
        "id",
        "String",
        "Script or put-file identifier.",
    ),
    (
        "modified_at",
        "Timestamp",
        "Last modification timestamp.",
    ),
    (
        "name",
        "String",
        "Script or put-file name.",
    ),
    (
        "platform",
        "String",
        "Target platform for script entities.",
    ),
    (
        "user_id",
        "String",
        "Owner / creator user identifier.",
    ),
]

SEARCH_RTR_ADMIN_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("created_at", "Sort by creation time"),
    ("modified_at", "Sort by last modification time"),
    ("name", "Sort by name"),
    ("platform", "Sort by platform"),
    ("user_id", "Sort by user ID"),
]

SEARCH_RTR_ADMIN_FQL_DOCUMENTATION = f"""
# RTR Admin Search FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_rtr_admin_scripts`
- `falcon_search_rtr_admin_put_files`

## Filter Fields

{generate_md_table(SEARCH_RTR_ADMIN_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_RTR_ADMIN_FQL_SORT_FIELDS)}

## Examples

- Scripts created by the current user:
  - `filter="user_id:'@me'"`
- Script names matching a prefix:
  - `filter="name:'triage*'"`
- Most recently created entities first:
  - `sort="created_at.desc"`

## Notes

- Field support can vary slightly between scripts and put-files.
- Validate filters in a test environment before production use.
"""

SEARCH_RTR_AUDIT_SESSIONS_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "aid",
        "String",
        "Falcon agent ID associated with the audited session.",
    ),
    (
        "created_at",
        "Timestamp",
        "Session creation timestamp.",
    ),
    (
        "deleted_at",
        "Timestamp",
        "Session deletion timestamp when present.",
    ),
    (
        "session_id",
        "String",
        "Audited RTR session identifier.",
    ),
    (
        "updated_at",
        "Timestamp",
        "Last session update timestamp.",
    ),
    (
        "user_id",
        "String",
        "User identifier that created the audited session.",
    ),
]

SEARCH_RTR_AUDIT_SESSIONS_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("created_at", "Sort by session creation time"),
    ("updated_at", "Sort by session update time"),
    ("deleted_at", "Sort by session deletion time"),
]

SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION = f"""
# RTR Audit Sessions FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_rtr_audit_sessions`.

## Filter Fields

{generate_md_table(SEARCH_RTR_AUDIT_SESSIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_RTR_AUDIT_SESSIONS_FQL_SORT_FIELDS)}

## Examples

- Audit sessions by the current user:
  - `filter="user_id:'@me'"`
- Newest audit sessions first:
  - `sort="created_at.desc"`

## Notes

- Set `with_command_info=true` in `falcon_search_rtr_audit_sessions` to include command details.
- Validate filters in a test environment before production use.
"""
