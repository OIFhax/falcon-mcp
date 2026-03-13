"""
Contains Firewall Policies resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_FIREWALL_POLICIES_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Firewall policy identifier."),
    ("name", "String", "Firewall policy name."),
    ("platform_name", "String", "Target platform name."),
    ("enabled", "Boolean", "Policy enablement state."),
    ("created_timestamp", "Timestamp", "Policy creation timestamp."),
    ("modified_timestamp", "Timestamp", "Policy last modification timestamp."),
]

SEARCH_FIREWALL_POLICIES_SORT_FIELDS = [
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

SEARCH_FIREWALL_POLICY_MEMBERS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("device_id", "String", "Host device identifier."),
    ("hostname", "String", "Host name."),
    ("platform_name", "String", "Host platform name."),
    ("policy_id", "String", "Assigned firewall policy ID."),
    ("policy_name", "String", "Assigned firewall policy name."),
]

SEARCH_FIREWALL_POLICY_MEMBERS_SORT_FIELDS = [
    ("Field", "Description"),
    ("hostname", "Sort by host name."),
    ("platform_name", "Sort by host platform."),
    ("policy_name", "Sort by assigned policy name."),
]

SEARCH_FIREWALL_POLICIES_FQL_DOCUMENTATION = f"""
# Firewall Policies: Policies FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_firewall_policies`
- `falcon_query_firewall_policy_ids`

## Filter Fields

{generate_md_table(SEARCH_FIREWALL_POLICIES_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_FIREWALL_POLICIES_SORT_FIELDS)}
"""

SEARCH_FIREWALL_POLICY_MEMBERS_FQL_DOCUMENTATION = f"""
# Firewall Policies: Policy Members FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_firewall_policy_members`
- `falcon_query_firewall_policy_member_ids`

## Filter Fields

{generate_md_table(SEARCH_FIREWALL_POLICY_MEMBERS_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_FIREWALL_POLICY_MEMBERS_SORT_FIELDS)}
"""

FIREWALL_POLICIES_SAFETY_GUIDE = """
# Firewall Policies Safety Guide

Firewall policy write operations can affect endpoint network control and enforcement behavior.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer read/search tools to validate target policy IDs before applying changes.
- Use explicit IDs for update/delete/action/precedence operations.
- Validate policy assignments and precedence changes in test tenants first.
- Document expected blast radius before enable/disable and host-group assignment actions.
"""
