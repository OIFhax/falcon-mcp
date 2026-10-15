<!-- meta:title IOA Exclusions -->
<!-- meta:description Searching, creating, updating, and deleting Falcon IOA exclusions -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching, creating, updating, and deleting Falcon IOA exclusions

## API Scopes

- `IOA Exclusions:read`
- `IOA Exclusions:write`

## Tools

### `falcon_search_ioa_exclusions`

**Required scopes:** `IOA Exclusions:read`

Search IOA exclusions and return full exclusion details.

### `falcon_add_ioa_exclusion`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IOA Exclusions:write`

Create an IOA exclusion.

### `falcon_update_ioa_exclusion`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `IOA Exclusions:write`

Update an existing IOA exclusion.

### `falcon_remove_ioa_exclusions`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `IOA Exclusions:write`

Delete IOA exclusions by IDs.

## Resources

- **`falcon://ioa-exclusions/search/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_ioa_exclusions` tool.
