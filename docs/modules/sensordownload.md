<!-- meta:title Sensor Download -->
<!-- meta:description Listing sensor installers, retrieving installer metadata, obtaining CCID values, and downloading installer binaries -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Listing sensor installers, retrieving installer metadata, obtaining CCID values, and downloading installer binaries

## API Scopes

- `Sensor Download:read`

## Tools

### `falcon_search_sensor_installer_ids`

**Required scopes:** `Sensor Download:read`

Query sensor installer IDs using v1 API.

### `falcon_search_sensor_installer_ids_v2`

**Required scopes:** `Sensor Download:read`

Query sensor installer IDs using v2 API.

### `falcon_get_sensor_installer_details`

**Required scopes:** `Sensor Download:read`

Retrieve installer metadata by SHA256 IDs using v1 API.

### `falcon_get_sensor_installer_details_v2`

**Required scopes:** `Sensor Download:read`

Retrieve installer metadata by SHA256 IDs using v2 API.

### `falcon_search_sensor_installers_combined`

**Required scopes:** `Sensor Download:read`

Search combined sensor installer details using v1 API.

### `falcon_search_sensor_installers_combined_v2`

**Required scopes:** `Sensor Download:read`

Search combined sensor installer details using v2 API.

### `falcon_get_sensor_installer_ccid`

**Required scopes:** `Sensor Download:read`

Retrieve sensor installer CCID values for this tenant.

### `falcon_download_sensor_installer`

**Required scopes:** `Sensor Download:read`

Download a sensor installer by SHA256 ID using v1 endpoint.

### `falcon_download_sensor_installer_v2`

**Required scopes:** `Sensor Download:read`

Download a sensor installer by SHA256 ID using v2 endpoint.

## Resources

- **`falcon://sensor-download/installers/fql-guide`**: Contains the guide for the `filter` parameter of sensor installer search tools.
- **`falcon://sensor-download/installers/download-guide`**: Guidance for using installer download tools and inline binary behavior.
