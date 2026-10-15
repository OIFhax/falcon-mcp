<!-- meta:title Downloads -->
<!-- meta:description Enumerating downloadable artifacts and requesting pre-signed download URLs -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Enumerating downloadable artifacts and requesting pre-signed download URLs

## API Scopes

- `infrastructure-as-code:read`

## Tools

### `falcon_enumerate_download_files`

**Required scopes:** `infrastructure-as-code:read`

Enumerate downloadable artifacts using the legacy enumerate endpoint.

### `falcon_fetch_download_file_info`

**Required scopes:** `infrastructure-as-code:read`

Fetch download file info and pre-signed URLs using v1 combined endpoint.

### `falcon_fetch_download_file_info_v2`

**Required scopes:** `infrastructure-as-code:read`

Fetch download file info and pre-signed URLs using v2 combined endpoint.

### `falcon_get_download_file_url`

**Required scopes:** `infrastructure-as-code:read`

Retrieve a pre-signed download URL using the legacy direct download endpoint.

## Resources

- **`falcon://downloads/files/fql-guide`**: FQL guidance for download file info query tools.
- **`falcon://downloads/files/usage-guide`**: Usage guidance for legacy enumerate/download tools.
