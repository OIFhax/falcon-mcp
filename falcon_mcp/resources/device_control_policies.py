"""
Contains Device Control Policies resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_DEVICE_CONTROL_POLICIES_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Device control policy identifier."),
    ("name", "String", "Device control policy name."),
    ("platform_name", "String", "Target platform name."),
    ("enabled", "Boolean", "Policy enablement state."),
    ("created_timestamp", "Timestamp", "Policy creation timestamp."),
    ("modified_timestamp", "Timestamp", "Policy last modification timestamp."),
]

SEARCH_DEVICE_CONTROL_POLICIES_SORT_FIELDS = [
    ("Field", "Description"),
    ("created_by", "Sort by policy creator."),
    ("created_timestamp", "Sort by creation timestamp."),
    ("enabled", "Sort by enabled state."),
    ("modified_by", "Sort by last modifier."),
    ("modified_timestamp", "Sort by last modification timestamp."),
    ("name", "Sort by policy name."),
    ("platform_name", "Sort by target platform."),
    ("precedence", "Sort by policy precedence."),
]

SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("device_id", "String", "Host device identifier."),
    ("hostname", "String", "Host name."),
    ("platform_name", "String", "Host platform name."),
    ("policy_id", "String", "Assigned device control policy ID."),
    ("policy_name", "String", "Assigned device control policy name."),
]

SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_SORT_FIELDS = [
    ("Field", "Description"),
    ("hostname", "Sort by host name."),
    ("platform_name", "Sort by host platform."),
    ("policy_name", "Sort by assigned policy name."),
]

SEARCH_DEVICE_CONTROL_POLICIES_FQL_DOCUMENTATION = f"""
# Device Control Policies: Policies FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_device_control_policies`
- `falcon_query_device_control_policy_ids`

## Filter Fields

{generate_md_table(SEARCH_DEVICE_CONTROL_POLICIES_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_DEVICE_CONTROL_POLICIES_SORT_FIELDS)}
"""

SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_FQL_DOCUMENTATION = f"""
# Device Control Policies: Policy Members FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_device_control_policy_members`
- `falcon_query_device_control_policy_member_ids`

## Filter Fields

{generate_md_table(SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_SORT_FIELDS)}
"""

DEVICE_CONTROL_DEFAULTS_GUIDE = """
# Device Control Policies: Defaults Guide

Default device control configuration is exposed via:

- `falcon_get_default_device_control_policies`
- `falcon_update_default_device_control_policies`
- `falcon_get_default_device_control_settings`
- `falcon_update_default_device_control_settings`
- `falcon_update_device_control_policies_classes`

## Notes

- Use explicit `body` payloads for default and class patch operations.
- Validate payload schema in a test tenant before applying in production.
"""

DEVICE_CONTROL_POLICIES_SAFETY_GUIDE = """
# Device Control Policies Safety Guide

Device control write operations can impact host USB/device enforcement behavior.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer read/search tools to validate target policy IDs before applying changes.
- Use explicit IDs for update/delete/action/precedence operations.
- Validate default and class payloads in non-production tenants before rollout.
- Document expected blast radius for enable/disable and host-group assignment actions.
"""
