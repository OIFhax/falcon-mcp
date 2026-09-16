<!-- meta:title NGSIEM -->
<!-- meta:description This module provides full FalconPy NGSIEM service collection coverage for search jobs, dashboards, lookup files, parsers, and saved queries -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full FalconPy NGSIEM service collection coverage for search jobs, dashboards, lookup files, parsers, and saved queries

## API Scopes

- `NGSIEM:read`
- `NGSIEM:write`

## Tools

### `falcon_search_ngsiem`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Execute asynchronous NGSIEM search and return matching events.

**Example prompts:**

- "Run this CQL query for the last 24 hours: #event_simpleName=ProcessRollup2"
- "Search NGSIEM for DNS events from January 2025"

### `falcon_start_ngsiem_search`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Start an NGSIEM search job and return job metadata.

### `falcon_get_ngsiem_search_status`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM search job status and results payload.

### `falcon_stop_ngsiem_search`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `NGSIEM:write`

Stop an NGSIEM search job.

### `falcon_get_ngsiem_dashboard_template`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM dashboard template.

### `falcon_create_ngsiem_dashboard_from_template`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Create NGSIEM dashboard from template.

### `falcon_update_ngsiem_dashboard_from_template`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Update NGSIEM dashboard from template.

### `falcon_delete_ngsiem_dashboard`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `NGSIEM:write`

Delete NGSIEM dashboard by ID.

### `falcon_list_ngsiem_dashboards`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

List NGSIEM dashboards.

### `falcon_upload_ngsiem_lookup`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Upload NGSIEM lookup file.

### `falcon_get_ngsiem_lookup`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM lookup by repository and filename.

### `falcon_get_ngsiem_lookup_from_package`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM lookup from package.

### `falcon_get_ngsiem_lookup_from_namespace_package`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM lookup from namespace and package.

### `falcon_get_ngsiem_lookup_file`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM lookup file metadata/content response.

### `falcon_create_ngsiem_lookup_file`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Create NGSIEM lookup file.

### `falcon_update_ngsiem_lookup_file`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Update NGSIEM lookup file.

### `falcon_delete_ngsiem_lookup_file`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `NGSIEM:write`

Delete NGSIEM lookup file.

### `falcon_list_ngsiem_lookup_files`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

List NGSIEM lookup files.

### `falcon_get_ngsiem_parser_template`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM parser template.

### `falcon_create_ngsiem_parser_from_template`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Create NGSIEM parser from template.

### `falcon_get_ngsiem_parser`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM parser by ID.

### `falcon_create_ngsiem_parser`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Create NGSIEM parser.

### `falcon_update_ngsiem_parser`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Update NGSIEM parser.

### `falcon_delete_ngsiem_parser`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `NGSIEM:write`

Delete NGSIEM parser.

### `falcon_list_ngsiem_parsers`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

List NGSIEM parsers.

### `falcon_get_ngsiem_saved_query_template`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

Get NGSIEM saved query template.

### `falcon_create_ngsiem_saved_query`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Create NGSIEM saved query.

### `falcon_update_ngsiem_saved_query_from_template`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `NGSIEM:write`

Update NGSIEM saved query from template.

### `falcon_delete_ngsiem_saved_query`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `NGSIEM:write`

Delete NGSIEM saved query.

### `falcon_list_ngsiem_saved_queries`

**Required scopes:** `NGSIEM:read`, `NGSIEM:write`

List NGSIEM saved queries.

## Resources

- **`falcon://ngsiem/repository-guide`**: Repository and operation guidance for NGSIEM tools.
- **`falcon://ngsiem/search-guide`**: Search workflow guidance for NGSIEM tools.
- **`falcon://ngsiem/safety-guide`**: Safety and operational guidance for NGSIEM write tools.
