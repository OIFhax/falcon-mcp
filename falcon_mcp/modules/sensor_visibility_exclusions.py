"""
Sensor Visibility Exclusions module for Falcon MCP Server.

This module provides tools for searching, retrieving, creating, updating,
and deleting Falcon Sensor Visibility exclusions.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.sensor_visibility_exclusions import (
    SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_DOCUMENTATION,
    SENSOR_VISIBILITY_EXCLUSIONS_SAFETY_GUIDE,
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
    idempotentHint=False,
    openWorldHint=True,
)


class SensorVisibilityExclusionsModule(BaseModule):
    """Module for Falcon Sensor Visibility exclusions operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_sensor_visibility_exclusions,
            name="search_sensor_visibility_exclusions",
        )
        self._add_tool(
            server=server,
            method=self.query_sensor_visibility_exclusion_ids,
            name="query_sensor_visibility_exclusion_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_sensor_visibility_exclusion_details,
            name="get_sensor_visibility_exclusion_details",
        )
        self._add_tool(
            server=server,
            method=self.create_sensor_visibility_exclusions,
            name="create_sensor_visibility_exclusions",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_sensor_visibility_exclusions,
            name="update_sensor_visibility_exclusions",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_sensor_visibility_exclusions,
            name="delete_sensor_visibility_exclusions",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_resource = TextResource(
            uri=AnyUrl("falcon://sensor-visibility-exclusions/search/fql-guide"),
            name="falcon_search_sensor_visibility_exclusions_fql_guide",
            description="Contains FQL guidance for sensor visibility exclusions search tools.",
            text=SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_DOCUMENTATION,
        )
        safety_resource = TextResource(
            uri=AnyUrl("falcon://sensor-visibility-exclusions/safety-guide"),
            name="falcon_sensor_visibility_exclusions_safety_guide",
            description="Safety and operational guidance for sensor visibility exclusion write tools.",
            text=SENSOR_VISIBILITY_EXCLUSIONS_SAFETY_GUIDE,
        )

        self._add_resource(server, search_resource)
        self._add_resource(server, safety_resource)

    def search_sensor_visibility_exclusions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor visibility exclusion search. IMPORTANT: use the `falcon://sensor-visibility-exclusions/search/fql-guide` resource when building this filter parameter.",
            examples={"applied_globally:true", "created_by:'mcp'"},
        ),
        limit: int = Field(
            default=100,
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
                Sort sensor visibility exclusions using FQL sort syntax.

                Supported fields include:
                applied_globally, created_by, created_on, last_modified,
                modified_by, value

                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
            """).strip(),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search sensor visibility exclusions and return full exclusion details."""
        exclusion_ids = self._base_search_api_call(
            operation="querySensorVisibilityExclusionsV1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search sensor visibility exclusions",
        )

        if self._is_error(exclusion_ids):
            if filter:
                return self._format_fql_error_response(
                    [exclusion_ids],
                    filter,
                    SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_DOCUMENTATION,
                )
            return [exclusion_ids]

        if not exclusion_ids:
            if filter:
                return self._format_fql_error_response(
                    [],
                    filter,
                    SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_DOCUMENTATION,
                )
            return []

        details = self._base_get_by_ids(
            operation="getSensorVisibilityExclusionsV1",
            ids=exclusion_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def query_sensor_visibility_exclusion_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor visibility exclusion ID query. IMPORTANT: use the `falcon://sensor-visibility-exclusions/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of exclusion IDs to return. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for sensor visibility exclusion IDs.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query sensor visibility exclusion IDs."""
        result = self._base_search_api_call(
            operation="querySensorVisibilityExclusionsV1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query sensor visibility exclusion IDs",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_SENSOR_VISIBILITY_EXCLUSIONS_FQL_DOCUMENTATION,
            )

        return result

    def get_sensor_visibility_exclusion_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Sensor visibility exclusion IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Get sensor visibility exclusion details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve sensor visibility exclusion details.",
                    operation="getSensorVisibilityExclusionsV1",
                )
            ]

        result = self._base_get_by_ids(
            operation="getSensorVisibilityExclusionsV1",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def create_sensor_visibility_exclusions(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        comment: str | None = Field(
            default=None,
            description="String comment describing why the exclusion is created.",
        ),
        groups: list[str] | None = Field(
            default=None,
            description="Group IDs impacted by the exclusion.",
        ),
        value: str | None = Field(
            default=None,
            description="Value to match for the exclusion.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a sensor visibility exclusion."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="createSVExclusionsV1",
                )
            ]

        request_body = body
        if request_body is None:
            if not value:
                return [
                    _format_error_response(
                        "`value` is required when `body` is not provided.",
                        operation="createSVExclusionsV1",
                    )
                ]
            request_body = {"value": value}
            if comment is not None:
                request_body["comment"] = comment
            if groups is not None:
                request_body["groups"] = groups

        result = self._base_query_api_call(
            operation="createSVExclusionsV1",
            body_params=request_body,
            error_message="Failed to create sensor visibility exclusion",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_sensor_visibility_exclusions(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        id: str | None = Field(
            default=None,
            description="Sensor visibility exclusion ID to update. Required when `body` is not provided.",
        ),
        comment: str | None = Field(
            default=None,
            description="String comment describing why the exclusion is updated.",
        ),
        groups: list[str] | None = Field(
            default=None,
            description="Group IDs impacted by the exclusion.",
        ),
        is_descendant_process: bool | None = Field(
            default=None,
            description="Flag indicating if this should apply to descendant processes.",
        ),
        value: str | None = Field(
            default=None,
            description="Updated value to match for the exclusion.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Update a sensor visibility exclusion."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="updateSensorVisibilityExclusionsV1",
                )
            ]

        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided.",
                        operation="updateSensorVisibilityExclusionsV1",
                    )
                ]
            if not any(
                value_ is not None for value_ in [comment, groups, is_descendant_process, value]
            ):
                return [
                    _format_error_response(
                        "Provide at least one update field (`comment`, `groups`, `is_descendant_process`, `value`) when `body` is not provided.",
                        operation="updateSensorVisibilityExclusionsV1",
                    )
                ]

            request_body = {"id": id}
            if comment is not None:
                request_body["comment"] = comment
            if groups is not None:
                request_body["groups"] = groups
            if is_descendant_process is not None:
                request_body["is_descendant_process"] = is_descendant_process
            if value is not None:
                request_body["value"] = value

        result = self._base_query_api_call(
            operation="updateSensorVisibilityExclusionsV1",
            body_params=request_body,
            error_message="Failed to update sensor visibility exclusion",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_sensor_visibility_exclusions(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Sensor visibility exclusion IDs to delete.",
        ),
        comment: str | None = Field(
            default=None,
            description="Explains why the exclusions are deleted.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete sensor visibility exclusions by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="deleteSensorVisibilityExclusionsV1",
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete sensor visibility exclusions.",
                    operation="deleteSensorVisibilityExclusionsV1",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteSensorVisibilityExclusionsV1",
            query_params={"ids": ids, "comment": comment},
            error_message="Failed to delete sensor visibility exclusions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
