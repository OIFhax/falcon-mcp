<!-- meta:title Response Policies -->
<!-- meta:description This module provides full Falcon Response Policies service collection coverage: search, query, get, create, update, delete, action, and precedence operations -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Response Policies service collection coverage: search, query, get, create, update, delete, action, and precedence operations

## API Scopes

- `Response Policies:read`
- `Response Policies:write`

## Tools

### `falcon_search_response_policies`

**Required scopes:** `Response Policies:read`

Search response policies and return combined details.

### `falcon_search_response_policy_members`

**Required scopes:** `Response Policies:read`

Search members of a response policy and return combined details.

### `falcon_query_response_policy_ids`

**Required scopes:** `Response Policies:read`

Query response policy IDs.

### `falcon_query_response_policy_member_ids`

**Required scopes:** `Response Policies:read`

Query response policy member IDs.

### `falcon_get_response_policy_details`

**Required scopes:** `Response Policies:read`

Get response policy details by ID.

### `falcon_create_response_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Response Policies:write`

Create response policies.

### `falcon_update_response_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Response Policies:write`

Update response policies.

### `falcon_delete_response_policies`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Response Policies:write`

Delete response policies by ID.

### `falcon_perform_response_policies_action`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Response Policies:write`

Perform an action against response policies.

### `falcon_set_response_policies_precedence`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Response Policies:write`

Set response policy precedence order.

## Resources

- **`falcon://response-policies/policies/fql-guide`**: Contains FQL guidance for response policy search tools.
- **`falcon://response-policies/members/fql-guide`**: Contains FQL guidance for response policy member search tools.
- **`falcon://response-policies/safety-guide`**: Safety and operational guidance for response policy write tools.
