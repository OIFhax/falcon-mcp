<!-- meta:title Firewall Management -->
<!-- meta:description This module provides full Falcon Firewall Management service collection coverage: query/get/aggregate operations for rules, rule groups, policy rules, events, fields, platforms, policy containers, and network locations, plus write lifecycle operations -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Firewall Management service collection coverage: query/get/aggregate operations for rules, rule groups, policy rules, events, fields, platforms, policy containers, and network locations, plus write lifecycle operations

## API Scopes

- `Firewall Management:read`
- `Firewall Management:write`

## Tools

### `falcon_search_firewall_rules`

**Required scopes:** `Firewall Management:read`

Search firewall rules and return full details.

**Example prompts:**

- "Show me all enabled Windows firewall rules"
- "Find firewall rules matching 'outbound'"

### `falcon_search_firewall_rule_groups`

**Required scopes:** `Firewall Management:read`

Search firewall rule groups and return full details.

**Example prompts:**

- "Find all enabled firewall rule groups for Windows"

### `falcon_search_firewall_policy_rules`

**Required scopes:** `Firewall Management:read`

Search rules within a specific policy container and return full details.

**Example prompts:**

- "Show me all rules in firewall policy abc123"

### `falcon_query_firewall_rule_ids`

**Required scopes:** `Firewall Management:read`

Query firewall rule IDs.

### `falcon_query_firewall_rule_group_ids`

**Required scopes:** `Firewall Management:read`

Query firewall rule-group IDs.

### `falcon_query_firewall_policy_rule_ids`

**Required scopes:** `Firewall Management:read`

Query firewall policy-rule IDs.

### `falcon_get_firewall_rules`

**Required scopes:** `Firewall Management:read`

Get firewall rules by ID.

### `falcon_get_firewall_rule_groups`

**Required scopes:** `Firewall Management:read`

Get firewall rule groups by ID.

### `falcon_aggregate_firewall_rules`

**Required scopes:** `Firewall Management:read`

Run aggregate query against firewall rules.

### `falcon_aggregate_firewall_rule_groups`

**Required scopes:** `Firewall Management:read`

Run aggregate query against firewall rule groups.

### `falcon_aggregate_firewall_policy_rules`

**Required scopes:** `Firewall Management:read`

Run aggregate query against firewall policy rules.

### `falcon_aggregate_firewall_events`

**Required scopes:** `Firewall Management:read`

Run aggregate query against firewall events.

### `falcon_query_firewall_event_ids`

**Required scopes:** `Firewall Management:read`

Query firewall event IDs.

### `falcon_get_firewall_events`

**Required scopes:** `Firewall Management:read`

Get firewall events by ID.

### `falcon_query_firewall_field_ids`

**Required scopes:** `Firewall Management:read`

Query firewall field IDs.

### `falcon_get_firewall_fields`

**Required scopes:** `Firewall Management:read`

Get firewall fields by ID.

### `falcon_query_firewall_platform_ids`

**Required scopes:** `Firewall Management:read`

Query firewall platform IDs.

### `falcon_get_firewall_platforms`

**Required scopes:** `Firewall Management:read`

Get firewall platforms by ID.

### `falcon_get_firewall_policy_containers`

**Required scopes:** `Firewall Management:read`

Get firewall policy containers by ID.

### `falcon_create_firewall_rule_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Create a firewall rule group.

**Example prompts:**

- "Create a Windows firewall rule group named 'Prod Outbound'"

### `falcon_update_firewall_rule_group`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Update a firewall rule group.

### `falcon_delete_firewall_rule_groups`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Firewall Management:write`

Delete firewall rule groups.

**Example prompts:**

- "Delete firewall rule group abc123"

### `falcon_validate_firewall_rule_group_create`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Validate a create-rule-group payload.

### `falcon_validate_firewall_rule_group_update`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Validate an update-rule-group payload.

### `falcon_update_firewall_policy_container`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Update firewall policy container (v2).

### `falcon_update_firewall_policy_container_v1`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Update firewall policy container (v1).

### `falcon_query_firewall_network_location_ids`

**Required scopes:** `Firewall Management:read`

Query firewall network-location IDs.

### `falcon_get_firewall_network_locations`

**Required scopes:** `Firewall Management:read`

Get firewall network locations by ID.

### `falcon_get_firewall_network_location_details`

**Required scopes:** `Firewall Management:read`

Get detailed firewall network-location entities by ID.

### `falcon_create_firewall_network_locations`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Create firewall network locations.

### `falcon_upsert_firewall_network_locations`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Upsert firewall network locations.

### `falcon_update_firewall_network_locations`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Update firewall network locations.

### `falcon_update_firewall_network_locations_metadata`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Update firewall network-location metadata.

### `falcon_update_firewall_network_locations_precedence`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Firewall Management:write`

Update firewall network-location precedence.

### `falcon_delete_firewall_network_locations`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Firewall Management:write`

Delete firewall network locations.

### `falcon_validate_firewall_filepath_pattern`

**Required scopes:** `Firewall Management:read`

Validate firewall file path pattern syntax.

## Resources

- **`falcon://firewall/rules/fql-guide`**: FQL guidance for firewall rules, rule groups, and policy-rule query tools.
- **`falcon://firewall/events/fql-guide`**: FQL guidance for firewall events query tools.
- **`falcon://firewall/network-locations/fql-guide`**: FQL guidance for firewall network location query tools.
- **`falcon://firewall/safety-guide`**: Safety and operational guidance for firewall management write tools.
