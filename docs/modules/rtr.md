<!-- meta:title Real Time Response (RTR) -->
<!-- meta:description Searching RTR sessions, running RTR / RTR Admin commands, and querying RTR audit sessions -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching RTR sessions, running RTR / RTR Admin commands, and querying RTR audit sessions

> [!NOTE]
> This module is not available on CrowdStrike's hosted Falcon MCP; it is only available when self-hosting this server. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

## API Scopes

- `Real Time Response Audit:read`
- `Real Time Response:read`
- `Real Time Response Admin:write`

## Tools

### `falcon_search_rtr_sessions`

**Required scopes:** `Real Time Response:read`

Search RTR sessions and return full session details.

**Example prompts:**

- "Find all active RTR sessions"
- "Show me RTR sessions for host abc123"

### `falcon_init_rtr_session`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Initialize an RTR session on a single host.

**Example prompts:**

- "Start an RTR session on host xyz"

### `falcon_execute_rtr_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Execute an RTR read-only command on a single host.

### `falcon_check_rtr_command_status`

**Required scopes:** `Real Time Response:read`

Check status for an RTR command execution request.

**Example prompts:**

- "Check the status of RTR command request abc123"

### `falcon_search_rtr_admin_scripts`

**Required scopes:** `Real Time Response Admin:write`

Search RTR admin scripts and return full script details.

### `falcon_search_rtr_admin_put_files`

**Required scopes:** `Real Time Response Admin:write`

Search RTR admin put-files and return full put-file details.

### `falcon_execute_rtr_admin_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response Admin:write`

Execute an RTR admin command on a single host.

### `falcon_execute_rtr_admin_batch_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response Admin:write`

Execute an RTR admin command in batch mode.

### `falcon_check_rtr_admin_command_status`

**Required scopes:** `Real Time Response Admin:write`

Check status for an RTR admin command request.

### `falcon_delete_rtr_session`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Real Time Response:read`

Delete an RTR session by session ID.

**Example prompts:**

- "End the RTR session abc123"

### `falcon_delete_rtr_queued_session`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Real Time Response:read`

Delete a queued RTR session by session and request IDs.

### `falcon_search_rtr_audit_sessions`

**Required scopes:** `Real Time Response Audit:read`

Search RTR audit sessions.

**Example prompts:**

- "Show me RTR audit activity from the last 7 days"
- "Who used RTR against host BRR-WB-LIB-22?"

### `falcon_aggregate_rtr_sessions`

**Required scopes:** `Real Time Response:read`

Run aggregate analysis over RTR session data.

**Example prompts:**

- "Summarize RTR sessions by command for the last 30 days"
- "Which hosts have the most RTR activity this week?"

### `falcon_search_rtr_queued_sessions`

**Required scopes:** `Real Time Response:read`

Retrieve queued-session metadata by session IDs.

### `falcon_pulse_rtr_session`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Refresh a session timeout on a single host.

**Example prompts:**

- "Refresh the RTR session to keep it alive"

### `falcon_execute_rtr_active_responder_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Execute an active-responder command on a single host.

### `falcon_check_rtr_active_responder_command_status`

**Required scopes:** `Real Time Response:read`

Check status for an active-responder command request.

### `falcon_batch_init_rtr_sessions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Initialize RTR sessions in batch mode.

### `falcon_batch_refresh_rtr_sessions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Refresh RTR batch session heartbeats.

### `falcon_execute_rtr_batch_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Execute a read-only RTR command in batch mode.

### `falcon_execute_rtr_batch_active_responder_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Execute an active-responder RTR command in batch mode.

### `falcon_execute_rtr_batch_get_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Execute batch `get` file retrieval command.

### `falcon_check_rtr_batch_get_command_status`

**Required scopes:** `Real Time Response:read`

Check status for a batch get command request.

### `falcon_get_rtr_extracted_file_contents`

**Required scopes:** `Real Time Response:read`

Retrieve extracted file contents for a session SHA256 artifact.

### `falcon_list_rtr_files_v1`

**Required scopes:** `Real Time Response:read`

List session files using RTR_ListFiles (v1).

### `falcon_list_rtr_files_v2`

**Required scopes:** `Real Time Response:read`

List session files using RTR_ListFilesV2.

