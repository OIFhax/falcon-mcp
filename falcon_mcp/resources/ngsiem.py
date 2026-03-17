"""
Contains NGSIEM resources.
"""

NGSIEM_REPOSITORY_GUIDE = """
# NGSIEM Repository Guide

Use repository values supported by your tenant and operation.

Common repositories:

- `search-all`: broad event search repository
- `investigate_view`: endpoint-focused investigation view
- `third-party`: third-party source events
- `falcon_for_it_view`: Falcon for IT datasets
- `forensics_view`: Falcon Forensics triage data
- `parsers-repository`: parser and parser-template operations
"""

NGSIEM_SEARCH_GUIDE = """
# NGSIEM Search Guide

Use `falcon_search_ngsiem` for asynchronous CQL search and event retrieval.

## Time fields

- `start` and `end` must be ISO-8601 UTC timestamps (example: `2026-03-17T00:00:00Z`)
- Internally converted to epoch milliseconds for `StartSearchV1`

## Search workflow

1. `falcon_start_ngsiem_search` starts a search job and returns a `search_id`
2. `falcon_get_ngsiem_search_status` polls the job until `done=true`
3. `falcon_stop_ngsiem_search` stops long-running jobs
"""

NGSIEM_SAFETY_GUIDE = """
# NGSIEM Safety Guide

NGSIEM write operations can modify shared dashboards, parsers, lookup files, and saved queries.

## Operational guardrails

- Require `confirm_execution=true` for all write/delete operations.
- Use explicit IDs, filenames, and repository values.
- Validate parser and lookup changes in non-production repositories first.
- Keep backups/export copies of parser and saved query objects before updates/deletes.
"""
