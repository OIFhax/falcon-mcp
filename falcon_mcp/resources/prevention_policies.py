"""
Contains Prevention Policies resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_PREVENTION_POLICIES_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Prevention policy identifier."),
    ("name", "String", "Prevention policy name."),
    ("platform_name", "String", "Target platform name."),
    ("enabled", "Boolean", "Policy enablement state."),
    ("created_timestamp", "Timestamp", "Policy creation timestamp."),
    ("modified_timestamp", "Timestamp", "Policy last modification timestamp."),
]

SEARCH_PREVENTION_POLICIES_SORT_FIELDS = [
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

SEARCH_PREVENTION_POLICY_MEMBERS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("device_id", "String", "Host device identifier."),
    ("hostname", "String", "Host name."),
    ("platform_name", "String", "Host platform name."),
    ("policy_id", "String", "Assigned prevention policy ID."),
    ("policy_name", "String", "Assigned prevention policy name."),
]

SEARCH_PREVENTION_POLICY_MEMBERS_SORT_FIELDS = [
    ("Field", "Description"),
    ("hostname", "Sort by host name."),
    ("platform_name", "Sort by host platform."),
    ("policy_name", "Sort by assigned policy name."),
]

SEARCH_PREVENTION_POLICIES_FQL_DOCUMENTATION = f"""
# Prevention Policies: Policies FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_prevention_policies`
- `falcon_query_prevention_policy_ids`

## Filter Fields

{generate_md_table(SEARCH_PREVENTION_POLICIES_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_PREVENTION_POLICIES_SORT_FIELDS)}
"""

SEARCH_PREVENTION_POLICY_MEMBERS_FQL_DOCUMENTATION = f"""
# Prevention Policies: Policy Members FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_prevention_policy_members`
- `falcon_query_prevention_policy_member_ids`

## Filter Fields

{generate_md_table(SEARCH_PREVENTION_POLICY_MEMBERS_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_PREVENTION_POLICY_MEMBERS_SORT_FIELDS)}
"""

PREVENTION_POLICIES_SAFETY_GUIDE = """
# Prevention Policies Safety Guide

Prevention policy write operations can impact endpoint detection and enforcement behavior.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer read/search tools to validate target policy IDs before applying actions.
- Use narrow selectors and explicit IDs for updates, deletions, and actions.
- Confirm platform scope before precedence changes.
- Document expected blast radius before enable, disable, add/remove-group, or delete actions.
"""
