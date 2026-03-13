"""
Contains Workflows resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_WORKFLOW_ACTIVITIES_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("name", "String", "Workflow activity name."),
    ("category", "String", "Workflow activity category."),
    ("is_enabled", "Boolean", "Whether activity is enabled."),
]

SEARCH_WORKFLOW_ACTIVITIES_SORT_FIELDS = [
    ("Field", "Description"),
    ("name", "Sort by activity name."),
    ("time", "Sort by activity time."),
]

SEARCH_WORKFLOW_DEFINITIONS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Workflow definition identifier."),
    ("name", "String", "Workflow definition name."),
    ("enabled", "Boolean", "Definition enabled status."),
    ("created_on", "Timestamp", "Definition creation timestamp."),
    ("updated_on", "Timestamp", "Definition update timestamp."),
]

SEARCH_WORKFLOW_DEFINITIONS_SORT_FIELDS = [
    ("Field", "Description"),
    ("name", "Sort by definition name."),
    ("created_on", "Sort by creation time."),
    ("updated_on", "Sort by update time."),
]

SEARCH_WORKFLOW_EXECUTIONS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Workflow execution identifier."),
    ("definition_id", "String", "Workflow definition identifier."),
    ("status", "String", "Execution status."),
    ("created_on", "Timestamp", "Execution creation timestamp."),
    ("updated_on", "Timestamp", "Execution update timestamp."),
]

SEARCH_WORKFLOW_EXECUTIONS_SORT_FIELDS = [
    ("Field", "Description"),
    ("created_on", "Sort by creation time."),
    ("updated_on", "Sort by update time."),
    ("status", "Sort by execution status."),
]

SEARCH_WORKFLOW_TRIGGERS_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("name", "String", "Trigger namespaced identifier."),
    ("namespace", "String", "Trigger namespace."),
]

SEARCH_WORKFLOW_ACTIVITIES_FQL_DOCUMENTATION = f"""
# Workflows: Activities FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_workflow_activities`
- `falcon_search_workflow_activities_content`

## Filter Fields

{generate_md_table(SEARCH_WORKFLOW_ACTIVITIES_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_WORKFLOW_ACTIVITIES_SORT_FIELDS)}
"""

SEARCH_WORKFLOW_DEFINITIONS_FQL_DOCUMENTATION = f"""
# Workflows: Definitions FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_workflow_definitions`

## Filter Fields

{generate_md_table(SEARCH_WORKFLOW_DEFINITIONS_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_WORKFLOW_DEFINITIONS_SORT_FIELDS)}
"""

SEARCH_WORKFLOW_EXECUTIONS_FQL_DOCUMENTATION = f"""
# Workflows: Executions FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_workflow_executions`

## Filter Fields

{generate_md_table(SEARCH_WORKFLOW_EXECUTIONS_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_WORKFLOW_EXECUTIONS_SORT_FIELDS)}
"""

SEARCH_WORKFLOW_TRIGGERS_FQL_DOCUMENTATION = f"""
# Workflows: Triggers FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_workflow_triggers`

## Filter Fields

{generate_md_table(SEARCH_WORKFLOW_TRIGGERS_FILTER_FIELDS)}
"""

WORKFLOW_IMPORT_GUIDE = """
# Workflow Import Guide

Use `falcon_import_workflow_definition` to import a workflow definition from
YAML content.

## Required input

- `data_file_content`: YAML definition text

## Optional query parameters

- `name`: override imported workflow name
- `validate_only`: validate import without saving
"""

WORKFLOW_SAFETY_GUIDE = """
# Workflow Safety Guide

Workflow write/execute tools can trigger automation across your environment.

## Operational guardrails

- Require `confirm_execution=true` for all write/execute actions.
- Prefer `validate_only=true` where supported before saving or executing.
- Use explicit IDs for definitions, executions, and human inputs.
- Use narrow query selectors for action endpoints.
- Review intended impact before provision/promote/deprovision operations.
"""
