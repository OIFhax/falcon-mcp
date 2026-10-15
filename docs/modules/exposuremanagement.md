<!-- meta:title Exposure Management -->
<!-- meta:description Searching external assets and performing controlled inventory / triage updates via Falcon Exposure Management APIs -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Searching external assets and performing controlled inventory / triage updates via Falcon Exposure Management APIs

## API Scopes

- `Exposure Management:read`
- `Exposure Management:write`

## Tools

### `falcon_search_exposure_assets`

**Required scopes:** `Exposure Management:read`

Search external assets and return full detail records.

### `falcon_get_exposure_asset_details`

**Required scopes:** `Exposure Management:read`

Retrieve full external asset details by ID.

### `falcon_aggregate_exposure_assets`

**Required scopes:** `Exposure Management:read`

Run an aggregate query over external assets.

### `falcon_add_exposure_assets`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Exposure Management:write`

Add external assets to exposure inventory scanning.

### `falcon_update_exposure_assets`

> [!NOTE]
> This tool modifies data.

**Required scopes:** `Exposure Management:write`

Update external asset criticality/triage details.

### `falcon_remove_exposure_assets`

> [!CAUTION]
> This tool performs destructive operations.

**Required scopes:** `Exposure Management:write`

Delete one or more external assets.

## Resources

- **`falcon://exposure-management/assets/fql-guide`**: Contains the guide for the `filter` parameter of the `falcon_search_exposure_assets` tool.
- **`falcon://exposure-management/safety-guide`**: Safety and operational guidance for Exposure Management write tools.
