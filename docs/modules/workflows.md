<!-- meta:title Workflows -->
<!-- meta:description This module provides full Falcon Workflows service collection coverage: search, export/import/update, execute, execution actions/results, human input actions, and system definition lifecycle operations -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Workflows service collection coverage: search, export/import/update, execute, execution actions/results, human input actions, and system definition lifecycle operations

## API Scopes

- `Workflow:read`
- `Workflow:write`

## Tools

### `falcon_search_workflow_activities`

**Required scopes:** `Workflow:read`

Search workflow activities.

### `falcon_search_workflow_activities_content`

**Required scopes:** `Workflow:read`

Search workflow activity content records.

### `falcon_search_workflow_definitions`

**Required scopes:** `Workflow:read`

Search workflow definitions.

**Example prompts:**

- "What Fusion SOAR workflows can I trigger on demand?"
- "Find the Fusion workflow called 'Adversary Exposure Mitigation'"
- "Which Fusion workflows are currently disabled?"

### `falcon_search_workflow_executions`

**Required scopes:** `Workflow:read`

Search workflow executions.

**Example prompts:**

- "Show me workflow executions that completed"
- "Which Fusion workflows failed in the last 7 days?"
- "Are any workflow runs waiting on someone to approve them?"

### `falcon_search_workflow_triggers`

**Required scopes:** `Workflow:read`

Search workflow triggers.

### `falcon_export_workflow_definition`

**Required scopes:** `Workflow:read`

Export a workflow definition by ID.

### `falcon_import_workflow_definition`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Import a workflow definition from YAML text.

### `falcon_update_workflow_definition`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Update a workflow definition.

### `falcon_update_workflow_definition_status`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Workflow:write`

Enable/disable definitions or cancel all in-flight definition executions.

### `falcon_execute_workflow`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Execute an on-demand workflow.

**Example prompts:**

- "Run the 'Notify SOC Channel' workflow"
- "Start workflow 2617e3fc with the hash abc123"

### `falcon_execute_workflow_internal`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Execute an internal on-demand workflow.

### `falcon_mock_execute_workflow`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Execute a workflow definition with mocks.

### `falcon_update_workflow_execution_state`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Workflow:write`

Resume or cancel workflow executions.

### `falcon_get_workflow_execution_results`

**Required scopes:** `Workflow:read`

Retrieve results for workflow execution IDs.

**Example prompts:**

- "What did workflow execution 714511d8 actually do?"
- "Show me the ticket number the incident workflow created"

### `falcon_get_workflow_human_input`

**Required scopes:** `Workflow:read`

Retrieve workflow human input records by ID.

### `falcon_update_workflow_human_input`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Provide input for a workflow human-input step.

### `falcon_deprovision_workflow_system_definition`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Workflow:write`

Deprovision a system workflow definition.

### `falcon_promote_workflow_system_definition`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Promote a system workflow definition template.

### `falcon_provision_workflow_system_definition`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Provision a system workflow definition template.

## Resources

- **`falcon://workflows/activities/fql-guide`**: Contains FQL guidance for workflow activity search tools.
- **`falcon://workflows/definitions/fql-guide`**: Contains FQL guidance for `falcon_search_workflow_definitions`.
- **`falcon://workflows/executions/fql-guide`**: Contains FQL guidance for `falcon_search_workflow_executions`.
- **`falcon://workflows/triggers/fql-guide`**: Contains FQL guidance for `falcon_search_workflow_triggers`.
- **`falcon://workflows/import/guide`**: Guidance for `falcon_import_workflow_definition`.
- **`falcon://workflows/safety-guide`**: Safety and operational guidance for workflow write/execute tools.
