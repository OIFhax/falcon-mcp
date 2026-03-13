"""
Contains Firewall Management resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_FIREWALL_RULES_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "enabled",
        "Boolean",
        "Filter by rule enabled state. Example: enabled:true",
    ),
    (
        "platform",
        "String",
        "Filter by platform. Example: platform:'windows'",
    ),
    (
        "name",
        "String",
        "Rule or rule group name. Example: name:'Block*'",
    ),
    (
        "description",
        "String",
        "Rule or rule group description text search.",
    ),
    (
        "created_on",
        "Timestamp",
        "Entity creation timestamp.",
    ),
    (
        "modified_on",
        "Timestamp",
        "Entity last modified timestamp.",
    ),
]

SEARCH_FIREWALL_RULES_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("name", "Sort by name"),
    ("platform", "Sort by platform"),
    ("created_on", "Sort by creation time"),
    ("modified_on", "Sort by last modified time"),
    ("enabled", "Sort by enabled flag"),
]

SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION = f"""
# Firewall Management FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_firewall_rules`
- `falcon_search_firewall_rule_groups`
- `falcon_query_firewall_rule_ids`
- `falcon_query_firewall_rule_group_ids`
- `falcon_query_firewall_policy_rule_ids`

## Filter Fields

{generate_md_table(SEARCH_FIREWALL_RULES_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_FIREWALL_RULES_FQL_SORT_FIELDS)}

## Examples

- Enabled rules:
  - `filter="enabled:true"`
- Windows rule groups:
  - `filter="platform:'windows'"`
- Recently modified entities:
  - `sort="modified_on.desc"`

## Notes

- For policy-specific searches, use `falcon_search_firewall_policy_rules` with `policy_id`.
- Start broad, then refine your filter if results are empty.
"""

SEARCH_FIREWALL_EVENTS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("aid", "String", "Agent ID for the endpoint."),
    ("device_id", "String", "Endpoint device identifier."),
    ("event_type", "String", "Firewall event type."),
    ("policy_id", "String", "Firewall policy container ID."),
    ("rule_id", "String", "Firewall rule ID."),
    ("hostname", "String", "Endpoint host name."),
]

SEARCH_FIREWALL_EVENTS_FQL_SORT_FIELDS = [
    ("Field", "Description"),
    ("timestamp", "Sort by event timestamp."),
    ("event_type", "Sort by firewall event type."),
    ("hostname", "Sort by endpoint hostname."),
]

SEARCH_FIREWALL_EVENTS_FQL_DOCUMENTATION = f"""
# Firewall Management Events FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_query_firewall_event_ids`

## Filter Fields

{generate_md_table(SEARCH_FIREWALL_EVENTS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_FIREWALL_EVENTS_FQL_SORT_FIELDS)}
"""

SEARCH_FIREWALL_NETWORK_LOCATIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Network location identifier."),
    ("name", "String", "Network location name."),
    ("enabled", "Boolean", "Network location enablement state."),
    ("description", "String", "Network location description text."),
    ("created_on", "Timestamp", "Entity creation timestamp."),
    ("modified_on", "Timestamp", "Entity modification timestamp."),
]

SEARCH_FIREWALL_NETWORK_LOCATIONS_FQL_SORT_FIELDS = [
    ("Field", "Description"),
    ("name", "Sort by network location name."),
    ("created_on", "Sort by creation timestamp."),
    ("modified_on", "Sort by modification timestamp."),
    ("enabled", "Sort by enabled state."),
]

SEARCH_FIREWALL_NETWORK_LOCATIONS_FQL_DOCUMENTATION = f"""
# Firewall Network Locations FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_query_firewall_network_location_ids`

## Filter Fields

{generate_md_table(SEARCH_FIREWALL_NETWORK_LOCATIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_FIREWALL_NETWORK_LOCATIONS_FQL_SORT_FIELDS)}
"""

FIREWALL_MANAGEMENT_SAFETY_GUIDE = """
# Firewall Management Safety Guide

Firewall Management write operations can change rule enforcement and network controls.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer read/query tools to verify IDs and current state before mutation.
- Use narrowly scoped filters and explicit IDs for updates and deletes.
- Validate rule, policy-container, and network-location changes in a test tenant first.
- Document expected blast radius before applying precedence and metadata changes.
"""
