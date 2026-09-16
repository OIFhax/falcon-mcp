<!-- meta:title Quick Scan -->
<!-- meta:description This module provides search, aggregation, detail, and sample-submission tools for Quick Scan -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides search, aggregation, detail, and sample-submission tools for Quick Scan

## API Scopes

- `quick-scan:read`
- `quick-scan:write`

## Tools

### `falcon_search_quick_scans`

**Required scopes:** `quick-scan:read`

Search Quick Scan submissions and return scan details.

### `falcon_query_quick_scan_ids`

**Required scopes:** `quick-scan:read`

Query Quick Scan submission IDs.

### `falcon_get_quick_scans`

**Required scopes:** `quick-scan:read`

Retrieve Quick Scan records by ID.

### `falcon_aggregate_quick_scans`

**Required scopes:** `quick-scan:read`

Run Quick Scan aggregate queries.

### `falcon_scan_quick_samples`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `quick-scan:write`

Submit sample hashes for Quick Scan.

## Resources

- **`falcon://quick-scan/fql-guide`**: FQL guidance for Quick Scan history queries.
- **`falcon://quick-scan/safety-guide`**: Safety guidance for Quick Scan sample submission.
