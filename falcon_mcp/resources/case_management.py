"""
Contains Case Management resources.
"""

CASE_MANAGEMENT_USAGE_GUIDE = """
# Case Management Guide

Case Management tools expose the FalconPy operation IDs as MCP tools using the pattern
`falcon_case_management_<operation_id>`.

## Workflow tips

- Use query tools first, such as `falcon_case_management_queries_cases_get_v1` or `falcon_case_management_queries_templates_get_v1`.
- Use entity-get tools with explicit IDs in `parameters` or `body`, depending on the operation.
- File upload and template import tools expect `file_name` and `file_data_base64`.
- File download, bulk download, and template export tools return metadata by default and can return inline content with `include_binary_base64=true`.
"""

CASE_MANAGEMENT_SAFETY_GUIDE = """
# Case Management Safety Guide

Case Management write tools can mutate cases, tags, evidence, notification groups, SLAs, templates, and case files.

## Operational guardrails

- Require `confirm_execution=true` for all write, delete, upload, import, and RTR-retrieval operations.
- Query the target case, template, notification group, or file before mutation or deletion.
- Keep file uploads and template imports small, deliberate, and attributable.
- Treat `falcon_case_management_entities_retrieve_rtr_file_post_v1` as a controlled remote retrieval workflow.
"""
