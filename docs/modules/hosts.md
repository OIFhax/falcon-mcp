<!-- meta:title Hosts -->
<!-- meta:description Hosts, Host Groups, and Host Migration -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Hosts, Host Groups, and Host Migration

## API Scopes

- `Host Groups:read`
- `Host Migration:read`
- `Hosts:read`
- `Host Groups:write`
- `Host Migration:write`
- `Hosts:write`

## Tools

### `falcon_search_hosts`

**Required scopes:** `Hosts:read`

Search for hosts and return full host details.

**Example prompts:**

- "Find all Windows hosts in my environment"
- "Show me hosts last seen in the past 24 hours"

### `falcon_get_host_details`

**Required scopes:** `Hosts:read`

Retrieve detailed information for specific host device IDs.

**Example prompts:**

- "Get the full details for host device abc123"

### `falcon_search_scoped_host_groups`

**Required scopes:** `Host Groups:read`

Search host groups and return full host group details.

### `falcon_search_scoped_host_group_members`

**Required scopes:** `Host Groups:read`

Search members in a host group and return full host details.

### `falcon_add_host_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Groups:write`

Create a host group.

### `falcon_update_scoped_host_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Groups:write`

Update a host group.

### `falcon_remove_host_groups`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Host Groups:write`

Delete host groups by IDs.

### `falcon_perform_scoped_host_group_action`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Groups:write`

Perform an action against one or more host groups.

### `falcon_search_migrations`

**Required scopes:** `Host Migration:read`

Search migration jobs and return full migration details.

### `falcon_search_host_migrations`

**Required scopes:** `Host Migration:read`

Search host migration entities and return full host migration details.

### `falcon_create_migration`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Migration:write`

Create a host migration job.

### `falcon_get_migration_destinations`

**Required scopes:** `Host Migration:read`

Get available migration destinations for selected hosts.

### `falcon_perform_migration_action`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Migration:write`

Perform an action on migration jobs.

### `falcon_perform_host_migration_action`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Host Migration:write`

Perform an action on host migration entities.

### `falcon_manage_host_grouping_tags`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Hosts:write`

Add or remove Falcon Grouping Tags on one or more hosts.

Set action to 'add' to attach tags, or 'remove' to detach them, on every device
in `ids`. Grouping tags can drive dynamic host group assignment and therefore
policy assignment, so changing them may change a host's security posture.
Adding a tag a host already has, or removing one it lacks, is a no-op. Returns
one record per device, each with `device_id`, `updated`, and `code`. Tag names
are case-sensitive, so removing a tag requires the exact casing it was created
with.

## Resources

- **`falcon://hosts/search/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_hosts` tool.
- **`falcon://hosts/groups/fql-guide`**: Contains the guide for the `filter` parameter of host group search tools.
- **`falcon://hosts/migrations/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_migrations` tool.
- **`falcon://hosts/host-migrations/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_host_migrations` tool.
