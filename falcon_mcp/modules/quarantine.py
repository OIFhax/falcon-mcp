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
    SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)

VALID_RESTORE_ACTIONS = {"release", "unrelease"}


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
        self._add_tool(
            server=server, method=self.search_quarantined_files, name="search_quarantined_files"
        )
        self._add_tool(
            server=server, method=self.preview_quarantine_actions, name="preview_quarantine_actions"
        )
        self._add_tool(
            server=server,
            method=self.update_quarantined_files,
            name="update_quarantined_files",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self._add_tool(
            server=server,
            method=self.delete_quarantined_files,
            name="delete_quarantined_files",
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
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://quarantine/files/search/fql-guide"),
                name="falcon_search_quarantined_files_fql_guide",
                description="Contains the guide for upstream quarantine search and filter-based actions.",
                text=SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION,
            ),
        )

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
        file_ids, pagination = self._base_search_with_meta(
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

        if self._is_error(file_ids):
            return self._format_fql_error_response(
                [file_ids],
                filter or q,
                SEARCH_QUARANTINE_FILES_FQL_DOCUMENTATION,
            )

        if not file_ids:
            return self._build_pagination_envelope([], pagination, filter or q)

        details = self._base_query_api_call(
            operation="GetQuarantineFiles",
            body_params={"ids": file_ids},
            error_message="Failed to retrieve quarantined file details",
            default_result=[],
        )

        if self._is_error(details):
            return [details]

        # Restore the query-step sort order if the details endpoint reorders results.
        details = self._reorder_by_ids(file_ids, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter or q)

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

    def search_quarantined_files(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://quarantine/files/search/fql-guide` for syntax.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="Maximum number of quarantine file IDs to return. Max: 500.",
        ),
        # API spec declares offset as string type (unlike most other Falcon endpoints)
        offset: str | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort quarantined files using FQL syntax such as `date_updated|desc` or `hostname|asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search quarantined files and return full quarantine metadata.

        Use this to discover quarantine records by host, hash, user, or state.
        Consult falcon://quarantine/files/search/fql-guide before constructing
        filter expressions. Returns full quarantine details including hostname,
        sha256, paths, state, and associated alert and detection IDs.
        Responses include `pagination.total` (the total number of records matching the filter, or null when the API does not report a count) — use it to answer "how many" questions.
        """
        file_ids, pagination = self._base_search_with_meta(
            operation="QueryQuarantineFiles",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search quarantined files",
        )

        if self._is_error(file_ids):
            return self._format_fql_error_response(
                [file_ids], filter, SEARCH_QUARANTINED_FILES_FQL_DOCUMENTATION
            )

        if not file_ids:
            return self._build_pagination_envelope([], pagination, filter)

        details = self._base_get_by_ids(
            operation="GetQuarantineFiles",
            ids=file_ids,
        )

        if self._is_error(details):
            return [details]

        # Restore the query-step sort order if the details endpoint reorders results.
        details = self._reorder_by_ids(file_ids, details, id_field="id")
        return self._build_pagination_envelope(details, pagination, filter)

    def preview_quarantine_actions(
        self,
        filter: str = Field(
            description="FQL filter expression. See `falcon://quarantine/files/search/fql-guide` for syntax.",
        ),
    ) -> list[dict[str, Any]]:
        """Estimate how many quarantine records each action would affect for a given filter.

        Use this read-only tool before calling a mutating quarantine action to
        understand the blast radius of a release, unrelease, or delete request.
        Consult falcon://quarantine/files/search/fql-guide before constructing
        filter expressions. Returns a list of action counts keyed by action name.
        """
        if not filter:
            return [
                _format_error_response(
                    "Provide a non-empty FQL `filter` for preview_quarantine_actions."
                )
            ]

        result = self._base_query_api_call(
            operation="ActionUpdateCount",
            query_params={"filter": filter},
            error_message="Failed to count quarantine actions",
        )

        if self._is_error(result):
            return [result]

        return result

    def update_quarantined_files(
        self,
        action: str = Field(
            description="Reversible action to apply. Supported values are `release` and `unrelease`.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Quarantine file ID(s) to update. Provide `ids` OR `filter` (not both).",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://quarantine/files/search/fql-guide` for syntax.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional audit comment describing why the action is being taken.",
        ),
    ) -> list[dict[str, Any]]:
        """Apply a reversible quarantine action to records selected by IDs or filter.

        Use this to release or unrelease quarantined files. Provide `ids` for
        specific records, or `filter` to select by query. Consult
        falcon://quarantine/files/search/fql-guide before constructing filter
        expressions. Returns an empty list on success.
        """
        normalized = self._normalize_restore_action(action)
        if self._is_error(normalized):
            return [normalized]

        if not ids and not filter:
            return [
                _format_error_response(
                    "Provide either `ids` or `filter` when updating quarantined files."
                )
            ]

        if ids:
            return self._apply_action_by_ids(
                ids=ids,
                action=normalized,
                comment=comment,
                error_message="Failed to update quarantined files by IDs",
            )

        return self._apply_action_by_query(
            action=normalized,
            filter=filter,
            comment=comment,
            error_message="Failed to update quarantined files by query",
        )

    def delete_quarantined_files(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Quarantine file ID(s) to delete. Provide `ids` OR `filter` (not both).",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter expression. See `falcon://quarantine/files/search/fql-guide` for syntax.",
        ),
        comment: str | None = Field(
            default=None,
            description="Optional audit comment describing why the records are being deleted.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete quarantine records selected by IDs or filter.

        This tool is destructive and should be used only when quarantine records
        should be removed rather than released. Provide `ids` for specific records,
        or `filter` to select by query. Consult falcon://quarantine/files/search/fql-guide
        before constructing filter expressions. Returns an empty list on success.
        """
        if not ids and not filter:
            return [
                _format_error_response(
                    "Provide either `ids` or `filter` when deleting quarantined files."
                )
            ]

        if ids:
            return self._apply_action_by_ids(
                ids=ids,
                action="delete",
                comment=comment,
                error_message="Failed to delete quarantined files by IDs",
            )

        return self._apply_action_by_query(
            action="delete",
            filter=filter,
            comment=comment,
            error_message="Failed to delete quarantined files by query",
        )

    def _apply_action_by_ids(
        self,
        ids: list[str],
        action: str,
        comment: str | None,
        error_message: str,
    ) -> list[dict[str, Any]]:
        """Apply a quarantine action to a specific set of record IDs."""
        result = self._base_query_api_call(
            operation="UpdateQuarantinedDetectsByIds",
            body_params={
                "ids": ids,
                "action": action,
                "comment": comment,
            },
            error_message=error_message,
        )

        if self._is_error(result):
            return [result]

        return result

    def _apply_action_by_query(
        self,
        action: str,
        filter: str,
        comment: str | None,
        error_message: str,
    ) -> list[dict[str, Any]]:
        """Apply a quarantine action to records selected by filter."""
        result = self._base_query_api_call(
            operation="UpdateQfByQuery",
            body_params={
                "action": action,
                "filter": filter,
                "comment": comment,
            },
            error_message=error_message,
        )

        if self._is_error(result):
            return [result]

        return result

    def _normalize_restore_action(self, action: str | None) -> str | dict[str, Any]:
        """Normalize and validate reversible quarantine action names."""
        if not isinstance(action, str):
            return _format_error_response(
                "Provide a quarantine `action` value of `release` or `unrelease`."
            )

        lowered = action.strip().lower()
        if lowered not in VALID_RESTORE_ACTIONS:
            return _format_error_response(
                "Unsupported quarantine `action`. Use `release` or `unrelease`."
            )

        return lowered
