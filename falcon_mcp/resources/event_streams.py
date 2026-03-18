"""
Contains Event Streams resources.
"""

EVENT_STREAMS_USAGE_GUIDE = """# Event Streams Usage Guide

Use this guide with:

- `falcon_list_event_streams`
- `falcon_refresh_event_stream_session`

## app_id requirements

- Required for both tools.
- Must be 1 to 32 alphanumeric characters.
- Reuse the same `app_id` for the same stream consumer.

## list tool

`falcon_list_event_streams` discovers the available event stream partitions for an `app_id`.

Inputs:

- `app_id`: Consumer label for your connection.
- `format`: Stream payload format. Valid values: `json`, `flatjson`.

Expected response fields usually include:

- `dataFeedURL`
- `sessionToken`
- `refreshActiveSessionURL`
- `refreshActiveSessionInterval`

## refresh tool

`falcon_refresh_event_stream_session` refreshes an already-active stream session for a partition.

Inputs:

- `app_id`: Same consumer label used to establish the session.
- `partition`: Partition number to refresh. Default: `0`.

## Important behavior

- Listing streams does not guarantee there is an active session to refresh.
- Refresh can return `404 no active stream session found` when no consumer is currently connected.
- Use the returned `dataFeedURL` and `sessionToken` with your stream consumer outside MCP.
"""
