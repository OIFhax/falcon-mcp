<!-- meta:title Scheduled Reports -->
<!-- meta:description This module provides full Scheduled Reports and Report Executions coverage: query/get/launch operations for scheduled report entities, query/get/retry/download operations for report executions, and search convenience tools -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Scheduled Reports and Report Executions coverage: query/get/launch operations for scheduled report entities, query/get/retry/download operations for report executions, and search convenience tools

## API Scopes

- `Scheduled Reports:read`

## Tools

### `falcon_search_scheduled_reports`

**Required scopes:** `Scheduled Reports:read`

Search scheduled reports and return full details.

**Example prompts:**

- "Show me all active scheduled reports"

### `falcon_query_scheduled_report_ids`

**Required scopes:** `Scheduled Reports:read`

Query scheduled report IDs.

### `falcon_get_scheduled_report_details`

**Required scopes:** `Scheduled Reports:read`

Get scheduled report detail records by ID.

### `falcon_launch_scheduled_report`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Scheduled Reports:read`

Launch a scheduled report/search on demand.

**Example prompts:**

- "Run scheduled report abc123 now"

### `falcon_search_report_executions`

**Required scopes:** `Scheduled Reports:read`

Search report executions and return full details.

**Example prompts:**

- "Show me completed executions for report abc123"

### `falcon_query_report_execution_ids`

**Required scopes:** `Scheduled Reports:read`

Query report execution IDs.

### `falcon_get_report_execution_details`

**Required scopes:** `Scheduled Reports:read`

Get report execution detail records by ID.

### `falcon_retry_report_execution`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Scheduled Reports:read`

Retry a failed/eligible report execution.

### `falcon_download_report_execution`

**Required scopes:** `Scheduled Reports:read`

Download generated report results.

**Example prompts:**

- "Download the results for report execution abc123"

## Resources

- **`falcon://scheduled-reports/search/fql-guide`**: Contains the guide for the `filter` parameter of scheduled report query/search tools.
- **`falcon://scheduled-reports/executions/search/fql-guide`**: Contains the guide for the `filter` parameter of report execution query/search tools.
