"""
Contains Falcon Data Replicator (FDR) resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_FDR_EVENT_SCHEMA_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Event schema identifier."),
    ("name", "String", "Event schema name."),
    ("platform", "String", "Platform associated with the event schema."),
    ("version", "Integer", "Schema version."),
]

SEARCH_FDR_EVENT_SCHEMA_SORT_FIELDS = [
    ("Field", "Description"),
    ("id", "Sort by schema ID"),
    ("name", "Sort by schema name"),
    ("platform", "Sort by platform"),
    ("version", "Sort by schema version"),
]

SEARCH_FDR_EVENT_SCHEMA_FQL_DOCUMENTATION = f"""
# FDR Event Schema FQL Guide

Use this guide for:

- `falcon_query_fdr_event_schema_ids`
- `falcon_search_fdr_event_schemas`

## Common Filter Fields

{generate_md_table(SEARCH_FDR_EVENT_SCHEMA_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_FDR_EVENT_SCHEMA_SORT_FIELDS)}

## Examples

- Match a specific schema name:
  - `filter="name:'EmailFileWritten'"`
- Return the newest versions first:
  - `sort="version.desc"`
- Sort alphabetically:
  - `sort="name.asc"`

## Notes

- Query tools return schema IDs only.
- Search tools perform query + detail retrieval and return full schema records.
- This guide covers common schema fields and is not an exhaustive catalog.
""".strip()

SEARCH_FDR_FIELD_SCHEMA_FILTERS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Field schema identifier."),
    ("name", "String", "Field schema name."),
    ("type", "String", "Field data type."),
    ("universal", "Boolean", "Whether the field is universal across schemas."),
]

SEARCH_FDR_FIELD_SCHEMA_SORT_FIELDS = [
    ("Field", "Description"),
    ("id", "Sort by field ID"),
    ("name", "Sort by field name"),
    ("type", "Sort by field type"),
    ("universal", "Sort by universal field flag"),
]

SEARCH_FDR_FIELD_SCHEMA_FQL_DOCUMENTATION = f"""
# FDR Field Schema FQL Guide

Use this guide for:

- `falcon_query_fdr_field_schema_ids`
- `falcon_search_fdr_field_schemas`

## Common Filter Fields

{generate_md_table(SEARCH_FDR_FIELD_SCHEMA_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_FDR_FIELD_SCHEMA_SORT_FIELDS)}

## Examples

- Match a specific field name:
  - `filter="name:'AzureFirewallRuleType'"`
- Sort alphabetically:
  - `sort="name.asc"`

## Notes

- Query tools return field IDs only.
- Search tools perform query + detail retrieval and return full field schema records.
- This guide covers common schema fields and is not an exhaustive catalog.
""".strip()
