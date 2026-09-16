<!-- meta:title Sensor Update Policies -->
<!-- meta:description This module provides full Falcon Sensor Update Policies service collection coverage, including v1/v2 policy lifecycle operations, build and kernel discovery, member searches, actions, precedence updates, and uninstall token reveal operations -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Sensor Update Policies service collection coverage, including v1/v2 policy lifecycle operations, build and kernel discovery, member searches, actions, precedence updates, and uninstall token reveal operations

## API Scopes

- `Sensor Update Policies:read`
- `Sensor Update Policies:write`

## Tools

### `falcon_reveal_sensor_uninstall_token`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Sensor Update Policies:write`

Reveal an uninstall token for a specific device.

### `falcon_search_sensor_update_builds`

**Required scopes:** `Sensor Update Policies:read`

Search available sensor update builds.

### `falcon_search_sensor_update_kernels`

**Required scopes:** `Sensor Update Policies:read`

Search sensor update kernel compatibility records.

### `falcon_search_sensor_update_policy_members`

**Required scopes:** `Sensor Update Policies:read`

Search members of a sensor update policy and return combined details.

### `falcon_search_sensor_update_policies`

**Required scopes:** `Sensor Update Policies:read`

Search sensor update policies (v1 combined endpoint).

### `falcon_search_sensor_update_policies_v2`

**Required scopes:** `Sensor Update Policies:read`

Search sensor update policies (v2 combined endpoint).

### `falcon_perform_sensor_update_policies_action`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Sensor Update Policies:write`

Perform an action against sensor update policies.

### `falcon_set_sensor_update_policies_precedence`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Sensor Update Policies:write`

Set sensor update policy precedence order.

### `falcon_get_sensor_update_policy_details`

**Required scopes:** `Sensor Update Policies:read`

Get sensor update policy details by ID (v1 endpoint).

### `falcon_create_sensor_update_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Sensor Update Policies:write`

Create sensor update policies (v1 endpoint).

### `falcon_update_sensor_update_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Sensor Update Policies:write`

Update sensor update policies (v1 endpoint).

### `falcon_delete_sensor_update_policies`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Sensor Update Policies:write`

Delete sensor update policies by ID.

### `falcon_get_sensor_update_policy_details_v2`

**Required scopes:** `Sensor Update Policies:read`

Get sensor update policy details by ID (v2 endpoint).

### `falcon_create_sensor_update_policies_v2`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Sensor Update Policies:write`

Create sensor update policies (v2 endpoint).

### `falcon_update_sensor_update_policies_v2`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Sensor Update Policies:write`

Update sensor update policies (v2 endpoint).

### `falcon_query_sensor_update_kernel_distinct`

**Required scopes:** `Sensor Update Policies:read`

Query distinct kernel compatibility values.

### `falcon_query_sensor_update_policy_member_ids`

**Required scopes:** `Sensor Update Policies:read`

Query sensor update policy member IDs.

### `falcon_query_sensor_update_policy_ids`

**Required scopes:** `Sensor Update Policies:read`

Query sensor update policy IDs.

## Resources

- **`falcon://sensor-update-policies/policies/fql-guide`**: Contains FQL guidance for sensor update policy search tools.
- **`falcon://sensor-update-policies/members/fql-guide`**: Contains FQL guidance for sensor update policy member search tools.
- **`falcon://sensor-update-policies/kernels/fql-guide`**: Contains FQL guidance for sensor update kernel search tools.
- **`falcon://sensor-update-policies/builds/guide`**: Guidance for available sensor update build queries.
- **`falcon://sensor-update-policies/safety-guide`**: Safety and operational guidance for sensor update policy write tools.
