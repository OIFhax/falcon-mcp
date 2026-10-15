<!-- meta:title Sensor Visibility Exclusions -->
<!-- meta:description Searching, retrieving, creating, updating, and deleting Falcon Sensor Visibility exclusions -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching, retrieving, creating, updating, and deleting Falcon Sensor Visibility exclusions

## API Scopes

- `sensor-visibility-exclusions:read`
- `sensor-visibility-exclusions:write`

## Tools

### `falcon_search_sensor_visibility_exclusions`

**Required scopes:** `sensor-visibility-exclusions:read`

Search sensor visibility exclusions and return full exclusion details.

### `falcon_query_sensor_visibility_exclusion_ids`

**Required scopes:** `sensor-visibility-exclusions:read`

Query sensor visibility exclusion IDs.

### `falcon_get_sensor_visibility_exclusion_details`

**Required scopes:** `sensor-visibility-exclusions:read`

Get sensor visibility exclusion details by ID.

### `falcon_create_sensor_visibility_exclusions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `sensor-visibility-exclusions:write`

Create a sensor visibility exclusion.

### `falcon_update_sensor_visibility_exclusions`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `sensor-visibility-exclusions:write`

Update a sensor visibility exclusion.

### `falcon_delete_sensor_visibility_exclusions`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `sensor-visibility-exclusions:write`

Delete sensor visibility exclusions by ID.

## Resources

- **`falcon://sensor-visibility-exclusions/search/fql-guide`**: Contains FQL guidance for sensor visibility exclusions search tools.
- **`falcon://sensor-visibility-exclusions/safety-guide`**: Safety and operational guidance for sensor visibility exclusion write tools.
