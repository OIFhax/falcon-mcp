<!-- meta:title MalQuery -->
<!-- meta:description MalQuery quotas, searches, metadata, request status, and downloads -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

MalQuery quotas, searches, metadata, request status, and downloads

## API Scopes

- `malquery:read`
- `malquery:write`

## Tools

### `falcon_get_malquery_quotas`

**Required scopes:** `malquery:read`

Retrieve MalQuery quotas.

### `falcon_fuzzy_search_malquery`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `malquery:write`

Run a fuzzy MalQuery search.

### `falcon_exact_search_malquery`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `malquery:write`

Run an exact MalQuery search.

### `falcon_hunt_malquery`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `malquery:write`

Schedule a YARA hunt in MalQuery.

### `falcon_get_malquery_request`

**Required scopes:** `malquery:read`

Retrieve asynchronous MalQuery request status.

### `falcon_get_malquery_metadata`

**Required scopes:** `malquery:read`

Retrieve MalQuery metadata for SHA256 values.

### `falcon_get_malquery_samples_archive`

**Required scopes:** `malquery:read`

Retrieve the MalQuery samples archive for a completed multi-download request.

### `falcon_schedule_malquery_samples_multidownload`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `malquery:write`

Schedule MalQuery sample hashes for multi-download.

### `falcon_download_malquery_sample`

**Required scopes:** `malquery:read`

Download a single MalQuery sample by SHA256.

## Resources

- **`falcon://malquery/usage-guide`**: Usage guidance for Falcon MalQuery tools.
- **`falcon://malquery/safety-guide`**: Safety guidance for Falcon MalQuery write operations.
