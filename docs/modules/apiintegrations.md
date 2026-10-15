<!-- meta:title API Integrations -->
<!-- meta:description Searching plugin configs and executing plugin operations -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching plugin configs and executing plugin operations

## API Scopes

- `api-integrations:read`
- `api-integrations:write`

## Tools

### `falcon_search_api_integration_plugin_configs`

**Required scopes:** `api-integrations:read`

Search API Integration plugin configs and return combined details.

### `falcon_execute_api_integration_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `api-integrations:write`

Execute an API Integration command.

### `falcon_execute_api_integration_command_proxy`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `api-integrations:write`

Execute an API Integration proxy command.

## Resources

- **`falcon://api-integrations/plugin-configs/fql-guide`**: FQL guidance for API Integrations plugin config search.
- **`falcon://api-integrations/safety-guide`**: Safety guidance for API Integrations execution tools.
