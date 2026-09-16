<!-- meta:title Prevention Policies -->
<!-- meta:description This module provides full Falcon Prevention Policies service collection coverage: search, query, get, create, update, delete, action, and precedence operations -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Prevention Policies service collection coverage: search, query, get, create, update, delete, action, and precedence operations

## API Scopes

- `Prevention Policies:read`
- `Prevention Policies:write`

## Tools

### `falcon_search_prevention_policies`

**Required scopes:** `Prevention Policies:read`

Search prevention policies and return combined details.

### `falcon_search_prevention_policy_members`

**Required scopes:** `Prevention Policies:read`

Search members of a prevention policy and return combined details.

### `falcon_query_prevention_policy_ids`

**Required scopes:** `Prevention Policies:read`

Query prevention policy IDs.

### `falcon_query_prevention_policy_member_ids`

**Required scopes:** `Prevention Policies:read`

Query prevention policy member IDs.

### `falcon_get_prevention_policy_details`

**Required scopes:** `Prevention Policies:read`

Get prevention policy details by ID.

### `falcon_create_prevention_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Prevention Policies:write`

Create prevention policies.

### `falcon_update_prevention_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Prevention Policies:write`

Update prevention policies.

### `falcon_delete_prevention_policies`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Prevention Policies:write`

Delete prevention policies by ID.

### `falcon_perform_prevention_policies_action`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Prevention Policies:write`

Perform an action against prevention policies.

### `falcon_set_prevention_policies_precedence`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Prevention Policies:write`

Set prevention policy precedence order.

## Resources

- **`falcon://prevention-policies/policies/fql-guide`**: Contains FQL guidance for prevention policy search tools.
- **`falcon://prevention-policies/members/fql-guide`**: Contains FQL guidance for prevention policy member search tools.
- **`falcon://prevention-policies/safety-guide`**: Safety and operational guidance for prevention policy write tools.
