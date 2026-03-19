"""
Downloads module for Falcon MCP Server.

This module provides tools for enumerating downloadable artifacts and
requesting pre-signed download URLs.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.downloads import (
    DOWNLOADS_FQL_DOCUMENTATION,
    DOWNLOADS_USAGE_GUIDE,
)


class DownloadsModule(BaseModule):
    """Module for Downloads operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.enumerate_download_files,
            name="enumerate_download_files",
        )
        self._add_tool(
            server=server,
            method=self.fetch_download_file_info,
            name="fetch_download_file_info",
        )
        self._add_tool(
            server=server,
            method=self.fetch_download_file_info_v2,
            name="fetch_download_file_info_v2",
        )
        self._add_tool(
            server=server,
            method=self.get_download_file_url,
            name="get_download_file_url",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        downloads_fql_resource = TextResource(
            uri=AnyUrl("falcon://downloads/files/fql-guide"),
            name="falcon_downloads_fql_guide",
            description="FQL guidance for download file info query tools.",
            text=DOWNLOADS_FQL_DOCUMENTATION,
        )
        downloads_usage_resource = TextResource(
            uri=AnyUrl("falcon://downloads/files/usage-guide"),
            name="falcon_downloads_usage_guide",
            description="Usage guidance for legacy enumerate/download tools.",
            text=DOWNLOADS_USAGE_GUIDE,
        )

        self._add_resource(server, downloads_fql_resource)
        self._add_resource(server, downloads_usage_resource)

    def enumerate_download_files(
        self,
        file_name: str | None = Field(default=None, description="Filter by file name."),
        file_version: str | None = Field(default=None, description="Filter by file version."),
        platform: str | None = Field(default=None, description="Filter by file platform."),
        os: str | None = Field(default=None, description="Filter by operating system."),
        arch: str | None = Field(default=None, description="Filter by architecture."),
        category: str | None = Field(default=None, description="Filter by artifact category."),
    ) -> list[dict[str, Any]]:
        """Enumerate downloadable artifacts using the legacy enumerate endpoint."""
        result = self._base_query_api_call(
            operation="EnumerateFile",
            query_params={
                "file_name": file_name,
                "file_version": file_version,
                "platform": platform,
                "os": os,
                "arch": arch,
                "category": category,
            },
            error_message="Failed to enumerate downloadable files",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def fetch_download_file_info(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for download info search. IMPORTANT: use `falcon://downloads/files/fql-guide` when building this parameter.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for download info results.",
            examples={"file_version.desc", "file_name.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Fetch download file info and pre-signed URLs using v1 combined endpoint."""
        result = self._base_search_api_call(
            operation="FetchFilesDownloadInfo",
            search_params={"filter": filter, "sort": sort},
            error_message="Failed to fetch download file info",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                DOWNLOADS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                DOWNLOADS_FQL_DOCUMENTATION,
            )

        return result

    def fetch_download_file_info_v2(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for download info search (v2). IMPORTANT: use `falcon://downloads/files/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of records to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results. Maximum offset is constrained by Falcon API pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for download info results.",
            examples={"file_version.desc", "file_name.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Fetch download file info and pre-signed URLs using v2 combined endpoint."""
        result = self._base_search_api_call(
            operation="FetchFilesDownloadInfoV2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to fetch download file info (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                DOWNLOADS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                DOWNLOADS_FQL_DOCUMENTATION,
            )

        return result

    def get_download_file_url(
        self,
        file_name: str | None = Field(
            default=None,
            description="Artifact file name to retrieve a pre-signed download URL for.",
        ),
        file_version: str | None = Field(
            default=None,
            description="Artifact file version to retrieve a pre-signed download URL for.",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Retrieve a pre-signed download URL using the legacy direct download endpoint."""
        if not file_name or not file_version:
            return [
                _format_error_response(
                    "Both `file_name` and `file_version` are required to retrieve a download URL.",
                    operation="DownloadFile",
                )
            ]

        response = self.client.command(
            "DownloadFile",
            parameters=prepare_api_parameters(
                {
                    "file_name": file_name,
                    "file_version": file_version,
                }
            ),
        )
        result = handle_api_response(
            response,
            operation="DownloadFile",
            error_message="Failed to retrieve download file URL",
            default_result={},
        )

        if self._is_error(result):
            return [result]

        return result
