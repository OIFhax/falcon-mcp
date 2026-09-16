<!-- meta:title Firewall Policies -->
<!-- meta:description This module provides full Falcon Firewall Policies service collection coverage: search, query, get, create, update, delete, action, and precedence operations -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Firewall Policies service collection coverage: search, query, get, create, update, delete, action, and precedence operations

## API Scopes

- `Firewall Policies:read`
- `Firewall Policies:write`

## Tools

### `falcon_search_firewall_policy_members`

**Required scopes:** `Firewall Policies:read`

Search members of a firewall policy and return combined details.

### `falcon_search_firewall_policies`

**Required scopes:** `Firewall Policies:read`

Search firewall policies and return combined details.

### `falcon_perform_firewall_policies_action`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Firewall Policies:write`

Perform an action against firewall policies.

### `falcon_set_firewall_policies_precedence`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Policies:write`

Set firewall policy precedence order.

### `falcon_get_firewall_policy_details`

**Required scopes:** `Firewall Policies:read`

Get firewall policy details by ID.

### `falcon_create_firewall_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Policies:write`

Create firewall policies.

### `falcon_update_firewall_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Policies:write`

Update firewall policies.

### `falcon_delete_firewall_policies`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Firewall Policies:write`

Delete firewall policies by ID.

### `falcon_query_firewall_policy_member_ids`

**Required scopes:** `Firewall Policies:read`

Query firewall policy member IDs.

### `falcon_query_firewall_policy_ids`

**Required scopes:** `Firewall Policies:read`

Query firewall policy IDs.

## Resources

- **`falcon://firewall-policies/policies/fql-guide`**: Contains FQL guidance for firewall policy search tools.
- **`falcon://firewall-policies/members/fql-guide`**: Contains FQL guidance for firewall policy member search tools.
- **`falcon://firewall-policies/safety-guide`**: Safety and operational guidance for firewall policy write tools.
