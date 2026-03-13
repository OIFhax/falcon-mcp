"""
Contains Installation Tokens resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_INSTALLATION_TOKENS_FQL_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("status", "String", "Token status (for example `valid`, `revoked`)."),
    ("label", "String", "Token label."),
    ("type", "String", "Token type."),
    ("created_timestamp", "Timestamp", "Token creation timestamp."),
    ("expires_timestamp", "Timestamp", "Token expiration timestamp."),
    ("last_used_timestamp", "Timestamp", "Token last-use timestamp."),
]

SEARCH_INSTALLATION_TOKENS_SORT_FIELDS = [
    ("Field", "Description"),
    ("created_timestamp", "Sort by creation timestamp."),
    ("expires_timestamp", "Sort by expiration timestamp."),
    ("last_used_timestamp", "Sort by last use timestamp."),
    ("label", "Sort by token label."),
]

SEARCH_INSTALLATION_TOKEN_AUDIT_FQL_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("action", "String", "Audit action (for example `token_create`, `token_delete`)."),
    ("token_id", "String", "Target token ID."),
    ("uid", "String", "User ID for actor."),
    ("cid", "String", "Customer ID."),
    ("timestamp", "Timestamp", "Audit event timestamp."),
]

SEARCH_INSTALLATION_TOKENS_FQL_DOCUMENTATION = f"""
# Installation Tokens: Token Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_installation_tokens`.

## Filter Fields

{generate_md_table(SEARCH_INSTALLATION_TOKENS_FQL_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_INSTALLATION_TOKENS_SORT_FIELDS)}

## Examples

- Active valid tokens:
  - `filter="status:'valid'"`
- Tokens expiring in the next 30 days:
  - `filter="expires_timestamp:<'now+30d'"`
"""

SEARCH_INSTALLATION_TOKEN_AUDIT_FQL_DOCUMENTATION = f"""
# Installation Tokens: Audit Search FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_installation_token_audit_events`.

## Filter Fields

{generate_md_table(SEARCH_INSTALLATION_TOKEN_AUDIT_FQL_FILTER_FIELDS)}

## Examples

- Token creation events:
  - `filter="action:'token_create'"`
- Events for one token:
  - `filter="token_id:'<token-id>'"`
"""

INSTALLATION_TOKENS_SAFETY_GUIDE = """
# Installation Tokens Safety Guide

Token write operations can affect sensor deployment behavior.

## Operational guardrails

- Require `confirm_execution=true` for all write operations.
- Create tokens with explicit labels and expirations.
- Revoke/update tokens before deleting when possible.
- Keep write operations scoped to explicit token IDs.
- For customer settings changes, read settings first and apply minimal updates.
"""
