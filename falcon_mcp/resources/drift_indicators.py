"""
Contains Drift Indicators resources.
"""

from falcon_mcp.common.utils import generate_md_table

DRIFT_INDICATORS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("cid", "String", "CrowdStrike customer identifier."),
    ("cloud_name", "String", "Cloud provider name."),
    ("command_line", "String", "Command line associated with the indicator."),
    ("container_id", "String", "Container identifier."),
    ("file_name", "String", "Observed file name."),
    ("file_sha256", "String", "Observed file SHA256."),
    ("host_id", "String", "Host identifier."),
    ("indicator_process_id", "String", "Indicator process ID."),
    ("namespace", "String", "Container namespace."),
    ("occurred_at", "Timestamp", "Indicator occurrence time."),
    ("parent_process_id", "String", "Parent process ID."),
    ("pod_name", "String", "Kubernetes pod name."),
    ("prevented", "Boolean", "Whether the drift indicator was prevented."),
    ("scheduler_name", "String", "Scheduler name."),
    ("severity", "String", "Severity level."),
    ("worker_node_name", "String", "Worker node name."),
]

DRIFT_INDICATORS_FQL_SORT_FIELDS = [
    ("Field", "Description"),
    ("occurred_at", "Sort by occurrence time"),
    ("severity", "Sort by severity"),
    ("cloud_name", "Sort by cloud provider"),
    ("pod_name", "Sort by pod name"),
]

SEARCH_DRIFT_INDICATORS_FQL_DOCUMENTATION = f"""
# Drift Indicators FQL Guide

Use this guide for:

- `falcon_get_drift_indicator_values_by_date`
- `falcon_get_drift_indicator_count`
- `falcon_query_drift_indicator_ids`
- `falcon_search_drift_indicator_entities`

## Filter Fields

{generate_md_table(DRIFT_INDICATORS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(DRIFT_INDICATORS_FQL_SORT_FIELDS)}

## Examples

- Prevented drift indicators:
  - `filter="prevented:'true'"`
- AWS indicators:
  - `filter="cloud_name:'aws'"`
- Recent indicators first:
  - `sort="occurred_at.desc"`

## Notes

- The same FQL surface is reused across count, by-date, query, and combined search endpoints.
- Some documented filters may behave inconsistently across tenants; start with simple filters and validate results incrementally.
- `falcon_query_drift_indicator_ids` returns IDs only, while `falcon_search_drift_indicator_entities` returns full entity records.
""".strip()
