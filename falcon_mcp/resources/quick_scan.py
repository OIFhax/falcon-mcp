"""
Contains Quick Scan resources.
"""

QUICK_SCAN_FQL_GUIDE = """
# Quick Scan FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_quick_scans`
- `falcon_query_quick_scan_ids`

## Notes

- Quick Scan search uses Falcon Query Language (FQL).
- Use `limit`, `offset`, and `sort` to page through submission history.
"""

QUICK_SCAN_SAFETY_GUIDE = """
# Quick Scan Safety Guide

Submitting hashes for scanning triggers backend analysis workflows.

## Operational guardrails

- Require `confirm_execution=true` for `falcon_scan_quick_samples`.
- Submit only hashes that were intentionally uploaded or prepared for scanning.
- Use query and detail tools first to understand existing scan state before submitting more samples.
"""
