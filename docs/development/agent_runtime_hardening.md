# Agent Runtime Hardening Guide

This document explains the AI-agent guardrails, observability, and recovery behaviors added to `falcon-mcp` to improve safe autonomous use.

## Goals

The hardening work focused on these outcomes:

- Use only declared `falcon_*` tools
- Require session-start validation
- Preserve raw Falcon tool I/O for troubleshooting
- Keep search/query claims grounded in tool results
- Block improvised NGSIEM query construction
- Classify common error modes consistently
- Retry transient Falcon backend failures for sensitive RTR flows
- Generate support bundles for vendor escalation
- Provide low-confidence read-only fallback data when RTR init fails

## Server Contract

The MCP server now publishes an explicit operating contract in `falcon_mcp/server.py`.

Agent clients are expected to:

1. Call `falcon_startup_check` at session start
2. Use only declared `falcon_*` tools returned by the server
3. Read module FQL/CQL resources before building filters
4. Avoid improvised NGSIEM natural-language queries
5. Ground final statements in returned tool results

This contract is exposed through the FastMCP `instructions` field. It is guidance for agent behavior, not a protocol-level block on final prose.

## New Core Tools

### `falcon_startup_check`

Recommended first call for every AI-agent session.

Returns:

- current timestamp
- connectivity status
- configured base URL
- derived region hint
- enabled modules
- available modules
- declared tools

Use this to confirm what the current server instance can actually do before making tool-selection decisions.

### `falcon_get_tool_io_history`

Returns recent preserved Falcon API call history captured during MCP tool execution.

Useful for:

- checking what tool actually ran
- confirming parameter shapes
- reviewing raw Falcon responses
- inspecting error objects before retrying or summarizing

### `falcon_generate_support_bundle`

Builds a support-oriented bundle from recent tool I/O.

The bundle includes:

- region
- timestamps
- MCP tool / Falcon function pairs
- trace IDs
- target device IDs
- raw preserved entries

Use this when troubleshooting with CrowdStrike support or when an AI workflow needs a compact failure package.

## Tool I/O Preservation Model

Falcon API calls made through MCP tools are now recorded with tool context in `falcon_mcp/client.py`.

Each history entry includes:

- `tool_name`
- `tool_parameters`
- `falcon_operation`
- `parameters`
- `timestamp`
- `attempt`
- `status_code`
- `raw_response`
- `error_object`
- `trace_ids`
- `target_device_ids`

Important notes:

- History is currently in-memory only
- The buffer uses a ring buffer with a maximum of 200 entries
- Binary content is converted to safe string form for storage
- Trace IDs and target device IDs are extracted heuristically from request/response payloads

## Error Classification

Shared error handling now returns `error_type` to help agents reason about failures consistently.

Current classifications:

- `validation_error`
- `malformed_query`
- `empty_result`
- `falcon_backend_4xx`
- `falcon_backend_5xx`

Implementation details:

- Shared API errors are classified in `falcon_mcp/common/errors.py`
- FQL helper flows label query problems as `malformed_query`
- Empty filtered searches can return `empty_result`

This reduces ambiguity when an agent decides whether to retry, refine a filter, stop, or escalate.

## NGSIEM Guardrails

NGSIEM tools now enforce a guide-first model for search execution.

Behavior:

- `falcon_search_ngsiem` and `falcon_start_ngsiem_search` reject improvised natural-language query strings
- callers are redirected to `falcon://ngsiem/search-guide`
- only explicit CQL-style query strings are allowed through

This does not teach CQL. It prevents the agent from guessing at CQL syntax and sending malformed search bodies to Falcon.

## RTR Resilience

RTR initialization and refresh paths now include transient retry handling in `falcon_mcp/client.py`.

Retry behavior:

- default retries: `1`
- default initial backoff: `0.5` seconds
- default RTR transport timeout: `15` seconds
- environment overrides:
  - `FALCON_MCP_RETRY_ATTEMPTS`
  - `FALCON_MCP_RETRY_BACKOFF_SECONDS`
  - `FALCON_MCP_RTR_HTTP_TIMEOUT_SECONDS`
  - `FALCON_MCP_HTTP_TIMEOUT_SECONDS`

Current retry allowlist:

- `RTR_InitSession`
- `BatchInitSessions`
- `BatchRefreshSessions`
- `RTR_PulseSession`

Retries apply only to transient Falcon backend `5xx` responses and Falcon transport timeouts
that are normalized to HTTP `504`.

## RTR Post-Failure Fallback

If RTR session initialization still fails with a backend `5xx`, the tool now attaches a low-confidence fallback payload.

Fallback behavior:

- queries existing RTR session metadata using read-only search calls
- targets the requested device IDs
- returns `confidence: "low"`
- clearly marks the fallback as read-only and non-confirmatory

This fallback does **not** prove that a new RTR session was created. It only provides nearby validated data that can help the agent continue safely or explain the failure.

## Recommended Agent Workflow

For autonomous agents, use this sequence:

1. Run `falcon_startup_check`
2. Confirm the required module is enabled
3. Read the relevant FQL/CQL guide resource
4. Execute only declared `falcon_*` tools
5. If a call fails, inspect `falcon_get_tool_io_history`
6. Generate `falcon_generate_support_bundle` for escalation when needed
7. Make final claims only from returned tool results

## File Map

Primary implementation locations:

- `falcon_mcp/server.py`
- `falcon_mcp/client.py`
- `falcon_mcp/common/errors.py`
- `falcon_mcp/modules/base.py`
- `falcon_mcp/modules/ngsiem.py`
- `falcon_mcp/modules/rtr.py`

Primary validation locations:

- `tests/test_server.py`
- `tests/test_client.py`
- `tests/common/test_errors.py`
- `tests/modules/test_ngsiem.py`
- `tests/modules/test_rtr.py`

## Current Limits

These items are partially addressed but not fully protocol-enforced:

- “Use only declared tools” is enforced through server instructions and startup discovery, not an external agent sandbox
- “No final statement unless linked to a tool result” is an agent-contract requirement, not a server-side proof system
- support bundles are currently ephemeral and tied to the running process

## Future Extensions

Good next steps if we want to extend this model:

- persistent audit storage for tool I/O history
- stronger unsupported-tool / module-not-enabled response shaping before tool selection
- module-specific fallback strategies beyond RTR
- richer confidence scoring for fallback data
