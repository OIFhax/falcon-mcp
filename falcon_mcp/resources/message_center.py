"""
Contains Message Center resources.
"""

MESSAGE_CENTER_USAGE_GUIDE = """
# Message Center Guide

Message Center tools support case discovery, case activity, attachment workflows, and case creation.

## Workflow tips

- Start with `falcon_query_message_center_case_ids` to find case IDs.
- Use `falcon_get_message_center_cases` and `falcon_get_message_center_case_activities` to inspect details.
- Attachment downloads are binary and are not rendered inline by default.
"""

MESSAGE_CENTER_SAFETY_GUIDE = """
# Message Center Safety Guide

Message Center write tools create cases, append activities, and upload attachments.

## Operational guardrails

- Require `confirm_execution=true` for create, activity, and attachment write tools.
- Keep attachment uploads small and intentional.
- Query existing cases before creating or mutating a case.
"""
