"""
IOA Exclusions module for Falcon MCP Server.

This module provides tools for searching, creating, updating, and deleting
Falcon IOA exclusions.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.ioa_exclusions import SEARCH_IOA_EXCLUSIONS_FQL_DOCUMENTATION


class IOAExclusionsModule(BaseModule):
    """Module for IOA Exclusions operations via FalconPy."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_ioa_exclusions,
            name="search_ioa_exclusions",
        )

        self._add_tool(
            server=server,
            method=self.add_ioa_exclusion,
            name="add_ioa_exclusion",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.update_ioa_exclusion,
            name="update_ioa_exclusion",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

        self._add_tool(
            server=server,
            method=self.remove_ioa_exclusions,
            name="remove_ioa_exclusions",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_ioa_exclusions_fql_resource = TextResource(
            uri=AnyUrl("falcon://ioa-exclusions/search/fql-guide"),
            name="falcon_search_ioa_exclusions_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_ioa_exclusions` tool.",
            text=SEARCH_IOA_EXCLUSIONS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_ioa_exclusions_fql_resource)

    def search_ioa_exclusions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for IOA exclusion search. IMPORTANT: use the `falcon://ioa-exclusions/search/fql-guide` resource when building this filter parameter.",
            examples={"pattern_name:'Suspicious PowerShell*'", "created_by:'mcp'"},
        ),
        ifn_regex: str | None = Field(
            default=None,
            description="Image File Name regex expression used alongside `filter`.",
        ),
        cl_regex: str | None = Field(
            default=None,
            description="Command Line regex expression used alongside `filter`.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="Maximum number of exclusion IDs to return from search. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort IOA exclusions using FQL sort syntax.

                Supported fields include:
                applied_globally, created_by, created_on, last_modified,
                modified_by, name, pattern_id, pattern_name

                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
            """).strip(),
            examples={"last_modified.desc", "pattern_name|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search IOA exclusions and return full exclusion details."""
        exclusion_ids = self._base_search_api_call(
            operation="queryIOAExclusionsV1",
            search_params={
                "filter": filter,
                "ifn_regex": ifn_regex,
                "cl_regex": cl_regex,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search IOA exclusions",
        )

        if self._is_error(exclusion_ids):
            if filter:
                return self._format_fql_error_response(
                    [exclusion_ids], filter, SEARCH_IOA_EXCLUSIONS_FQL_DOCUMENTATION
                )
            return [exclusion_ids]

        if not exclusion_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_IOA_EXCLUSIONS_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="getIOAExclusionsV1",
            ids=exclusion_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def add_ioa_exclusion(
        self,
        name: str | None = Field(
            default=None,
            description="Exclusion name.",
        ),
        pattern_id: str | None = Field(
            default=None,
            description="Target IOA pattern ID.",
        ),
        pattern_name: str | None = Field(
            default=None,
            description="Target IOA pattern name.",
        ),
        ifn_regex: str | None = Field(
            default=None,
            description="Image File Name regex expression for the exclusion.",
        ),
        cl_regex: str | None = Field(
            default=None,
            description="Command Line regex expression for the exclusion.",
        ),
        groups: list[str] | None = Field(
            default=None,
            description="Host group IDs to scope the exclusion.",
        ),
        description: str | None = Field(
            default=None,
            description="Exclusion description text.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment for creation.",
        ),
        detection_json: str | None = Field(
            default=None,
            description="Optional JSON expression used by the underlying API.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Create an IOA exclusion."""
        request_body = body
        if request_body is None:
            request_body = {}
            optional_values = {
                "name": name,
                "pattern_id": pattern_id,
                "pattern_name": pattern_name,
                "ifn_regex": ifn_regex,
                "cl_regex": cl_regex,
                "groups": groups,
                "description": description,
                "comment": comment,
                "detection_json": detection_json,
            }
            for key, value_ in optional_values.items():
                if value_ is not None:
                    request_body[key] = value_

            if not request_body:
                return [
                    _format_error_response(
                        "Provide `body` or at least one exclusion field to create an IOA exclusion.",
                        operation="createIOAExclusionsV1",
                    )
                ]

        result = self._base_query_api_call(
            operation="createIOAExclusionsV1",
            body_params=request_body,
            error_message="Failed to create IOA exclusion",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_ioa_exclusion(
        self,
        id: str | None = Field(
            default=None,
            description="Exclusion ID to update. Required when `body` is not provided.",
        ),
        name: str | None = Field(
            default=None,
            description="Updated exclusion name.",
        ),
        pattern_id: str | None = Field(
            default=None,
            description="Updated IOA pattern ID.",
        ),
        pattern_name: str | None = Field(
            default=None,
            description="Updated IOA pattern name.",
        ),
        ifn_regex: str | None = Field(
            default=None,
            description="Updated Image File Name regex expression.",
        ),
        cl_regex: str | None = Field(
            default=None,
            description="Updated Command Line regex expression.",
        ),
        groups: list[str] | None = Field(
            default=None,
            description="Updated host group IDs scope.",
        ),
        description: str | None = Field(
            default=None,
            description="Updated exclusion description text.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment for the update.",
        ),
        detection_json: str | None = Field(
            default=None,
            description="Updated optional JSON expression used by the underlying API.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Update an existing IOA exclusion."""
        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided for IOA exclusion updates.",
                        operation="updateIOAExclusionsV1",
                    )
                ]

            request_body = {"id": id}
            optional_values = {
                "name": name,
                "pattern_id": pattern_id,
                "pattern_name": pattern_name,
                "ifn_regex": ifn_regex,
                "cl_regex": cl_regex,
                "groups": groups,
                "description": description,
                "comment": comment,
                "detection_json": detection_json,
            }
            for key, value_ in optional_values.items():
                if value_ is not None:
                    request_body[key] = value_

            if len(request_body) == 1:
                return [
                    _format_error_response(
                        "Provide at least one field to update alongside `id`.",
                        operation="updateIOAExclusionsV1",
                    )
                ]

        result = self._base_query_api_call(
            operation="updateIOAExclusionsV1",
            body_params=request_body,
            error_message="Failed to update IOA exclusion",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def remove_ioa_exclusions(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Exclusion IDs to delete.",
        ),
        comment: str | None = Field(
            default=None,
            description="Audit comment describing why exclusions are being removed.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete IOA exclusions by IDs."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required when deleting IOA exclusions.",
                    operation="deleteIOAExclusionsV1",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteIOAExclusionsV1",
            query_params={
                "ids": ids,
                "comment": comment,
            },
            error_message="Failed to delete IOA exclusions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
