"""
Contains MalQuery resources.
"""

MALQUERY_USAGE_GUIDE = """
# MalQuery Guide

MalQuery supports content-based search, YARA hunts, metadata lookup, and file retrieval.

## Workflow tips

- Use `falcon_get_malquery_quotas` first to understand tenant limits.
- Use `falcon_exact_search_malquery` or `falcon_fuzzy_search_malquery` to create request IDs.
- Use `falcon_get_malquery_request` to poll asynchronous request status.
- Use `falcon_schedule_malquery_samples_multidownload` before `falcon_get_malquery_samples_archive`.
- Binary downloads are not rendered inline by default.
"""

MALQUERY_SAFETY_GUIDE = """
# MalQuery Safety Guide

MalQuery write operations schedule searches and downloads against Falcon's malware corpus.

## Operational guardrails

- Require `confirm_execution=true` for search, hunt, and multi-download scheduling tools.
- Use precise patterns and narrow filters to avoid excessive searches.
- Prefer metadata lookup before downloading binaries when analysis goals permit.
"""
