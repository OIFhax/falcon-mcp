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
  - [Core Functionality (Built into Server)](#core-functionality-built-into-server)
  - [Custom IOA Module](#custom-ioa-module)
  - [Detections Module](#detections-module)
  - [Discover Module](#discover-module)
  - [Exposure Management Module](#exposure-management-module)
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
  - [IOC Module](#ioc-module)
  - [IOA Exclusions Module](#ioa-exclusions-module)
  - [Firewall Management Module](#firewall-management-module)
  - [Quarantine Module](#quarantine-module)
  - [Real Time Response Module](#real-time-response-module)
  - [Scheduled Reports Module](#scheduled-reports-module)
  - [Sensor Download Module](#sensor-download-module)
  - [Sensor Usage Module](#sensor-usage-module)
  - [Serverless Module](#serverless-module)
  - [Spotlight Module](#spotlight-module)
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
| **Cloud Security** | `Falcon Container Image:read` | Find and analyze kubernetes containers inventory and container imges vulnerabilities |
| **Core** | _No additional scopes_ | Basic connectivity and system information |
| **Custom IOA** | `Custom IOA Rules:read`<br>`Custom IOA Rules:write` | Create and manage Custom IOA behavioral detection rules and rule groups |
| **Detections** | `Alerts:read` | Find and analyze detections to understand malicious activity |
| **Discover** | `Assets:read` | Search and analyze application inventory across your environment |
| **Exposure Management** | `Exposure Management:read`<br>`Exposure Management:write` | Search external assets and perform controlled asset inventory/triage updates |
| **Hosts** | `Hosts:read`<br>`Host Groups:read`<br>`Host Groups:write`<br>`Host Migration:read`<br>`Host Migration:write` | Search hosts, manage host groups, and orchestrate migration workflows |
| **Identity Protection** | `Identity Protection Entities:read`<br>`Identity Protection Timeline:read`<br>`Identity Protection Detections:read`<br>`Identity Protection Assessment:read`<br>`Identity Protection GraphQL:write` | Comprehensive entity investigation and identity protection analysis |
| **User Management** | `User Management:read`<br>`User Management:write` | Search users and roles, review grants, and perform controlled user/role assignment changes |
| **Incidents** | `Incidents:read` | Analyze security incidents and coordinated activities |
| **Installation Tokens** | `Installation Tokens:read`<br>`Installation Tokens:write`<br>`Installation Tokens Settings:write` | Search and manage installation tokens, inspect audit events, and control tenant token settings |
| **Prevention Policies** | `Prevention Policies:read`<br>`Prevention Policies:write` | Search and manage prevention policies, policy members, policy actions, and precedence ordering |
| **Response Policies** | `Response Policies:read`<br>`Response Policies:write` | Search and manage response policies, policy members, policy actions, and precedence ordering |
| **Device Control Policies** | `Device Control Policies:read`<br>`Device Control Policies:write` | Search and manage device control policies, defaults, classes, precedence, actions, and policy member relationships |
| **Firewall Policies** | `Firewall Policies:read`<br>`Firewall Policies:write` | Search and manage firewall policies, policy actions, precedence, and policy member relationships |
| **Sensor Update Policies** | `Sensor Update Policies:read`<br>`Sensor Update Policies:write` | Search and manage sensor update policies, builds, kernels, precedence, actions, and uninstall token reveal workflows |
| **Workflows** | `Workflow:read`<br>`Workflow:write` | Search and manage workflow definitions, executions, human inputs, and system-definition lifecycle actions |
| **IT Automation** | `IT Automation:read`<br>`IT Automation:write` | Execute high-impact task runs and live queries with execution status/result controls |
| **NGSIEM** | `NGSIEM:read`<br>`NGSIEM:write` | Full NGSIEM coverage for search jobs, dashboards, lookup files, parsers, and saved queries |
| **Intel** | `Actors (Falcon Intelligence):read`<br>`Indicators (Falcon Intelligence):read`<br>`Reports (Falcon Intelligence):read` | Research threat actors, IOCs, and intelligence reports |
| **IOC** | `IOC Management:read`<br>`IOC Management:write` | Search, create, and remove custom IOCs using IOC Service Collection endpoints |
| **IOA Exclusions** | `IOA Exclusions:read`<br>`IOA Exclusions:write` | Search, create, update, and delete IOA exclusions |
| **Firewall Management** | `Firewall Management:read`<br>`Firewall Management:write` | Full firewall management coverage for rules, rule groups, policy containers, events, fields, platforms, and network locations |
| **Quarantine** | `Quarantined Files:read`<br>`Quarantined Files:write` | Search and aggregate quarantined files, estimate update impact, and apply quarantine actions |
| **Real Time Response** | `Real Time Response:read`<br>`Real Time Response Admin:write`<br>`Real Time Response Audit:read` | Unified RTR module covering session workflows, admin command/script operations, and audit session search |
| **Scheduled Reports** | `Scheduled Reports:read` | Get details about scheduled reports and searches, run reports on demand, and download report files |
| **Sensor Download** | `Sensor Download:read` | Query installer catalogs, retrieve metadata and CCID values, and download installer binaries |
| **Sensor Usage** | `Sensor Usage:read` | Access and analyze sensor usage data |
| **Serverless** | `Falcon Container Image:read` | Search for vulnerabilities in serverless functions across cloud service providers |
| **Spotlight** | `Vulnerabilities:read` | Manage and analyze vulnerability data and security assessments |
| **Zero Trust Assessment** | `Zero Trust Assessment:read` | Search host Zero Trust scores and retrieve tenant-wide audit metrics |

## Available Modules, Tools & Resources

> [!IMPORTANT]
> ⚠️ **Important Note on FQL Guide Resources**: Several modules include FQL (Falcon Query Language) guide resources that provide comprehensive query documentation and examples. While these resources are designed to assist AI assistants and users with query construction, **FQL has nuanced syntax requirements and field-specific behaviors** that may not be immediately apparent. AI-generated FQL filters should be **tested and validated** before use in production environments. We recommend starting with simple queries and gradually building complexity while verifying results in a test environment first.

**About Tools & Resources**: This server provides both tools (actions you can perform) and resources (documentation and context). Tools execute operations like searching for detections or analyzing threats, while resources provide comprehensive documentation like FQL query guides that AI assistants can reference for context without requiring tool calls.

### Cloud Security Module

**API Scopes Required**:

- `Falcon Container Image:read`

Provides tools for accessing and analyzing CrowdStrike Cloud Security resources:

- `falcon_search_kubernetes_containers`: Search for containers from CrowdStrike Kubernetes & Containers inventory
- `falcon_count_kubernetes_containers`: Count for containers by filter criteria from CrowdStrike Kubernetes & Containers inventory
- `falcon_search_images_vulnerabilities`: Search for images vulnerabilities from CrowdStrike Image Assessments

**Resources**:

- `falcon://cloud/kubernetes-containers/fql-guide`: Comprehensive FQL documentation and examples for kubernetes containers searches
- `falcon://cloud/images-vulnerabilities/fql-guide`: Comprehensive FQL documentation and examples for images vulnerabilities searches

**Use Cases**: Manage kubernetes containers inventory, container images vulnerabilities analysis

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

### Core Functionality (Built into Server)

**API Scopes**: _None required beyond basic API access_

The server provides core tools for interacting with the Falcon API:

- `falcon_check_connectivity`: Check connectivity to the Falcon API
- `falcon_list_enabled_modules`: Lists enabled modules in the falcon-mcp server
    > These modules are determined by the `--modules` [flag](#module-configuration) when starting the server. If no modules are specified, all available modules are enabled.
- `falcon_list_modules`: Lists all available modules in the falcon-mcp server

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

**API Scopes Required**: `Alerts:read`

Provides tools for accessing and analyzing CrowdStrike Falcon detections:

- `falcon_search_detections`: Find and analyze detections to understand malicious activity in your environment
- `falcon_get_detection_details`: Get comprehensive detection details for specific detection IDs to understand security threats

**Resources**:

- `falcon://detections/search/fql-guide`: Comprehensive FQL documentation and examples for detection searches

**Use Cases**: Threat hunting, security analysis, incident response, malware investigation

### Discover Module

**API Scopes Required**: `Assets:read`

Provides tools for accessing and managing CrowdStrike Falcon Discover applications and unmanaged assets:

- `falcon_search_applications`: Search for applications in your CrowdStrike environment
- `falcon_search_unmanaged_assets`: Search for unmanaged assets (systems without Falcon sensor installed) that have been discovered by managed systems

**Resources**:

- `falcon://discover/applications/fql-guide`: Comprehensive FQL documentation and examples for application searches
- `falcon://discover/hosts/fql-guide`: Comprehensive FQL documentation and examples for unmanaged assets searches

**Use Cases**: Application inventory management, software asset management, license compliance, vulnerability assessment, unmanaged asset discovery, security gap analysis

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

Provides tools for Falcon User Management workflows:

- `falcon_search_users`: Search users and return full user details (two-step query + entity retrieval)
- `falcon_get_user_details`: Retrieve full user records by UUID
- `falcon_search_user_roles`: Search available roles and return full role details
- `falcon_get_user_role_grants`: Review role grants for a specific user
- `falcon_create_user`: Create users (`confirm_execution=true` required)
- `falcon_delete_user`: Delete users (`confirm_execution=true` required)
- `falcon_grant_user_roles`: Grant roles to a user (`confirm_execution=true` required)
- `falcon_revoke_user_roles`: Revoke roles from a user (`confirm_execution=true` required)

**Resources**:

- `falcon://user-management/users/fql-guide`: FQL documentation and examples for user searches
- `falcon://user-management/user-role-grants/fql-guide`: FQL documentation and examples for grant queries
- `falcon://user-management/safety-guide`: Safety and operational guidance for IAM write actions

**Use Cases**: IAM automation with guardrails, user access review, role assignment governance, least-privilege enforcement

### Incidents Module

**API Scopes Required**: `Incidents:read`

Provides tools for accessing and analyzing CrowdStrike Falcon incidents:

- `falcon_show_crowd_score`: View calculated CrowdScores and security posture metrics for your environment
- `falcon_search_incidents`: Find and analyze security incidents to understand coordinated activity in your environment
- `falcon_get_incident_details`: Get comprehensive incident details to understand attack patterns and coordinated activities
- `falcon_search_behaviors`: Find and analyze behaviors to understand suspicious activity in your environment
- `falcon_get_behavior_details`: Get detailed behavior information to understand attack techniques and tactics

**Resources**:

- `falcon://incidents/crowd-score/fql-guide`: Comprehensive FQL documentation for CrowdScore queries
- `falcon://incidents/search/fql-guide`: Comprehensive FQL documentation and examples for incident searches
- `falcon://incidents/behaviors/fql-guide`: Comprehensive FQL documentation and examples for behavior searches

**Use Cases**: Incident management, threat assessment, attack pattern analysis, security posture monitoring

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

Provides Phase 3 IT Automation execution tools:

- `falcon_search_it_automation_task_executions`: Search task execution records
- `falcon_get_it_automation_task_executions`: Retrieve task execution records by ID
- `falcon_get_it_automation_task_execution_host_status`: Retrieve host-level execution status
- `falcon_start_it_automation_task_execution`: Start execution of an existing IT Automation task (`confirm_execution=true` required)
- `falcon_run_it_automation_live_query`: Run live query execution (`confirm_execution=true` required)
- `falcon_cancel_it_automation_task_execution`: Cancel an active task execution (`confirm_execution=true` required)
- `falcon_rerun_it_automation_task_execution`: Rerun a task execution (`confirm_execution=true` required)
- `falcon_start_it_automation_execution_results_search`: Start async execution results search
- `falcon_get_it_automation_execution_results_search_status`: Poll async search status
- `falcon_get_it_automation_execution_results`: Retrieve execution results from search jobs

**Resources**:

- `falcon://it-automation/task-executions/fql-guide`: FQL documentation and examples for task execution searches
- `falcon://it-automation/phase3/safety-guide`: Safety and execution guidance for high-impact tools

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

Provides tools for accessing and analyzing CrowdStrike Intelligence:

- `falcon_search_actors`: Research threat actors and adversary groups tracked by CrowdStrike intelligence
- `falcon_search_indicators`: Search for threat indicators and indicators of compromise (IOCs) from CrowdStrike intelligence
- `falcon_search_reports`: Access CrowdStrike intelligence publications and threat reports
- `falcon_get_mitre_report`: Generate MITRE ATT&CK reports for threat actors, providing detailed tactics, techniques, and procedures (TTPs) in JSON or CSV format

**Resources**:

- `falcon://intel/actors/fql-guide`: Comprehensive FQL documentation and examples for threat actor searches
- `falcon://intel/indicators/fql-guide`: Comprehensive FQL documentation and examples for indicator searches
- `falcon://intel/reports/fql-guide`: Comprehensive FQL documentation and examples for intelligence report searches

**Use Cases**: Threat intelligence research, adversary tracking, IOC analysis, threat landscape assessment, MITRE ATT&CK framework analysis

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

### Real Time Response Module

**API Scopes Required**:

- `Real Time Response:read`
- `Real Time Response Admin:write`
- `Real Time Response Audit:read`

Provides unified tools for RTR core, RTR admin, and RTR audit workflows:

- `falcon_search_rtr_sessions`: Search RTR sessions using FQL and return full session details
- `falcon_init_rtr_session`: Initialize a single-host RTR session
- `falcon_execute_rtr_command`: Execute an RTR read-only command on a host session
- `falcon_check_rtr_command_status`: Check status for an RTR command request
- `falcon_search_rtr_admin_scripts`: Search RTR admin scripts and return full script details
- `falcon_search_rtr_admin_put_files`: Search RTR admin put-files and return full put-file details
- `falcon_execute_rtr_admin_command`: Execute an RTR admin command on a host session
- `falcon_execute_rtr_admin_batch_command`: Execute an RTR admin command across a batch session
- `falcon_check_rtr_admin_command_status`: Check status for an RTR admin command request
- `falcon_delete_rtr_session`: Delete an RTR session by session ID
- `falcon_delete_rtr_queued_session`: Delete a queued RTR session by session and request ID
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

- `falcon_search_scheduled_reports`: Search for scheduled reports and searches in your CrowdStrike environment
- `falcon_launch_scheduled_report`: Launch a scheduled report on demand outside of its recurring schedule
- `falcon_search_report_executions`: Search for report executions to track status and results
- `falcon_download_report_execution`: Download generated report files

**Resources**:

- `falcon://scheduled-reports/search/fql-guide`: Comprehensive FQL documentation for searching scheduled report entities
- `falcon://scheduled-reports/executions/search/fql-guide`: Comprehensive FQL documentation for searching report executions

**Use Cases**: Automated report management, report execution monitoring, scheduled search analysis, report download automation

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
