<!-- meta:title Drift Indicators -->
<!-- meta:description Counting, querying, and retrieving drift indicator entities -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Counting, querying, and retrieving drift indicator entities

## API Scopes

- `drift-indicators:read`

## Tools

### `falcon_get_drift_indicator_values_by_date`

**Required scopes:** `drift-indicators:read`

Return drift indicator counts grouped by date.

### `falcon_get_drift_indicator_count`

**Required scopes:** `drift-indicators:read`

Return the total count of drift indicators.

### `falcon_query_drift_indicator_ids`

**Required scopes:** `drift-indicators:read`

Query drift indicator IDs.

### `falcon_get_drift_indicator_details`

**Required scopes:** `drift-indicators:read`

Retrieve drift indicator entities by ID.

### `falcon_search_drift_indicator_entities`

**Required scopes:** `drift-indicators:read`

Search drift indicators and return full entity records.

## Resources

- **`falcon://drift-indicators/fql-guide`**: FQL guidance for Drift Indicators query and search tools.
