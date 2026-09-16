<!-- meta:title Spotlight -->
<!-- meta:description This module provides full Falcon Spotlight Vulnerabilities service collection coverage: combined search, ID query, vulnerability detail retrieval, and remediation retrieval -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Spotlight Vulnerabilities service collection coverage: combined search, ID query, vulnerability detail retrieval, and remediation retrieval

## API Scopes

- `Vulnerabilities:read`

## Tools

### `falcon_search_vulnerabilities`

**Required scopes:** `Vulnerabilities:read`

Search Spotlight vulnerabilities using the combined endpoint.

**Example prompts:**

- "Show me open HIGH severity vulnerabilities"
- "Find vulnerabilities on host xyz"

### `falcon_query_vulnerability_ids`

**Required scopes:** `Vulnerabilities:read`

Query Spotlight vulnerability IDs.

### `falcon_get_vulnerability_details`

**Required scopes:** `Vulnerabilities:read`

Get vulnerability detail records by ID.

### `falcon_get_remediation_details`

**Required scopes:** `Vulnerabilities:read`

Get remediation detail records by ID (v1 endpoint).

### `falcon_get_remediation_details_v2`

**Required scopes:** `Vulnerabilities:read`

Get remediation detail records by ID (v2 endpoint).

## Resources

- **`falcon://spotlight/vulnerabilities/fql-guide`**: FQL guidance for Spotlight vulnerability search and query tools.
- **`falcon://spotlight/remediations/usage-guide`**: Guidance for retrieving Spotlight remediations by remediation ID.
