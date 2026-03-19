"""
Contains ML Exclusions resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_ML_EXCLUSIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("applied_globally", "Boolean", "Whether the exclusion applies globally."),
    ("created_by", "String", "User or identifier that created the exclusion."),
    ("created_on", "Timestamp", "Exclusion creation timestamp."),
    ("last_modified", "Timestamp", "Exclusion last modification timestamp."),
    ("modified_by", "String", "User or identifier that last modified the exclusion."),
    ("value", "String", "Excluded value or path expression."),
]

SEARCH_ML_EXCLUSIONS_FQL_SORT_FIELDS = [
    ("Field", "Description"),
    ("applied_globally", "Sort by global scope."),
    ("created_by", "Sort by creator."),
    ("created_on", "Sort by creation timestamp."),
    ("last_modified", "Sort by modification timestamp."),
    ("modified_by", "Sort by modifier."),
    ("value", "Sort by excluded value."),
]

SEARCH_ML_EXCLUSIONS_FQL_DOCUMENTATION = f"""
# ML Exclusions Search FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_ml_exclusions`
- `falcon_query_ml_exclusion_ids`

## Filter Fields

{generate_md_table(SEARCH_ML_EXCLUSIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_ML_EXCLUSIONS_FQL_SORT_FIELDS)}

## Examples

- Global ML exclusions only:
  - `filter="applied_globally:true"`
- Exclusions created by your integration:
  - `filter="created_by:'mcp'"`
- Most recently modified exclusions first:
  - `sort="last_modified.desc"`

## Notes

- Validate filters in a test environment before production use.
- Use broad filters first, then refine as needed.
"""

ML_EXCLUSIONS_SAFETY_GUIDE = """
# ML Exclusions Safety Guide

ML exclusion write operations can suppress protection and extraction workflows if used incorrectly.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer search and detail tools to validate target exclusion IDs before applying changes.
- Use narrowly-scoped values whenever possible and avoid broad wildcard-style exclusions.
- Omit `groups` only when a tenant-wide exclusion is explicitly intended; the default behavior is `["all"]`.
- Document the business justification in `comment` for every create, update, or delete.
"""
