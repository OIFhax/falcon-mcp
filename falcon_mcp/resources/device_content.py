"""
Contains Device Content resources.
"""

DEVICE_CONTENT_FQL_DOCUMENTATION = """
# Device Content FQL Guide

Use this guide to build the `filter` parameter for:

- `falcon_search_device_content_states`
- `falcon_query_device_content_state_ids`

## Notes

- Device Content filters use Falcon Query Language (FQL).
- Start with narrow host- or state-focused predicates and add sort fields only when needed.
- Use `limit` and `offset` to page through large result sets.
"""
