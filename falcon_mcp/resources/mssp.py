"""
Contains MSSP (Flight Control) resources.
"""

MSSP_USAGE_GUIDE = """
# MSSP (Flight Control) Guide

This module exposes query, get, create, update, membership, and role management tools for Flight Control.

## Workflow tips

- Start with the query tools to discover child CIDs, CID groups, roles, user groups, and members.
- Use the get tools for exact identifier lookups after you have IDs from query results.
- Use the write tools only with deliberate payloads and explicit confirmation.
"""

MSSP_SAFETY_GUIDE = """
# MSSP (Flight Control) Safety Guide

Flight Control write tools change MSSP hierarchy groupings, roles, and user memberships.

## Operational guardrails

- Require `confirm_execution=true` for every write operation.
- Query current state before changing groups, roles, or memberships.
- Validate request bodies and IDs carefully before applying changes.
"""
