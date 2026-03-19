"""
Contains Content Update Policies resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_CONTENT_UPDATE_POLICIES_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Content update policy identifier."),
    ("name", "String", "Content update policy name."),
    ("description", "String", "Policy description."),
    ("platform_name", "String", "Target platform name."),
    ("enabled", "Boolean", "Policy enablement state."),
    ("created_timestamp", "Timestamp", "Policy creation timestamp."),
    ("modified_timestamp", "Timestamp", "Policy last modification timestamp."),
]

SEARCH_CONTENT_UPDATE_POLICIES_SORT_FIELDS = [
    ("Field", "Description"),
    ("created_by", "Sort by policy creator."),
    ("created_timestamp", "Sort by creation timestamp."),
    ("enabled", "Sort by enabled state."),
    ("modified_by", "Sort by last modifier."),
    ("modified_timestamp", "Sort by last modification timestamp."),
    ("name", "Sort by policy name."),
    ("platform_name", "Sort by target platform."),
]

SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("device_id", "String", "Host device identifier."),
    ("hostname", "String", "Host name."),
    ("platform_name", "String", "Host platform name."),
    ("policy_id", "String", "Assigned content update policy ID."),
    ("policy_name", "String", "Assigned content update policy name."),
]

SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_SORT_FIELDS = [
    ("Field", "Description"),
    ("hostname", "Sort by host name."),
    ("platform_name", "Sort by host platform."),
    ("policy_name", "Sort by assigned policy name."),
]

SEARCH_CONTENT_UPDATE_POLICIES_FQL_DOCUMENTATION = f"""
# Content Update Policies: Policies FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_content_update_policies`
- `falcon_query_content_update_policy_ids`

## Filter Fields

{generate_md_table(SEARCH_CONTENT_UPDATE_POLICIES_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_CONTENT_UPDATE_POLICIES_SORT_FIELDS)}
"""

SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION = f"""
# Content Update Policies: Policy Members FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_content_update_policy_members`
- `falcon_query_content_update_policy_member_ids`

## Filter Fields

{generate_md_table(SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_SORT_FIELDS)}
"""

CONTENT_UPDATE_PINNABLE_VERSIONS_GUIDE = """
# Content Update Policies: Pinnable Versions Guide

Use `falcon_query_content_update_pinnable_versions` to retrieve content versions available for pinning.

## Required input

- `category`: one of:
  - `rapid_response_al_bl_listing`
  - `sensor_operations`
  - `system_critical`
  - `vulnerability_management`

## Optional input

- `sort`: defaults to `deployed_timestamp.desc`
"""

CONTENT_UPDATE_POLICIES_SAFETY_GUIDE = """
# Content Update Policies Safety Guide

Content update policy write operations can change content rollout, allow / pause overrides, host-group assignments, and pinned-content behavior.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer read/search tools to validate target policy IDs before applying changes.
- Use explicit IDs for create/update/delete/action/precedence operations.
- Validate pinned-content changes and override actions in a test tenant first.
- Document the expected operational impact before applying policy-wide actions.
"""
