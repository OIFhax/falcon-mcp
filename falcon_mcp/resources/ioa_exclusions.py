"""
Contains IOA Exclusions resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_IOA_EXCLUSIONS_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "applied_globally",
        "Boolean",
        "Whether the exclusion applies globally.",
    ),
    (
        "created_by",
        "String",
        "User or identifier that created the exclusion.",
    ),
    (
        "created_on",
        "Timestamp",
        "Exclusion creation timestamp.",
    ),
    (
        "last_modified",
        "Timestamp",
        "Exclusion last modification timestamp.",
    ),
    (
        "modified_by",
        "String",
        "User or identifier that last modified the exclusion.",
    ),
    (
        "name",
        "String",
        "Exclusion name.",
    ),
    (
        "pattern_id",
        "String",
        "Target IOA pattern ID.",
    ),
    (
        "pattern_name",
        "String",
        "Target IOA pattern name.",
    ),
]

SEARCH_IOA_EXCLUSIONS_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("applied_globally", "Sort by global scope"),
    ("created_by", "Sort by creator"),
    ("created_on", "Sort by creation timestamp"),
    ("last_modified", "Sort by modification timestamp"),
    ("modified_by", "Sort by modifier"),
    ("name", "Sort by name"),
    ("pattern_id", "Sort by pattern ID"),
    ("pattern_name", "Sort by pattern name"),
]

SEARCH_IOA_EXCLUSIONS_FQL_DOCUMENTATION = f"""
# IOA Exclusions Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_ioa_exclusions`.

## Filter Fields

{generate_md_table(SEARCH_IOA_EXCLUSIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_IOA_EXCLUSIONS_FQL_SORT_FIELDS)}

## Additional Regex Parameters

- `ifn_regex`: Filter using Image File Name regex criteria
- `cl_regex`: Filter using Command Line regex criteria

## Examples

- Exclusions created by your integration:
  - `filter="created_by:'mcp'"`
- Exclusions for a specific IOA pattern:
  - `filter="pattern_name:'Suspicious PowerShell*'"`
- Most recently modified exclusions first:
  - `sort="last_modified.desc"`

## Notes

- Validate filters in a test environment before production use.
- Use broad filters first, then refine as needed.
"""
