<!-- meta:title Intel -->
<!-- meta:description Provides full FalconPy Intel service collection coverage for actors, indicators, reports, rules, malware, MITRE ATT&CK, and vulnerability intelligence data -->
<!-- meta:section modules -->
<!-- meta:link-base /falcon-mcp/ -->
<!-- frontmatter:sidebar order:10 -->

Provides full FalconPy Intel service collection coverage for actors, indicators, reports, rules, malware, MITRE ATT&CK, and vulnerability intelligence data

## API Scopes

- `Actors (Falcon Intelligence):read`
- `Indicators (Falcon Intelligence):read`
- `Reports (Falcon Intelligence):read`

## Tools

### `falcon_search_actors`

**Required scopes:** `Actors (Falcon Intelligence):read`

Query actor entities (QueryIntelActorEntities).

**Example prompts:**

- "Find threat actors targeting financial services"
- "Search for BEAR adversary groups"

### `falcon_query_actor_ids`

**Required scopes:** `Actors (Falcon Intelligence):read`

Query actor IDs (QueryIntelActorIds).

### `falcon_get_actor_details`

**Required scopes:** `Actors (Falcon Intelligence):read`

Get actor entities by ID (GetIntelActorEntities).

### `falcon_search_indicators`

**Required scopes:** `Indicators (Falcon Intelligence):read`

Query indicator entities (QueryIntelIndicatorEntities).

**Example prompts:**

- "Find intelligence IOCs of type domain published this year"

### `falcon_query_indicator_ids`

**Required scopes:** `Indicators (Falcon Intelligence):read`

Query indicator IDs (QueryIntelIndicatorIds).

### `falcon_get_indicator_details`

**Required scopes:** `Indicators (Falcon Intelligence):read`

Get indicator entities by ID (GetIntelIndicatorEntities).

### `falcon_search_reports`

**Required scopes:** `Reports (Falcon Intelligence):read`

Query report entities (QueryIntelReportEntities).

**Example prompts:**

- "Find intelligence reports published in the last 30 days"

### `falcon_query_report_ids`

**Required scopes:** `Reports (Falcon Intelligence):read`

Query report IDs (QueryIntelReportIds).

### `falcon_get_report_details`

**Required scopes:** `Reports (Falcon Intelligence):read`

Get report entities by ID (GetIntelReportEntities).

### `falcon_download_report_pdf`

**Required scopes:** `Reports (Falcon Intelligence):read`

Download report PDF metadata (GetIntelReportPDF).

### `falcon_query_rule_ids`

**Required scopes:** `Reports (Falcon Intelligence):read`

Query rule IDs (QueryIntelRuleIds).

### `falcon_get_rule_details`

**Required scopes:** `Reports (Falcon Intelligence):read`

Get rule entities by ID (GetIntelRuleEntities).

### `falcon_download_rule_file`

**Required scopes:** `Reports (Falcon Intelligence):read`

Download rule archive metadata (GetIntelRuleFile).

### `falcon_download_latest_rule_file`

**Required scopes:** `Reports (Falcon Intelligence):read`

Download latest rule archive metadata (GetLatestIntelRuleFile).

### `falcon_query_malware_ids`

**Required scopes:** `Reports (Falcon Intelligence):read`

Query malware family IDs/names (QueryMalware).

### `falcon_search_malware`

**Required scopes:** `Reports (Falcon Intelligence):read`

Query malware entities (QueryMalwareEntities).

### `falcon_get_malware_details`

**Required scopes:** `Reports (Falcon Intelligence):read`

Get malware entities by ID (GetMalwareEntities).

### `falcon_get_malware_mitre_report`

**Required scopes:** `Reports (Falcon Intelligence):read`

Get malware MITRE ATT&CK report (GetMalwareMitreReport).

### `falcon_query_mitre_attacks`

**Required scopes:** `Actors (Falcon Intelligence):read`

Query MITRE tactics/techniques by actor (QueryMitreAttacks).

### `falcon_query_mitre_attacks_for_malware`

**Required scopes:** `Reports (Falcon Intelligence):read`

Query MITRE tactics/techniques by malware (QueryMitreAttacksForMalware).

### `falcon_get_mitre_attack_details`

**Required scopes:** `Actors (Falcon Intelligence):read`

Retrieve report and observable detail by MITRE attack IDs (PostMitreAttacks).

### `falcon_get_mitre_report`

**Required scopes:** `Actors (Falcon Intelligence):read`

Generate MITRE ATT&CK report for a threat actor (GetMitreReport).

**Example prompts:**

- "Generate MITRE ATT&CK report for FANCY BEAR"

### `falcon_query_intel_vulnerability_ids`

**Required scopes:** `Indicators (Falcon Intelligence):read`

Query vulnerability IDs (QueryVulnerabilities).

### `falcon_get_intel_vulnerability_details`

**Required scopes:** `Indicators (Falcon Intelligence):read`

Get vulnerability entities by ID (GetVulnerabilities).

## Resources

- **`falcon://intel/actors/fql-guide`**: Contains the guide for the `filter` parameter of actor tools.
- **`falcon://intel/indicators/fql-guide`**: Contains the guide for the `filter` parameter of indicator tools.
- **`falcon://intel/reports/fql-guide`**: Contains the guide for the `filter` parameter of report tools.
