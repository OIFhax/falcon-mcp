<!-- meta:title Content Update Policies -->
<!-- meta:description This module provides full Falcon Content Update Policies service collection coverage: search, query, get, create, update, delete, action, and precedence operations -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Content Update Policies service collection coverage: search, query, get, create, update, delete, action, and precedence operations

## API Scopes

- `Content Update Policies:read`
- `Content Update Policies:write`

## Tools

### `falcon_search_content_update_policies`

**Required scopes:** `Content Update Policies:read`

Search content update policies and return combined details.

### `falcon_search_content_update_policy_members`

**Required scopes:** `Content Update Policies:read`

Search members of a content update policy and return combined details.

### `falcon_query_content_update_policy_ids`

**Required scopes:** `Content Update Policies:read`

Query content update policy IDs.

### `falcon_query_content_update_policy_member_ids`

**Required scopes:** `Content Update Policies:read`

Query content update policy member IDs.

### `falcon_query_content_update_pinnable_versions`

**Required scopes:** `Content Update Policies:read`

Query pinnable content versions for a category.

### `falcon_get_content_update_policy_details`

**Required scopes:** `Content Update Policies:read`

Get content update policy details by ID.

### `falcon_create_content_update_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Content Update Policies:write`

Create content update policies.

### `falcon_update_content_update_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Content Update Policies:write`

Update content update policies.

### `falcon_delete_content_update_policies`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Content Update Policies:write`

Delete content update policies by ID.

### `falcon_perform_content_update_policies_action`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Content Update Policies:write`

Perform an action against content update policies.

### `falcon_set_content_update_policies_precedence`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Content Update Policies:write`

Set content update policy precedence order.

## Resources

- **`falcon://content-update-policies/policies/fql-guide`**: Contains FQL guidance for content update policy search tools.
- **`falcon://content-update-policies/members/fql-guide`**: Contains FQL guidance for content update policy member search tools.
- **`falcon://content-update-policies/pinnable-versions/guide`**: Guidance for querying pinnable content versions.
- **`falcon://content-update-policies/safety-guide`**: Safety and operational guidance for content update policy write tools.
