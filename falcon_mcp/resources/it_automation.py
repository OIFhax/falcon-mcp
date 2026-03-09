"""
Contains IT Automation resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "end_time",
        "Timestamp",
        "Execution end timestamp.",
    ),
    (
        "run_by",
        "String",
        "User or principal that triggered the execution.",
    ),
    (
        "run_type",
        "String",
        "Execution run mode/type.",
    ),
    (
        "start_time",
        "Timestamp",
        "Execution start timestamp.",
    ),
    (
        "status",
        "String",
        "Execution status state.",
    ),
    (
        "task_id",
        "String",
        "Task identifier.",
    ),
    (
        "task_name",
        "String",
        "Task name.",
    ),
    (
        "task_type",
        "String",
        "Task type.",
    ),
]

SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("end_time", "Sort by execution end timestamp"),
    ("run_by", "Sort by execution initiator"),
    ("run_type", "Sort by run mode/type"),
    ("start_time", "Sort by execution start timestamp"),
    ("status", "Sort by execution status"),
    ("task_id", "Sort by task ID"),
    ("task_name", "Sort by task name"),
    ("task_type", "Sort by task type"),
]

SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_DOCUMENTATION = f"""
# IT Automation Task Executions FQL Guide

Use this guide to build the `filter` parameter for
`falcon_search_it_automation_task_executions`.

## Filter Fields

{generate_md_table(SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_IT_AUTOMATION_TASK_EXECUTIONS_FQL_SORT_FIELDS)}

## Examples

- Running executions:
  - `filter="status:'running'"`
- Executions for a specific task:
  - `filter="task_id:'<task_id>'"`
- Most recent executions first:
  - `sort="start_time.desc"`

## Notes

- Validate filters in a test environment before production use.
- Use execution IDs from these results with `falcon_get_it_automation_task_executions`.
"""

IT_AUTOMATION_PHASE3_SAFETY_GUIDE = """
# IT Automation Phase 3 Safety Guide

Phase 3 tools can trigger broad and high-impact execution behavior across managed hosts.

## Safety Expectations

- Use dedicated API credentials and MCP instances for high-impact execution tooling.
- Prefer tightly scoped `target` selectors and explicit `task_id` values.
- Set conservative `guardrails` values before large-scale executions.
- Review returned execution IDs and poll status before running follow-up actions.

## Confirmation Guardrail

The following tools require explicit `confirm_execution=true`:

- `falcon_start_it_automation_task_execution`
- `falcon_run_it_automation_live_query`
- `falcon_cancel_it_automation_task_execution`
- `falcon_rerun_it_automation_task_execution`

## Recommended Workflow

1. Search and inspect recent executions with read tools.
2. Launch one scoped execution and verify host-level status.
3. Retrieve execution results and validate expected behavior.
4. Expand rollout gradually with strict targeting and auditing.
"""
