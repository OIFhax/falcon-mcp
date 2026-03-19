"""
Contains Deployments resources.
"""

DEPLOYMENTS_FQL_GUIDE = """
# Deployments FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_deployment_releases`
- `falcon_search_release_notes`
- `falcon_query_release_note_ids`

## Notes

- Deployments and release-notes queries use Falcon Query Language (FQL).
- Use `limit`, `offset`, and `sort` for pagination and result ordering.
- Prefer searching first, then use the detail tools for exact IDs when you need a stable follow-up workflow.
"""
