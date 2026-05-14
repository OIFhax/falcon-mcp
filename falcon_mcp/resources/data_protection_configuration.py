"""
Contains Data Protection Configuration resources.
"""

from falcon_mcp.common.utils import generate_md_table

DATA_PROTECTION_RESOURCE_TYPES = [
    ("Resource type", "Purpose"),
    ("classification", "DLP classifications and rules."),
    ("content_pattern", "Custom data-pattern definitions."),
    ("cloud_application", "Cloud application catalog entries."),
    ("enterprise_account", "Enterprise SaaS/account scope entries."),
    ("file_type", "File-type reference entities."),
    ("sensitivity_label", "Sensitivity label entities."),
    ("local_application_group", "Local application group definitions."),
    ("local_application", "Local application definitions."),
    ("policy", "Data protection policies."),
    ("web_location", "Web location definitions."),
]

DATA_PROTECTION_FQL_FIELDS = [
    ("Field", "Type", "Notes"),
    ("name", "String", "Commonly available on policies, labels, applications, groups, and locations."),
    ("created_at", "Timestamp", "Available on several configuration query endpoints."),
    ("updated_at", "Timestamp", "Available on several configuration query endpoints."),
    ("is_deleted", "Boolean", "Available on application and group query endpoints."),
    ("category", "String", "Commonly used for content-pattern searches, such as `pii`."),
]

DATA_PROTECTION_CONFIGURATION_GUIDE = f"""
# Data Protection Configuration Guide

Use this guide when working with:

- Generic resource tools:
  - `falcon_query_data_protection_resources`
  - `falcon_get_data_protection_resources`
  - `falcon_create_data_protection_resource`
  - `falcon_update_data_protection_resource`
  - `falcon_delete_data_protection_resources`
- Explicit policy tools:
  - `falcon_query_data_protection_policy_ids`
  - `falcon_get_data_protection_policies`
  - `falcon_create_data_protection_policy`
  - `falcon_update_data_protection_policy`
  - `falcon_delete_data_protection_policies`
  - `falcon_set_data_protection_policy_precedence`
- Explicit classification, content-pattern, cloud-application, enterprise-account,
  file-type, sensitivity-label, local-application-group, local-application, and
  web-location tools.

## Resource Types

{generate_md_table(DATA_PROTECTION_RESOURCE_TYPES)}

## Common Query Filters

The Falcon Data Protection Configuration API exposes resource-specific FQL fields.
Start with broad `name` or timestamp filters and refine after inspecting returned IDs.

{generate_md_table(DATA_PROTECTION_FQL_FIELDS)}

## Examples

- Query Windows policies:
  - `resource_type="policy"`, `parameters={{"platform_name": "win"}}`, `sort="precedence.asc"`
- Query content patterns:
  - `resource_type="content_pattern"`, `filter="category:'pii'"`, `sort="created_at.desc"`
- Query custom web locations:
  - `resource_type="web_location"`, `parameters={{"type": "custom"}}`, `filter="name:'*sharepoint*'"`

## Notes

- Policy operations require a `platform_name` parameter, usually `win` or `mac`.
- Web-location queries can take a `type` parameter such as `predefined` or `custom`.
- Use read tools to validate IDs and current state before running write tools.
"""

DATA_PROTECTION_CONFIGURATION_SAFETY_GUIDE = """
# Data Protection Configuration Safety Guide

Data protection write operations can change DLP detection, content inspection,
network inspection, classification, and egress behavior.

## Operational guardrails

- Require `confirm_execution=true` for all create, update, delete, and precedence changes.
- Prefer query and get tools before making changes so the target IDs and scope are explicit.
- For policy changes, include `platform_name` and document the intended blast radius.
- For classification changes, validate content patterns, file types, labels, user scope,
  and response actions before enforcement.
- For content patterns, validate regular expressions outside production before rollout.
- Keep operator-facing audit notes with the exact tool name and authenticated user.
"""
