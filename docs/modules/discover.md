<!-- meta:title Discover -->
<!-- meta:description This module provides full read coverage for Falcon Discover applications, hosts, accounts, IoT hosts, and login entities -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

This module provides full read coverage for Falcon Discover applications, hosts, accounts, IoT hosts, and login entities

## API Scopes

- `Assets:read`

## Tools

### `falcon_search_applications`

**Required scopes:** `Assets:read`

Search applications using the combined applications endpoint.

Read `falcon://discover/applications/fql-guide` before composing the filter.

**Example prompts:**

- "Find all Chrome installations across my environment"

### `falcon_query_application_ids`

**Required scopes:** `Assets:read`

Query application IDs.

### `falcon_get_application_details`

**Required scopes:** `Assets:read`

Retrieve application details by ID.

### `falcon_search_hosts_combined`

**Required scopes:** `Assets:read`

Search host assets using the combined hosts endpoint.

### `falcon_query_host_ids`

**Required scopes:** `Assets:read`

Query host IDs.

### `falcon_get_discover_host_details`

**Required scopes:** `Assets:read`

Retrieve host asset details by ID.

### `falcon_search_discover_hosts`

**Required scopes:** `Assets:read`

Search hosts using query + get-by-ids workflow.

### `falcon_search_unmanaged_assets`

**Required scopes:** `Assets:read`

Search unmanaged assets using combined hosts with enforced unmanaged filter.

**Example prompts:**

- "Show me unmanaged Windows devices on the network"

### `falcon_query_account_ids`

**Required scopes:** `Assets:read`

Query account IDs.

### `falcon_get_account_details`

**Required scopes:** `Assets:read`

Retrieve account details by ID.

### `falcon_search_accounts`

**Required scopes:** `Assets:read`

Search accounts using query + get-by-ids workflow.

### `falcon_query_login_ids`

**Required scopes:** `Assets:read`

Query login IDs.

### `falcon_get_login_details`

**Required scopes:** `Assets:read`

Retrieve login details by ID.

### `falcon_search_logins`

**Required scopes:** `Assets:read`

Search logins using query + get-by-ids workflow.

### `falcon_query_iot_host_ids`

**Required scopes:** `Assets:read`

Query IoT host IDs using v1 endpoint.

### `falcon_query_iot_host_ids_v2`

**Required scopes:** `Assets:read`

Query IoT host IDs using v2 endpoint.

### `falcon_get_iot_host_details`

**Required scopes:** `Assets:read`

Retrieve IoT host details by ID.

### `falcon_search_iot_hosts`

**Required scopes:** `Assets:read`

Search IoT hosts using v2 query + get-by-ids workflow.

### `falcon_search_managed_assets`

> [!NOTE]
> Not available on CrowdStrike's hosted Falcon MCP. See [module overview](/falcon-mcp/modules/overview/#crowdstrike-hosted-mcp-differences).

**Required scopes:** `Assets:read`

Search hosts by asset and configuration posture: drive encryption status, encrypted/unencrypted drives, OS security settings (Secure Boot, Credential Guard, IOMMU), disk/memory/CPU usage, asset criticality, and internet exposure.

Use this when the question is about a device's storage, hardware, or security
configuration rather than its sensor state. For containment status, sensor version,
or policy assignment, use `falcon_search_hosts`. See
`falcon://discover/managed-assets/fql-guide` for filters; returns full asset details.
Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.

**Example prompts:**

- "Which managed Windows hosts are unencrypted?"
- "List critical assets that don't have Credential Guard enabled"

## Resources

- **`falcon://discover/applications/fql-guide`**: Contains the guide for the `filter` parameter of application search/query tools.
- **`falcon://discover/hosts/fql-guide`**: Contains the guide for the `filter` parameter of host and unmanaged asset search/query tools.
- **`falcon://discover/managed-assets/fql-guide`**: Contains the guide for the `filter` parameter of managed asset search tools.
