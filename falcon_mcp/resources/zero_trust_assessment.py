"""
Contains Zero Trust Assessment resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_ZTA_ASSESSMENTS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("score", "Integer", "Overall Zero Trust Assessment score."),
]

SEARCH_ZTA_ASSESSMENTS_SORT_FIELDS = [
    ("Field", "Description"),
    ("score", "Sort by score."),
]

SEARCH_ZTA_COMBINED_ASSESSMENTS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("aid", "String", "Host agent ID."),
    ("cid", "String", "Tenant CID."),
    ("created_timestamp", "Timestamp", "Assessment creation timestamp."),
    ("updated_timestamp", "Timestamp", "Assessment update timestamp."),
]

SEARCH_ZTA_COMBINED_ASSESSMENTS_FACET_VALUES = [
    ("Facet", "Description"),
    ("host", "Include host details block in each result."),
    ("finding.rule", "Include finding rule details block in each result."),
]

SEARCH_ZTA_COMBINED_ASSESSMENTS_SORT_FIELDS = [
    ("Field", "Description"),
    ("created_timestamp", "Sort by creation timestamp."),
    ("updated_timestamp", "Sort by update timestamp."),
]

SEARCH_ZTA_ASSESSMENTS_FQL_DOCUMENTATION = f"""
# Zero Trust Assessment: Score Query FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_zta_assessments_by_score`.
This tool uses Zero Trust Assessment endpoint `getAssessmentsByScoreV1`.

## Required Filter Field

{generate_md_table(SEARCH_ZTA_ASSESSMENTS_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_ZTA_ASSESSMENTS_SORT_FIELDS)}

## Examples

- Scores greater than or equal to 80:
  - `filter="score:>=80"`
- Scores below 50:
  - `filter="score:<50"`
- Highest scores first:
  - `sort="score|desc"`
"""

SEARCH_ZTA_COMBINED_ASSESSMENTS_FQL_DOCUMENTATION = f"""
# Zero Trust Assessment: Combined Assessments FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_zta_combined_assessments`.
This tool uses Zero Trust Assessment endpoint `getCombinedAssessmentsQuery`.

## Filter Fields

{generate_md_table(SEARCH_ZTA_COMBINED_ASSESSMENTS_FILTER_FIELDS)}

## Facet Values

{generate_md_table(SEARCH_ZTA_COMBINED_ASSESSMENTS_FACET_VALUES)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_ZTA_COMBINED_ASSESSMENTS_SORT_FIELDS)}

## Examples

- Assessments updated in the last 7 days:
  - `filter="updated_timestamp:>'now-7d'"`
- Assessments for a specific host:
  - `filter="aid:'<aid>'"`
- Include host details and newest first:
  - `facet=['host']`
  - `sort="updated_timestamp.desc"`
"""
