"""
Deployments module for Falcon MCP Server.

This module provides tools for Falcon release and release-note lookups.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.deployments import DEPLOYMENTS_FQL_GUIDE


class DeploymentsModule(BaseModule):
    """Module for Falcon Deployments operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_deployment_releases, name="search_deployment_releases")
        self._add_tool(server=server, method=self.get_deployment_details, name="get_deployment_details")
        self._add_tool(server=server, method=self.search_release_notes, name="search_release_notes")
        self._add_tool(server=server, method=self.query_release_note_ids, name="query_release_note_ids")
        self._add_tool(server=server, method=self.get_release_notes_v1, name="get_release_notes_v1")
        self._add_tool(server=server, method=self.get_release_notes_v2, name="get_release_notes_v2")

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://deployments/fql-guide"),
                name="falcon_deployments_fql_guide",
                description="FQL guidance for Falcon Deployments tools.",
                text=DEPLOYMENTS_FQL_GUIDE,
            ),
        )

    def search_deployment_releases(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for deployment release search. IMPORTANT: use `falcon://deployments/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000),
        offset: int = Field(default=0, ge=0),
        sort: str | None = Field(default=None),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search deployment releases and return combined details."""
        result = self._base_search_api_call(
            operation="CombinedReleasesV1Mixin0",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search deployment releases",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response([result], filter, DEPLOYMENTS_FQL_GUIDE)

        if not result and filter:
            return self._format_fql_error_response([], filter, DEPLOYMENTS_FQL_GUIDE)

        return result

    def get_deployment_details(
        self,
        ids: list[str] | None = Field(default=None, description="Deployment release IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Retrieve deployment details by release ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve deployment details.",
                    operation="GetDeploymentsExternalV1",
                )
            ]

        result = self._base_get_by_ids(
            operation="GetDeploymentsExternalV1",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def search_release_notes(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for release-note search. IMPORTANT: use `falcon://deployments/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000),
        offset: int = Field(default=0, ge=0),
        sort: str | None = Field(default=None),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search release notes and return combined details."""
        result = self._base_search_api_call(
            operation="CombinedReleaseNotesV1",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search release notes",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response([result], filter, DEPLOYMENTS_FQL_GUIDE)

        if not result and filter:
            return self._format_fql_error_response([], filter, DEPLOYMENTS_FQL_GUIDE)

        return result

    def query_release_note_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for release-note ID query. IMPORTANT: use `falcon://deployments/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000),
        offset: int = Field(default=0, ge=0),
        sort: str | None = Field(default=None),
    ) -> list[str] | dict[str, Any]:
        """Query release-note IDs."""
        result = self._base_search_api_call(
            operation="QueryReleaseNotesV1",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to query release note IDs",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response([result], filter, DEPLOYMENTS_FQL_GUIDE)

        if not result and filter:
            return self._format_fql_error_response([], filter, DEPLOYMENTS_FQL_GUIDE)

        return result

    def get_release_notes_v1(
        self,
        ids: list[str] | None = Field(default=None, description="Release note IDs to retrieve with v1."),
        body: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve release notes using the v1 detail operation."""
        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required to retrieve release notes.",
                        operation="GetEntityIDsByQueryPOST",
                    )
                ]
            request_body = {"ids": ids}

        result = self._base_query_api_call(
            operation="GetEntityIDsByQueryPOST",
            body_params=request_body,
            error_message="Failed to retrieve release notes (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_release_notes_v2(
        self,
        ids: list[str] | None = Field(default=None, description="Release note IDs to retrieve with v2."),
        body: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve release notes using the v2 detail operation."""
        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required to retrieve release notes.",
                        operation="GetEntityIDsByQueryPOSTV2",
                    )
                ]
            request_body = {"ids": ids}

        result = self._base_query_api_call(
            operation="GetEntityIDsByQueryPOSTV2",
            body_params=request_body,
            error_message="Failed to retrieve release notes (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
