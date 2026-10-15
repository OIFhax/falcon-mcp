<!-- meta:title Installation Tokens -->
<!-- meta:description Querying and managing installation tokens, reviewing token audit events, and reading/updating token customer settings -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Querying and managing installation tokens, reviewing token audit events, and reading/updating token customer settings

## API Scopes

- `Installation Tokens:read`
- `Installation Tokens Settings:write`
- `Installation Tokens:write`

## Tools

### `falcon_search_installation_tokens`

**Required scopes:** `Installation Tokens:read`

Search installation tokens and return full token details.

### `falcon_get_installation_token_details`

**Required scopes:** `Installation Tokens:read`

Retrieve installation token details by ID.

### `falcon_create_installation_token`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Installation Tokens:write`

Create an installation token.

### `falcon_update_installation_tokens`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Installation Tokens:write`

Update installation tokens by ID.

### `falcon_delete_installation_tokens`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Installation Tokens:write`

Delete installation tokens by ID.

### `falcon_search_installation_token_audit_events`

**Required scopes:** `Installation Tokens:read`

Search installation token audit events and return full event details.

### `falcon_get_installation_token_audit_event_details`

**Required scopes:** `Installation Tokens:read`

Retrieve installation token audit event details by ID.

### `falcon_get_installation_token_customer_settings`

**Required scopes:** `Installation Tokens:read`

Retrieve installation token customer settings.

### `falcon_update_installation_token_customer_settings`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Installation Tokens Settings:write`

Update installation token customer settings.

## Resources

- **`falcon://installation-tokens/tokens/fql-guide`**: Contains the guide for the `filter` parameter of `falcon_search_installation_tokens`.
- **`falcon://installation-tokens/audit/fql-guide`**: Contains the guide for the `filter` parameter of `falcon_search_installation_token_audit_events`.
- **`falcon://installation-tokens/safety-guide`**: Safety and operational guidance for installation token write tools.
