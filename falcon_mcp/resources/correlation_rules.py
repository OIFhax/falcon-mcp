"""
Contains Correlation Rules resources.
"""

CORRELATION_RULES_FQL_GUIDE = """
# Correlation Rules FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_correlation_rules_v1`
- `falcon_search_correlation_rules_v2`
- `falcon_query_correlation_rule_ids`
- `falcon_query_correlation_rule_version_ids`

## Notes

- Supported filters include `customer_id`, `user_id`, `user_uuid`, `status`, `name`, `created_on`, and `last_updated_on`.
- Use `q` for free-text matching across rule fields.
- Use `sort`, `limit`, and `offset` to page through rule inventories.
"""

CORRELATION_RULES_SAFETY_GUIDE = """
# Correlation Rules Safety Guide

Correlation rule write tools can change detections and downstream automation behavior.

## Operational guardrails

- Require `confirm_execution=true` for create, update, publish, import, export, and delete workflows.
- Prefer the read/search tools before modifying rules or versions.
- Keep exports and imports controlled and traceable.
"""
