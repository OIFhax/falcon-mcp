<!-- meta:title IT Automation -->
<!-- meta:description This module provides full Falcon IT Automation service collection coverage: search/query/get operations across tasks, task groups, scheduled tasks, user groups, and policies, plus controlled write and execution actions -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon IT Automation service collection coverage: search/query/get operations across tasks, task groups, scheduled tasks, user groups, and policies, plus controlled write and execution actions

## API Scopes

- `IT Automation:read`
- `IT Automation:write`

## Tools

### `falcon_search_it_automation_associated_tasks`

**Required scopes:** `IT Automation:read`

Retrieve tasks associated with a file ID.

### `falcon_search_it_automation_scheduled_tasks_combined`

**Required scopes:** `IT Automation:read`

Search combined scheduled-task details.

### `falcon_search_it_automation_task_executions`

**Required scopes:** `IT Automation:read`

Search combined task execution records.

### `falcon_search_it_automation_task_groups_combined`

**Required scopes:** `IT Automation:read`

Search combined task-group details.

### `falcon_search_it_automation_tasks_combined`

**Required scopes:** `IT Automation:read`

Search combined task details.

### `falcon_search_it_automation_user_group_ids`

**Required scopes:** `IT Automation:read`

Search user-group IDs.

### `falcon_query_it_automation_policy_ids`

**Required scopes:** `IT Automation:read`

Query policy IDs by platform.

### `falcon_search_it_automation_scheduled_task_ids`

**Required scopes:** `IT Automation:read`

Search scheduled-task IDs.

### `falcon_search_it_automation_task_execution_ids`

**Required scopes:** `IT Automation:read`

Search task execution IDs.

### `falcon_search_it_automation_task_group_ids`

**Required scopes:** `IT Automation:read`

Search task-group IDs.

### `falcon_search_it_automation_task_ids`

**Required scopes:** `IT Automation:read`

Search task IDs.

### `falcon_get_it_automation_user_groups`

**Required scopes:** `IT Automation:read`

Retrieve user groups by ID.

### `falcon_get_it_automation_policies`

**Required scopes:** `IT Automation:read`

Retrieve policies by ID.

### `falcon_get_it_automation_scheduled_tasks`

**Required scopes:** `IT Automation:read`

Retrieve scheduled tasks by ID.

### `falcon_get_it_automation_task_executions`

**Required scopes:** `IT Automation:read`

Retrieve task execution records by ID.

### `falcon_get_it_automation_task_groups`

**Required scopes:** `IT Automation:read`

Retrieve task groups by ID.

### `falcon_get_it_automation_tasks`

**Required scopes:** `IT Automation:read`

Retrieve tasks by ID.

### `falcon_get_it_automation_task_execution_host_status`

**Required scopes:** `IT Automation:read`

Retrieve host-level execution status for task executions.

### `falcon_start_it_automation_execution_results_search`

**Required scopes:** `IT Automation:read`

Start asynchronous execution-results search.

### `falcon_get_it_automation_execution_results_search_status`

**Required scopes:** `IT Automation:read`

Get status of asynchronous execution-results search.

### `falcon_get_it_automation_execution_results`

**Required scopes:** `IT Automation:read`

Get asynchronous execution results by search job ID.

### `falcon_create_it_automation_user_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Create an IT Automation user group.

### `falcon_update_it_automation_user_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Update an IT Automation user group.

### `falcon_delete_it_automation_user_groups`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Delete IT Automation user groups.

### `falcon_create_it_automation_policy`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Create an IT Automation policy.

### `falcon_update_it_automation_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Update IT Automation policies.

### `falcon_delete_it_automation_policies`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Delete IT Automation policies.

### `falcon_update_it_automation_policy_host_groups`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Manage host groups assigned to IT Automation policies.

### `falcon_update_it_automation_policies_precedence`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Update IT Automation policy precedence for a platform.

### `falcon_create_it_automation_scheduled_task`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Create an IT Automation scheduled task.

### `falcon_update_it_automation_scheduled_task`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Update an IT Automation scheduled task.

### `falcon_delete_it_automation_scheduled_tasks`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Delete IT Automation scheduled tasks.

### `falcon_create_it_automation_task_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Create an IT Automation task group.

### `falcon_update_it_automation_task_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Update an IT Automation task group.

### `falcon_delete_it_automation_task_groups`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Delete IT Automation task groups.

### `falcon_create_it_automation_task`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Create an IT Automation task.

### `falcon_update_it_automation_task`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IT Automation:write`

Update an IT Automation task.

### `falcon_delete_it_automation_tasks`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Delete IT Automation tasks.

### `falcon_start_it_automation_task_execution`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Start execution of an existing IT Automation task.

### `falcon_run_it_automation_live_query`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Run an IT Automation live query execution.

### `falcon_cancel_it_automation_task_execution`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Cancel an active IT Automation task execution.

### `falcon_rerun_it_automation_task_execution`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IT Automation:write`

Rerun an IT Automation task execution.

## Resources

- **`falcon://it-automation/task-executions/fql-guide`**: Contains the guide for the `filter` parameter of IT Automation task execution search tools.
- **`falcon://it-automation/phase3/safety-guide`**: Safety and execution guidance for high-impact IT Automation write and execution tools.
