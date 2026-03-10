"""
Exposure Management module for Falcon MCP Server.

This module provides tools for searching external assets and performing
controlled inventory / triage updates via Falcon Exposure Management APIs.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.exposure_management import (
    EXPOSURE_MANAGEMENT_SAFETY_GUIDE,
    SEARCH_EXPOSURE_ASSETS_FQL_DOCUMENTATION,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)


class ExposureManagementModule(BaseModule):
    """Module for Falcon Exposure Management operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_exposure_assets,
            name="search_exposure_assets",
        )
        self._add_tool(
            server=server,
            method=self.get_exposure_asset_details,
            name="get_exposure_asset_details",
        )
        self._add_tool(
            server=server,
            method=self.aggregate_exposure_assets,
            name="aggregate_exposure_assets",
        )
        self._add_tool(
            server=server,
            method=self.add_exposure_assets,
            name="add_exposure_assets",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_exposure_assets,
            name="update_exposure_assets",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.remove_exposure_assets,
            name="remove_exposure_assets",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_assets_fql_resource = TextResource(
            uri=AnyUrl("falcon://exposure-management/assets/fql-guide"),
            name="falcon_search_exposure_assets_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_exposure_assets` tool.",
            text=SEARCH_EXPOSURE_ASSETS_FQL_DOCUMENTATION,
        )

        safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://exposure-management/safety-guide"),
            name="falcon_exposure_management_safety_guide",
            description="Safety and operational guidance for Exposure Management write tools.",
            text=EXPOSURE_MANAGEMENT_SAFETY_GUIDE,
        )

        self._add_resource(server, search_assets_fql_resource)
        self._add_resource(server, safety_guide_resource)

    def search_exposure_assets(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for external asset search. IMPORTANT: use the `falcon://exposure-management/assets/fql-guide` resource when building this filter parameter.",
            examples={"asset_type:'ip'+internet_exposure:true", "last_seen:>'now-7d'"},
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=500,
            description="Maximum number of external asset IDs to return from search. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return asset IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort assets using FQL sort syntax.

                Common fields include:
                asset_id, asset_type, criticality, first_seen, last_seen, triage.status

                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
                Examples: 'last_seen.desc', 'criticality|desc'
            """).strip(),
            examples={"last_seen.desc", "criticality|desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search external assets and return full detail records."""
        asset_ids = self._base_search_api_call(
            operation="query_external_assets_v2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search exposure assets",
        )

        if self._is_error(asset_ids):
            return self._format_fql_error_response(
                [asset_ids], filter, SEARCH_EXPOSURE_ASSETS_FQL_DOCUMENTATION
            )

        if not asset_ids:
            if filter:
                return self._format_fql_error_response(
                    [], filter, SEARCH_EXPOSURE_ASSETS_FQL_DOCUMENTATION
                )
            return []

        details = self._base_get_by_ids(
            operation="get_external_assets",
            ids=asset_ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_exposure_asset_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="External asset IDs to retrieve. Use `falcon_search_exposure_assets` to discover IDs.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve full external asset details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve exposure asset details.",
                    operation="get_external_assets",
                )
            ]

        result = self._base_get_by_ids(
            operation="get_external_assets",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def aggregate_exposure_assets(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Exposure Management aggregation specification body for `aggregate_external_assets`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run an aggregate query over external assets."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for asset aggregation.",
                    operation="aggregate_external_assets",
                )
            ]

        command_response = self.client.command(
            "aggregate_external_assets",
            body=body,
        )
        result = handle_api_response(
            command_response,
            operation="aggregate_external_assets",
            error_message="Failed to aggregate exposure assets",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def add_exposure_assets(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        data: list[dict[str, Any]] | None = Field(
            default=None,
            description="Optional full `data` payload for `post_external_assets_inventory_v1`.",
        ),
        subsidiary_id: str | None = Field(
            default=None,
            description="Subsidiary ID for convenience single-batch asset additions.",
        ),
        assets: list[dict[str, Any]] | None = Field(
            default=None,
            description="Convenience asset list. Each item should include `id` and `value`.",
        ),
        asset_id: str | None = Field(
            default=None,
            description="Single-asset convenience ID (used with `value` when `assets` is not provided).",
        ),
        value: str | None = Field(
            default=None,
            description="Single-asset convenience value (used with `asset_id`).",
        ),
    ) -> list[dict[str, Any]]:
        """Add external assets to exposure inventory scanning."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="post_external_assets_inventory_v1",
                )
            ]

        payload_data = data
        if not payload_data:
            if not subsidiary_id:
                return [
                    _format_error_response(
                        "`subsidiary_id` is required when `data` is not provided.",
                        operation="post_external_assets_inventory_v1",
                    )
                ]

            payload_assets = assets
            if not payload_assets and asset_id and value:
                payload_assets = [{"id": asset_id, "value": value}]

            if not payload_assets:
                return [
                    _format_error_response(
                        "Provide either `assets` or both `asset_id` and `value` when `data` is not provided.",
                        operation="post_external_assets_inventory_v1",
                    )
                ]

            payload_data = [
                {
                    "subsidiary_id": subsidiary_id,
                    "assets": payload_assets,
                }
            ]

        result = self._base_query_api_call(
            operation="post_external_assets_inventory_v1",
            body_params={"data": payload_data},
            error_message="Failed to add exposure assets",
            default_result=[
                {
                    "status": "submitted",
                    "submitted_batches": len(payload_data),
                }
            ],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_exposure_assets(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        assets: list[dict[str, Any]] | None = Field(
            default=None,
            description="Optional full `assets` patch payload.",
        ),
        id: str | None = Field(
            default=None,
            description="Convenience single-asset ID when `assets` is not provided.",
        ),
        cid: str | None = Field(
            default=None,
            description="Falcon customer ID for the asset record.",
        ),
        criticality: str | None = Field(
            default=None,
            description="Manual criticality value for the asset.",
        ),
        criticality_description: str | None = Field(
            default=None,
            description="Context text for manual criticality.",
        ),
        action: str | None = Field(
            default=None,
            description="Triage action value.",
        ),
        assigned_to: str | None = Field(
            default=None,
            description="Triage assignment username.",
        ),
        description: str | None = Field(
            default=None,
            description="Triage description/comment.",
        ),
        status: str | None = Field(
            default=None,
            description="Triage status value.",
        ),
    ) -> list[dict[str, Any]]:
        """Update external asset criticality/triage details."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="patch_external_assets",
                )
            ]

        payload_assets = assets
        if not payload_assets:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `assets` is not provided.",
                        operation="patch_external_assets",
                    )
                ]

            asset_patch: dict[str, Any] = {
                "id": id,
                "cid": cid,
                "criticality": criticality,
                "criticality_description": criticality_description,
            }
            asset_patch = {k: v for k, v in asset_patch.items() if v is not None}

            triage: dict[str, Any] = {
                "action": action,
                "assigned_to": assigned_to,
                "description": description,
                "status": status,
            }
            triage = {k: v for k, v in triage.items() if v is not None}
            if triage:
                asset_patch["triage"] = triage

            payload_assets = [asset_patch]

        result = self._base_query_api_call(
            operation="patch_external_assets",
            body_params={"assets": payload_assets},
            error_message="Failed to update exposure assets",
            default_result=[
                {
                    "status": "submitted",
                    "updated_assets": len(payload_assets),
                }
            ],
        )

        if self._is_error(result):
            return [result]

        return result

    def remove_exposure_assets(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this destructive operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="External asset IDs to remove.",
        ),
        description: str = Field(
            default="Deleted via falcon-mcp",
            description="Audit description for the delete operation body.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete one or more external assets."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="delete_external_assets",
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to remove exposure assets.",
                    operation="delete_external_assets",
                )
            ]

        result = self._base_query_api_call(
            operation="delete_external_assets",
            query_params={"ids": ids},
            body_params={"description": description},
            error_message="Failed to remove exposure assets",
            default_result=[
                {
                    "status": "submitted",
                    "deleted_assets": len(ids),
                }
            ],
        )

        if self._is_error(result):
            return [result]

        return result
