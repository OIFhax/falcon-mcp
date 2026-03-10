"""
Contains Exposure Management resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_EXPOSURE_ASSETS_FQL_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("asset_id", "String", "External asset identifier."),
    ("asset_type", "String", "Asset category (for example `ip`, `dns_domain`)."),
    ("confidence", "String", "Confidence level assigned by Falcon."),
    ("connectivity_status", "String", "Connectivity status of the external asset."),
    ("criticality", "String", "Criticality classification."),
    ("criticality_description", "String", "Analyst-provided criticality context."),
    ("discovered_by", "String", "Source that discovered the asset."),
    ("internet_exposure", "Boolean/String", "Whether the asset is internet-exposed."),
    ("ip.ip_address", "String", "Observed external IP address."),
    ("dns_domain.fqdn", "String", "Observed domain/FQDN."),
    ("first_seen", "Timestamp", "First time the asset was observed."),
    ("last_seen", "Timestamp", "Most recent observation timestamp."),
    ("triage.status", "String", "Triage workflow status."),
    ("triage.assigned_to", "String", "Assigned user for triage."),
    ("subsidiaries.id", "String", "Subsidiary identifier associated to the asset."),
]

SEARCH_EXPOSURE_ASSETS_SORT_FIELDS = [
    ("Field", "Description"),
    ("asset_id", "Sort by asset identifier"),
    ("asset_type", "Sort by asset type"),
    ("criticality", "Sort by criticality"),
    ("first_seen", "Sort by first observation time"),
    ("last_seen", "Sort by last observation time"),
    ("triage.status", "Sort by triage status"),
]

SEARCH_EXPOSURE_ASSETS_FQL_DOCUMENTATION = f"""
# Exposure Management: External Assets FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_exposure_assets`.
This tool uses Exposure Management endpoint `query_external_assets_v2`.

## Filter Fields

{generate_md_table(SEARCH_EXPOSURE_ASSETS_FQL_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_EXPOSURE_ASSETS_SORT_FIELDS)}

## Examples

- Internet-facing IP assets:
  - `filter="asset_type:'ip'+internet_exposure:true"`
- Assets seen in the last week:
  - `filter="last_seen:>'now-7d'"`
- Prioritize by criticality and recency:
  - `sort="criticality|desc"` and `sort="last_seen.desc"`
"""

EXPOSURE_MANAGEMENT_SAFETY_GUIDE = """
# Exposure Management Safety Guide

Exposure Management write tools can alter your external asset inventory and triage data.

## Operational guardrails

- Use read-only discovery first (`search_exposure_assets`, `get_exposure_asset_details`).
- Require `confirm_execution=true` for all write operations.
- Use precise `asset_ids` and avoid broad bulk changes without a review step.
- Capture an audit description for destructive deletes.
- Re-query assets after every write operation to confirm expected state.

## Recommended change flow

1. Search target assets with a narrow FQL filter.
2. Fetch full details for final verification.
3. Execute one write action with `confirm_execution=true`.
4. Re-run search/details to validate outcomes.
"""

