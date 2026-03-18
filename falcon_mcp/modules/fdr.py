"""
Falcon Data Replicator (FDR) module for Falcon MCP Server.

This module provides tools for retrieving the combined FDR schema and
querying event and field schema entities.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.fdr import (
    SEARCH_FDR_EVENT_SCHEMA_FQL_DOCUMENTATION,
    SEARCH_FDR_FIELD_SCHEMA_FQL_DOCUMENTATION,
)


class FDRModule(BaseModule):
    """Module for Falcon Data Replicator schema operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.get_fdr_combined_schema,
            name="get_fdr_combined_schema",
        )
        self._add_tool(
            server=server,
            method=self.query_fdr_event_schema_ids,
            name="query_fdr_event_schema_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_fdr_event_schema_details,
            name="get_fdr_event_schema_details",
        )
        self._add_tool(
            server=server,
            method=self.search_fdr_event_schemas,
            name="search_fdr_event_schemas",
        )
        self._add_tool(
            server=server,
            method=self.query_fdr_field_schema_ids,
            name="query_fdr_field_schema_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_fdr_field_schema_details,
            name="get_fdr_field_schema_details",
        )
        self._add_tool(
            server=server,
            method=self.search_fdr_field_schemas,
            name="search_fdr_field_schemas",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        event_schema_guide = TextResource(
            uri=AnyUrl("falcon://fdr/events/fql-guide"),
            name="falcon_fdr_event_schema_fql_guide",
            description="FQL guidance for FDR event schema query tools.",
            text=SEARCH_FDR_EVENT_SCHEMA_FQL_DOCUMENTATION,
        )
        field_schema_guide = TextResource(
            uri=AnyUrl("falcon://fdr/fields/fql-guide"),
            name="falcon_fdr_field_schema_fql_guide",
            description="FQL guidance for FDR field schema query tools.",
            text=SEARCH_FDR_FIELD_SCHEMA_FQL_DOCUMENTATION,
        )

        self._add_resource(server, event_schema_guide)
        self._add_resource(server, field_schema_guide)

    def get_fdr_combined_schema(self) -> list[dict[str, Any]]:
        """Retrieve the combined FDR schema document."""
        operation = "fdrschema_combined_event_get"
        result = self._base_query_api_call(
            operation=operation,
            error_message="Failed to retrieve FDR combined schema",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def query_fdr_event_schema_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for FDR event schema IDs. IMPORTANT: use `falcon://fdr/events/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of IDs to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for event schema IDs.",
            examples={"name.asc", "version.desc"},
        ),
    ) -> list[str] | dict[str, Any]:
        """Query FDR event schema IDs."""
        operation = "fdrschema_queries_event_get"
        result = self._base_search_api_call(
            operation=operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query FDR event schema IDs",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_FDR_EVENT_SCHEMA_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_FDR_EVENT_SCHEMA_FQL_DOCUMENTATION,
            )

        return result

    def get_fdr_event_schema_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="FDR event schema IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve FDR event schema details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve FDR event schema details.",
                    operation="fdrschema_entities_event_get",
                )
            ]

        result = self._base_get_by_ids(
            operation="fdrschema_entities_event_get",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def search_fdr_event_schemas(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for FDR event schema search. IMPORTANT: use `falcon://fdr/events/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of schema IDs to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for event schema search.",
            examples={"name.asc", "version.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search FDR event schemas and return full schema details."""
        ids = self.query_fdr_event_schema_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(ids):
            return [ids]

        if isinstance(ids, dict):
            return ids

        if not ids:
            return []

        details = self.get_fdr_event_schema_details(ids=ids)
        if self._is_error(details):
            return [details]

        return details

    def query_fdr_field_schema_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for FDR field schema IDs. IMPORTANT: use `falcon://fdr/fields/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of IDs to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for field schema IDs.",
            examples={"name.asc", "type.desc"},
        ),
    ) -> list[str] | dict[str, Any]:
        """Query FDR field schema IDs."""
        operation = "fdrschema_queries_field_get"
        result = self._base_search_api_call(
            operation=operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query FDR field schema IDs",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_FDR_FIELD_SCHEMA_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_FDR_FIELD_SCHEMA_FQL_DOCUMENTATION,
            )

        return result

    def get_fdr_field_schema_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="FDR field schema IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve FDR field schema details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve FDR field schema details.",
                    operation="fdrschema_entities_field_get",
                )
            ]

        result = self._base_get_by_ids(
            operation="fdrschema_entities_field_get",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def search_fdr_field_schemas(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for FDR field schema search. IMPORTANT: use `falcon://fdr/fields/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of schema IDs to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for field schema search.",
            examples={"name.asc", "type.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search FDR field schemas and return full schema details."""
        ids = self.query_fdr_field_schema_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(ids):
            return [ids]

        if isinstance(ids, dict):
            return ids

        if not ids:
            return []

        details = self.get_fdr_field_schema_details(ids=ids)
        if self._is_error(details):
            return [details]

        return details
