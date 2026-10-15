<!-- meta:title Quarantine -->
<!-- meta:description Searching quarantined files, aggregating quarantine data, reviewing action impact counts, and applying quarantine update actions -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching quarantined files, aggregating quarantine data, reviewing action impact counts, and applying quarantine update actions

## API Scopes

- `Quarantined Files:read`
- `Quarantined Files:write`

## Tools

### `falcon_search_quarantine_files`

**Required scopes:** `Quarantined Files:read`

Search quarantined files and return full metadata records.

### `falcon_get_quarantine_file_details`

**Required scopes:** `Quarantined Files:read`

Retrieve quarantined file metadata by ID.

### `falcon_aggregate_quarantine_files`

**Required scopes:** `Quarantined Files:read`

Run aggregate queries for quarantined file data.

### `falcon_get_quarantine_action_update_count`

**Required scopes:** `Quarantined Files:read`

Return count of potentially affected quarantined files for each action.

### `falcon_update_quarantine_files_by_ids`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Quarantined Files:write`

Apply release / unrelease / delete action to quarantine files by ID.

### `falcon_update_quarantine_files_by_query`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Quarantined Files:write`

Apply release / unrelease / delete action to quarantine files by query.

### `falcon_search_quarantined_files`

**Required scopes:** `Quarantined Files:read`

Search quarantined files and return full quarantine metadata.

Use this to discover quarantine records by host, hash, user, or state.
Consult falcon://quarantine/files/search/fql-guide before constructing
filter expressions. Returns full quarantine details including hostname,
sha256, paths, state, and associated alert and detection IDs.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me quarantined files on host SE-DAO-WIN10-CO"
- "Find quarantined files for user badguy updated in the last 7 days"
- "Search for quarantined files with SHA256 starting with 3dd9"

### `falcon_preview_quarantine_actions`

**Required scopes:** `Quarantined Files:read`

Estimate how many quarantine records each action would affect for a given filter.

Use this read-only tool before calling a mutating quarantine action to
understand the blast radius of a release, unrelease, or delete request.
Consult falcon://quarantine/files/search/fql-guide before constructing
filter expressions. Returns a list of action counts keyed by action name.

**Example prompts:**

- "Preview how many quarantined files can be released vs deleted"
- "Preview quarantine action impact for state quarantined on host SE-DAO-WIN10-CO"

### `falcon_update_quarantined_files`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Quarantined Files:write`

Apply a reversible quarantine action to records selected by IDs or filter.

Use this to release or unrelease quarantined files. Provide `ids` for
specific records, or `filter` to select by query. Consult
falcon://quarantine/files/search/fql-guide before constructing filter
expressions. Returns an empty list on success.

**Example prompts:**

- "Release quarantine record abc123"
- "Release all quarantined files for user badguy"

### `falcon_delete_quarantined_files`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Quarantined Files:write`

Delete quarantine records selected by IDs or filter.

This tool is destructive and should be used only when quarantine records
should be removed rather than released. Provide `ids` for specific records,
or `filter` to select by query. Consult falcon://quarantine/files/search/fql-guide
before constructing filter expressions. Returns an empty list on success.

**Example prompts:**

- "Delete quarantine records for host SE-DAO-WIN10-CO"
- "Delete quarantine record abc123"

## Resources

- **`falcon://quarantine/files/fql-guide`**: Contains the guide for the `filter` parameter of quarantine search and action count tools.
- **`falcon://quarantine/files/aggregation-guide`**: Guidance and example body for `falcon_aggregate_quarantine_files`.
- **`falcon://quarantine/files/safety-guide`**: Safety and operational guidance for quarantine update tools.
- **`falcon://quarantine/files/search/fql-guide`**: Contains the guide for upstream quarantine search and filter-based actions.
