"""
Quarantine module for Falcon MCP Server.

This module provides tools for searching quarantined files, aggregating
quarantine data, reviewing action impact counts, and applying quarantine
update actions.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.quarantine import (
    QUARANTINE_AGGREGATION_GUIDE,
    QUARANTINE_SAFETY_GUIDE,
    SEARCH_QUARANTINE_FILES_FQL_DOCUMENTATION,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


class QuarantineModule(BaseModule):
    """Module for Quarantine operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_quarantine_files,
            name="search_quarantine_files",
        )
        self._add_tool(
            server=server,
            method=self.get_quarantine_file_details,
            name="get_quarantine_file_details",
        )
        self._add_tool(
            server=server,
            method=self.aggregate_quarantine_files,
            name="aggregate_quarantine_files",
        )
        self._add_tool(
            server=server,
            method=self.get_quarantine_action_update_count,
            name="get_quarantine_action_update_count",
        )
        self._add_tool(
            server=server,
            method=self.update_quarantine_files_by_ids,
            name="update_quarantine_files_by_ids",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_quarantine_files_by_query,
            name="update_quarantine_files_by_query",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_quarantine_files_fql_resource = TextResource(
            uri=AnyUrl("falcon://quarantine/files/fql-guide"),
            name="falcon_search_quarantine_files_fql_guide",
            description="Contains the guide for the `filter` parameter of quarantine search and action count tools.",
            text=SEARCH_QUARANTINE_FILES_FQL_DOCUMENTATION,
        )

        quarantine_aggregation_guide_resource = TextResource(
            uri=AnyUrl("falcon://quarantine/files/aggregation-guide"),
            name="falcon_quarantine_aggregation_guide",
            description="Guidance and example body for `falcon_aggregate_quarantine_files`.",
            text=QUARANTINE_AGGREGATION_GUIDE,
        )

        quarantine_safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://quarantine/files/safety-guide"),
            name="falcon_quarantine_safety_guide",
            description="Safety and operational guidance for quarantine update tools.",
            text=QUARANTINE_SAFETY_GUIDE,
        )

        self._add_resource(server, search_quarantine_files_fql_resource)
        self._add_resource(server, quarantine_aggregation_guide_resource)
        self._add_resource(server, quarantine_safety_guide_resource)

    def search_quarantine_files(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for quarantined file search. IMPORTANT: use the `falcon://quarantine/files/fql-guide` resource when building this filter parameter.",
        ),
        q: str | None = Field(
            default=None,
            description="Phrase-prefix text query across searchable quarantine fields.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of quarantine file IDs to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort quarantined files. Examples: `date_updated.desc`, `hostname|asc`.",
            examples={"date_updated.desc", "hostname|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search quarantined files and return full metadata records."""
        quarantine_file_ids = self._base_search_api_call(
            operation="QueryQuarantineFiles",
            search_params={
                "filter": filter,
                "q": q,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search quarantined files",
        )

        if self._is_error(quarantine_file_ids):
            return self._format_fql_error_response(
                [quarantine_file_ids],
                filter or q,
                SEARCH_QUARANTINE_FILES_FQL_DOCUMENTATION,
            )

        if not quarantine_file_ids:
            if filter or q:
                return self._format_fql_error_response(
                    [],
                    filter or q,
                    SEARCH_QUARANTINE_FILES_FQL_DOCUMENTATION,
                )
            return []

        details = self._base_query_api_call(
            operation="GetQuarantineFiles",
            body_params={"ids": quarantine_file_ids},
            error_message="Failed to retrieve quarantined file details",
            default_result=[],
        )

        if self._is_error(details):
            return [details]

        return details

    def get_quarantine_file_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Quarantine file IDs to retrieve metadata for.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve quarantined file metadata by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve quarantined file details.",
                    operation="GetQuarantineFiles",
                )
            ]

        result = self._base_query_api_call(
            operation="GetQuarantineFiles",
            body_params={"ids": ids},
            error_message="Failed to retrieve quarantined file details",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def aggregate_quarantine_files(
        self,
        body: list[dict[str, Any]] | dict[str, Any] | None = Field(
            default=None,
            description="Aggregation specification body for `GetAggregateFiles`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate queries for quarantined file data."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for quarantine aggregation.",
                    operation="GetAggregateFiles",
                )
            ]

        command_response = self.client.command("GetAggregateFiles", body=body)
        result = handle_api_response(
            command_response,
            operation="GetAggregateFiles",
            error_message="Failed to aggregate quarantined files",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_quarantine_action_update_count(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter used to estimate impacted quarantined files by action. IMPORTANT: use the `falcon://quarantine/files/fql-guide` resource when building this filter parameter.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Return count of potentially affected quarantined files for each action."""
        if not filter:
            return [
                _format_error_response(
                    "`filter` is required to estimate impacted quarantined files.",
                    operation="ActionUpdateCount",
                )
            ]

        result = self._base_search_api_call(
            operation="ActionUpdateCount",
            search_params={"filter": filter},
            error_message="Failed to retrieve quarantine action update count",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_QUARANTINE_FILES_FQL_DOCUMENTATION,
            )

        return result

    def update_quarantine_files_by_ids(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        action: Literal["release", "unrelease", "delete"] | None = Field(
            default=None,
            description="Action to apply to targeted quarantine IDs.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Quarantine file IDs to update.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional audit comment for the action.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full request body override for `UpdateQuarantinedDetectsByIds`.",
        ),
    ) -> list[dict[str, Any]]:
        """Apply release / unrelease / delete action to quarantine files by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="UpdateQuarantinedDetectsByIds",
                )
            ]

        request_body = body
        if request_body is None:
            if not action:
                return [
                    _format_error_response(
                        "`action` is required when `body` is not provided.",
                        operation="UpdateQuarantinedDetectsByIds",
                    )
                ]
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="UpdateQuarantinedDetectsByIds",
                    )
                ]
            request_body = {"action": action, "ids": ids}
            if comment:
                request_body["comment"] = comment

        prepared_body = prepare_api_parameters(request_body)
        command_response = self.client.command(
            "UpdateQuarantinedDetectsByIds",
            body=prepared_body,
        )
        result = handle_api_response(
            command_response,
            operation="UpdateQuarantinedDetectsByIds",
            error_message="Failed to update quarantined files by IDs",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_quarantine_files_by_query(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        action: Literal["release", "unrelease", "delete"] | None = Field(
            default=None,
            description="Action to apply to matched quarantined files.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter used to target quarantine files for update.",
        ),
        q: str | None = Field(
            default=None,
            description="Phrase-prefix text query used to target quarantine files for update.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional audit comment for the action.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full request body override for `UpdateQfByQuery`.",
        ),
    ) -> list[dict[str, Any]]:
        """Apply release / unrelease / delete action to quarantine files by query."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="UpdateQfByQuery",
                )
            ]

        request_body = body
        if request_body is None:
            if not action:
                return [
                    _format_error_response(
                        "`action` is required when `body` is not provided.",
                        operation="UpdateQfByQuery",
                    )
                ]
            if not filter and not q:
                return [
                    _format_error_response(
                        "At least one selector (`filter` or `q`) is required when `body` is not provided.",
                        operation="UpdateQfByQuery",
                    )
                ]
            request_body = {"action": action}
            if filter:
                request_body["filter"] = filter
            if q:
                request_body["q"] = q
            if comment:
                request_body["comment"] = comment

        prepared_body = prepare_api_parameters(request_body)
        command_response = self.client.command(
            "UpdateQfByQuery",
            body=prepared_body,
        )
        result = handle_api_response(
            command_response,
            operation="UpdateQfByQuery",
            error_message="Failed to update quarantined files by query",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
