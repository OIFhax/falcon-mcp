"""
MalQuery module for Falcon MCP Server.

This module provides tools for MalQuery quotas, searches, metadata, request status, and downloads.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.malquery import MALQUERY_SAFETY_GUIDE, MALQUERY_USAGE_GUIDE

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class MalQueryModule(BaseModule):
    """Module for Falcon MalQuery operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.get_malquery_quotas, name="get_malquery_quotas")
        self._add_tool(server=server, method=self.fuzzy_search_malquery, name="fuzzy_search_malquery", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.exact_search_malquery, name="exact_search_malquery", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.hunt_malquery, name="hunt_malquery", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.get_malquery_request, name="get_malquery_request")
        self._add_tool(server=server, method=self.get_malquery_metadata, name="get_malquery_metadata")
        self._add_tool(server=server, method=self.get_malquery_samples_archive, name="get_malquery_samples_archive")
        self._add_tool(server=server, method=self.schedule_malquery_samples_multidownload, name="schedule_malquery_samples_multidownload", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.download_malquery_sample, name="download_malquery_sample")

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://malquery/usage-guide"),
                name="falcon_malquery_usage_guide",
                description="Usage guidance for Falcon MalQuery tools.",
                text=MALQUERY_USAGE_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://malquery/safety-guide"),
                name="falcon_malquery_safety_guide",
                description="Safety guidance for Falcon MalQuery write operations.",
                text=MALQUERY_SAFETY_GUIDE,
            ),
        )

    def get_malquery_quotas(self) -> list[dict[str, Any]]:
        """Retrieve MalQuery quotas."""
        result = self._base_query_api_call(
            operation="GetMalQueryQuotasV1",
            error_message="Failed to retrieve MalQuery quotas",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def fuzzy_search_malquery(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = None,
        patterns: list[dict[str, Any]] | None = None,
        filter_meta: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Run a fuzzy MalQuery search."""
        return self._run_search_operation(
            operation="PostMalQueryFuzzySearchV1",
            confirm_execution=confirm_execution,
            body=body,
            patterns=patterns,
            options={"filter_meta": filter_meta, "limit": limit},
            required_message="Provide `body` or `patterns` to run a fuzzy MalQuery search.",
            error_message="Failed to run fuzzy MalQuery search",
        )

    def exact_search_malquery(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = None,
        patterns: list[dict[str, Any]] | None = None,
        filter_filetypes: list[str] | None = None,
        filter_meta: list[str] | None = None,
        limit: int | None = None,
        min_date: str | None = None,
        max_date: str | None = None,
        min_size: str | None = None,
        max_size: str | None = None,
    ) -> list[dict[str, Any]]:
        """Run an exact MalQuery search."""
        return self._run_search_operation(
            operation="PostMalQueryExactSearchV1",
            confirm_execution=confirm_execution,
            body=body,
            patterns=patterns,
            options={
                "filter_filetypes": filter_filetypes,
                "filter_meta": filter_meta,
                "limit": limit,
                "min_date": min_date,
                "max_date": max_date,
                "min_size": min_size,
                "max_size": max_size,
            },
            required_message="Provide `body` or `patterns` to run an exact MalQuery search.",
            error_message="Failed to run exact MalQuery search",
        )

    def hunt_malquery(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = None,
        yara_rule: str | None = None,
        filter_filetypes: list[str] | None = None,
        filter_meta: list[str] | None = None,
        limit: int | None = None,
        min_date: str | None = None,
        max_date: str | None = None,
        min_size: str | None = None,
        max_size: str | None = None,
    ) -> list[dict[str, Any]]:
        """Schedule a YARA hunt in MalQuery."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="PostMalQueryHuntV1",
                )
            ]
        request_body = body or self._build_search_body(
            options={
                "filter_filetypes": filter_filetypes,
                "filter_meta": filter_meta,
                "limit": limit,
                "min_date": min_date,
                "max_date": max_date,
                "min_size": min_size,
                "max_size": max_size,
            },
            yara_rule=yara_rule,
        )
        if request_body is None:
            return [
                _format_error_response(
                    "Provide `body` or `yara_rule` to run a MalQuery hunt.",
                    operation="PostMalQueryHuntV1",
                )
            ]
        result = self._base_query_api_call(
            operation="PostMalQueryHuntV1",
            body_params=request_body,
            error_message="Failed to run MalQuery hunt",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def get_malquery_request(
        self,
        ids: list[str] | None = Field(default=None, description="MalQuery request IDs."),
    ) -> list[dict[str, Any]]:
        """Retrieve asynchronous MalQuery request status."""
        return self._run_get_ids_operation(
            operation="GetMalQueryRequestV1",
            ids=ids,
            validation_message="`ids` is required to retrieve MalQuery request details.",
        )

    def get_malquery_metadata(
        self,
        ids: list[str] | None = Field(default=None, description="SHA256 values to retrieve metadata for."),
    ) -> list[dict[str, Any]]:
        """Retrieve MalQuery metadata for SHA256 values."""
        return self._run_get_ids_operation(
            operation="GetMalQueryMetadataV1",
            ids=ids,
            validation_message="`ids` is required to retrieve MalQuery metadata.",
        )

    def get_malquery_samples_archive(
        self,
        ids: list[str] | None = Field(default=None, description="MalQuery multi-download request ID."),
    ) -> list[dict[str, Any]]:
        """Retrieve the MalQuery samples archive for a completed multi-download request."""
        return self._run_binary_download(
            operation="GetMalQueryEntitiesSamplesFetchV1",
            ids=ids,
            validation_message="`ids` is required to retrieve the MalQuery samples archive.",
            error_message="Failed to retrieve MalQuery samples archive",
        )

    def schedule_malquery_samples_multidownload(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = None,
        samples: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Schedule MalQuery sample hashes for multi-download."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="PostMalQueryEntitiesSamplesMultidownloadV1",
                )
            ]
        request_body = body or ({"samples": samples} if samples else None)
        if request_body is None:
            return [
                _format_error_response(
                    "Provide `body` or `samples` to schedule MalQuery sample downloads.",
                    operation="PostMalQueryEntitiesSamplesMultidownloadV1",
                )
            ]
        result = self._base_query_api_call(
            operation="PostMalQueryEntitiesSamplesMultidownloadV1",
            body_params=request_body,
            error_message="Failed to schedule MalQuery multi-download",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def download_malquery_sample(
        self,
        ids: list[str] | None = Field(default=None, description="Single SHA256 to download from MalQuery."),
    ) -> list[dict[str, Any]]:
        """Download a single MalQuery sample by SHA256."""
        return self._run_binary_download(
            operation="GetMalQueryDownloadV1",
            ids=ids,
            validation_message="`ids` is required to download a MalQuery sample.",
            error_message="Failed to download MalQuery sample",
        )

    def _run_search_operation(
        self,
        operation: str,
        confirm_execution: bool,
        body: dict[str, Any] | None,
        patterns: list[dict[str, Any]] | None,
        options: dict[str, Any],
        required_message: str,
        error_message: str,
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation=operation,
                )
            ]
        request_body = body or self._build_search_body(options=options, patterns=patterns)
        if request_body is None:
            return [_format_error_response(required_message, operation=operation)]
        result = self._base_query_api_call(
            operation=operation,
            body_params=request_body,
            error_message=error_message,
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    @staticmethod
    def _build_search_body(
        options: dict[str, Any],
        patterns: list[dict[str, Any]] | None = None,
        yara_rule: str | None = None,
    ) -> dict[str, Any] | None:
        payload = {}
        filtered_options = {key: value for key, value in options.items() if value is not None}
        if filtered_options:
            payload["options"] = filtered_options
        if patterns:
            payload["patterns"] = patterns
        if yara_rule:
            payload["yara_rule"] = yara_rule
        return payload or None

    def _run_get_ids_operation(
        self,
        operation: str,
        ids: list[str] | None,
        validation_message: str,
    ) -> list[dict[str, Any]]:
        if not ids:
            return [_format_error_response(validation_message, operation=operation)]
        result = self._base_get_by_ids(
            operation=operation,
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def _run_binary_download(
        self,
        operation: str,
        ids: list[str] | None,
        validation_message: str,
        error_message: str,
    ) -> list[dict[str, Any]]:
        if not ids:
            return [_format_error_response(validation_message, operation=operation)]

        command_response = self.client.command(
            operation,
            parameters=prepare_api_parameters({"ids": ids}),
        )

        if isinstance(command_response, (bytes, bytearray)):
            return [
                {
                    "message": (
                        "Archive content is binary and is not rendered inline by this MCP tool. "
                        "Use a file download-capable client to save and inspect it."
                    ),
                    "operation": operation,
                    "size_bytes": len(command_response),
                }
            ]

        if not isinstance(command_response, dict):
            return [
                _format_error_response(
                    f"Unexpected response type: {type(command_response).__name__}",
                    operation=operation,
                )
            ]

        body = command_response.get("body")
        if isinstance(body, (bytes, bytearray)):
            return [
                {
                    "message": (
                        "Archive content is binary and is not rendered inline by this MCP tool. "
                        "Use a file download-capable client to save and inspect it."
                    ),
                    "operation": operation,
                    "size_bytes": len(body),
                }
            ]

        result = handle_api_response(
            command_response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result
