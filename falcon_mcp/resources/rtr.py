"""
Contains Real Time Response (RTR) resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_RTR_SESSIONS_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "aid",
        "String",
        "Falcon agent ID for the host tied to the RTR session.",
    ),
    (
        "date_created",
        "Timestamp",
        "Session creation time.",
    ),
    (
        "date_deleted",
        "Timestamp",
        "Session deletion time, when present.",
    ),
    (
        "date_updated",
        "Timestamp",
        "Last session update time.",
    ),
    (
        "session_id",
        "String",
        "RTR session identifier.",
    ),
    (
        "user_id",
        "String",
        "User identifier that created the session. Supports `@me` in filters.",
    ),
]

SEARCH_RTR_SESSIONS_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("date_created", "Sort by session creation time"),
    ("date_updated", "Sort by last update time"),
    ("date_deleted", "Sort by deletion time"),
    ("session_id", "Sort by session ID"),
    ("user_id", "Sort by user ID"),
]

SEARCH_RTR_SESSIONS_FQL_DOCUMENTATION = f"""
# RTR Session Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_rtr_sessions`.

## Filter Fields

{generate_md_table(SEARCH_RTR_SESSIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_RTR_SESSIONS_FQL_SORT_FIELDS)}

## Examples

- Sessions created by the current user:
  - `filter="user_id:'@me'"`
- Sessions for a specific host:
  - `filter="aid:'1234567890abcdef1234567890abcdef'"`
- Most recent sessions first:
  - `sort="date_created.desc"`

## Notes

- Start with broad filters and narrow gradually.
- Validate filters in a test environment before production use.
"""

SEARCH_RTR_ADMIN_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "created_at",
        "Timestamp",
        "Entity creation time for scripts or put-files.",
    ),
    (
        "description",
        "String",
        "Description text for scripts or put-files.",
    ),
    (
        "id",
        "String",
        "Script or put-file identifier.",
    ),
    (
        "modified_at",
        "Timestamp",
        "Last modification timestamp.",
    ),
    (
        "name",
        "String",
        "Script or put-file name.",
    ),
    (
        "platform",
        "String",
        "Target platform for script entities.",
    ),
    (
        "user_id",
        "String",
        "Owner / creator user identifier.",
    ),
]

SEARCH_RTR_ADMIN_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("created_at", "Sort by creation time"),
    ("modified_at", "Sort by last modification time"),
    ("name", "Sort by name"),
    ("platform", "Sort by platform"),
    ("user_id", "Sort by user ID"),
]

SEARCH_RTR_ADMIN_FQL_DOCUMENTATION = f"""
# RTR Admin Search FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_rtr_admin_scripts`
- `falcon_search_rtr_admin_put_files`
- `falcon_search_rtr_falcon_scripts`

## Filter Fields

{generate_md_table(SEARCH_RTR_ADMIN_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_RTR_ADMIN_FQL_SORT_FIELDS)}

## Examples

- Scripts created by the current user:
  - `filter="user_id:'@me'"`
- Script names matching a prefix:
  - `filter="name:'triage*'"`
- Most recently created entities first:
  - `sort="created_at.desc"`

## Notes

- Field support can vary slightly between custom scripts, Falcon scripts, and put-files.
- Validate filters in a test environment before production use.
"""

SEARCH_RTR_AUDIT_SESSIONS_FQL_FILTERS = [
    (
        "Field",
        "Type",
        "Description",
    ),
    (
        "aid",
        "String",
        "Falcon agent ID associated with the audited session.",
    ),
    (
        "created_at",
        "Timestamp",
        "Session creation timestamp.",
    ),
    (
        "deleted_at",
        "Timestamp",
        "Session deletion timestamp when present.",
    ),
    (
        "session_id",
        "String",
        "Audited RTR session identifier.",
    ),
    (
        "updated_at",
        "Timestamp",
        "Last session update timestamp.",
    ),
    (
        "user_id",
        "String",
        "User identifier that created the audited session.",
    ),
]

SEARCH_RTR_AUDIT_SESSIONS_FQL_SORT_FIELDS = [
    (
        "Field",
        "Description",
    ),
    ("created_at", "Sort by session creation time"),
    ("updated_at", "Sort by session update time"),
    ("deleted_at", "Sort by session deletion time"),
]

SEARCH_RTR_AUDIT_SESSIONS_FQL_DOCUMENTATION = f"""
# RTR Audit Sessions FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_rtr_audit_sessions`.

## Filter Fields

{generate_md_table(SEARCH_RTR_AUDIT_SESSIONS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_RTR_AUDIT_SESSIONS_FQL_SORT_FIELDS)}

## Examples

- Audit sessions by the current user:
  - `filter="user_id:'@me'"`
- Newest audit sessions first:
  - `sort="created_at.desc"`

## Notes

- Set `with_command_info=true` in `falcon_search_rtr_audit_sessions` to include command details.
- Validate filters in a test environment before production use.
"""

EMBEDDED_FQL_SYNTAX = """FQL filter string for querying RTR sessions.

