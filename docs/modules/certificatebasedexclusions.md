<!-- meta:title Certificate Based Exclusions -->
<!-- meta:description Searching, retrieving, creating, updating, and deleting Falcon certificate based exclusions, plus certificate lookup -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching, retrieving, creating, updating, and deleting Falcon certificate based exclusions, plus certificate lookup

## API Scopes

- `ml-exclusions:read`
- `ml-exclusions:write`

## Tools

### `falcon_search_certificate_based_exclusions`

**Required scopes:** `ml-exclusions:read`

### `falcon_query_certificate_based_exclusion_ids`

**Required scopes:** `ml-exclusions:read`

### `falcon_get_certificate_based_exclusion_details`

**Required scopes:** `ml-exclusions:read`

### `falcon_get_certificate_signing_info`

**Required scopes:** `ml-exclusions:read`

### `falcon_create_certificate_based_exclusions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `ml-exclusions:write`

### `falcon_update_certificate_based_exclusions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `ml-exclusions:write`

### `falcon_delete_certificate_based_exclusions`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `ml-exclusions:write`

## Resources

- **`falcon://certificate-based-exclusions/search/fql-guide`**: FQL guidance for certificate based exclusions search tools.
- **`falcon://certificate-based-exclusions/certificates/guide`**: Usage guidance for certificate signing lookups.
- **`falcon://certificate-based-exclusions/safety-guide`**: Safety and operational guidance for certificate based exclusion write tools.
