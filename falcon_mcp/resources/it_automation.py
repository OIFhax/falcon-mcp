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
# IT Automation Safety Guide

IT Automation tools can create/update/delete tasks, task groups, scheduled tasks,
policies, and trigger broad host-side execution behavior.

## Safety Expectations

- Use dedicated API credentials and MCP instances for high-impact execution tooling.
- Prefer tightly scoped `target` selectors and explicit `task_id` values.
- Set conservative `guardrails` values before large-scale executions.
- Review returned execution IDs and poll status before running follow-up actions.

## Confirmation Guardrail

All write and execution tools require explicit `confirm_execution=true`,
including create/update/delete operations and execution controls.

## Recommended Workflow

1. Use read tools to discover target IDs and current state.
2. Execute one scoped write action and validate the response.
3. Re-query the affected entities and execution status/results.
4. Expand rollout gradually with strict targeting and auditing.
"""
