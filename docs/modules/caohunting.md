<!-- meta:title CAO Hunting -->
<!-- meta:description Searching and retrieving hunting guides and intelligence queries via CrowdStrike CAO Hunting APIs -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching and retrieving hunting guides and intelligence queries via CrowdStrike CAO Hunting APIs

## API Scopes

- `CAO Hunting:read`

## Tools

### `falcon_search_hunting_guides`

**Required scopes:** `CAO Hunting:read`

Search hunting guides and return full guide details.

### `falcon_get_hunting_guide_details`

**Required scopes:** `CAO Hunting:read`

Retrieve hunting guide details by ID.

### `falcon_search_intelligence_queries`

**Required scopes:** `CAO Hunting:read`

Search intelligence queries and return full query details.

### `falcon_get_intelligence_query_details`

**Required scopes:** `CAO Hunting:read`

Retrieve intelligence query details by ID.

### `falcon_aggregate_hunting_guides`

**Required scopes:** `CAO Hunting:read`

Run aggregate analysis over hunting guides.

### `falcon_aggregate_intelligence_queries`

**Required scopes:** `CAO Hunting:read`

Run aggregate analysis over intelligence queries.

### `falcon_create_hunting_archive_export`

**Required scopes:** `CAO Hunting:read`

Create an archive export request for intelligence queries.

## Resources

- **`falcon://cao-hunting/guides/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_hunting_guides` tool.
- **`falcon://cao-hunting/intelligence-queries/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_intelligence_queries` tool.
- **`falcon://cao-hunting/archive-export/guide`**: Usage guidance for `falcon_create_hunting_archive_export`.
