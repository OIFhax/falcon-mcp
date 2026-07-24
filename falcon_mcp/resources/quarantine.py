"""
Contains Quarantine resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_QUARANTINE_FILES_FQL_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("status", "String", "Detection/quarantine status."),
    ("adversary_id", "String", "Adversary identifier."),
    ("device.device_id", "String", "Host agent ID."),
    ("device.country", "String", "Host country."),
    ("device.hostname", "String", "Host name."),
    ("behaviors.behavior_id", "String", "Behavior identifier."),
    ("behaviors.ioc_type", "String", "IOC type."),
    ("behaviors.ioc_value", "String", "IOC value."),
    ("behaviors.username", "String", "Username associated with behavior."),
    ("behaviors.tree_root_hash", "String", "Tree root hash."),
    ("first_behavior", "Timestamp", "First observed behavior timestamp."),
    ("last_behavior", "Timestamp", "Last observed behavior timestamp."),
    ("max_severity", "Integer", "Maximum severity."),
    ("max_confidence", "Integer", "Maximum confidence."),
]

SEARCH_QUARANTINE_FILES_SORT_FIELDS = [
    ("Field", "Description"),
    ("date_created", "Sort by quarantine create time."),
    ("date_updated", "Sort by quarantine update time."),
    ("hostname", "Sort by host name."),
    ("username", "Sort by username."),
    ("paths.path", "Sort by file path."),
    ("paths.state", "Sort by path state."),
    ("state", "Sort by quarantine state."),
]

SEARCH_QUARANTINE_FILES_FQL_DOCUMENTATION = f"""
# Quarantine: File Search FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_quarantine_files`
- `falcon_get_quarantine_action_update_count`

## Filter Fields

{generate_md_table(SEARCH_QUARANTINE_FILES_FQL_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_QUARANTINE_FILES_SORT_FIELDS)}

## Examples

- Quarantined files for a specific host:
  - `filter="device.hostname:'host01'"`
- High-severity quarantined content:
  - `filter="max_severity:>80"`
- Most recently updated first:
  - `sort="date_updated.desc"`
"""

QUARANTINE_AGGREGATION_GUIDE = """
# Quarantine Aggregation Guide

Use `falcon_aggregate_quarantine_files` with an aggregation body accepted by
`GetAggregateFiles`.

## Example

```json
[
  {"field": "state", "name": "state", "type": "terms"}
]
```
"""

QUARANTINE_SAFETY_GUIDE = """
# Quarantine Update Safety Guide

Quarantine update tools can release or delete quarantined files.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer targeting by explicit IDs before using broad query updates.
- Use precise `filter` / `q` criteria for query-based updates.
- Capture a meaningful `comment` for audit traceability.
- For destructive actions (`delete`), validate scope with `search` and `action_update_count` first.

## Supported actions

- `release`
- `unrelease`
- `delete`
"""

SEARCH_QUARANTINED_FILES_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "id",
        "String",
        "Quarantine file record ID. Example: id:'1234567890abcdef'",
    ),
    (
        "state",
        "String",
        "Quarantine state (response field). Also queryable as `status` in FQL. Example: state:'quarantined' or status:'released'",
    ),
    (
        "sha256",
        "String",
        "SHA256 hash of the quarantined file. Example: sha256:'a1b2c3...'",
    ),
    (
        "date_updated",
        "Timestamp",
        "Last update timestamp. Example: date_updated:>'2026-03-01T00:00:00Z'",
    ),
    (
        "hostname",
        "String",
        "Host name tied to the quarantine event (top-level field). Example: hostname:'BRR-WB-LIB-22'",
    ),
    (
        "behaviors.username",
        "String",
        "Username associated with the quarantined behavior. Example: behaviors.username:'alice'",
    ),
    (
        "behaviors.ioc_value",
        "String",
        "IOC value associated with the quarantined behavior. Example: behaviors.ioc_value:'Shift - Print_d3lsk.exe'",
    ),
]

SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION = f"""Quarantine Files FQL Filter Guide

Use this guide when building the `filter` parameter for `falcon_search_quarantined_files`,
`falcon_count_quarantine_actions`, `falcon_update_quarantined_files`,
or `falcon_delete_quarantined_files`.

=== BASIC SYNTAX ===
field_name:[operator]'value'

=== OPERATORS ===
• = (default): field_name:'value'
• !: field_name:!'value'
• >, >=, <, <=: field_name:>'2026-03-01T00:00:00Z'
• ~: field_name:~'partial'
• !~: field_name:!~'exclude'
• *: field_name:'prefix*' or field_name:'*suffix*'

=== COMBINING ===
• + = AND
• , = OR
• () = GROUPING

=== AVAILABLE FIELDS ===

{generate_md_table(SEARCH_QUARANTINED_FILES_FQL_FILTERS)}

=== NOTES ===

• The response entity uses `state` for the quarantine status field.
• Both `state` and `status` work as FQL filter fields.

=== EXAMPLES ===

# Quarantined files for a host
hostname:'BRR-WB-LIB-22'

# Records updated recently
date_updated:>'2026-03-01T00:00:00Z'

# Released files for a user
status:'released'+behaviors.username:'alice'

# File hash on a specific host
sha256:'a1b2c3*'+hostname:'DC*'
"""
