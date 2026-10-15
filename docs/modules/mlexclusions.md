<!-- meta:title ML Exclusions -->
<!-- meta:description Searching, retrieving, creating, updating, and deleting Falcon ML exclusions -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching, retrieving, creating, updating, and deleting Falcon ML exclusions

## API Scopes

- `ml-exclusions:read`
- `ml-exclusions:write`

## Tools

### `falcon_search_ml_exclusions`

**Required scopes:** `ml-exclusions:read`

Search ML exclusions and return full exclusion details.

### `falcon_query_ml_exclusion_ids`

**Required scopes:** `ml-exclusions:read`

Query ML exclusion IDs.

### `falcon_get_ml_exclusion_details`

**Required scopes:** `ml-exclusions:read`

Get ML exclusion details by ID.

### `falcon_create_ml_exclusions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `ml-exclusions:write`

Create an ML exclusion.

### `falcon_update_ml_exclusions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `ml-exclusions:write`

Update an ML exclusion.

### `falcon_delete_ml_exclusions`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `ml-exclusions:write`

Delete ML exclusions by ID.

## Resources

- **`falcon://ml-exclusions/search/fql-guide`**: Contains FQL guidance for ML exclusions search tools.
- **`falcon://ml-exclusions/safety-guide`**: Safety and operational guidance for ML exclusions write tools.
