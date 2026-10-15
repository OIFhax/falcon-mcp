<!-- meta:title User Management -->
<!-- meta:description Searching users/roles and performing controlled user and role assignment changes through Falcon User Management APIs -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching users/roles and performing controlled user and role assignment changes through Falcon User Management APIs

## API Scopes

- `User Management:read`
- `User Management:write`

## Tools

### `falcon_aggregate_users`

**Required scopes:** `User Management:read`

Run aggregate analysis over user-management records.

### `falcon_search_users`

**Required scopes:** `User Management:read`

Search users and return full user details.

### `falcon_get_user_details`

**Required scopes:** `User Management:read`

Retrieve user records by user UUID.

### `falcon_search_user_roles`

**Required scopes:** `User Management:read`

Search roles and return full role details.

### `falcon_get_user_role_details`

**Required scopes:** `User Management:read`

Retrieve role records by role ID using entitiesRolesGETV2.

### `falcon_get_user_role_details_v1`

**Required scopes:** `User Management:read`

Retrieve role records by role ID using entitiesRolesV1.

### `falcon_get_user_role_grants`

**Required scopes:** `User Management:read`

Retrieve user role grants for a specific user UUID.

### `falcon_create_user`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `User Management:write`

Create a user (or validate the creation payload).

### `falcon_update_user`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `User Management:write`

Update a user's first and last name.

### `falcon_delete_user`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `User Management:write`

Delete a user by user UUID.

### `falcon_perform_user_action`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `User Management:write`

Apply user actions such as password or 2FA reset.

### `falcon_grant_user_roles`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `User Management:write`

Grant one or more roles to a user.

### `falcon_revoke_user_roles`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `User Management:write`

Revoke one or more roles from a user.

## Resources

- **`falcon://user-management/users/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_users` tool.
- **`falcon://user-management/user-role-grants/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_get_user_role_grants` tool.
- **`falcon://user-management/safety-guide`**: Safety and operational guidance for User Management write tools.
