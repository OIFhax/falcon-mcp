<!-- meta:title Fusion playbooks -->
<!-- meta:description This module fills the narrow read-only gap between public workflow-definition APIs and newer Fusion playbook UI routes -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module fills the narrow read-only gap between public workflow-definition APIs and newer Fusion playbook UI routes

## API Scopes

- `Workflow:read`
- `Workflow:write`

## Tools

### `falcon_get_fusion_playbook`

**Required scopes:** `Workflow:read`

Retrieve a Fusion playbook or compatible workflow definition by ID.

### `falcon_import_fusion_playbook`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Import a Fusion playbook from workflow-definition YAML text.

### `falcon_update_fusion_playbook`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Update a Fusion playbook backed by a workflow definition.

### `falcon_update_fusion_playbook_status`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Workflow:write`

Enable, disable, or cancel in-flight executions for Fusion playbooks.

### `falcon_execute_fusion_playbook`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Execute an on-demand Fusion playbook.

### `falcon_mock_execute_fusion_playbook`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Workflow:write`

Execute a Fusion playbook definition with mocks.

## Resources

- **`falcon://fusion-playbooks/guide`**: Guidance for read-only Fusion playbook retrieval.
