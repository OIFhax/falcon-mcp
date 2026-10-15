<!-- meta:title Deployments -->
<!-- meta:description Falcon release and release-note lookups -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Falcon release and release-note lookups

## API Scopes

- `deployment-coordinator:read`
- `deployments:read`

## Tools

### `falcon_search_deployment_releases`

**Required scopes:** `deployment-coordinator:read`

Search deployment releases and return combined details.

### `falcon_get_deployment_details`

**Required scopes:** `deployment-coordinator:read`

Retrieve deployment details by release ID.

### `falcon_search_release_notes`

**Required scopes:** `deployment-coordinator:read`

Search release notes and return combined details.

### `falcon_query_release_note_ids`

**Required scopes:** `deployment-coordinator:read`

Query release-note IDs.

### `falcon_get_release_notes_v1`

**Required scopes:** `deployment-coordinator:read`

Retrieve release notes using the v1 detail operation.

### `falcon_get_release_notes_v2`

**Required scopes:** `deployments:read`

Retrieve release notes using the v2 detail operation.

## Resources

- **`falcon://deployments/fql-guide`**: FQL guidance for Falcon Deployments tools.
