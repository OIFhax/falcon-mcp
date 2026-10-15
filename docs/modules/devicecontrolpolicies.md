<!-- meta:title Device Control Policies -->
<!-- meta:description This module provides full Falcon Device Control Policies service collection coverage, including policy lifecycle operations, default/class configuration operations, policy actions, precedence updates, and member/policy searches -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full Falcon Device Control Policies service collection coverage, including policy lifecycle operations, default/class configuration operations, policy actions, precedence updates, and member/policy searches

## API Scopes

- `Device Control Policies:read`
- `Device Control Policies:write`

## Tools

### `falcon_search_device_control_policy_members`

**Required scopes:** `Device Control Policies:read`

Search members of a device control policy and return combined details.

### `falcon_search_device_control_policies`

**Required scopes:** `Device Control Policies:read`

Search device control policies and return combined details.

### `falcon_get_default_device_control_policies`

**Required scopes:** `Device Control Policies:read`

Get default device control policies.

### `falcon_update_default_device_control_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Device Control Policies:write`

Update default device control policies.

### `falcon_perform_device_control_policies_action`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Device Control Policies:write`

Perform an action against device control policies.

### `falcon_update_device_control_policies_classes`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Device Control Policies:write`

Patch device control policy classes.

### `falcon_get_default_device_control_settings`

**Required scopes:** `Device Control Policies:read`

Get default device control settings.

### `falcon_update_default_device_control_settings`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Device Control Policies:write`

Update default device control settings.

### `falcon_set_device_control_policies_precedence`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Device Control Policies:write`

Set device control policy precedence order.

### `falcon_get_device_control_policy_details`

**Required scopes:** `Device Control Policies:read`

Get device control policy details by ID (v1 endpoint).

### `falcon_create_device_control_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Device Control Policies:write`

Create device control policies (v1 endpoint).

### `falcon_update_device_control_policies`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Device Control Policies:write`

Update device control policies (v1 endpoint).

### `falcon_delete_device_control_policies`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Device Control Policies:write`

Delete device control policies by ID.

### `falcon_get_device_control_policy_details_v2`

**Required scopes:** `Device Control Policies:read`

Get device control policy details by ID (v2 endpoint).

### `falcon_create_device_control_policies_v2`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Device Control Policies:write`

Create device control policies (v2 endpoint).

### `falcon_update_device_control_policies_v2`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Device Control Policies:write`

Update device control policies (v2 endpoint).

### `falcon_query_device_control_policy_member_ids`

**Required scopes:** `Device Control Policies:read`

Query device control policy member IDs.

### `falcon_query_device_control_policy_ids`

**Required scopes:** `Device Control Policies:read`

Query device control policy IDs.

## Resources

- **`falcon://device-control-policies/policies/fql-guide`**: Contains FQL guidance for device control policy search tools.
- **`falcon://device-control-policies/members/fql-guide`**: Contains FQL guidance for device control policy member search tools.
- **`falcon://device-control-policies/defaults/guide`**: Guidance for default and class-level device control operations.
- **`falcon://device-control-policies/safety-guide`**: Safety and operational guidance for device control policy write tools.
