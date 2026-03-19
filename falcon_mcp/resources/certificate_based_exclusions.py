"""
Contains Certificate Based Exclusions resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("created_by", "String", "User or identifier that created the exclusion."),
    ("created_on", "Timestamp", "Exclusion creation timestamp."),
    ("modified_by", "String", "User or identifier that last modified the exclusion."),
    ("modified_on", "Timestamp", "Exclusion last modification timestamp."),
    ("name", "String", "Certificate-based exclusion name."),
]

SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_SORT_FIELDS = [
    ("Field", "Description"),
    ("created_by", "Sort by creator."),
    ("created_on", "Sort by creation timestamp."),
    ("modified_by", "Sort by modifier."),
    ("modified_on", "Sort by modification timestamp."),
    ("name", "Sort by exclusion name."),
]

SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_DOCUMENTATION = f"""
# Certificate Based Exclusions Search FQL Guide

Use this guide to build the `filter` parameter for:
- `falcon_search_certificate_based_exclusions`
- `falcon_query_certificate_based_exclusion_ids`

## Filter Fields

{generate_md_table(SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_FILTERS)}

## Sort Fields

Use field names accepted by the Falcon API, commonly combined with direction such as `created_on.desc`.

{generate_md_table(SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_SORT_FIELDS)}
"""

CERTIFICATE_BASED_EXCLUSIONS_CERT_GUIDE = """
# Certificate Based Exclusions Certificate Lookup Guide

Use `falcon_get_certificate_signing_info` to retrieve certificate signing information for a file SHA256.

## Required input

- `sha256`: SHA256 hash of the file to inspect

## Notes

- This tool is read-only and is useful for building or validating certificate-based exclusions.
"""

CERTIFICATE_BASED_EXCLUSIONS_SAFETY_GUIDE = """
# Certificate Based Exclusions Safety Guide

Certificate based exclusions can suppress protection broadly if a certificate is over-scoped.

## Operational guardrails

- Require `confirm_execution=true` for all write actions.
- Prefer certificate lookup and search tools before creating or updating exclusions.
- Keep exclusions as narrow as possible by using precise certificate metadata and host-group scope where appropriate.
- Document the business justification in `comment` for every create, update, or delete.
"""
