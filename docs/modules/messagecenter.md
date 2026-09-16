<!-- meta:title Message Center -->
<!-- meta:description This module provides case, activity, attachment, and aggregation tools for Message Center -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides case, activity, attachment, and aggregation tools for Message Center

## API Scopes

- `message-center:read`
- `message-center:write`

## Tools

### `falcon_aggregate_message_center_cases`

**Required scopes:** `message-center:read`

### `falcon_get_message_center_case_activities`

**Required scopes:** `message-center:read`

### `falcon_add_message_center_case_activity`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `message-center:write`

### `falcon_download_message_center_case_attachment`

**Required scopes:** `message-center:read`

### `falcon_add_message_center_case_attachment`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `message-center:write`

### `falcon_create_message_center_case`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `message-center:write`

### `falcon_get_message_center_cases`

**Required scopes:** `message-center:read`

### `falcon_query_message_center_case_activity_ids`

**Required scopes:** `message-center:read`

### `falcon_query_message_center_case_ids`

**Required scopes:** `message-center:read`

## Resources

- **`falcon://message-center/usage-guide`**: Usage guidance for Message Center workflows.
- **`falcon://message-center/safety-guide`**: Safety guidance for Message Center write tools.
