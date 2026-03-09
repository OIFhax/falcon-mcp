"""
Contains User Management resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_USERS_FQL_FILTER_FIELDS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    ("assigned_cids", "String/List", "CIDs assigned to the user."),
    ("cid", "String", "Primary CID for the user."),
    ("direct_assigned_cids", "String/List", "Directly assigned CIDs."),
    ("factors", "String/List", "Authentication factors associated with the user."),
    ("first_name", "String", "User first name."),
    ("has_temporary_roles", "Boolean", "Whether user currently has temporary role grants."),
    ("last_name", "String", "User last name."),
    ("name", "String", "Display name for the user."),
    ("status", "String", "User state (for example active/disabled depending on tenant)."),
    ("temporarily_assigned_cids", "String/List", "Temporarily assigned CIDs."),
    ("uid", "String", "User login identifier (typically email)."),
    ("uuid", "String", "User UUID."),
]

SEARCH_USERS_SORT_FIELDS = [
    ("Field", "Description"),
    ("cid_name", "Sort by CID name"),
    ("created_at", "Sort by account creation time"),
    ("first_name", "Sort by first name"),
    ("has_temporary_roles", "Sort by temporary-role state"),
    ("last_login_at", "Sort by last login time"),
    ("last_name", "Sort by last name"),
    ("name", "Sort by display name"),
    ("status", "Sort by user status"),
    ("temporarily_assigned_cids", "Sort by temporary CID assignments"),
    ("uid", "Sort by user login identifier"),
]

USER_ROLE_GRANTS_FQL_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("expires_at", "Timestamp", "Role assignment expiration timestamp."),
    ("role_id", "String", "Role identifier."),
    ("role_name", "String", "Role name."),
]

USER_ROLE_GRANTS_SORT_FIELDS = [
    ("Field", "Description"),
    ("cid", "Sort by customer ID"),
    ("expires_at", "Sort by grant expiration time"),
    ("role_name", "Sort by role name"),
    ("type", "Sort by grant type"),
    ("user_uuid", "Sort by user UUID"),
]

SEARCH_USERS_FQL_DOCUMENTATION = f"""
# User Management: Search Users FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_users`.
This tool uses the Falcon User Management service (`queryUserV1`).

## Filter Fields

{generate_md_table(SEARCH_USERS_FQL_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_USERS_SORT_FIELDS)}

## Examples

- Search by login/email:
  - `filter="uid:'analyst@example.com'"`
- Search active users:
  - `filter="status:'active'"`
- Most recent logins first:
  - `sort="last_login_at.desc"`
"""

USER_ROLE_GRANTS_FQL_DOCUMENTATION = f"""
# User Management: User Role Grants FQL Guide

Use this guide to build the `filter` parameter for `falcon_get_user_role_grants`.
This tool uses `CombinedUserRolesV2`.

## Filter Fields

{generate_md_table(USER_ROLE_GRANTS_FQL_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(USER_ROLE_GRANTS_SORT_FIELDS)}

## Examples

- Show grants for one role name:
  - `filter="role_name:'Falcon Administrator'"`
- Show grants expiring soon:
  - `sort="expires_at.asc"`
"""

USER_MANAGEMENT_SAFETY_GUIDE = """
# User Management Safety Guide

User Management tools can change access across your Falcon tenant.

## Operational guardrails

- Use a dedicated API client for IAM automation and apply least privilege scopes.
- Run in a separate MCP instance from endpoint-response modules when possible.
- Keep write actions gated with `confirm_execution=true`.
- Prefer read-only discovery tools first (`search_users`, `search_user_roles`, `get_user_role_grants`).
- Log all user and role changes through your internal change-control process.

## High-impact tool sequence

1. `search_users` and confirm the target `uuid`.
2. `search_user_roles` and confirm intended role IDs.
3. Execute a single write action with `confirm_execution=true`.
4. Re-check role grants using `get_user_role_grants`.
"""

