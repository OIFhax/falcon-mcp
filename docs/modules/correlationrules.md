<!-- meta:title Correlation Rules -->
<!-- meta:description This module provides full Falcon Correlation Rules coverage across query, get, aggregate, version lifecycle, and rule lifecycle workflows -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Correlation Rules coverage across query, get, aggregate, version lifecycle, and rule lifecycle workflows

## API Scopes

- `correlation-rules:read`
- `correlation-rules:write`

## Tools

### `falcon_search_correlation_rules`

**Required scopes:** `correlation-rules:read`

Search NG-SIEM Correlation Rules and return full rule details.

Use this to find detection rules by name, status, severity, or MITRE tactic/technique.
Consult falcon://correlation-rules/search/fql-guide before constructing filter expressions.
Returns full rule objects; use the `rule_id` field when passing results to update or
delete tools. Filter with state:'published' to get one result per rule.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Show me all active high-severity correlation rules"
- "Find correlation rules covering lateral movement tactics"

### `falcon_search_correlation_rules_v1`

**Required scopes:** `correlation-rules:read`

Search correlation rules using the v1 combined endpoint.

### `falcon_search_correlation_rules_v2`

**Required scopes:** `correlation-rules:read`

Search correlation rules using the v2 combined endpoint.

### `falcon_query_correlation_rule_ids`

**Required scopes:** `correlation-rules:read`

Query correlation rule IDs.

### `falcon_query_correlation_rule_version_ids`

**Required scopes:** `correlation-rules:read`

Query correlation rule version IDs.

### `falcon_get_correlation_rules`

**Required scopes:** `correlation-rules:read`

Retrieve correlation rules by ID.

### `falcon_get_correlation_rule_versions`

**Required scopes:** `correlation-rules:read`

Retrieve correlation rule versions by ID.

### `falcon_get_latest_correlation_rule_versions`

**Required scopes:** `correlation-rules:read`

Retrieve latest rule versions by rule ID.

### `falcon_aggregate_correlation_rule_versions`

**Required scopes:** `correlation-rules:write`

Aggregate correlation rule versions.

### `falcon_create_correlation_rule`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `correlation-rules:write`

Create a correlation rule from structured fields or a confirmed raw body.

**Example prompts:**

- "Create a correlation rule using this CQL query: #event_simpleName=ProcessRollup2 | CommandLine=*-EncodedCommand*"

### `falcon_update_correlation_rule`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `correlation-rules:write`

Update a correlation rule from structured fields or a confirmed raw body.

**Example prompts:**

- "Disable the correlation rule — set its status to inactive"
- "Update the rule severity to critical (90)"

### `falcon_delete_correlation_rules`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `correlation-rules:write`

Delete correlation rules by ID.

**Example prompts:**

- "Delete the test correlation rule we created"

### `falcon_export_correlation_rule_versions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `correlation-rules:write`

Export correlation rule versions.

### `falcon_import_correlation_rule`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `correlation-rules:write`

Import a correlation rule version.

### `falcon_publish_correlation_rule_version`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `correlation-rules:write`

Publish a correlation rule version.

### `falcon_delete_correlation_rule_versions`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `correlation-rules:write`

Delete correlation rule versions by ID.

## Resources

- **`falcon://correlation-rules/search/fql-guide`**: Contains the guide for the `filter` parameter of `falcon_search_correlation_rules`.
- **`falcon://correlation-rules/fql-guide`**: FQL guidance for Correlation Rules search tools.
- **`falcon://correlation-rules/safety-guide`**: Safety guidance for Correlation Rules write tools.
