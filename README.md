![CrowdStrike Logo (Light)](https://raw.githubusercontent.com/CrowdStrike/.github/main/assets/cs-logo-light-mode.png#gh-light-mode-only)
![CrowdStrike Logo (Dark)](https://raw.githubusercontent.com/CrowdStrike/.github/main/assets/cs-logo-dark-mode.png#gh-dark-mode-only)

# falcon-mcp

[![PyPI version](https://badge.fury.io/py/falcon-mcp.svg)](https://badge.fury.io/py/falcon-mcp)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/falcon-mcp)](https://pypi.org/project/falcon-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**falcon-mcp** is a Model Context Protocol (MCP) server that connects AI agents with the CrowdStrike Falcon platform, powering intelligent security analysis in your agentic workflows. It delivers programmatic access to essential security capabilities—including detections, incidents, and behaviors—establishing the foundation for advanced security operations and automation.

> [!IMPORTANT]
> **🚧 Public Preview**: This project is currently in public preview and under active development. Features and functionality may change before the stable 1.0 release. While we encourage exploration and testing, please avoid production deployments. We welcome your feedback through [GitHub Issues](https://github.com/crowdstrike/falcon-mcp/issues) to help shape the final release.

## Table of Contents

- [API Credentials \& Required Scopes](#api-credentials--required-scopes)
  - [Setting Up CrowdStrike API Credentials](#setting-up-crowdstrike-api-credentials)
  - [Required API Scopes by Module](#required-api-scopes-by-module)
- [Available Modules, Tools \& Resources](#available-modules-tools--resources)
  - [Cloud Security Module](#cloud-security-module)
  - [CAO Hunting Module](#cao-hunting-module)
  - [API Integrations Module](#api-integrations-module)
  - [Certificate Based Exclusions Module](#certificate-based-exclusions-module)
  - [Core Functionality (Built into Server)](#core-functionality-built-into-server)
  - [Content Update Policies Module](#content-update-policies-module)
  - [Custom IOA Module](#custom-ioa-module)
  - [Detections Module](#detections-module)
  - [Delivery Settings Module](#delivery-settings-module)
  - [Deployments Module](#deployments-module)
  - [Device Content Module](#device-content-module)
  - [Discover Module](#discover-module)
  - [Downloads Module](#downloads-module)
  - [Drift Indicators Module](#drift-indicators-module)
  - [Exposure Management Module](#exposure-management-module)
  - [Event Streams Module](#event-streams-module)
  - [FDR Module](#fdr-module)
  - [Hosts Module](#hosts-module)
  - [Identity Protection Module](#identity-protection-module)
  - [User Management Module](#user-management-module)
  - [Incidents Module](#incidents-module)
  - [Installation Tokens Module](#installation-tokens-module)
  - [Prevention Policies Module](#prevention-policies-module)
  - [Response Policies Module](#response-policies-module)
  - [Device Control Policies Module](#device-control-policies-module)
  - [Firewall Policies Module](#firewall-policies-module)
  - [Sensor Update Policies Module](#sensor-update-policies-module)
  - [Workflows Module](#workflows-module)
  - [IT Automation Module](#it-automation-module)
  - [NGSIEM Module](#ngsiem-module)
  - [Intel Module](#intel-module)
  - [Intelligence Feeds Module](#intelligence-feeds-module)
  - [MalQuery Module](#malquery-module)
  - [ML Exclusions Module](#ml-exclusions-module)
  - [IOC Module](#ioc-module)
  - [IOA Exclusions Module](#ioa-exclusions-module)
  - [Sensor Visibility Exclusions Module](#sensor-visibility-exclusions-module)
  - [Firewall Management Module](#firewall-management-module)
  - [Quarantine Module](#quarantine-module)
  - [Quick Scan Module](#quick-scan-module)
  - [Real Time Response Module](#real-time-response-module)
  - [Scheduled Reports Module](#scheduled-reports-module)
  - [Sensor Download Module](#sensor-download-module)
  - [Sensor Usage Module](#sensor-usage-module)
  - [Serverless Module](#serverless-module)
  - [Spotlight Module](#spotlight-module)
  - [ThreatGraph Module](#threatgraph-module)
  - [Zero Trust Assessment Module](#zero-trust-assessment-module)
- [Installation \& Setup](#installation--setup)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Installation](#installation)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Module Configuration](#module-configuration)
  - [Additional Command Line Options](#additional-command-line-options)
  - [As a Library](#as-a-library)
  - [Running Examples](#running-examples)
- [Container Usage](#container-usage)
  - [Using Pre-built Image (Recommended)](#using-pre-built-image-recommended)
  - [Building Locally (Development)](#building-locally-development)
- [Editor/Assistant Integration](#editorassistant-integration)
  - [Using `uvx` (recommended)](#using-uvx-recommended)
  - [With Module Selection](#with-module-selection)
  - [Using Individual Environment Variables](#using-individual-environment-variables)
  - [Docker Version](#docker-version)
- [Additional Deployment Options](#additional-deployment-options)
  - [Amazon Bedrock AgentCore](#amazon-bedrock-agentcore)
  - [Google Cloud (Cloud Run and Vertex AI)](#google-cloud-cloud-run-and-vertex-ai)
- [Contributing](#contributing)
  - [Getting Started for Contributors](#getting-started-for-contributors)
  - [Running Tests](#running-tests)
  - [Developer Documentation](#developer-documentation)
- [License](#license)
- [Support](#support)

## API Credentials & Required Scopes

### Setting Up CrowdStrike API Credentials

Before using the Falcon MCP Server, you need to create API credentials in your CrowdStrike console:

1. **Log into your CrowdStrike console**
2. **Navigate to Support > API Clients and Keys**
3. **Click "Add new API client"**
4. **Configure your API client**:
   - **Client Name**: Choose a descriptive name (e.g., "Falcon MCP Server")
   - **Description**: Optional description for your records
   - **API Scopes**: Select the scopes based on which modules you plan to use (see below)

> **Important**: Ensure your API client has the necessary scopes for the modules you plan to use. You can always update scopes later in the CrowdStrike console.

### Required API Scopes by Module

The Falcon MCP Server supports different modules, each requiring specific API scopes:

| Module | Required API Scopes | Purpose |
| - | - | - |
| **CAO Hunting** | `CAO Hunting:read` | Search hunting guides and intelligence queries, run aggregations, and request archive exports |
| **API Integrations** | `api-integrations:read`<br>`api-integrations:write` | Search plugin configurations and execute API Integration commands with guarded write controls |
| **Certificate Based Exclusions** | `ml-exclusions:read`<br>`ml-exclusions:write` | Search and manage certificate based exclusions and retrieve file signing information |
| **Cloud Security** | `Falcon Container Image:read` | Search Kubernetes container inventory and run full container vulnerability analytics |
| **Core** | _No additional scopes_ | Basic connectivity and system information |
| **Content Update Policies** | `Content Update Policies:read`<br>`Content Update Policies:write` | Search and manage content update policies, policy members, actions, precedence, and pinnable content versions |
| **Custom IOA** | `Custom IOA Rules:read`<br>`Custom IOA Rules:write` | Create and manage Custom IOA behavioral detection rules and rule groups |
| **Detections** | `Alerts:read`<br>`Alerts:write` | Full detections coverage for query/search/details, aggregation, and controlled detection update actions |
| **Delivery Settings** | `delivery-settings:read`<br>`delivery-settings:write` | Inspect and update Falcon delivery settings with guarded write execution |
| **Deployments** | `deployment-coordinator:read`<br>`deployments:read` | Search releases and release notes and retrieve deployment details by ID |
| **Device Content** | `device-content:read` | Search and retrieve device content state records |
| **Discover** | `Assets:read` | Full Discover coverage for applications, hosts, accounts, IoT hosts, and login entities (query/get/combined workflows) |
| **Downloads** | `infrastructure-as-code:read` | Enumerate downloadable artifacts and request pre-signed download URLs |
| **Drift Indicators** | `drift-indicators:read` | Count, query, and retrieve drift indicator entities across cloud workloads |
| **Exposure Management** | `Exposure Management:read`<br>`Exposure Management:write` | Search external assets and perform controlled asset inventory/triage updates |
| **Event Streams** | `event-streams:read` | Discover available Falcon event streams and refresh active partition sessions for an existing consumer |
| **FDR** | `falcon-data-replicator:read` | Retrieve Falcon Data Replicator schema metadata for events and fields |
| **Hosts** | `Hosts:read`<br>`Host Groups:read`<br>`Host Groups:write`<br>`Host Migration:read`<br>`Host Migration:write` | Search hosts, manage host groups, and orchestrate migration workflows |
| **Identity Protection** | `Identity Protection Entities:read`<br>`Identity Protection Timeline:read`<br>`Identity Protection Detections:read`<br>`Identity Protection Assessment:read`<br>`Identity Protection GraphQL:write` | Comprehensive entity investigation and identity protection analysis |
| **User Management** | `User Management:read`<br>`User Management:write` | Full User Management coverage for aggregation, user/role discovery, grants, and controlled user/role actions |
| **Incidents** | `Incidents:read`<br>`Incidents:write` | Full incidents coverage for crowd score, incident/behavior query+details, and controlled incident action workflows |
| **Installation Tokens** | `Installation Tokens:read`<br>`Installation Tokens:write`<br>`Installation Tokens Settings:write` | Search and manage installation tokens, inspect audit events, and control tenant token settings |
| **Prevention Policies** | `Prevention Policies:read`<br>`Prevention Policies:write` | Search and manage prevention policies, policy members, policy actions, and precedence ordering |
| **Response Policies** | `Response Policies:read`<br>`Response Policies:write` | Search and manage response policies, policy members, policy actions, and precedence ordering |
| **Device Control Policies** | `Device Control Policies:read`<br>`Device Control Policies:write` | Search and manage device control policies, defaults, classes, precedence, actions, and policy member relationships |
| **Firewall Policies** | `Firewall Policies:read`<br>`Firewall Policies:write` | Search and manage firewall policies, policy actions, precedence, and policy member relationships |
| **Sensor Update Policies** | `Sensor Update Policies:read`<br>`Sensor Update Policies:write` | Search and manage sensor update policies, builds, kernels, precedence, actions, and uninstall token reveal workflows |
| **Workflows** | `Workflow:read`<br>`Workflow:write` | Search and manage workflow definitions, executions, human inputs, and system-definition lifecycle actions |
| **IT Automation** | `IT Automation:read`<br>`IT Automation:write` | Full IT Automation coverage for search/query/get, policy/task lifecycle management, and high-impact execution controls |
| **NGSIEM** | `NGSIEM:read`<br>`NGSIEM:write` | Full NGSIEM coverage for search jobs, dashboards, lookup files, parsers, and saved queries |
| **Intel** | `Actors (Falcon Intelligence):read`<br>`Indicators (Falcon Intelligence):read`<br>`Reports (Falcon Intelligence):read` | Research threat actors, IOCs, and intelligence reports |
| **Intelligence Feeds** | `indicator-graph:read` | List accessible feeds, query archive items, and request archive downloads |
| **MalQuery** | `malquery:read`<br>`malquery:write` | Run corpus searches and hunts, inspect request status and metadata, and retrieve MalQuery downloads |
| **ML Exclusions** | `ml-exclusions:read`<br>`ml-exclusions:write` | Search and manage machine learning exclusions with guarded write operations |
| **IOC** | `IOC Management:read`<br>`IOC Management:write` | Search, create, and remove custom IOCs using IOC Service Collection endpoints |
| **IOA Exclusions** | `IOA Exclusions:read`<br>`IOA Exclusions:write` | Search, create, update, and delete IOA exclusions |
| **Sensor Visibility Exclusions** | `sensor-visibility-exclusions:read`<br>`sensor-visibility-exclusions:write` | Search and manage sensor visibility exclusions with guarded write operations |
| **Firewall Management** | `Firewall Management:read`<br>`Firewall Management:write` | Full firewall management coverage for rules, rule groups, policy containers, events, fields, platforms, and network locations |
| **Quarantine** | `Quarantined Files:read`<br>`Quarantined Files:write` | Search and aggregate quarantined files, estimate update impact, and apply quarantine actions |
| **Quick Scan** | `quick-scan:read`<br>`quick-scan:write` | Search and aggregate scan submissions, retrieve scan details, and submit hashes for quick scanning |
| **Real Time Response** | `Real Time Response:read`<br>`Real Time Response Admin:write`<br>`Real Time Response Audit:read` | Unified RTR module covering session workflows, admin command/script operations, and audit session search |
| **Scheduled Reports** | `Scheduled Reports:read` | Get details about scheduled reports and searches, run reports on demand, and download report files |
| **Sensor Download** | `Sensor Download:read` | Query installer catalogs, retrieve metadata and CCID values, and download installer binaries |
| **Sensor Usage** | `Sensor Usage:read` | Access and analyze sensor usage data |
| **Serverless** | `Falcon Container Image:read` | Search for vulnerabilities in serverless functions across cloud service providers |
| **Spotlight** | `Vulnerabilities:read` | Manage and analyze vulnerability data and security assessments |
| **ThreatGraph** | `threatgraph:read` | Pivot across ThreatGraph vertices, edges, summaries, and indicator sightings |
| **Zero Trust Assessment** | `Zero Trust Assessment:read` | Search host Zero Trust scores and retrieve tenant-wide audit metrics |

## Available Modules, Tools & Resources

> [!IMPORTANT]
> ⚠️ **Important Note on FQL Guide Resources**: Several modules include FQL (Falcon Query Language) guide resources that provide comprehensive query documentation and examples. While these resources are designed to assist AI assistants and users with query construction, **FQL has nuanced syntax requirements and field-specific behaviors** that may not be immediately apparent. AI-generated FQL filters should be **tested and validated** before use in production environments. We recommend starting with simple queries and gradually building complexity while verifying results in a test environment first.

**About Tools & Resources**: This server provides both tools (actions you can perform) and resources (documentation and context). Tools execute operations like searching for detections or analyzing threats, while resources provide comprehensive documentation like FQL query guides that AI assistants can reference for context without requiring tool calls.

### Cloud Security Module

**API Scopes Required**:

- `Falcon Container Image:read`

Provides tools for CrowdStrike Cloud Security inventory and full Container Vulnerabilities coverage:

- Kubernetes container inventory:
  - `falcon_search_kubernetes_containers`
  - `falcon_count_kubernetes_containers`
- Vulnerability search and enrichment:
  - `falcon_search_images_vulnerabilities`
  - `falcon_get_image_vulnerability_details`
  - `falcon_get_image_vulnerability_info`
- Vulnerability aggregations and ranking views:
  - `falcon_count_image_vulnerabilities`
  - `falcon_count_image_vulnerabilities_by_severity`
  - `falcon_count_image_vulnerabilities_by_cps_rating`
  - `falcon_count_image_vulnerabilities_by_cvss_score`
  - `falcon_count_image_vulnerabilities_by_actively_exploited`
  - `falcon_get_top_vulnerabilities_by_image_count`
  - `falcon_get_recent_vulnerabilities_by_publication_date`

**Resources**:

- `falcon://cloud/kubernetes-containers/fql-guide`: Comprehensive FQL documentation and examples for kubernetes containers searches
- `falcon://cloud/images-vulnerabilities/fql-guide`: Comprehensive FQL documentation and examples for images vulnerabilities searches

**Use Cases**: Container inventory hygiene, image vulnerability triage, CVE enrichment, exploitability-focused risk analysis

### CAO Hunting Module

**API Scopes Required**:

- `CAO Hunting:read`

Provides read-only tools for CAO hunting workflows:

- `falcon_search_hunting_guides`: Search hunting guides and return full guide details
- `falcon_get_hunting_guide_details`: Retrieve hunting guide records by ID
- `falcon_search_intelligence_queries`: Search intelligence queries and return full query details
- `falcon_get_intelligence_query_details`: Retrieve intelligence query records by ID
- `falcon_aggregate_hunting_guides`: Run aggregate queries for hunting guides
- `falcon_aggregate_intelligence_queries`: Run aggregate queries for intelligence queries
- `falcon_create_hunting_archive_export`: Request archive exports by language and filter

**Resources**:

- `falcon://cao-hunting/guides/fql-guide`: FQL documentation and examples for hunting guide searches
- `falcon://cao-hunting/intelligence-queries/fql-guide`: FQL documentation and examples for intelligence query searches
- `falcon://cao-hunting/archive-export/guide`: Archive export parameter guidance

**Use Cases**: Threat-hunt content discovery, query analysis, language-specific export workflows, CAO content reporting

### API Integrations Module

**API Scopes Required**:

- `api-integrations:read`
- `api-integrations:write`

Provides Falcon API Integrations tools:

- `falcon_search_api_integration_plugin_configs`: Search plugin configuration records
- `falcon_execute_api_integration_command`: Execute a plugin command (requires `confirm_execution=true`)
- `falcon_execute_api_integration_command_proxy`: Execute a proxy-style plugin command (requires `confirm_execution=true`)

**Resources**:

- `falcon://api-integrations/plugin-configs/fql-guide`: FQL guidance for plugin configuration searches
- `falcon://api-integrations/safety-guide`: Operational guardrails for plugin execution tools

**Use Cases**: Plugin configuration discovery, controlled downstream command execution, and external integration orchestration

### Certificate Based Exclusions Module

**API Scopes Required**:

- `ml-exclusions:read`
- `ml-exclusions:write`

Provides tools for Falcon certificate based exclusion workflows:

- `falcon_search_certificate_based_exclusions`: Search certificate based exclusions and return full exclusion details
- `falcon_query_certificate_based_exclusion_ids`: Query certificate based exclusion IDs
- `falcon_get_certificate_based_exclusion_details`: Retrieve certificate based exclusion records by ID
- `falcon_get_certificate_signing_info`: Retrieve certificate signing information for a file SHA256
- `falcon_create_certificate_based_exclusions`: Create certificate based exclusions (requires `confirm_execution=true`)
- `falcon_update_certificate_based_exclusions`: Update certificate based exclusions (requires `confirm_execution=true`)
- `falcon_delete_certificate_based_exclusions`: Delete certificate based exclusions by ID (requires `confirm_execution=true`)

**Resources**:

- `falcon://certificate-based-exclusions/search/fql-guide`: FQL documentation for certificate based exclusion search tools
- `falcon://certificate-based-exclusions/certificates/guide`: Guidance for certificate signing lookups by SHA256
- `falcon://certificate-based-exclusions/safety-guide`: Operational guardrails for certificate based exclusion write operations

**Use Cases**: Signed software allowlisting, certificate-driven suppression workflows, certificate lookup for exclusion design, and guarded cleanup of obsolete certificate exclusions

### Core Functionality (Built into Server)

**API Scopes**: _None required beyond basic API access_

The server provides core tools for interacting with the Falcon API:

- `falcon_check_connectivity`: Check connectivity to the Falcon API
- `falcon_list_enabled_modules`: Lists enabled modules in the falcon-mcp server
    > These modules are determined by the `--modules` [flag](#module-configuration) when starting the server. If no modules are specified, all available modules are enabled.
- `falcon_list_modules`: Lists all available modules in the falcon-mcp server

### Content Update Policies Module

**API Scopes Required**:

- `Content Update Policies:read`
- `Content Update Policies:write`

Provides full Content Update Policies service collection coverage:

- Policy search and retrieval:
  - `falcon_search_content_update_policies`
  - `falcon_query_content_update_policy_ids`
  - `falcon_get_content_update_policy_details`
- Policy member workflows:
  - `falcon_search_content_update_policy_members`
  - `falcon_query_content_update_policy_member_ids`
- Content version discovery:
  - `falcon_query_content_update_pinnable_versions`
- Policy lifecycle and execution controls:
  - `falcon_create_content_update_policies`
  - `falcon_update_content_update_policies`
  - `falcon_delete_content_update_policies`
  - `falcon_perform_content_update_policies_action`
  - `falcon_set_content_update_policies_precedence`
  - All write tools above require `confirm_execution=true`

**Resources**:

- `falcon://content-update-policies/policies/fql-guide`: FQL documentation for content update policy search and ID query tools
- `falcon://content-update-policies/members/fql-guide`: FQL documentation for content update policy member search and ID query tools
- `falcon://content-update-policies/pinnable-versions/guide`: Valid content categories and sorting guidance for pinnable version queries
- `falcon://content-update-policies/safety-guide`: Operational guardrails for content update policy write operations

**Use Cases**: Content rollout governance, pinned-content verification, policy assignment analysis, and safe override / precedence orchestration

### Custom IOA Module

**API Scopes Required**:

- `Custom IOA Rules:read`
- `Custom IOA Rules:write`

Provides tools for managing Custom IOA (Indicators of Attack) behavioral detection rules and rule groups:

- `search_ioa_rule_groups`: Search Custom IOA rule groups and return full details including their rules
- `get_ioa_platforms`: Get all available platforms for Custom IOA rule groups
- `get_ioa_rule_types`: Get all available Custom IOA rule types with fields and disposition IDs
- `create_ioa_rule_group`: Create a new Custom IOA rule group for a specific platform
- `update_ioa_rule_group`: Update an existing Custom IOA rule group (name, description, enabled state)
- `delete_ioa_rule_groups`: Delete Custom IOA rule groups by ID
- `create_ioa_rule`: Create a new behavioral detection rule within a rule group
- `update_ioa_rule`: Update an existing behavioral detection rule
- `delete_ioa_rules`: Delete behavioral detection rules from a rule group

**Resources**:

- `falcon://custom-ioa/rule-groups/fql-guide`: FQL documentation and examples for IOA rule group searches

**Use Cases**: Custom behavioral detection management, IOA rule lifecycle, platform-specific detection rules, security policy enforcement

### Detections Module

**API Scopes Required**:

- `Alerts:read`
- `Alerts:write`

Provides full Alerts/detections operation coverage:

- `falcon_search_detections`: Two-step v2 detection search (query IDs then fetch full details)
- `falcon_search_detections_combined`: Combined detections search using cursor-style pagination
- `falcon_query_detection_ids_v1`: Query detection IDs with the v1 query operation
- `falcon_query_detection_ids_v2`: Query detection IDs with the v2 query operation
- `falcon_get_detection_details`: Backward-compatible v2 details lookup by composite IDs
- `falcon_get_detection_details_v1`: Retrieve detection details by legacy detection IDs
- `falcon_get_detection_details_v2`: Retrieve detection details by composite IDs with `include_hidden`
- `falcon_aggregate_detections_v1`: Run detections aggregate queries with v1 operation
- `falcon_aggregate_detections_v2`: Run detections aggregate queries with v2 operation
- `falcon_update_detections_v1`: Apply detection actions with v1 update operation (requires `confirm_execution=true`)
- `falcon_update_detections_v2`: Apply detection actions with v2 update operation (requires `confirm_execution=true`)
- `falcon_update_detections_v3`: Apply detection actions with v3 update operation (requires `confirm_execution=true`)

**Resources**:

- `falcon://detections/search/fql-guide`: Comprehensive FQL documentation and examples for detection searches
- `falcon://detections/aggregation/guide`: Aggregation body examples and usage guidance
- `falcon://detections/update-actions/guide`: Update action parameter and safety guidance

**Use Cases**: Threat hunting, security analysis, incident response, detection triage automation, assignment/status lifecycle workflows

### Delivery Settings Module

**API Scopes Required**:

- `delivery-settings:read`
- `delivery-settings:write`

Provides tools for Falcon Delivery Settings operations:

- `falcon_get_delivery_settings`: Retrieve the current delivery settings configuration
- `falcon_create_delivery_settings`: Create or update delivery settings (requires `confirm_execution=true`)

**Resources**:

- `falcon://delivery-settings/usage-guide`: Payload guidance for retrieving and updating delivery settings
- `falcon://delivery-settings/safety-guide`: Operational guardrails for delivery settings writes

**Use Cases**: Delivery configuration review, controlled settings updates, and tenant configuration automation

### Deployments Module

**API Scopes Required**:

- `deployment-coordinator:read`
- `deployments:read`

Provides read-only release and release-note tools:

- `falcon_search_deployment_releases`: Search release records and return combined details
- `falcon_get_deployment_details`: Retrieve deployment records by release ID
- `falcon_search_release_notes`: Search release notes and return combined details
- `falcon_query_release_note_ids`: Query release note IDs only
- `falcon_get_release_notes_v1`: Retrieve release notes by ID with the legacy detail endpoint
- `falcon_get_release_notes_v2`: Retrieve release notes by ID with the v2 detail endpoint

**Resources**:

- `falcon://deployments/fql-guide`: FQL guidance for release and release-note filters

**Use Cases**: Release visibility, deployment detail review, release-note lookup workflows, and release metadata automation

### Device Content Module

**API Scopes Required**:

- `device-content:read`

Provides read-only Device Content tools:

- `falcon_search_device_content_states`: Query Device Content state IDs and return full details
- `falcon_query_device_content_state_ids`: Query Device Content state IDs only
- `falcon_get_device_content_states`: Retrieve Device Content states by ID

**Resources**:

- `falcon://device-content/states/fql-guide`: FQL guidance for Device Content state queries

**Use Cases**: Host content state review, content readiness analysis, and Device Content inventory lookups

### Discover Module

**API Scopes Required**: `Assets:read`

Provides full Discover read coverage:

- `falcon_search_applications`, `falcon_query_application_ids`, `falcon_get_application_details`
- `falcon_search_hosts_combined`, `falcon_query_host_ids`, `falcon_get_host_details`, `falcon_search_hosts`
- `falcon_search_unmanaged_assets` (enforces `entity_type:'unmanaged'`)
- `falcon_query_account_ids`, `falcon_get_account_details`, `falcon_search_accounts`
- `falcon_query_login_ids`, `falcon_get_login_details`, `falcon_search_logins`
- `falcon_query_iot_host_ids`, `falcon_query_iot_host_ids_v2`, `falcon_get_iot_host_details`, `falcon_search_iot_hosts`

**Resources**:

- `falcon://discover/applications/fql-guide`: Comprehensive FQL documentation and examples for application searches
- `falcon://discover/hosts/fql-guide`: Comprehensive FQL documentation and examples for unmanaged assets searches

**Use Cases**: Application inventory management, software asset management, unmanaged and managed host visibility, account/login telemetry analysis, IoT asset discovery workflows

### Downloads Module

**API Scopes Required**: `infrastructure-as-code:read`

Provides tools for download artifact discovery and URL retrieval:

- `falcon_enumerate_download_files`: Enumerate download artifacts using discrete legacy filters
- `falcon_fetch_download_file_info`: Fetch download file metadata and pre-signed URLs using combined v1 FQL search
- `falcon_fetch_download_file_info_v2`: Fetch download file metadata and pre-signed URLs using combined v2 FQL search
- `falcon_get_download_file_url`: Retrieve a direct pre-signed URL for a specific file name and version

**Resources**:

- `falcon://downloads/files/fql-guide`: FQL guidance for combined downloads search tools
- `falcon://downloads/files/usage-guide`: Usage notes for legacy enumerate and direct download URL tools

**Use Cases**: Artifact catalog discovery, automated tooling bootstrap, download URL retrieval, and version-aware package lookup

### Drift Indicators Module

**API Scopes Required**: `drift-indicators:read`

Provides tools for Drift Indicators analytics and entity retrieval:

- `falcon_get_drift_indicator_values_by_date`: Return drift indicator counts grouped by date
- `falcon_get_drift_indicator_count`: Return the total drift indicator count for a filter
- `falcon_query_drift_indicator_ids`: Query drift indicator IDs
- `falcon_get_drift_indicator_details`: Retrieve drift indicator entities by ID
- `falcon_search_drift_indicator_entities`: Search and return full drift indicator entities

**Resources**:

- `falcon://drift-indicators/fql-guide`: Shared FQL guidance for count, query, and combined search tools

**Use Cases**: Cloud workload drift triage, indicator trend analysis, prevented-vs-observed review, and Kubernetes/container drift investigations

### Exposure Management Module

**API Scopes Required**:

- `Exposure Management:read`
- `Exposure Management:write`

Provides tools for external asset exposure management:

- `falcon_search_exposure_assets`: Search external assets and return full asset details
- `falcon_get_exposure_asset_details`: Retrieve full external asset records by ID
- `falcon_aggregate_exposure_assets`: Run aggregate queries over external assets
- `falcon_add_exposure_assets`: Add assets to external asset inventory (`confirm_execution=true` required)
- `falcon_update_exposure_assets`: Patch asset criticality / triage metadata (`confirm_execution=true` required)
- `falcon_remove_exposure_assets`: Delete external assets (`confirm_execution=true` required)

**Resources**:

- `falcon://exposure-management/assets/fql-guide`: FQL documentation and examples for exposure asset searches
- `falcon://exposure-management/safety-guide`: Safety and operational guidance for write operations

**Use Cases**: External attack-surface inventory, triage workflow automation, asset criticality governance

### Event Streams Module

**API Scopes Required**: `event-streams:read`

Provides tools for Event Streams discovery and session maintenance:

- `falcon_list_event_streams`: Discover stream partitions, session tokens, and refresh URLs for a consumer `app_id`
- `falcon_refresh_event_stream_session`: Refresh an already-active event stream partition session

**Resources**:

- `falcon://event-streams/usage-guide`: Guidance for `app_id` rules, stream formats, and refresh behavior

**Use Cases**: Discovering Firehose connection details for downstream consumers, validating stream configuration, and refreshing active stream consumers outside MCP

### FDR Module

**API Scopes Required**: `falcon-data-replicator:read`

Provides tools for Falcon Data Replicator schema discovery:

- `falcon_get_fdr_combined_schema`: Retrieve the combined FDR schema summary
- `falcon_query_fdr_event_schema_ids`, `falcon_get_fdr_event_schema_details`, `falcon_search_fdr_event_schemas`
- `falcon_query_fdr_field_schema_ids`, `falcon_get_fdr_field_schema_details`, `falcon_search_fdr_field_schemas`

**Resources**:

- `falcon://fdr/events/fql-guide`: FQL guidance for event schema query/search tools
- `falcon://fdr/fields/fql-guide`: FQL guidance for field schema query/search tools

**Use Cases**: Building downstream FDR parsers, schema-aware enrichment, event catalog discovery, and field reference lookups

### Hosts Module

**API Scopes Required**:

- `Hosts:read`
- `Host Groups:read`
- `Host Groups:write`
- `Host Migration:read`
- `Host Migration:write`

Provides tools for hosts, host groups, and host migration workflows:

- `falcon_search_hosts`: Search for hosts in your CrowdStrike environment
- `falcon_get_host_details`: Retrieve detailed information for specific host device IDs
- `falcon_search_host_groups`: Search host groups and return full group details
- `falcon_search_host_group_members`: Search host group members and return full host records
- `falcon_add_host_group`: Create a host group
- `falcon_update_host_group`: Update an existing host group
- `falcon_remove_host_groups`: Delete host groups by ID
- `falcon_perform_host_group_action`: Add/remove hosts in host groups using filters or action parameters
- `falcon_search_migrations`: Search migration jobs and return full migration details
- `falcon_search_host_migrations`: Search host migration entities within a migration job
- `falcon_create_migration`: Create a host migration job
- `falcon_get_migration_destinations`: Resolve available migration destinations for selected hosts
- `falcon_perform_migration_action`: Start, cancel, rename, or delete migration jobs
- `falcon_perform_host_migration_action`: Update host migration entities inside a migration job

**Resources**:

- `falcon://hosts/search/fql-guide`: FQL documentation and examples for host searches
- `falcon://hosts/groups/fql-guide`: FQL documentation and examples for host group searches
- `falcon://hosts/migrations/fql-guide`: FQL documentation and examples for migration job searches
- `falcon://hosts/host-migrations/fql-guide`: FQL documentation and examples for host migration entity searches

**Use Cases**: Host inventory, host group lifecycle management, migration planning, and migration execution workflows

### Identity Protection Module

**API Scopes Required**: `Identity Protection Entities:read`, `Identity Protection Timeline:read`, `Identity Protection Detections:read`, `Identity Protection Assessment:read`, `Identity Protection GraphQL:write`

Provides tools for accessing and managing CrowdStrike Falcon Identity Protection capabilities:

- `idp_investigate_entity`: Entity investigation tool for analyzing users, endpoints, and other entities with support for timeline analysis, relationship mapping, and risk assessment

**Use Cases**: Entity investigation, identity protection analysis, user behavior analysis, endpoint security assessment, relationship mapping, risk assessment

### User Management Module

**API Scopes Required**:

- `User Management:read`
- `User Management:write`

Provides full User Management service collection coverage:

- `falcon_aggregate_users`: Run user-management aggregate queries with list-based aggregation payloads
- `falcon_search_users`: Search users and return full user details (two-step query + entity retrieval)
- `falcon_get_user_details`: Retrieve full user records by UUID
- `falcon_search_user_roles`: Search available roles and return full role details
- `falcon_get_user_role_details`: Retrieve role records by ID using `entitiesRolesGETV2`
- `falcon_get_user_role_details_v1`: Retrieve role records by ID using `entitiesRolesV1`
- `falcon_get_user_role_grants`: Review role grants for a specific user
- `falcon_create_user`: Create users (`confirm_execution=true` required)
- `falcon_update_user`: Update user first/last name (`confirm_execution=true` required)
- `falcon_delete_user`: Delete users (`confirm_execution=true` required)
- `falcon_perform_user_action`: Apply user actions (`reset_password` / `reset_2fa`) (`confirm_execution=true` required)
- `falcon_grant_user_roles`: Grant roles to a user (`confirm_execution=true` required)
- `falcon_revoke_user_roles`: Revoke roles from a user (`confirm_execution=true` required)

**Resources**:

- `falcon://user-management/users/fql-guide`: FQL documentation and examples for user searches
- `falcon://user-management/user-role-grants/fql-guide`: FQL documentation and examples for grant queries
- `falcon://user-management/safety-guide`: Safety and operational guidance for IAM write actions

**Use Cases**: IAM automation with guardrails, user access review, role assignment governance, least-privilege enforcement

### Incidents Module

**API Scopes Required**:

- `Incidents:read`
- `Incidents:write`

Provides full Incidents service collection coverage:

- `falcon_show_crowd_score`: View calculated CrowdScore records with environment-level score summaries
- `falcon_search_incidents`: Search incidents and return full incident details (two-step query + detail retrieval)
- `falcon_query_incident_ids`: Query incident IDs directly from FQL criteria
- `falcon_get_incident_details`: Retrieve full incident records by ID
- `falcon_search_behaviors`: Search incident behaviors and return full behavior details
- `falcon_query_behavior_ids`: Query behavior IDs directly from FQL criteria
- `falcon_get_behavior_details`: Retrieve full behavior records by ID
- `falcon_perform_incident_action`: Apply incident update actions (`confirm_execution=true` required)

**Resources**:

- `falcon://incidents/crowd-score/fql-guide`: Comprehensive FQL documentation for CrowdScore queries
- `falcon://incidents/search/fql-guide`: Comprehensive FQL documentation and examples for incident searches
- `falcon://incidents/behaviors/fql-guide`: Comprehensive FQL documentation and examples for behavior searches
- `falcon://incidents/actions/guide`: Incident action safety and parameter guidance

**Use Cases**: Incident management, threat assessment, attack pattern analysis, analyst assignment/status updates, SOC triage workflow automation

### Installation Tokens Module

**API Scopes Required**:

- `Installation Tokens:read`
- `Installation Tokens:write`
- `Installation Tokens Settings:write`

Provides full Installation Tokens service collection coverage:

- `falcon_search_installation_tokens`: Search installation token IDs and return full token details
- `falcon_get_installation_token_details`: Retrieve token records by ID
- `falcon_create_installation_token`: Create a token (`confirm_execution=true` required)
- `falcon_update_installation_tokens`: Update token fields (`confirm_execution=true` required)
- `falcon_delete_installation_tokens`: Delete token IDs (`confirm_execution=true` required)
- `falcon_search_installation_token_audit_events`: Search audit event IDs and return full event details
- `falcon_get_installation_token_audit_event_details`: Retrieve audit event records by ID
- `falcon_get_installation_token_customer_settings`: Read token customer settings
- `falcon_update_installation_token_customer_settings`: Update token customer settings (`confirm_execution=true` required)

**Resources**:

- `falcon://installation-tokens/tokens/fql-guide`: FQL documentation and examples for token searches
- `falcon://installation-tokens/audit/fql-guide`: FQL documentation and examples for audit event searches
- `falcon://installation-tokens/safety-guide`: Operational guardrails for write operations

**Use Cases**: Sensor installation token lifecycle management, token audit investigations, revocation workflows, tenant token policy governance

### Prevention Policies Module

**API Scopes Required**:

- `Prevention Policies:read`
- `Prevention Policies:write`

Provides full Prevention Policies service collection coverage:

- `falcon_search_prevention_policies`: Search prevention policies with combined detail responses
- `falcon_search_prevention_policy_members`: Search members assigned to a specific prevention policy
- `falcon_query_prevention_policy_ids`: Query prevention policy IDs
- `falcon_query_prevention_policy_member_ids`: Query prevention policy member IDs for a specific policy
- `falcon_get_prevention_policy_details`: Retrieve prevention policy records by ID
- `falcon_create_prevention_policies`: Create prevention policies (`confirm_execution=true` required)
- `falcon_update_prevention_policies`: Update prevention policies (`confirm_execution=true` required)
- `falcon_delete_prevention_policies`: Delete prevention policies (`confirm_execution=true` required)
- `falcon_perform_prevention_policies_action`: Apply prevention policy actions (`confirm_execution=true` required)
- `falcon_set_prevention_policies_precedence`: Set prevention policy precedence ordering (`confirm_execution=true` required)

**Resources**:

- `falcon://prevention-policies/policies/fql-guide`: FQL documentation and examples for prevention policy search/query tools
- `falcon://prevention-policies/members/fql-guide`: FQL documentation and examples for prevention policy member search/query tools
- `falcon://prevention-policies/safety-guide`: Operational guardrails for prevention policy write operations

**Use Cases**: Prevention policy inventory, policy-member assignment analysis, controlled policy lifecycle actions, and precedence governance

### Response Policies Module

**API Scopes Required**:

- `Response Policies:read`
- `Response Policies:write`

Provides full Response Policies service collection coverage:

- `falcon_search_response_policies`: Search response policies with combined detail responses
- `falcon_search_response_policy_members`: Search members assigned to a specific response policy
- `falcon_query_response_policy_ids`: Query response policy IDs
- `falcon_query_response_policy_member_ids`: Query response policy member IDs for a specific policy
- `falcon_get_response_policy_details`: Retrieve response policy records by ID
- `falcon_create_response_policies`: Create response policies (`confirm_execution=true` required)
- `falcon_update_response_policies`: Update response policies (`confirm_execution=true` required)
- `falcon_delete_response_policies`: Delete response policies (`confirm_execution=true` required)
- `falcon_perform_response_policies_action`: Apply response policy actions (`confirm_execution=true` required)
- `falcon_set_response_policies_precedence`: Set response policy precedence ordering (`confirm_execution=true` required)

**Resources**:

- `falcon://response-policies/policies/fql-guide`: FQL documentation and examples for response policy search/query tools
- `falcon://response-policies/members/fql-guide`: FQL documentation and examples for response policy member search/query tools
- `falcon://response-policies/safety-guide`: Operational guardrails for response policy write operations

**Use Cases**: Response policy inventory, policy-member assignment analysis, controlled policy lifecycle actions, and precedence governance

### Device Control Policies Module

**API Scopes Required**:

- `Device Control Policies:read`
- `Device Control Policies:write`

Provides full Device Control Policies service collection coverage:

- `falcon_search_device_control_policy_members`: Search members assigned to a specific device control policy
- `falcon_search_device_control_policies`: Search device control policies with combined detail responses
- `falcon_get_default_device_control_policies`: Retrieve default device control policy configuration
- `falcon_update_default_device_control_policies`: Update default policy configuration (`confirm_execution=true` required)
- `falcon_perform_device_control_policies_action`: Apply policy actions (`confirm_execution=true` required)
- `falcon_update_device_control_policies_classes`: Patch policy class configuration (`confirm_execution=true` required)
- `falcon_get_default_device_control_settings`: Retrieve default device control settings
- `falcon_update_default_device_control_settings`: Update default settings (`confirm_execution=true` required)
- `falcon_set_device_control_policies_precedence`: Set policy precedence ordering (`confirm_execution=true` required)
- `falcon_get_device_control_policy_details`: Retrieve policy records by ID (v1)
- `falcon_create_device_control_policies`: Create policies (v1, `confirm_execution=true` required)
- `falcon_update_device_control_policies`: Update policies (v1, `confirm_execution=true` required)
- `falcon_delete_device_control_policies`: Delete policies (`confirm_execution=true` required)
- `falcon_get_device_control_policy_details_v2`: Retrieve policy records by ID (v2)
- `falcon_create_device_control_policies_v2`: Create policies (v2, `confirm_execution=true` required)
- `falcon_update_device_control_policies_v2`: Update policies (v2, `confirm_execution=true` required)
- `falcon_query_device_control_policy_member_ids`: Query policy member IDs
- `falcon_query_device_control_policy_ids`: Query policy IDs

**Resources**:

- `falcon://device-control-policies/policies/fql-guide`: FQL documentation and examples for device control policy search/query tools
- `falcon://device-control-policies/members/fql-guide`: FQL documentation and examples for device control policy member search/query tools
- `falcon://device-control-policies/defaults/guide`: Guidance for default and class-level policy operations
- `falcon://device-control-policies/safety-guide`: Operational guardrails for device control policy write operations

**Use Cases**: Device policy inventory, host assignment analysis, default policy governance, class configuration management, and precedence orchestration

### Firewall Policies Module

**API Scopes Required**:

- `Firewall Policies:read`
- `Firewall Policies:write`

Provides full Firewall Policies service collection coverage:

- `falcon_search_firewall_policy_members`: Search members assigned to a specific firewall policy
- `falcon_search_firewall_policies`: Search firewall policies with combined detail responses
- `falcon_perform_firewall_policies_action`: Apply firewall policy actions (`confirm_execution=true` required)
- `falcon_set_firewall_policies_precedence`: Set firewall policy precedence ordering (`confirm_execution=true` required)
- `falcon_get_firewall_policy_details`: Retrieve firewall policy records by ID
- `falcon_create_firewall_policies`: Create firewall policies (`confirm_execution=true` required)
- `falcon_update_firewall_policies`: Update firewall policies (`confirm_execution=true` required)
- `falcon_delete_firewall_policies`: Delete firewall policies (`confirm_execution=true` required)
- `falcon_query_firewall_policy_member_ids`: Query firewall policy member IDs
- `falcon_query_firewall_policy_ids`: Query firewall policy IDs

**Resources**:

- `falcon://firewall-policies/policies/fql-guide`: FQL documentation and examples for firewall policy search/query tools
- `falcon://firewall-policies/members/fql-guide`: FQL documentation and examples for firewall policy member search/query tools
- `falcon://firewall-policies/safety-guide`: Operational guardrails for firewall policy write operations

**Use Cases**: Firewall policy inventory, host assignment analysis, policy lifecycle control, and precedence orchestration

### Sensor Update Policies Module

**API Scopes Required**:

- `Sensor Update Policies:read`
- `Sensor Update Policies:write`

Provides full Sensor Update Policies service collection coverage:

- `falcon_reveal_sensor_uninstall_token`: Reveal uninstall tokens (`confirm_execution=true` required)
- `falcon_search_sensor_update_builds`: Search available sensor update builds by platform and optional stage
- `falcon_search_sensor_update_kernels`: Search kernel compatibility records
- `falcon_search_sensor_update_policy_members`: Search members assigned to a specific sensor update policy
- `falcon_search_sensor_update_policies`: Search sensor update policies (v1)
- `falcon_search_sensor_update_policies_v2`: Search sensor update policies (v2)
- `falcon_perform_sensor_update_policies_action`: Apply policy actions (`confirm_execution=true` required)
- `falcon_set_sensor_update_policies_precedence`: Set policy precedence ordering (`confirm_execution=true` required)
- `falcon_get_sensor_update_policy_details`: Retrieve policy records by ID (v1)
- `falcon_create_sensor_update_policies`: Create policies (v1, `confirm_execution=true` required)
- `falcon_update_sensor_update_policies`: Update policies (v1, `confirm_execution=true` required)
- `falcon_delete_sensor_update_policies`: Delete policies (`confirm_execution=true` required)
- `falcon_get_sensor_update_policy_details_v2`: Retrieve policy records by ID (v2)
- `falcon_create_sensor_update_policies_v2`: Create policies (v2, `confirm_execution=true` required)
- `falcon_update_sensor_update_policies_v2`: Update policies (v2, `confirm_execution=true` required)
- `falcon_query_sensor_update_kernel_distinct`: Query distinct kernel compatibility values
- `falcon_query_sensor_update_policy_member_ids`: Query policy member IDs
- `falcon_query_sensor_update_policy_ids`: Query policy IDs

**Resources**:

- `falcon://sensor-update-policies/policies/fql-guide`: FQL documentation and examples for sensor update policy search/query tools
- `falcon://sensor-update-policies/members/fql-guide`: FQL documentation and examples for sensor update policy member search/query tools
- `falcon://sensor-update-policies/kernels/fql-guide`: FQL documentation for kernel compatibility searches
- `falcon://sensor-update-policies/builds/guide`: Build query parameter guidance
- `falcon://sensor-update-policies/safety-guide`: Operational guardrails for sensor update policy write and token-reveal operations

**Use Cases**: Sensor rollout planning, kernel/build compatibility analysis, policy lifecycle control, uninstall token governance, and update precedence management

### Workflows Module

**API Scopes Required**:

- `Workflow:read`
- `Workflow:write`

Provides full Falcon Workflows service collection coverage:

- `falcon_search_workflow_activities`: Search workflow activities with FQL filters
- `falcon_search_workflow_activities_content`: Search workflow activity content records with FQL filters
- `falcon_search_workflow_definitions`: Search workflow definitions
- `falcon_search_workflow_executions`: Search workflow execution records
- `falcon_search_workflow_triggers`: Search workflow trigger records
- `falcon_export_workflow_definition`: Export a workflow definition by ID
- `falcon_import_workflow_definition`: Import a workflow definition from YAML (`confirm_execution=true` required)
- `falcon_update_workflow_definition`: Update workflow definition payloads (`confirm_execution=true` required)
- `falcon_update_workflow_definition_status`: Enable, disable, or cancel definition executions (`confirm_execution=true` required)
- `falcon_execute_workflow`: Execute on-demand workflows (`confirm_execution=true` required)
- `falcon_execute_workflow_internal`: Execute internal on-demand workflows (`confirm_execution=true` required)
- `falcon_mock_execute_workflow`: Execute workflow definitions with mocks (`confirm_execution=true` required)
- `falcon_update_workflow_execution_state`: Resume or cancel workflow executions (`confirm_execution=true` required)
- `falcon_get_workflow_execution_results`: Retrieve workflow execution results by ID
- `falcon_get_workflow_human_input`: Retrieve workflow human input records by ID
- `falcon_update_workflow_human_input`: Submit workflow human-input decisions (`confirm_execution=true` required)
- `falcon_deprovision_workflow_system_definition`: Deprovision system definitions (`confirm_execution=true` required)
- `falcon_promote_workflow_system_definition`: Promote system definitions (`confirm_execution=true` required)
- `falcon_provision_workflow_system_definition`: Provision system definitions (`confirm_execution=true` required)

**Resources**:

- `falcon://workflows/activities/fql-guide`: FQL documentation and examples for workflow activity searches
- `falcon://workflows/definitions/fql-guide`: FQL documentation and examples for workflow definition searches
- `falcon://workflows/executions/fql-guide`: FQL documentation and examples for workflow execution searches
- `falcon://workflows/triggers/fql-guide`: FQL documentation and examples for workflow trigger searches
- `falcon://workflows/import/guide`: Import guidance for workflow definition YAML payloads
- `falcon://workflows/safety-guide`: Operational guardrails for workflow write and execution tools

**Use Cases**: Workflow inventory and lifecycle management, controlled workflow execution, execution recovery actions, and human-approval orchestration

### IT Automation Module

**API Scopes Required**:

- `IT Automation:read`
- `IT Automation:write`

Provides full IT Automation service collection coverage:

- Search/query operations for:
  - tasks (`falcon_search_it_automation_tasks_combined`, `falcon_search_it_automation_task_ids`)
  - task groups (`falcon_search_it_automation_task_groups_combined`, `falcon_search_it_automation_task_group_ids`)
  - scheduled tasks (`falcon_search_it_automation_scheduled_tasks_combined`, `falcon_search_it_automation_scheduled_task_ids`)
  - executions (`falcon_search_it_automation_task_executions`, `falcon_search_it_automation_task_execution_ids`)
  - user groups and policies (`falcon_search_it_automation_user_group_ids`, `falcon_query_it_automation_policy_ids`)
  - file associations (`falcon_search_it_automation_associated_tasks`)
- Entity retrieval tools for tasks, task groups, scheduled tasks, user groups, policies, execution details, and host status
- Execution-results workflow tools:
  - `falcon_start_it_automation_execution_results_search`
  - `falcon_get_it_automation_execution_results_search_status`
  - `falcon_get_it_automation_execution_results`
- Write lifecycle tools for create/update/delete operations across user groups, policies, tasks, task groups, and scheduled tasks (`confirm_execution=true` required)
- High-impact execution controls:
  - `falcon_start_it_automation_task_execution` (`confirm_execution=true` required)
  - `falcon_run_it_automation_live_query` (`confirm_execution=true` required)
  - `falcon_cancel_it_automation_task_execution` (`confirm_execution=true` required)
  - `falcon_rerun_it_automation_task_execution` (`confirm_execution=true` required)

**Resources**:

- `falcon://it-automation/task-executions/fql-guide`: FQL documentation and examples for task execution searches
- `falcon://it-automation/phase3/safety-guide`: Safety and execution guidance for IT Automation write and execution tools

**Use Cases**: Controlled remote response actions, live query operations, execution monitoring, and execution result retrieval

### NGSIEM Module

**API Scopes Required**: `NGSIEM:read`, `NGSIEM:write`

Provides full NGSIEM service collection coverage:

- Search jobs:
  - `falcon_search_ngsiem` (async convenience execution + polling)
  - `falcon_start_ngsiem_search`, `falcon_get_ngsiem_search_status`, `falcon_stop_ngsiem_search`
- Dashboards:
  - `falcon_get_ngsiem_dashboard_template`, `falcon_list_ngsiem_dashboards`
  - `falcon_create_ngsiem_dashboard_from_template`, `falcon_update_ngsiem_dashboard_from_template`, `falcon_delete_ngsiem_dashboard`
- Lookup files:
  - `falcon_upload_ngsiem_lookup`, `falcon_get_ngsiem_lookup`, `falcon_get_ngsiem_lookup_from_package`
  - `falcon_get_ngsiem_lookup_from_namespace_package`, `falcon_get_ngsiem_lookup_file`, `falcon_list_ngsiem_lookup_files`
  - `falcon_create_ngsiem_lookup_file`, `falcon_update_ngsiem_lookup_file`, `falcon_delete_ngsiem_lookup_file`
- Parsers:
  - `falcon_get_ngsiem_parser_template`, `falcon_get_ngsiem_parser`, `falcon_list_ngsiem_parsers`
  - `falcon_create_ngsiem_parser_from_template`, `falcon_create_ngsiem_parser`, `falcon_update_ngsiem_parser`, `falcon_delete_ngsiem_parser`
- Saved queries:
  - `falcon_get_ngsiem_saved_query_template`, `falcon_list_ngsiem_saved_queries`
  - `falcon_create_ngsiem_saved_query`, `falcon_update_ngsiem_saved_query_from_template`, `falcon_delete_ngsiem_saved_query`
- Write/delete operations require `confirm_execution=true`

**Resources**:

- `falcon://ngsiem/repository-guide`: Repository and operation guidance for NGSIEM tools
- `falcon://ngsiem/search-guide`: Search workflow guidance and timestamp requirements
- `falcon://ngsiem/safety-guide`: Operational guardrails for NGSIEM write/delete operations

> [!IMPORTANT]
> This tool executes pre-written CQL queries only. It does **not** assist with query construction or provide CQL syntax guidance. Users must supply complete, valid CQL queries. For CQL documentation, refer to the [CrowdStrike LogScale documentation](https://library.humio.com/).

**Use Cases**: Log search and analysis, event correlation, threat hunting with custom CQL queries, security monitoring

### Intel Module

**API Scopes Required**:

- `Actors (Falcon Intelligence):read`
- `Indicators (Falcon Intelligence):read`
- `Reports (Falcon Intelligence):read`

Provides full FalconPy Intel service collection coverage:

- Actors:
  - `falcon_search_actors`, `falcon_query_actor_ids`, `falcon_get_actor_details`
- Indicators:
  - `falcon_search_indicators`, `falcon_query_indicator_ids`, `falcon_get_indicator_details`
- Reports:
  - `falcon_search_reports`, `falcon_query_report_ids`, `falcon_get_report_details`, `falcon_download_report_pdf`
- Rules:
  - `falcon_query_rule_ids`, `falcon_get_rule_details`, `falcon_download_rule_file`, `falcon_download_latest_rule_file`
- Malware:
  - `falcon_query_malware_ids`, `falcon_search_malware`, `falcon_get_malware_details`, `falcon_get_malware_mitre_report`
- MITRE:
  - `falcon_query_mitre_attacks`, `falcon_query_mitre_attacks_for_malware`, `falcon_get_mitre_attack_details`, `falcon_get_mitre_report`
- Vulnerabilities:
  - `falcon_query_vulnerability_ids`, `falcon_get_vulnerability_details`

**Resources**:

- `falcon://intel/actors/fql-guide`: Comprehensive FQL documentation and examples for threat actor searches
- `falcon://intel/indicators/fql-guide`: Comprehensive FQL documentation and examples for indicator searches
- `falcon://intel/reports/fql-guide`: Comprehensive FQL documentation and examples for intelligence report searches

**Use Cases**: Threat intelligence research, adversary tracking, IOC analysis, threat landscape assessment, MITRE ATT&CK framework analysis

### Intelligence Feeds Module

**API Scopes Required**:

- `indicator-graph:read`

Provides read-only intelligence feed tools:

- `falcon_list_intelligence_feeds`: List feed types accessible to the current tenant
- `falcon_query_intelligence_feed_archives`: Query accessible feed archive items
- `falcon_download_intelligence_feed_archive`: Request an archive download by feed item ID

**Resources**:

- `falcon://intelligence-feeds/usage-guide`: Usage guidance for feed discovery and archive download workflows

**Use Cases**: Feed discovery, archive inventory, indicator-feed retrieval workflows, and downstream archive processing

### MalQuery Module

**API Scopes Required**:

- `malquery:read`
- `malquery:write`

Provides MalQuery tools for quotas, search, request tracking, metadata, and downloads:

- `falcon_get_malquery_quotas`: Retrieve MalQuery search and download quotas
- `falcon_fuzzy_search_malquery`: Run a fuzzy MalQuery search (requires `confirm_execution=true`)
- `falcon_exact_search_malquery`: Run an exact MalQuery search (requires `confirm_execution=true`)
- `falcon_hunt_malquery`: Schedule a YARA-based MalQuery hunt (requires `confirm_execution=true`)
- `falcon_get_malquery_request`: Retrieve asynchronous request status by ID
- `falcon_get_malquery_metadata`: Retrieve metadata for indexed SHA256 values
- `falcon_get_malquery_samples_archive`: Retrieve the archive for a completed multi-download request
- `falcon_schedule_malquery_samples_multidownload`: Schedule sample hashes for multi-download (requires `confirm_execution=true`)
- `falcon_download_malquery_sample`: Download a single indexed sample by SHA256

**Resources**:

- `falcon://malquery/usage-guide`: Workflow guidance for search, polling, and download operations
- `falcon://malquery/safety-guide`: Operational guardrails for MalQuery write tools

**Use Cases**: Malware corpus search, YARA hunting, sample metadata lookup, request polling, and guarded malware retrieval workflows

### ML Exclusions Module

**API Scopes Required**:

- `ml-exclusions:read`
- `ml-exclusions:write`

Provides tools for Falcon ML exclusion workflows:

- `falcon_search_ml_exclusions`: Search ML exclusions and return full exclusion details
- `falcon_query_ml_exclusion_ids`: Query ML exclusion IDs
- `falcon_get_ml_exclusion_details`: Retrieve ML exclusion records by ID
- `falcon_create_ml_exclusions`: Create ML exclusions (requires `confirm_execution=true`)
- `falcon_update_ml_exclusions`: Update ML exclusions (requires `confirm_execution=true`)
- `falcon_delete_ml_exclusions`: Delete ML exclusions by ID (requires `confirm_execution=true`)

**Resources**:

- `falcon://ml-exclusions/search/fql-guide`: FQL documentation and examples for ML exclusion search tools
- `falcon://ml-exclusions/safety-guide`: Operational guardrails for ML exclusion write operations

**Use Cases**: Suppression tuning for known-safe binaries or paths, exclusion review, fleet-wide ML exception governance, and guarded cleanup of obsolete exclusions

### IOC Module

**API Scopes Required**:

- `IOC Management:read`
- `IOC Management:write`

Provides tools for managing custom indicators of compromise (IOCs) with Falcon IOC Service Collection endpoints:

- `falcon_search_iocs`: Search custom IOCs using FQL and return full IOC details
- `falcon_add_ioc`: Create one IOC or submit multiple IOCs in a single request
- `falcon_remove_iocs`: Remove IOCs by explicit IDs or by FQL filter for bulk cleanup

**Resources**:

- `falcon://ioc/search/fql-guide`: FQL documentation and examples for IOC searches

**Use Cases**: IOC lifecycle management, automated IOC onboarding, IOC cleanup and hygiene workflows

### Sensor Visibility Exclusions Module

**API Scopes Required**:

- `sensor-visibility-exclusions:read`
- `sensor-visibility-exclusions:write`

Provides tools for Falcon Sensor Visibility exclusion workflows:

- `falcon_search_sensor_visibility_exclusions`: Search sensor visibility exclusions and return full exclusion details
- `falcon_query_sensor_visibility_exclusion_ids`: Query sensor visibility exclusion IDs
- `falcon_get_sensor_visibility_exclusion_details`: Retrieve sensor visibility exclusion records by ID
- `falcon_create_sensor_visibility_exclusions`: Create sensor visibility exclusions (requires `confirm_execution=true`)
- `falcon_update_sensor_visibility_exclusions`: Update sensor visibility exclusions (requires `confirm_execution=true`)
- `falcon_delete_sensor_visibility_exclusions`: Delete sensor visibility exclusions by ID (requires `confirm_execution=true`)

**Resources**:

- `falcon://sensor-visibility-exclusions/search/fql-guide`: FQL documentation and examples for sensor visibility exclusion search tools
- `falcon://sensor-visibility-exclusions/safety-guide`: Operational guardrails for sensor visibility exclusion write operations

**Use Cases**: Telemetry suppression tuning for known-safe software, descendant-process visibility exception management, exclusion review, and guarded cleanup of obsolete exclusions

### IOA Exclusions Module

**API Scopes Required**:

- `IOA Exclusions:read`
- `IOA Exclusions:write`

Provides tools for managing IOA exclusions:

- `falcon_search_ioa_exclusions`: Search IOA exclusions with FQL (plus optional regex constraints) and return full details
- `falcon_add_ioa_exclusion`: Create an IOA exclusion using convenience fields or a full body payload
- `falcon_update_ioa_exclusion`: Update an IOA exclusion by ID using convenience fields or a full body payload
- `falcon_remove_ioa_exclusions`: Delete IOA exclusions by IDs with optional audit comment

**Resources**:

- `falcon://ioa-exclusions/search/fql-guide`: FQL documentation and examples for IOA exclusion searches

**Use Cases**: Exclusion lifecycle management, false-positive suppression workflows, and policy hygiene automation

### Firewall Management Module

**API Scopes Required**:

- `Firewall Management:read`
- `Firewall Management:write`

Provides full Firewall Management service collection coverage:

- Rules and rule groups:
  - `falcon_search_firewall_rules`, `falcon_search_firewall_rule_groups`, `falcon_search_firewall_policy_rules`
  - `falcon_query_firewall_rule_ids`, `falcon_query_firewall_rule_group_ids`, `falcon_query_firewall_policy_rule_ids`
  - `falcon_get_firewall_rules`, `falcon_get_firewall_rule_groups`
  - `falcon_aggregate_firewall_rules`, `falcon_aggregate_firewall_rule_groups`, `falcon_aggregate_firewall_policy_rules`
- Events and fields:
  - `falcon_query_firewall_event_ids`, `falcon_get_firewall_events`, `falcon_aggregate_firewall_events`
  - `falcon_query_firewall_field_ids`, `falcon_get_firewall_fields`
- Platforms and containers:
  - `falcon_query_firewall_platform_ids`, `falcon_get_firewall_platforms`, `falcon_get_firewall_policy_containers`
  - `falcon_update_firewall_policy_container`, `falcon_update_firewall_policy_container_v1` (`confirm_execution=true` required)
- Rule-group lifecycle:
  - `falcon_create_firewall_rule_group`, `falcon_update_firewall_rule_group`, `falcon_delete_firewall_rule_groups`
  - `falcon_validate_firewall_rule_group_create`, `falcon_validate_firewall_rule_group_update`
  - All write tools above require `confirm_execution=true`
- Network locations:
  - `falcon_query_firewall_network_location_ids`, `falcon_get_firewall_network_locations`, `falcon_get_firewall_network_location_details`
  - `falcon_create_firewall_network_locations`, `falcon_upsert_firewall_network_locations`, `falcon_update_firewall_network_locations`
  - `falcon_update_firewall_network_locations_metadata`, `falcon_update_firewall_network_locations_precedence`, `falcon_delete_firewall_network_locations`
  - All write tools above require `confirm_execution=true`
- Validation:
  - `falcon_validate_firewall_filepath_pattern`

**Resources**:

- `falcon://firewall/rules/fql-guide`: FQL documentation for rules, rule groups, and policy-rule query/search tools
- `falcon://firewall/events/fql-guide`: FQL documentation for firewall events ID query tools
- `falcon://firewall/network-locations/fql-guide`: FQL documentation for network location ID query tools
- `falcon://firewall/safety-guide`: Operational guardrails for firewall management write operations

**Use Cases**: Firewall rule governance, policy container changes, network location lifecycle automation, event analytics, and safe change orchestration

### Quarantine Module

**API Scopes Required**:

- `Quarantined Files:read`
- `Quarantined Files:write`

Provides full Quarantine service collection coverage:

- `falcon_search_quarantine_files`: Search quarantined file IDs and return full metadata details
- `falcon_get_quarantine_file_details`: Retrieve quarantined file metadata by ID
- `falcon_aggregate_quarantine_files`: Run aggregate queries against quarantined file data
- `falcon_get_quarantine_action_update_count`: Estimate impacted file counts per action using a filter
- `falcon_update_quarantine_files_by_ids`: Apply `release`, `unrelease`, or `delete` action by explicit file IDs (requires `confirm_execution=true`)
- `falcon_update_quarantine_files_by_query`: Apply `release`, `unrelease`, or `delete` action by query filter or phrase search (requires `confirm_execution=true`)

**Resources**:

- `falcon://quarantine/files/fql-guide`: FQL documentation and examples for quarantine search/action-count filters
- `falcon://quarantine/files/aggregation-guide`: Aggregation body example for quarantine aggregate queries
- `falcon://quarantine/files/safety-guide`: Operational guardrails for quarantine update operations

**Use Cases**: Quarantine triage, release/delete workflow automation, impact estimation before actions, quarantine state analytics

### Quick Scan Module

**API Scopes Required**:

- `quick-scan:read`
- `quick-scan:write`

Provides Quick Scan tools for query, detail, aggregation, and submission workflows:

- `falcon_search_quick_scans`: Query submission IDs and return full scan details
- `falcon_query_quick_scan_ids`: Query Quick Scan submission IDs only
- `falcon_get_quick_scans`: Retrieve Quick Scan records by ID
- `falcon_aggregate_quick_scans`: Run aggregate queries across scan history
- `falcon_scan_quick_samples`: Submit sample hashes for Quick Scan (requires `confirm_execution=true`)

**Resources**:

- `falcon://quick-scan/fql-guide`: FQL guidance for Quick Scan history queries
- `falcon://quick-scan/safety-guide`: Operational guardrails for sample submission workflows

**Use Cases**: Scan history review, scan-status lookup, aggregate reporting, and guarded sample submission workflows

### Real Time Response Module

**API Scopes Required**:

- `Real Time Response:read`
- `Real Time Response Admin:write`
- `Real Time Response Audit:read`

Provides unified tools for RTR core, RTR admin, and RTR audit workflows:

- **RTR Core**:
  - `falcon_search_rtr_sessions`: Search RTR sessions and return full session details
  - `falcon_aggregate_rtr_sessions`: Aggregate RTR session data
  - `falcon_search_rtr_queued_sessions`: Retrieve queued session metadata by session IDs
  - `falcon_init_rtr_session`: Initialize a single-host RTR session
  - `falcon_pulse_rtr_session`: Refresh a single-host RTR session timeout
  - `falcon_execute_rtr_command`: Execute an RTR read-only command
  - `falcon_check_rtr_command_status`: Check RTR command status
  - `falcon_execute_rtr_active_responder_command`: Execute an active-responder command
  - `falcon_check_rtr_active_responder_command_status`: Check active-responder command status
  - `falcon_batch_init_rtr_sessions`: Initialize RTR sessions in batch
  - `falcon_batch_refresh_rtr_sessions`: Refresh RTR batch session state
  - `falcon_execute_rtr_batch_command`: Execute read-only RTR command in batch
  - `falcon_execute_rtr_batch_active_responder_command`: Execute active-responder command in batch
  - `falcon_execute_rtr_batch_get_command`: Execute batch file retrieval command
  - `falcon_check_rtr_batch_get_command_status`: Check batch get command status
  - `falcon_get_rtr_extracted_file_contents`: Retrieve extracted file contents
  - `falcon_list_rtr_files_v1` / `falcon_list_rtr_files_v2`: List session files
  - `falcon_delete_rtr_file_v1` / `falcon_delete_rtr_file_v2`: Delete session files
  - `falcon_delete_rtr_session`: Delete RTR session by session ID
  - `falcon_delete_rtr_queued_session`: Delete queued RTR request by session and request ID
- **RTR Admin**:
  - `falcon_search_rtr_admin_scripts`: Search custom RTR scripts
  - `falcon_search_rtr_falcon_scripts`: Search Falcon-provided RTR scripts
  - `falcon_get_rtr_falcon_script_details`: Retrieve Falcon script details by ID
  - `falcon_search_rtr_admin_put_files`: Search RTR put-files
  - `falcon_get_rtr_put_file_contents`: Retrieve put-file contents by ID
  - `falcon_get_rtr_admin_put_file_details_v2`: Retrieve put-file metadata by ID (v2)
  - `falcon_create_rtr_admin_put_file_v1` / `falcon_create_rtr_admin_put_file_v2`: Create put-files
  - `falcon_delete_rtr_admin_put_file`: Delete put-file by ID
  - `falcon_get_rtr_admin_script_details_v2`: Retrieve custom script metadata by ID (v2)
  - `falcon_create_rtr_admin_script_v1` / `falcon_create_rtr_admin_script_v2`: Create custom scripts
  - `falcon_update_rtr_admin_script_v1` / `falcon_update_rtr_admin_script_v2`: Update custom scripts
  - `falcon_delete_rtr_admin_script`: Delete custom script by ID
  - `falcon_execute_rtr_admin_command`: Execute admin command on a single host
  - `falcon_execute_rtr_admin_batch_command`: Execute admin command in batch
  - `falcon_check_rtr_admin_command_status`: Check admin command status
- **RTR Audit**:
  - `falcon_search_rtr_audit_sessions`: Search RTR audit sessions with optional command metadata

**Resources**:

- `falcon://rtr/sessions/fql-guide`: FQL documentation and examples for RTR session searches
- `falcon://rtr/admin/fql-guide`: FQL documentation and examples for RTR admin script / put-file searches
- `falcon://rtr/audit/sessions/fql-guide`: FQL documentation and examples for RTR audit session searches

**Use Cases**: Host-level triage, remote session management, admin command and script operations, audit-driven RTR investigations, RTR workflow cleanup

### Sensor Usage Module

**API Scopes Required**: `Sensor Usage:read`

Provides tools for accessing and analyzing CrowdStrike Falcon sensor usage data:

- `falcon_search_sensor_usage`: Search for weekly sensor usage data in your CrowdStrike environment

**Resources**:

- `falcon://sensor-usage/weekly/fql-guide`: Comprehensive FQL documentation and examples for sensor usage searches

**Use Cases**: Sensor deployment monitoring, license utilization analysis, sensor health tracking

### Scheduled Reports Module

**API Scopes Required**: `Scheduled Reports:read`

Provides tools for accessing and managing CrowdStrike Falcon scheduled reports and scheduled searches:

- `falcon_search_scheduled_reports`: Search scheduled reports and return full report details
- `falcon_query_scheduled_report_ids`: Query scheduled report IDs with FQL
- `falcon_get_scheduled_report_details`: Retrieve scheduled report details by ID
- `falcon_launch_scheduled_report`: Launch scheduled reports on demand (`confirm_execution=true` required)
- `falcon_search_report_executions`: Search report executions and return full execution details
- `falcon_query_report_execution_ids`: Query report execution IDs with FQL
- `falcon_get_report_execution_details`: Retrieve report execution details by ID
- `falcon_retry_report_execution`: Retry failed/eligible report executions (`confirm_execution=true` required)
- `falcon_download_report_execution`: Download generated report execution files

**Resources**:

- `falcon://scheduled-reports/search/fql-guide`: Comprehensive FQL documentation for searching scheduled report entities
- `falcon://scheduled-reports/executions/search/fql-guide`: Comprehensive FQL documentation for searching report executions

**Use Cases**: Scheduled report lifecycle automation, execution monitoring and retries, scheduled search operations, and report download workflows

### Sensor Download Module

**API Scopes Required**: `Sensor Download:read`

Provides tools for querying and downloading Falcon sensor installers:

- `falcon_search_sensor_installer_ids`: Query installer SHA256 IDs using Sensor Download v1 query endpoint
- `falcon_search_sensor_installer_ids_v2`: Query installer SHA256 IDs using Sensor Download v2 query endpoint
- `falcon_get_sensor_installer_details`: Retrieve installer metadata by SHA256 (v1)
- `falcon_get_sensor_installer_details_v2`: Retrieve installer metadata by SHA256 (v2, includes architectures)
- `falcon_search_sensor_installers_combined`: Search installer metadata directly using combined v1 endpoint
- `falcon_search_sensor_installers_combined_v2`: Search installer metadata directly using combined v2 endpoint
- `falcon_get_sensor_installer_ccid`: Retrieve tenant installer CCID values
- `falcon_download_sensor_installer`: Download installer binary via v1 endpoint with optional inline base64 return
- `falcon_download_sensor_installer_v2`: Download installer binary via v2 endpoint with optional inline base64 return

**Resources**:

- `falcon://sensor-download/installers/fql-guide`: FQL filter/sort guidance for installer search tools
- `falcon://sensor-download/installers/download-guide`: Binary download behavior and inline content guidance

**Use Cases**: Sensor deployment automation, installer inventory validation, installer retrieval workflows, architecture-aware sensor packaging

### Serverless Module

**API Scopes Required**: `Falcon Container Image:read`

Provides tools for accessing and managing CrowdStrike Falcon Serverless Vulnerabilities:

- `falcon_search_serverless_vulnerabilities`: Search for vulnerabilities in your serverless functions across all cloud service providers

**Resources**:

- `falcon://serverless/vulnerabilities/fql-guide`: Comprehensive FQL documentation and examples for serverless vulnerabilities searches

**Use Cases**: Serverless security assessment, vulnerability management, cloud security monitoring

### Spotlight Module

**API Scopes Required**: `Vulnerabilities:read`

Provides tools for accessing and managing CrowdStrike Spotlight vulnerabilities:

- `falcon_search_vulnerabilities`: Search vulnerabilities with combined detail records
- `falcon_query_vulnerability_ids`: Query vulnerability IDs using Spotlight FQL
- `falcon_get_vulnerability_details`: Retrieve vulnerability detail records by ID
- `falcon_get_remediation_details`: Retrieve remediation detail records by remediation ID (v1)
- `falcon_get_remediation_details_v2`: Retrieve remediation detail records by remediation ID (v2)

**Resources**:

- `falcon://spotlight/vulnerabilities/fql-guide`: Comprehensive FQL documentation and examples for vulnerability searches
- `falcon://spotlight/remediations/usage-guide`: Guidance for resolving and using remediation IDs with remediation detail tools

**Use Cases**: Vulnerability inventory and triage, remediation enrichment workflows, compliance reporting, risk analysis, and patch prioritization

### ThreatGraph Module

**API Scopes Required**:

- `threatgraph:read`

Provides read-only ThreatGraph pivot tools:

- `falcon_get_threatgraph_edge_types`: List all available edge types
- `falcon_get_threatgraph_edges`: Retrieve edges for a vertex and edge type
- `falcon_get_threatgraph_ran_on`: Find indicator sightings in the environment
- `falcon_get_threatgraph_summary`: Retrieve summary data for vertex IDs
- `falcon_get_threatgraph_vertices_v1`: Retrieve vertex metadata with the v1 endpoint
- `falcon_get_threatgraph_vertices_v2`: Retrieve vertex metadata with the v2 endpoint

**Resources**:

- `falcon://threatgraph/usage-guide`: Workflow guidance for ThreatGraph pivots

**Use Cases**: Graph pivoting, vertex enrichment, indicator sighting lookups, and relationship analysis

### Zero Trust Assessment Module

**API Scopes Required**: `Zero Trust Assessment:read`

Provides read-only tools for Zero Trust posture review:

- `falcon_search_zta_assessments_by_score`: Query host Zero Trust assessments using score-based FQL filters
- `falcon_search_zta_combined_assessments`: Search combined Zero Trust assessments with optional host/finding facets
- `falcon_get_zta_assessment_details`: Retrieve detailed Zero Trust assessment records by host AID
- `falcon_get_zta_audit_report`: Retrieve tenant-wide Zero Trust audit metrics

**Resources**:

- `falcon://zero-trust-assessment/assessments/fql-guide`: Score filter and sort guidance for Zero Trust Assessment searches
- `falcon://zero-trust-assessment/combined-assessments/fql-guide`: Combined assessment filter, facet, and sort guidance

**Use Cases**: Zero Trust posture monitoring, low-score host triage, tenant-level audit and reporting

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- [`uv`](https://docs.astral.sh/uv/) or pip
- CrowdStrike Falcon API credentials (see above)

### Environment Configuration

You can configure your CrowdStrike API credentials in several ways:

#### Use a `.env` File

If you prefer using a `.env` file, you have several options:

##### Option 1: Copy from cloned repository (if you've cloned it)

```bash
cp .env.example .env
```

##### Option 2: Download the example file from GitHub

```bash
curl -o .env https://raw.githubusercontent.com/CrowdStrike/falcon-mcp/main/.env.example
```

##### Option 3: Create manually with the following content

```bash
# Required Configuration
FALCON_CLIENT_ID=your-client-id
FALCON_CLIENT_SECRET=your-client-secret
FALCON_BASE_URL=https://api.crowdstrike.com

# Optional Configuration (uncomment and modify as needed)
#FALCON_MCP_MODULES=detections,incidents,intel
#FALCON_MCP_TRANSPORT=stdio
#FALCON_MCP_DEBUG=false
#FALCON_MCP_HOST=127.0.0.1
#FALCON_MCP_PORT=8000
#FALCON_MCP_STATELESS_HTTP=false
#FALCON_MCP_API_KEY=your-api-key
```

#### Environment Variables

Alternatively, you can use environment variables directly.

Set the following environment variables in your shell:

```bash
# Required Configuration
export FALCON_CLIENT_ID="your-client-id"
export FALCON_CLIENT_SECRET="your-client-secret"
export FALCON_BASE_URL="https://api.crowdstrike.com"

# Optional Configuration
export FALCON_MCP_MODULES="detections,incidents,intel"  # Comma-separated list (default: all modules)
export FALCON_MCP_TRANSPORT="stdio"                     # Transport method: stdio, sse, streamable-http
export FALCON_MCP_DEBUG="false"                         # Enable debug logging: true, false
export FALCON_MCP_HOST="127.0.0.1"                      # Host for HTTP transports
export FALCON_MCP_PORT="8000"                           # Port for HTTP transports
export FALCON_MCP_STATELESS_HTTP="false"                # Stateless mode for scalable deployments
export FALCON_MCP_API_KEY="your-api-key"                # API key for HTTP transport auth (x-api-key header)
```

**CrowdStrike API Region URLs:**

- **US-1 (Default)**: `https://api.crowdstrike.com`
- **US-2**: `https://api.us-2.crowdstrike.com`
- **EU-1**: `https://api.eu-1.crowdstrike.com`
- **US-GOV**: `https://api.laggar.gcw.crowdstrike.com`

### Installation

> [!NOTE]
> If you just want to interact with falcon-mcp via an agent chat interface rather than running the server itself, take a look at [Additional Deployment Options](#additional-deployment-options). Otherwise continue to the installations steps below.

#### Install using uv

```bash
uv tool install falcon-mcp
```

#### Install using pip

```bash
pip install falcon-mcp
```

> [!TIP]
> If `falcon-mcp` isn't found, update your shell PATH.

For installation via code editors/assistants, see the [Editor/Assitant](#editorassistant-integration) section below

## Usage

### Command Line

Run the server with default settings (stdio transport):

```bash
falcon-mcp
```

Run with SSE transport:

```bash
falcon-mcp --transport sse
```

Run with streamable-http transport:

```bash
falcon-mcp --transport streamable-http
```

Run with streamable-http transport on custom port:

```bash
falcon-mcp --transport streamable-http --host 0.0.0.0 --port 8080
```

Run with stateless HTTP mode (for scalable deployments like AWS AgentCore):

```bash
falcon-mcp --transport streamable-http --stateless-http
```

Run with API key authentication (recommended for HTTP transports):

```bash
falcon-mcp --transport streamable-http --api-key your-secret-key
```

> **Security Note**: When using HTTP transports (`sse` or `streamable-http`), consider enabling API key authentication via `--api-key` or `FALCON_MCP_API_KEY` to protect the endpoint. This is a self-generated key (any secure string you create) that ensures only authorized clients with the matching key can access the MCP server when running remotely. This is separate from your CrowdStrike API credentials.

### Module Configuration

The Falcon MCP Server supports multiple ways to specify which modules to enable:

#### 1. Command Line Arguments (highest priority)

Specify modules using comma-separated lists:

```bash
# Enable specific modules
falcon-mcp --modules detections,incidents,intel,spotlight,idp

# Enable only one module
falcon-mcp --modules detections
```

#### 2. Environment Variable (fallback)

Set the `FALCON_MCP_MODULES` environment variable:

```bash
# Export environment variable
export FALCON_MCP_MODULES=detections,incidents,intel,spotlight,idp
falcon-mcp

# Or set inline
FALCON_MCP_MODULES=detections,incidents,intel,spotlight,idp falcon-mcp
```

#### 3. Default Behavior (all modules)

If no modules are specified via command line or environment variable, all available modules are enabled by default.

**Module Priority Order:**

1. Command line `--modules` argument (overrides all)
2. `FALCON_MCP_MODULES` environment variable (fallback)
3. All modules (default when none specified)

### Additional Command Line Options

For all available options:

```bash
falcon-mcp --help
```

### As a Library

```python
from falcon_mcp.server import FalconMCPServer

# Create and run the server
server = FalconMCPServer(
    base_url="https://api.us-2.crowdstrike.com",  # Optional, defaults to env var
    debug=True,  # Optional, enable debug logging
    enabled_modules=["detections", "incidents", "spotlight", "idp"],  # Optional, defaults to all modules
    api_key="your-api-key"  # Optional: API key for HTTP transport auth
)

# Run with stdio transport (default)
server.run()

# Or run with SSE transport
server.run("sse")

# Or run with streamable-http transport
server.run("streamable-http")

# Or run with streamable-http transport on custom host/port
server = FalconMCPServer(host="0.0.0.0", port=8080)
server.run("streamable-http")
```

#### Direct Credentials (Secret Management Integration)

For enterprise deployments using secret management systems (HashiCorp Vault, AWS Secrets Manager, etc.), you can pass credentials directly instead of using environment variables:

```python
from falcon_mcp.server import FalconMCPServer

# Example: Retrieve credentials from a secrets manager
# client_id = vault.read_secret("crowdstrike/client_id")
# client_secret = vault.read_secret("crowdstrike/client_secret")

# Create server with direct credentials
server = FalconMCPServer(
    client_id="your-client-id",           # Or retrieved from vault/secrets manager
    client_secret="your-client-secret",   # Or retrieved from vault/secrets manager
    base_url="https://api.us-2.crowdstrike.com",  # Optional
    enabled_modules=["detections", "incidents"]   # Optional
)

server.run()
```

> **Note**: When both direct parameters and environment variables are available, direct parameters take precedence.

### Running Examples

```bash
# Run with stdio transport
python examples/basic_usage.py

# Run with SSE transport
python examples/sse_usage.py

# Run with streamable-http transport
python examples/streamable_http_usage.py
```

## Container Usage

The Falcon MCP Server is available as a pre-built container image for easy deployment:

### Using Pre-built Image (Recommended)

```bash
# Pull the latest pre-built image
docker pull quay.io/crowdstrike/falcon-mcp:latest

# Run with .env file (recommended)
docker run -i --rm --env-file /path/to/.env quay.io/crowdstrike/falcon-mcp:latest

# Run with .env file and SSE transport
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport sse --host 0.0.0.0

# Run with .env file and streamable-http transport
docker run --rm -p 8000:8000 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport streamable-http --host 0.0.0.0

# Run with .env file and custom port
docker run --rm -p 8080:8080 --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --transport streamable-http --host 0.0.0.0 --port 8080

# Run with .env file and specific modules (stdio transport - requires -i flag)
docker run -i --rm --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:latest --modules detections,incidents,spotlight,idp

# Use a specific version instead of latest (stdio transport - requires -i flag)
docker run -i --rm --env-file /path/to/.env \
  quay.io/crowdstrike/falcon-mcp:1.2.3

# Alternative: Individual environment variables (stdio transport - requires -i flag)
docker run -i --rm -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret \
  quay.io/crowdstrike/falcon-mcp:latest
```

### Building Locally (Development)

For development or customization purposes, you can build the image locally:

```bash
# Build the Docker image
docker build -t falcon-mcp .

# Run the locally built image
docker run --rm -e FALCON_CLIENT_ID=your_client_id -e FALCON_CLIENT_SECRET=your_secret falcon-mcp
```

> [!NOTE]
> When using HTTP transports in Docker, always set `--host 0.0.0.0` to allow external connections to the container.

## Editor/Assistant Integration

You can integrate the Falcon MCP server with your editor or AI assistant. Here are configuration examples for popular MCP clients:

### Using `uvx` (recommended)

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "/path/to/.env",
        "falcon-mcp"
      ]
    }
  }
}
```

### With Module Selection

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "/path/to/.env",
        "falcon-mcp",
        "--modules",
        "detections,incidents,intel"
      ]
    }
  }
}
```

### Using Individual Environment Variables

```json
{
  "mcpServers": {
    "falcon-mcp": {
      "command": "uvx",
      "args": ["falcon-mcp"],
      "env": {
        "FALCON_CLIENT_ID": "your-client-id",
        "FALCON_CLIENT_SECRET": "your-client-secret",
        "FALCON_BASE_URL": "https://api.crowdstrike.com"
      }
    }
  }
}
```

### Docker Version

```json
{
  "mcpServers": {
    "falcon-mcp-docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/full/path/to/.env",
        "quay.io/crowdstrike/falcon-mcp:latest"
      ]
    }
  }
}
```

> [!NOTE]
> The `-i` flag is required when using the default stdio transport.

## Additional Deployment Options

### Amazon Bedrock AgentCore

To deploy the MCP Server as a tool in Amazon Bedrock AgentCore, please refer to the [following document](./docs/deployment/amazon_bedrock_agentcore.md).

### Google Cloud (Cloud Run and Vertex AI)

To deploy the MCP server as an agent within Cloud Run or Vertex AI Agent Engine (including for registration within Agentspace), refer to the [Google ADK example](./examples/adk/README.md).

### Gemini CLI

1. Install `uv`
1. `gemini extensions install https://github.com/CrowdStrike/falcon-mcp`
1. Copy a valid `.env` file to `~/.gemini/extensions/falcon-mcp/.env`

## Contributing

### Getting Started for Contributors

1. Clone the repository:

   ```bash
   git clone https://github.com/CrowdStrike/falcon-mcp.git
   cd falcon-mcp
   ```

2. Install in development mode:

   ```bash
   # Create .venv and install dependencies
   uv sync --all-extras

   # Activate the venv
   source .venv/bin/activate
   ```

> [!IMPORTANT]
> This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated releases and semantic versioning. Please follow the commit message format outlined in our [Contributing Guide](docs/CONTRIBUTING.md) when submitting changes.

### Running Tests

```bash
# Run all unit tests
pytest

# Run end-to-end tests (requires API credentials)
pytest --run-e2e tests/e2e/

# Run end-to-end tests with verbose output (note: -s is required to see output)
pytest --run-e2e -v -s tests/e2e/

# Run integration tests (requires API credentials)
pytest --run-integration tests/integration/

# Run integration tests with verbose output
pytest --run-integration -v -s tests/integration/

# Run integration tests for a specific module
pytest --run-integration tests/integration/test_detections.py
```

> **Note**: The `-s` flag is required to see detailed output from E2E and integration tests.

#### Integration Tests

Integration tests make real API calls to validate FalconPy operation names, HTTP methods, and response schemas. They catch issues that mocked unit tests cannot detect:

- Incorrect FalconPy operation names (typos)
- HTTP method mismatches (POST body vs GET query parameters)
- Two-step search patterns not returning full details
- API response schema changes

**Requirements**: Valid CrowdStrike API credentials must be configured (see [Environment Configuration](#environment-configuration)).

### Developer Documentation

- [Module Development Guide](docs/development/module_development.md): Instructions for implementing new modules
- [Resource Development Guide](docs/development/resource_development.md): Instructions for implementing resources
- [End-to-End Testing Guide](docs/development/e2e_testing.md): Guide for running and understanding E2E tests
- [Integration Testing Guide](docs/development/integration_testing.md): Guide for running integration tests with real API calls

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

This is a community-driven, open source project. While it is not an official CrowdStroke product, it is actively maintained by CrowdStrike and supported in collaboration with the open source developer community.

For more information, please see our [SUPPORT](SUPPORT.md) file.