### `falcon_delete_rtr_file_v1`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Real Time Response:read`

Delete an RTR session file using RTR_DeleteFile (v1).

### `falcon_delete_rtr_file_v2`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Real Time Response:read`

Delete an RTR session file using RTR_DeleteFileV2.

### `falcon_search_rtr_falcon_scripts`

**Required scopes:** `Real Time Response Admin:write`

Search Falcon-provided RTR scripts and return full script details.

### `falcon_get_rtr_falcon_script_details`

**Required scopes:** `Real Time Response Admin:write`

Retrieve Falcon RTR scripts by ID.

### `falcon_get_rtr_put_file_contents`

**Required scopes:** `Real Time Response Admin:write`

Retrieve RTR put-file content payload for a file ID.

### `falcon_get_rtr_admin_put_file_details_v2`

**Required scopes:** `Real Time Response Admin:write`

Retrieve RTR put-file metadata using v2 endpoint.

### `falcon_create_rtr_admin_put_file_v1`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response Admin:write`

Create RTR put-file using v1 endpoint.

### `falcon_create_rtr_admin_put_file_v2`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response Admin:write`

Create RTR put-file using v2 endpoint.

### `falcon_delete_rtr_admin_put_file`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Real Time Response Admin:write`

Delete RTR put-file by ID.

### `falcon_get_rtr_admin_script_details_v2`

**Required scopes:** `Real Time Response Admin:write`

Retrieve RTR script metadata using v2 endpoint.

### `falcon_create_rtr_admin_script_v1`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response Admin:write`

Create an RTR custom script using v1 endpoint.

### `falcon_create_rtr_admin_script_v2`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response Admin:write`

Create an RTR custom script using v2 endpoint.

### `falcon_update_rtr_admin_script_v1`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response Admin:write`

Update an RTR custom script using v1 endpoint.

### `falcon_update_rtr_admin_script_v2`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response Admin:write`

Update an RTR custom script using v2 endpoint.

### `falcon_delete_rtr_admin_script`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Real Time Response Admin:write`

Delete an RTR custom script by ID.

### `falcon_get_rtr_session_details`

**Required scopes:** `Real Time Response:read`

Retrieve detailed metadata for one or more RTR sessions.

Use when you already have session IDs from search results. For discovering
sessions by criteria, use falcon_search_rtr_sessions instead. Returns full
session records.

**Example prompts:**

- "Get details for RTR session abc123"

### `falcon_execute_rtr_read_only_command`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Execute a read-only Real Time Response (RTR) command on a single host.

Limited to read-only commands (ls, ps, cat, filehash, reg) for hunt and triage
workflows. Does not expose admin or remediation commands. Returns command records
containing a cloud_request_id for polling output via falcon_check_rtr_command_status.

**Example prompts:**

- "Run 'ps' on this host via RTR"
- "List running processes on host xyz"

### `falcon_run_rtr_read_only_command_and_wait`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Real Time Response:read`

Execute a read-only RTR command and poll until completion.

Use this for simple, focused RTR evidence collection when the user
wants the command output directly and does not need to manually manage
a cloud request ID. This polls command status until completion or
timeout, accumulating output chunks into one result. It still executes
an RTR command and creates RTR command activity, but it does not expose
RTR Admin or remediation APIs.

**Example prompts:**

- "Run 'ps' via RTR and return the output when it completes"
- "Check C:\Windows\win.ini on this RTR session and wait for the result"

### `falcon_list_rtr_session_files`

**Required scopes:** `Real Time Response:read`

List files extracted during an RTR session.

Returns file metadata for artifacts captured during the session, such as
files pulled with the `get` command.

**Example prompts:**

- "List files extracted during RTR session abc123"

## Resources

- **`falcon://rtr/sessions/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_rtr_sessions` tool.
- **`falcon://rtr/admin/fql-guide`**: Contains the guide for the `filter` parameter of RTR admin search tools.
- **`falcon://rtr/audit/sessions/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_rtr_audit_sessions` tool.
- **`falcon://rtr/sessions/aggregate-guide`**: Explains how to summarize RTR session activity.
- **`falcon://rtr/workflows/investigation-guide`**: Provides a safe read-only RTR endpoint investigation workflow.
