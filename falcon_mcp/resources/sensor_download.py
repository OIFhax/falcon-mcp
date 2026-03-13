"""
Contains Sensor Download resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_SENSOR_INSTALLERS_FQL_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("platform", "String", "Installer platform (for example `windows`, `mac`, `linux`)."),
    ("version", "String", "Sensor version string."),
    ("release_date", "Timestamp", "Installer release date."),
    ("os", "String", "Operating system target."),
    ("name", "String", "Installer name."),
]

SEARCH_SENSOR_INSTALLERS_SORT_FIELDS = [
    ("Field", "Description"),
    ("version", "Sort by sensor version."),
    ("release_date", "Sort by release date."),
    ("platform", "Sort by platform."),
]

SEARCH_SENSOR_INSTALLERS_FQL_DOCUMENTATION = f"""
# Sensor Download: Installer Search FQL Guide

Use this guide to build `filter` values for:
- `falcon_search_sensor_installer_ids`
- `falcon_search_sensor_installer_ids_v2`
- `falcon_search_sensor_installers_combined`
- `falcon_search_sensor_installers_combined_v2`

## Filter Fields

{generate_md_table(SEARCH_SENSOR_INSTALLERS_FQL_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_SENSOR_INSTALLERS_SORT_FIELDS)}

## Examples

- Latest Windows installers:
  - `filter="platform:'windows'"` and `sort="release_date.desc"`
- Linux installers for a specific version:
  - `filter="platform:'linux'+version:'7.10*'"`
"""

SENSOR_INSTALLER_DOWNLOAD_GUIDE = """
# Sensor Installer Download Guide

The installer download tools return binary data from Falcon APIs.

## Response behavior

- Default (`include_binary_base64=false`): returns metadata only
  (`size_bytes`, `sha256`, operation, and installer id).
- Optional inline binary (`include_binary_base64=true`):
  returns base64 content only when payload size is below `max_inline_bytes`.

## Operational guidance

- Prefer metadata-only mode for normal workflows.
- Use inline binary mode only when the caller explicitly needs transportable bytes.
- Keep `max_inline_bytes` low to avoid oversized MCP responses.
"""
