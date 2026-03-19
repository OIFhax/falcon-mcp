"""
Contains Downloads resources.
"""

from falcon_mcp.common.utils import generate_md_table

DOWNLOADS_FQL_FILTERS = [
    ("Field", "Type", "Description"),
    ("arch", "String", "System architecture for the downloadable artifact."),
    ("category", "String", "Artifact category."),
    ("file_name", "String", "Downloadable file name."),
    ("file_version", "String", "Artifact version string."),
    ("os", "String", "Operating system family."),
]

DOWNLOADS_FQL_SORT_FIELDS = [
    ("Field", "Description"),
    ("arch", "Sort by architecture"),
    ("category", "Sort by category"),
    ("file_name", "Sort by file name"),
    ("file_version", "Sort by version"),
    ("os", "Sort by operating system"),
]

DOWNLOADS_FQL_DOCUMENTATION = f"""
# Downloads FQL Guide

Use this guide for:

- `falcon_fetch_download_file_info`
- `falcon_fetch_download_file_info_v2`

## Filter Fields

{generate_md_table(DOWNLOADS_FQL_FILTERS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(DOWNLOADS_FQL_SORT_FIELDS)}

## Examples

- Windows sensor downloads:
  - `filter="category:'sensor'+os:'Windows'"`
- Linux downloads for a specific architecture:
  - `filter="os:'Linux'+arch:'x86_64'"`
- Newest versions first:
  - `sort="file_version.desc"`

## Notes

- The v1 combined endpoint supports `filter` and `sort`.
- The v2 combined endpoint also supports `limit` and `offset`.
- Empty results are valid when no downloads match your tenant and filters.
""".strip()

DOWNLOADS_USAGE_GUIDE = """# Downloads Usage Guide

Use this guide with:

- `falcon_enumerate_download_files`
- `falcon_get_download_file_url`

## Deprecated endpoints

- `falcon_enumerate_download_files` maps to the legacy `EnumerateFile` endpoint.
- `falcon_get_download_file_url` maps to the legacy `DownloadFile` endpoint.
- Prefer the combined `falcon_fetch_download_file_info` tools when possible.

## enumerate tool

`falcon_enumerate_download_files` accepts individual filter fields instead of FQL:

- `file_name`
- `file_version`
- `platform`
- `os`
- `arch`
- `category`

## direct URL tool

`falcon_get_download_file_url` requires:

- `file_name`
- `file_version`

It requests a pre-signed download URL for a single artifact.

## Important behavior

- These endpoints may legitimately return zero results for a tenant.
- A direct URL request can return `404 unable to fetch the download url` when the file name and version do not exist for the tenant.
"""
