<!-- meta:title Falcon Data Replicator (FDR) -->
<!-- meta:description Retrieving the combined FDR schema and querying event and field schema entities -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Retrieving the combined FDR schema and querying event and field schema entities

## API Scopes

- `falcon-data-replicator:read`

## Tools

### `falcon_get_fdr_combined_schema`

**Required scopes:** `falcon-data-replicator:read`

Retrieve the combined FDR schema document.

### `falcon_query_fdr_event_schema_ids`

**Required scopes:** `falcon-data-replicator:read`

Query FDR event schema IDs.

### `falcon_get_fdr_event_schema_details`

**Required scopes:** `falcon-data-replicator:read`

Retrieve FDR event schema details by ID.

### `falcon_search_fdr_event_schemas`

**Required scopes:** `falcon-data-replicator:read`

Search FDR event schemas and return full schema details.

### `falcon_query_fdr_field_schema_ids`

**Required scopes:** `falcon-data-replicator:read`

Query FDR field schema IDs.

### `falcon_get_fdr_field_schema_details`

**Required scopes:** `falcon-data-replicator:read`

Retrieve FDR field schema details by ID.

### `falcon_search_fdr_field_schemas`

**Required scopes:** `falcon-data-replicator:read`

Search FDR field schemas and return full schema details.

## Resources

- **`falcon://fdr/events/fql-guide`**: FQL guidance for FDR event schema query tools.
- **`falcon://fdr/fields/fql-guide`**: FQL guidance for FDR field schema query tools.
