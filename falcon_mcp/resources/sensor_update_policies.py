"""
Contains Sensor Update Policies resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_SENSOR_UPDATE_POLICIES_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Sensor update policy identifier."),
    ("name", "String", "Sensor update policy name."),
    ("platform_name", "String", "Target platform name."),
    ("enabled", "Boolean", "Policy enablement state."),
    ("created_timestamp", "Timestamp", "Policy creation timestamp."),
    ("modified_timestamp", "Timestamp", "Policy last modification timestamp."),
]

SEARCH_SENSOR_UPDATE_POLICIES_SORT_FIELDS = [
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

SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("device_id", "String", "Host device identifier."),
    ("hostname", "String", "Host name."),
    ("platform_name", "String", "Host platform name."),
    ("policy_id", "String", "Assigned sensor update policy ID."),
    ("policy_name", "String", "Assigned sensor update policy name."),
]

SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_SORT_FIELDS = [
    ("Field", "Description"),
    ("hostname", "Sort by host name."),
    ("platform_name", "Sort by host platform."),
    ("policy_name", "Sort by assigned policy name."),
]

SEARCH_SENSOR_UPDATE_KERNELS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Kernel compatibility record identifier."),
    ("platform", "String", "Target sensor platform."),
    ("release", "String", "OS release identifier."),
    ("version", "String", "Kernel version string."),
]

SEARCH_SENSOR_UPDATE_POLICIES_FQL_DOCUMENTATION = f"""
# Sensor Update Policies: Policies FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_sensor_update_policies`
- `falcon_search_sensor_update_policies_v2`
- `falcon_query_sensor_update_policy_ids`

## Filter Fields

{generate_md_table(SEARCH_SENSOR_UPDATE_POLICIES_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_SENSOR_UPDATE_POLICIES_SORT_FIELDS)}
"""

SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION = f"""
# Sensor Update Policies: Policy Members FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_sensor_update_policy_members`
- `falcon_query_sensor_update_policy_member_ids`

## Filter Fields

{generate_md_table(SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_SORT_FIELDS)}
"""

SEARCH_SENSOR_UPDATE_KERNELS_FQL_DOCUMENTATION = f"""
# Sensor Update Policies: Kernels FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_sensor_update_kernels`
- `falcon_query_sensor_update_kernel_distinct`

## Filter Fields

{generate_md_table(SEARCH_SENSOR_UPDATE_KERNELS_FILTER_FIELDS)}
"""

SENSOR_UPDATE_BUILDS_GUIDE = """
# Sensor Update Policies: Builds Guide

Use `falcon_search_sensor_update_builds` to retrieve available builds.

## Required input

- `platform`: linux, linuxarm64, mac, windows, or zlinux

## Optional input

- `stage`: rollout stage selector (string or list of strings)
"""

SENSOR_UPDATE_POLICIES_SAFETY_GUIDE = """
# Sensor Update Policies Safety Guide

Sensor update policy write operations can affect fleet update cadence and uninstall protection.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer read/search tools to validate target policy IDs before applying changes.
- Use explicit IDs for create/update/delete/action/precedence operations.
- Validate build and platform compatibility before creating or updating policies.
- Treat `falcon_reveal_sensor_uninstall_token` as sensitive and audit every use.
"""
