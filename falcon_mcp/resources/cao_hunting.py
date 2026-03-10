"""
Contains CAO Hunting resources.
"""

from falcon_mcp.common.utils import generate_md_table

SEARCH_HUNTING_GUIDES_FQL_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Hunting guide identifier."),
    ("name", "String", "Hunting guide name/title."),
    ("author", "String", "Guide author metadata."),
    ("language", "String", "Primary query language."),
    ("tags", "String/List", "Guide tags or categories."),
    ("created_at", "Timestamp", "Guide creation timestamp."),
    ("updated_at", "Timestamp", "Guide update timestamp."),
]

SEARCH_HUNTING_GUIDES_SORT_FIELDS = [
    ("Field", "Description"),
    ("name", "Sort by guide name"),
    ("author", "Sort by author"),
    ("language", "Sort by language"),
    ("created_at", "Sort by creation timestamp"),
    ("updated_at", "Sort by update timestamp"),
]

SEARCH_INTELLIGENCE_QUERIES_FQL_FILTER_FIELDS = [
    ("Field", "Type", "Description"),
    ("id", "String", "Intelligence query identifier."),
    ("name", "String", "Query name/title."),
    ("language", "String", "Query language (for example cql, spl, yara)."),
    ("author", "String", "Query author metadata."),
    ("tags", "String/List", "Query tags / categories."),
    ("created_at", "Timestamp", "Query creation timestamp."),
    ("updated_at", "Timestamp", "Query update timestamp."),
]

SEARCH_INTELLIGENCE_QUERIES_SORT_FIELDS = [
    ("Field", "Description"),
    ("name", "Sort by query name"),
    ("language", "Sort by language"),
    ("author", "Sort by author"),
    ("created_at", "Sort by creation timestamp"),
    ("updated_at", "Sort by update timestamp"),
]

SEARCH_HUNTING_GUIDES_FQL_DOCUMENTATION = f"""
# CAO Hunting: Hunting Guides FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_hunting_guides`.
This tool uses `SearchHuntingGuides` + `GetHuntingGuides` two-step retrieval.

## Filter Fields

{generate_md_table(SEARCH_HUNTING_GUIDES_FQL_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_HUNTING_GUIDES_SORT_FIELDS)}

## Examples

- Search by language:
  - `filter="language:'cql'"`
- Search by tag:
  - `filter="tags:'ransomware'"`
- Most recently updated first:
  - `sort="updated_at.desc"`
"""

SEARCH_INTELLIGENCE_QUERIES_FQL_DOCUMENTATION = f"""
# CAO Hunting: Intelligence Queries FQL Guide

Use this guide to build the `filter` parameter for `falcon_search_intelligence_queries`.
This tool uses `SearchIntelligenceQueries` + `GetIntelligenceQueries` two-step retrieval.

## Filter Fields

{generate_md_table(SEARCH_INTELLIGENCE_QUERIES_FQL_FILTER_FIELDS)}

## Sort Fields

Use either `field.asc` / `field.desc` or `field|asc` / `field|desc`.

{generate_md_table(SEARCH_INTELLIGENCE_QUERIES_SORT_FIELDS)}

## Examples

- Search SPL queries:
  - `filter="language:'SPL'"`
- Search threat-hunting queries:
  - `filter="tags:'threat-hunting'"`
- Newest queries first:
  - `sort="updated_at.desc"`
"""

CAO_ARCHIVE_EXPORT_GUIDE = """
# CAO Hunting Archive Export Guide

`falcon_create_hunting_archive_export` creates an archive export from CAO intelligence query results.

## Key parameters

- `language` (required): one of `cql`, `snort`, `suricata`, `yara`, `SPL`, `__all__`
- `filter` (optional): FQL filter to limit exported query set
- `archive_type` (optional): `zip` (default) or `gzip`

## Usage notes

- Start with narrow filters before requesting large exports.
- Use `__all__` only when you need all available query-language variants.
- Archive export creation is asynchronous from a workflow perspective; capture response metadata for downstream retrieval.
"""

