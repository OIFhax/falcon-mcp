<!-- meta:title ThreatGraph -->
<!-- meta:description This module provides read-only tools for ThreatGraph vertices, edges, and indicator pivots -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides read-only tools for ThreatGraph vertices, edges, and indicator pivots

## API Scopes

- `threatgraph:read`

## Tools

### `falcon_get_threatgraph_edge_types`

**Required scopes:** `threatgraph:read`

List available ThreatGraph edge types.

### `falcon_get_threatgraph_edges`

**Required scopes:** `threatgraph:read`

Retrieve ThreatGraph edges for a vertex.

### `falcon_get_threatgraph_ran_on`

**Required scopes:** `threatgraph:read`

Retrieve indicator sightings via ThreatGraph.

### `falcon_get_threatgraph_summary`

**Required scopes:** `threatgraph:read`

Retrieve a ThreatGraph summary for vertex IDs.

### `falcon_get_threatgraph_vertices_v1`

**Required scopes:** `threatgraph:read`

Retrieve ThreatGraph vertex metadata using the v1 endpoint.

### `falcon_get_threatgraph_vertices_v2`

**Required scopes:** `threatgraph:read`

Retrieve ThreatGraph vertex metadata using the v2 endpoint.

## Resources

- **`falcon://threatgraph/usage-guide`**: Usage guidance for ThreatGraph pivot workflows.
