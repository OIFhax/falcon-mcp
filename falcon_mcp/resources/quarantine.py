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
