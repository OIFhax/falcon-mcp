<!-- meta:title Zero Trust Assessment -->
<!-- meta:description Querying host Zero Trust scores and retrieving assessment details and tenant audit metrics -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Querying host Zero Trust scores and retrieving assessment details and tenant audit metrics

> [!NOTE]
> This module is not available on CrowdStrike's hosted Falcon MCP; it is only available when self-hosting this server. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

## API Scopes

- `Zero Trust Assessment:read`

## Tools

### `falcon_search_zta_assessments`

**Required scopes:** `Zero Trust Assessment:read`

Search Zero Trust scores and return full assessment details.

**Example prompts:**

- "Which hosts have the weakest Zero Trust posture?"
- "Show me hosts scoring below 40 on Zero Trust Assessment"

### `falcon_search_zta_assessments_by_score`

**Required scopes:** `Zero Trust Assessment:read`

Search for host Zero Trust assessments by score filter.

### `falcon_search_zta_combined_assessments`

**Required scopes:** `Zero Trust Assessment:read`

Search for combined Zero Trust assessments with host/finding facets.

### `falcon_get_zta_assessment_details`

**Required scopes:** `Zero Trust Assessment:read`

Retrieve Zero Trust assessment details for specific host agent IDs.

### `falcon_get_zta_audit_report`

**Required scopes:** `Zero Trust Assessment:read`

Retrieve tenant-wide Zero Trust Assessment audit metrics.

## Resources

- **`falcon://zero-trust-assessment/assessments/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_zta_assessments_by_score` tool.
- **`falcon://zero-trust-assessment/combined-assessments/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_zta_combined_assessments` tool.
