<!-- meta:title Event Streams -->
<!-- meta:description Discovering available event streams and refreshing active stream sessions -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Discovering available event streams and refreshing active stream sessions

## API Scopes

- `event-streams:read`

## Tools

### `falcon_list_event_streams`

**Required scopes:** `event-streams:read`

Discover available event streams for a specific consumer label.

### `falcon_refresh_event_stream_session`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `event-streams:read`

Refresh an already-active event stream session for a partition.

## Resources

- **`falcon://event-streams/usage-guide`**: Usage guidance for Event Streams discovery and refresh tools.
