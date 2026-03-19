"""
Contains Sensor Visibility Exclusions resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("applied_globally", "Boolean", "Whether the exclusion applies globally."),
    ("created_by", "String", "User or identifier that created the exclusion."),
    ("created_on", "Timestamp", "Exclusion creation timestamp."),
    ("last_modified", "Timestamp", "Exclusion last modification timestamp."),
    ("modified_by", "String", "User or identifier that last modified the exclusion."),
    ("value", "String", "Excluded value or path expression."),
]

SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_SORT_FIELDS = [
    ("Field", "Description"),
    ("applied_globally", "Sort by global scope."),
    ("created_by", "Sort by creator."),
    ("created_on", "Sort by creation timestamp."),
    ("last_modified", "Sort by modification timestamp."),
    ("modified_by", "Sort by modifier."),
    ("value", "Sort by excluded value."),
]

SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_DOCUMENTATION = f"""
# Sensor Visibility Exclusions Search FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_sensor_visibility_exclusions`
- `falcon_query_sensor_visibility_exclusion_ids`

## Filter Fields

{generate_md_table(SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_SORT_FIELDS)}
"""

SENSOR_VISIBILITY_EXCLUSIONS_SAFETY_GUIDE = """
# Sensor Visibility Exclusions Safety Guide

Sensor visibility exclusions can suppress process telemetry and descendant-process visibility if used incorrectly.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer search and detail tools to validate target exclusion IDs before applying changes.
- Use narrowly-scoped values and avoid broad patterns that mask large portions of endpoint activity.
- Document the business justification in `comment` for every create, update, or delete.
"""
