"""
Sensor Download module for Falcon MCP Server.

This module provides tools for listing sensor installers, retrieving installer
metadata, obtaining CCID values, and downloading installer binaries.
"""

import base64
import hashlib
from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.sensor_download import (
    SEARCH_SENSOR_INSTALLERS_FQL_DOCUMENTATION,
    SENSOR_INSTALLER_DOWNLOAD_GUIDE,
)


class SensorDownloadModule(BaseModule):
    """Module for Sensor Download operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_sensor_installer_ids,
            name="search_sensor_installer_ids",
        )
        self._add_tool(
            server=server,
            method=self.search_sensor_installer_ids_v2,
            name="search_sensor_installer_ids_v2",
        )
        self._add_tool(
            server=server,
            method=self.get_sensor_installer_details,
            name="get_sensor_installer_details",
        )
        self._add_tool(
            server=server,
            method=self.get_sensor_installer_details_v2,
            name="get_sensor_installer_details_v2",
        )
        self._add_tool(
            server=server,
            method=self.search_sensor_installers_combined,
            name="search_sensor_installers_combined",
        )
        self._add_tool(
            server=server,
            method=self.search_sensor_installers_combined_v2,
            name="search_sensor_installers_combined_v2",
        )
        self._add_tool(
            server=server,
            method=self.get_sensor_installer_ccid,
            name="get_sensor_installer_ccid",
        )
        self._add_tool(
            server=server,
            method=self.download_sensor_installer,
            name="download_sensor_installer",
        )
        self._add_tool(
            server=server,
            method=self.download_sensor_installer_v2,
            name="download_sensor_installer_v2",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_sensor_installers_fql_resource = TextResource(
            uri=AnyUrl("falcon://sensor-download/installers/fql-guide"),
            name="falcon_search_sensor_installers_fql_guide",
            description="Contains the guide for the `filter` parameter of sensor installer search tools.",
            text=SEARCH_SENSOR_INSTALLERS_FQL_DOCUMENTATION,
        )

        sensor_installer_download_guide_resource = TextResource(
            uri=AnyUrl("falcon://sensor-download/installers/download-guide"),
            name="falcon_sensor_installer_download_guide",
            description="Guidance for using installer download tools and inline binary behavior.",
            text=SENSOR_INSTALLER_DOWNLOAD_GUIDE,
        )

        self._add_resource(server, search_sensor_installers_fql_resource)
        self._add_resource(server, sensor_installer_download_guide_resource)

    def search_sensor_installer_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor installer ID search. IMPORTANT: use the `falcon://sensor-download/installers/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of installer IDs to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort sensor installers using FQL syntax.

                Common examples: release_date.desc, version|asc
            """).strip(),
            examples={"release_date.desc", "version|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Query sensor installer IDs using v1 API."""
        return self._search_sensor_installer_ids_operation(
            operation="GetSensorInstallersByQuery",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def search_sensor_installer_ids_v2(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor installer ID search (v2). IMPORTANT: use the `falcon://sensor-download/installers/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of installer IDs to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort sensor installers using FQL syntax.

                Common examples: release_date.desc, version|asc
            """).strip(),
            examples={"release_date.desc", "version|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Query sensor installer IDs using v2 API."""
        return self._search_sensor_installer_ids_operation(
            operation="GetSensorInstallersByQueryV2",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def get_sensor_installer_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Installer SHA256 IDs to retrieve metadata for.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve installer metadata by SHA256 IDs using v1 API."""
        return self._get_sensor_installer_details_operation(
            operation="GetSensorInstallersEntities",
            ids=ids,
        )

    def get_sensor_installer_details_v2(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Installer SHA256 IDs to retrieve metadata for (v2 response with architecture details).",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve installer metadata by SHA256 IDs using v2 API."""
        return self._get_sensor_installer_details_operation(
            operation="GetSensorInstallersEntitiesV2",
            ids=ids,
        )

    def search_sensor_installers_combined(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for combined installer search. IMPORTANT: use the `falcon://sensor-download/installers/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of installer records to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort sensor installers using FQL syntax.

                Common examples: release_date.desc, version|asc
            """).strip(),
            examples={"release_date.desc", "version|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search combined sensor installer details using v1 API."""
        return self._search_sensor_installers_combined_operation(
            operation="GetCombinedSensorInstallersByQuery",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def search_sensor_installers_combined_v2(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for combined installer search (v2). IMPORTANT: use the `falcon://sensor-download/installers/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of installer records to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort sensor installers using FQL syntax.

                Common examples: release_date.desc, version|asc
            """).strip(),
            examples={"release_date.desc", "version|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search combined sensor installer details using v2 API."""
        return self._search_sensor_installers_combined_operation(
            operation="GetCombinedSensorInstallersByQueryV2",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def get_sensor_installer_ccid(self) -> list[dict[str, Any]]:
        """Retrieve sensor installer CCID values for this tenant."""
        command_response = self.client.command("GetSensorInstallersCCIDByQuery")
        result = handle_api_response(
            command_response,
            operation="GetSensorInstallersCCIDByQuery",
            error_message="Failed to retrieve sensor installer CCID",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def download_sensor_installer(
        self,
        id: str | None = Field(
            default=None,
            description="Installer SHA256 ID to download using v1 endpoint.",
        ),
        include_binary_base64: bool = Field(
            default=False,
            description="When true, include base64-encoded installer content in the response (bounded by `max_inline_bytes`).",
        ),
        max_inline_bytes: int = Field(
            default=5_000_000,
            ge=1,
            le=20_000_000,
            description="Maximum binary size (bytes) allowed for inline base64 return. [1-20000000]",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Download a sensor installer by SHA256 ID using v1 endpoint."""
        return self._download_sensor_installer_operation(
            operation="DownloadSensorInstallerById",
            id=id,
            include_binary_base64=include_binary_base64,
            max_inline_bytes=max_inline_bytes,
        )

    def download_sensor_installer_v2(
        self,
        id: str | None = Field(
            default=None,
            description="Installer SHA256 ID to download using v2 endpoint.",
        ),
        include_binary_base64: bool = Field(
            default=False,
            description="When true, include base64-encoded installer content in the response (bounded by `max_inline_bytes`).",
        ),
        max_inline_bytes: int = Field(
            default=5_000_000,
            ge=1,
            le=20_000_000,
            description="Maximum binary size (bytes) allowed for inline base64 return. [1-20000000]",
        ),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Download a sensor installer by SHA256 ID using v2 endpoint."""
        return self._download_sensor_installer_operation(
            operation="DownloadSensorInstallerByIdV2",
            id=id,
            include_binary_base64=include_binary_base64,
            max_inline_bytes=max_inline_bytes,
        )

    def _search_sensor_installer_ids_operation(
        self,
        operation: str,
        filter: str | None,
        limit: int,
        offset: int,
        sort: str | None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search sensor installer IDs",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_SENSOR_INSTALLERS_FQL_DOCUMENTATION,
            )

        return result

    def _search_sensor_installers_combined_operation(
        self,
        operation: str,
        filter: str | None,
        limit: int,
        offset: int,
        sort: str | None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search sensor installers",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_SENSOR_INSTALLERS_FQL_DOCUMENTATION,
            )

        return result

    def _get_sensor_installer_details_operation(
        self,
        operation: str,
        ids: list[str] | None,
    ) -> list[dict[str, Any]]:
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve sensor installer details.",
                    operation=operation,
                )
            ]

        result = self._base_get_by_ids(
            operation=operation,
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def _download_sensor_installer_operation(
        self,
        operation: str,
        id: str | None,
        include_binary_base64: bool,
        max_inline_bytes: int,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if not id:
            return [
                _format_error_response(
                    "`id` is required to download a sensor installer.",
                    operation=operation,
                )
            ]

        prepared_params = prepare_api_parameters({"id": id})
        command_response = self.client.command(operation, parameters=prepared_params)

        if isinstance(command_response, bytes):
            result: dict[str, Any] = {
                "operation": operation,
                "id": id,
                "size_bytes": len(command_response),
                "sha256": hashlib.sha256(command_response).hexdigest(),
            }

            if include_binary_base64:
                if len(command_response) > max_inline_bytes:
                    return [
                        _format_error_response(
                            "Installer binary exceeds `max_inline_bytes`. Increase limit or keep `include_binary_base64=false`.",
                            details={
                                "size_bytes": len(command_response),
                                "max_inline_bytes": max_inline_bytes,
                            },
                            operation=operation,
                        )
                    ]

                result["binary_base64"] = base64.b64encode(command_response).decode("ascii")
            else:
                result["hint"] = (
                    "Binary content omitted. Set `include_binary_base64=true` to include inline bytes."
                )

            return result

        if isinstance(command_response, dict):
            result = handle_api_response(
                command_response,
                operation=operation,
                error_message="Failed to download sensor installer",
                default_result=[],
            )

            if self._is_error(result):
                return [result]

            return result

        return [
            _format_error_response(
                f"Unexpected response type from Falcon API: {type(command_response).__name__}",
                operation=operation,
            )
        ]