SYNTAX:
- Equals: field:'value'
- Not equals: field:!'value'
- Comparison: field:>50, field:>=50, field:<50, field:<=50
- Contains (case-insensitive): field:~'partial'
- Wildcard: field:'prefix*', field:'*suffix'

COMBINING:
- AND (all must match): field1:'value1'+field2:'value2'
- OR (any can match): field:'value1',field:'value2'
- Grouping: (field1:'v1',field1:'v2')+field2:'v3'

COMMON FIELDS:
- aid: Host agent ID
- hostname: Host name
- user_id: API user who created the session ('@me' for current user)
- origin: Session origin label (e.g., 'falcon-mcp')
- created_at: Session creation timestamp (ISO 8601)
- updated_at: Last update timestamp (ISO 8601)
- base_command: RTR command name (e.g., 'ls', 'ps', 'cat')
- command_string: Full command line executed
- offline_queued: Whether session was queued offline (true/false)

EXAMPLES:
- Sessions for a host: hostname:'BRR-WB-LIB-22'
- Sessions by agent ID: aid:'2c5c4e7738004deaa9dfcdb86f633f3e'
- Current user sessions: user_id:'@me'
- Offline-queued sessions: offline_queued:true+hostname:'DC*'
"""

AUDIT_RTR_SESSIONS_EMBEDDED_FQL_SYNTAX = """FQL filter string for querying RTR audit sessions.

SYNTAX:
- Equals: field:'value'
- Not equals: field:!'value'
- Comparison: field:>'2025-01-01T00:00:00Z'
- Contains (case-insensitive): field:~'partial'
- Wildcard: field:'prefix*', field:'*suffix'

COMMON STARTING POINTS:
- Use created_at or updated_at filters to keep audit searches time-bound.
- Set with_command_info=true when you need command IDs and command log context.
- If a field is rejected by Falcon, reduce to a timestamp-bounded search and inspect returned fields.

EXAMPLES:
- Recent RTR audit sessions: created_at:>'now-7d'
- RTR audit sessions for a host pattern: hostname:'DC*'+created_at:>'now-7d'
- RTR audit sessions for current API user: user_id:'@me'+created_at:>'now-7d'
"""

# List of tuples containing filter options data: (name, type, description)

AGGREGATE_RTR_SESSIONS_GUIDE = """RTR Session Aggregation Guide

Use falcon_aggregate_rtr_sessions to summarize RTR session activity without pulling every
individual session record.

Recommended aggregation fields:
- hostname: Which hosts have the most RTR activity
- aid: Which host agent IDs have RTR activity
- user_id: Which Falcon users or API clients created sessions
- origin: Which integration or source created sessions
- base_command: Which RTR commands are most common
- created_at: Time-based activity buckets with aggregate_type=date_range

Recommended filters:
- created_at:>'now-7d'
- user_id:'@me'
- hostname:'DC*'
- offline_queued:true
- commands_queued:true

Example terms aggregation:
- aggregate_type: terms
- field: base_command
- filter: created_at:>'now-7d'
- size: 10

Example date range aggregation:
- aggregate_type: date_range
- field: created_at
- date_ranges: [{"from": "now-7d", "to": "now"}]

Use this before detailed searches when the user asks "how much", "which hosts", "which users",
or "what commands" across many RTR sessions.
"""

READ_ONLY_RTR_INVESTIGATION_GUIDE = """Read-only RTR Investigation Guide

This guide helps agents use RTR safely for endpoint triage. The current RTR MCP module exposes
the read-only RTR command endpoint for host investigation. It does not expose RTR Admin,
Active Responder, remediation, or arbitrary script execution.

Recommended sequence:
1. Use Falcon detections, cases, hosts, or NGSIEM to identify the host AID.
2. Use falcon_init_rtr_session to open or reuse a single-host RTR session.
3. Use falcon_run_rtr_read_only_command_and_wait for simple focused evidence collection.
4. Use falcon_execute_rtr_read_only_command plus falcon_check_rtr_command_status when you
   need manual control over request IDs, polling, or output sequence chunks.
5. Use falcon_search_rtr_audit_sessions when accountability or session history matters.
6. Use falcon_delete_rtr_session when the session is no longer needed.

Useful read-only command patterns:
- Processes: base_command=ps, command_string="ps"
- Directory listing: base_command=ls, command_string="ls C:\\Path"
- File hash: base_command=filehash, command_string="filehash C:\\Path\\file.exe"
- File preview: base_command=cat, command_string="cat C:\\Path\\file.txt"
- Registry query: base_command=reg, command_string="reg query HKLM\\Software\\..."
- Network state: base_command=netstat, command_string="netstat"
- Event log review: base_command=eventlog, command_string="eventlog view Security 50"

Model behavior guidance:
- Prefer one host and one question at a time.
- Keep commands narrow and explain what evidence each command is collecting.
- Use audit and aggregation tools before broad RTR activity conclusions.
- Treat offline or queued behavior as a telemetry state, not proof the host is powered off.
- Do not attempt remediation, deletion, script execution, or active-response behavior through
  the read-only RTR tool.
"""
