"""
Contains API Integrations resources.
"""

API_INTEGRATIONS_FQL_GUIDE = """
# API Integrations FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_api_integration_plugin_configs`.

## Notes

- Plugin configuration search uses Falcon Query Language (FQL).
- Start with exact configuration identifiers or narrow plugin predicates when possible.
"""

API_INTEGRATIONS_SAFETY_GUIDE = """
# API Integrations Safety Guide

Execution tools invoke downstream plugin operations and may trigger external side effects.

## Operational guardrails

- Require `confirm_execution=true` for both execution tools.
- Search plugin configurations first to identify the correct `config_id`, plugin `id`, and `operation_id`.
- Prefer the non-proxy execution tool unless you specifically need direct request proxy semantics.
- Use minimal request bodies and validate plugin targets before execution.
"""
