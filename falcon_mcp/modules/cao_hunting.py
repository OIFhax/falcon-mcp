"""
CAO Hunting module for Falcon MCP Server.

This module provides tools for searching and retrieving hunting guides and
intelligence queries via CrowdStrike CAO Hunting APIs.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.cao_hunting import (
    CAO_ARCHIVE_EXPORT_GUIDE,
    SEARCH_HUNTING_GUIDES_FQL_DOCUMENTATION,
    SEARCH_INTELLIGENCE_QUERIES_FQL_DOCUMENTATION,
)


class CAOHuntingModule(BaseModule):
    """Module for CAO Hunting operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_hunting_guides,
            name="search_hunting_guides",
        )
        self._add_tool(
            server=server,
            method=self.get_hunting_guide_details,
            name="get_hunting_guide_details",
        )
        self._add_tool(
            server=server,
            method=self.search_intelligence_queries,
            name="search_intelligence_queries",
        )
        self._add_tool(
            server=server,
            method=self.get_intelligence_query_details,
            name="get_intelligence_query_details",
        )
        self._add_tool(
            server=server,
            method=self.aggregate_hunting_guides,
            name="aggregate_hunting_guides",
        )
        self._add_tool(
            server=server,
            method=self.aggregate_intelligence_queries,
            name="aggregate_intelligence_queries",
        )
        self._add_tool(
            server=server,
            method=self.create_hunting_archive_export,
            name="create_hunting_archive_export",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_hunting_guides_fql_resource = TextResource(
            uri=AnyUrl("falcon://cao-hunting/guides/fql-guide"),
            name="falcon_search_hunting_guides_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_hunting_guides` tool.",
            text=SEARCH_HUNTING_GUIDES_FQL_DOCUMENTATION,
        )

        search_intelligence_queries_fql_resource = TextResource(
            uri=AnyUrl("falcon://cao-hunting/intelligence-queries/fql-guide"),
            name="falcon_search_intelligence_queries_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_intelligence_queries` tool.",
            text=SEARCH_INTELLIGENCE_QUERIES_FQL_DOCUMENTATION,
        )

        archive_export_guide_resource = TextResource(
            uri=AnyUrl("falcon://cao-hunting/archive-export/guide"),
            name="falcon_cao_hunting_archive_export_guide",
            description="Usage guidance for `falcon_create_hunting_archive_export`.",
            text=CAO_ARCHIVE_EXPORT_GUIDE,
        )

        self._add_resource(server, search_hunting_guides_fql_resource)
        self._add_resource(server, search_intelligence_queries_fql_resource)
        self._add_resource(server, archive_export_guide_resource)

    def search_hunting_guides(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for hunting guide search. IMPORTANT: use the `falcon://cao-hunting/guides/fql-guide` resource when building this filter parameter.",
        ),
        q: str | None = Field(
            default=None,
            description="Phrase-prefix text search over indexed guide fields.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=500,
            description="Maximum number of hunting guide IDs to return from search. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort hunting guides using FQL sort syntax.

                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
                Examples: 'updated_at.desc', 'name|asc'
            """).strip(),
            examples={"updated_at.desc", "name|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search hunting guides and return full guide details."""
        guide_ids = self._base_search_api_call(
            operation="SearchHuntingGuides",
            search_params={
                "filter": filter,
                "q": q,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search hunting guides",
        )

        if self._is_error(guide_ids):
            return self._format_fql_error_response(
                [guide_ids], filter, SEARCH_HUNTING_GUIDES_FQL_DOCUMENTATION
            )

        if not guide_ids:
            if filter or q:
                return self._format_fql_error_response(
                    [], filter or q, SEARCH_HUNTING_GUIDES_FQL_DOCUMENTATION
                )
            return []

        details = self._base_get_by_ids(
            operation="GetHuntingGuides",
            ids=guide_ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_hunting_guide_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Hunting guide IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve hunting guide details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve hunting guides.",
                    operation="GetHuntingGuides",
                )
            ]

        result = self._base_get_by_ids(
            operation="GetHuntingGuides",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def search_intelligence_queries(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for intelligence query search. IMPORTANT: use the `falcon://cao-hunting/intelligence-queries/fql-guide` resource when building this filter parameter.",
        ),
        q: str | None = Field(
            default=None,
            description="Phrase-prefix text search over indexed intelligence query fields.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=500,
            description="Maximum number of intelligence query IDs to return from search. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort intelligence queries using FQL sort syntax.

                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
                Examples: 'updated_at.desc', 'name|asc'
            """).strip(),
            examples={"updated_at.desc", "name|asc"},
        ),
        include_translated_content: list[str] | None = Field(
            default=None,
            description="Optional translated content to include in details (for example `['SPL']` or `['__all__']`).",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search intelligence queries and return full query details."""
        query_ids = self._base_search_api_call(
            operation="SearchIntelligenceQueries",
            search_params={
                "filter": filter,
                "q": q,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search intelligence queries",
        )

        if self._is_error(query_ids):
            return self._format_fql_error_response(
                [query_ids], filter, SEARCH_INTELLIGENCE_QUERIES_FQL_DOCUMENTATION
            )

        if not query_ids:
            if filter or q:
                return self._format_fql_error_response(
                    [], filter or q, SEARCH_INTELLIGENCE_QUERIES_FQL_DOCUMENTATION
                )
            return []

        details = self._base_get_by_ids(
            operation="GetIntelligenceQueries",
            ids=query_ids,
            id_key="ids",
            use_params=True,
            include_translated_content=include_translated_content,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_intelligence_query_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Intelligence query IDs to retrieve.",
        ),
        include_translated_content: list[str] | None = Field(
            default=None,
            description="Optional translated content to include (for example `['SPL']` or `['__all__']`).",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve intelligence query details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve intelligence query details.",
                    operation="GetIntelligenceQueries",
                )
            ]

        result = self._base_get_by_ids(
            operation="GetIntelligenceQueries",
            ids=ids,
            id_key="ids",
            use_params=True,
            include_translated_content=include_translated_content,
        )

        if self._is_error(result):
            return [result]

        return result

    def aggregate_hunting_guides(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Aggregation specification body for `AggregateHuntingGuides`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate analysis over hunting guides."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for hunting guide aggregation.",
                    operation="AggregateHuntingGuides",
                )
            ]

        command_response = self.client.command(
            "AggregateHuntingGuides",
            body=body,
        )
        result = handle_api_response(
            command_response,
            operation="AggregateHuntingGuides",
            error_message="Failed to aggregate hunting guides",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def aggregate_intelligence_queries(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Aggregation specification body for `AggregateIntelligenceQueries`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate analysis over intelligence queries."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for intelligence query aggregation.",
                    operation="AggregateIntelligenceQueries",
                )
            ]

        command_response = self.client.command(
            "AggregateIntelligenceQueries",
            body=body,
        )
        result = handle_api_response(
            command_response,
            operation="AggregateIntelligenceQueries",
            error_message="Failed to aggregate intelligence queries",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_hunting_archive_export(
        self,
        language: str | None = Field(
            default=None,
            description="Query language for archive export. Supported values include `cql`, `snort`, `suricata`, `yara`, `SPL`, `__all__`.",
        ),
        filter: str | None = Field(
            default=None,
            description="Optional FQL filter to limit exported intelligence queries.",
        ),
        archive_type: str = Field(
            default="zip",
            description="Archive format. Supported values: `zip`, `gzip`.",
        ),
    ) -> list[dict[str, Any]]:
        """Create an archive export request for intelligence queries."""
        if not language:
            return [
                _format_error_response(
                    "`language` is required to create a CAO Hunting archive export.",
                    operation="GetArchiveExport",
                )
            ]

        result = self._base_query_api_call(
            operation="GetArchiveExport",
            query_params={
                "language": language,
                "filter": filter,
                "archive_type": archive_type,
            },
            error_message="Failed to create hunting archive export",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

