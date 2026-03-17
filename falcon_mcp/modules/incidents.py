"""
Incidents module for Falcon MCP Server

This module provides tools for accessing and analyzing CrowdStrike Falcon incidents.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.incidents import (
    CROWD_SCORE_FQL_DOCUMENTATION,
    INCIDENT_ACTIONS_GUIDE,
    SEARCH_BEHAVIORS_FQL_DOCUMENTATION,
    SEARCH_INCIDENTS_FQL_DOCUMENTATION,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class IncidentsModule(BaseModule):
    """Module for accessing and analyzing CrowdStrike Falcon incidents."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        # Register tools
        self._add_tool(
            server=server,
            method=self.show_crowd_score,
            name="show_crowd_score",
        )

        self._add_tool(
            server=server,
            method=self.search_incidents,
            name="search_incidents",
        )
        self._add_tool(
            server=server,
            method=self.query_incident_ids,
            name="query_incident_ids",
        )

        self._add_tool(
            server=server,
            method=self.get_incident_details,
            name="get_incident_details",
        )

        self._add_tool(
            server=server,
            method=self.search_behaviors,
            name="search_behaviors",
        )
        self._add_tool(
            server=server,
            method=self.query_behavior_ids,
            name="query_behavior_ids",
        )

        self._add_tool(
            server=server,
            method=self.get_behavior_details,
            name="get_behavior_details",
        )
        self._add_tool(
            server=server,
            method=self.perform_incident_action,
            name="perform_incident_action",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        crowd_score_fql_resource = TextResource(
            uri=AnyUrl("falcon://incidents/crowd-score/fql-guide"),
            name="falcon_show_crowd_score_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_show_crowd_score` tool.",
            text=CROWD_SCORE_FQL_DOCUMENTATION,
        )

        search_incidents_fql_resource = TextResource(
            uri=AnyUrl("falcon://incidents/search/fql-guide"),
            name="falcon_search_incidents_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_incidents` tool.",
            text=SEARCH_INCIDENTS_FQL_DOCUMENTATION,
        )

        search_behaviors_fql_resource = TextResource(
            uri=AnyUrl("falcon://incidents/behaviors/fql-guide"),
            name="falcon_search_behaviors_fql_guide",
            description="Contains the guide for the `filter` param of the `falcon_search_behaviors` tool.",
            text=SEARCH_BEHAVIORS_FQL_DOCUMENTATION,
        )
        incident_actions_guide_resource = TextResource(
            uri=AnyUrl("falcon://incidents/actions/guide"),
            name="falcon_incident_actions_guide",
            description="Operational guidance for incident update actions.",
            text=INCIDENT_ACTIONS_GUIDE,
        )

        self._add_resource(
            server,
            crowd_score_fql_resource,
        )
        self._add_resource(
            server,
            search_incidents_fql_resource,
        )
        self._add_resource(
            server,
            search_behaviors_fql_resource,
        )
        self._add_resource(
            server,
            incident_actions_guide_resource,
        )

    def show_crowd_score(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://incidents/crowd-score/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=2500,
            description="Maximum number of records to return. (Max: 2500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return ids.",
        ),
        sort: str | None = Field(
            default=None,
            description="The property to sort by. (Ex: modified_timestamp.desc)",
            examples={"modified_timestamp.desc"},
        ),
    ) -> dict[str, Any]:
        """View calculated CrowdScores and security posture metrics for your environment.

        IMPORTANT: You must use the `falcon://incidents/crowd-score/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_show_crowd_score` tool.
        """
        api_response = self._base_search_api_call(
            operation="CrowdScore",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to get crowd score",
        )

        # Check if we received an error response
        if self._is_error(api_response):
            # Return the error response as is
            return api_response

        # Initialize result with all scores
        result = {
            "average_score": 0,
            "average_adjusted_score": 0,
            "scores": api_response,  # Include all the scores in the result
        }

        if api_response:  # If we have scores (list of score objects)
            score_sum = 0
            adjusted_score_sum = 0
            count = len(api_response)

            for item in api_response:
                score_sum += item.get("score", 0)
                adjusted_score_sum += item.get("adjusted_score", 0)

            if count > 0:
                # Round to ensure integer output
                result["average_score"] = round(score_sum / count)
                result["average_adjusted_score"] = round(adjusted_score_sum / count)

        return result

    def search_incidents(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://incidents/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="Maximum number of records to return. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return ids.",
        ),
        sort: str | None = Field(
            default=None,
            description="The property to sort by. FQL syntax. Ex: state.asc, name.desc",
        ),
    ) -> list[dict[str, Any]]:
        """Find and analyze security incidents to understand coordinated activity in your environment.

        IMPORTANT: You must use the `falcon://incidents/search/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_incidents` tool.
        """
        incident_ids = self.query_incident_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(incident_ids):
            return [incident_ids]

        # If we have incident IDs, get the details for each one
        if incident_ids:
            return self.get_incident_details(incident_ids)

        return []

    def query_incident_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit incident IDs. IMPORTANT: use the `falcon://incidents/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="Maximum number of IDs to return. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="The property to sort by. FQL syntax. Ex: state.asc, name.desc",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query incident IDs by FQL criteria."""
        return self._base_query(
            operation="QueryIncidents",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def get_incident_details(
        self,
        ids: list[str] = Field(description="Incident ID(s) to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get comprehensive incident details to understand attack patterns and coordinated activities.

        This tool returns comprehensive incident details for one or more incident IDs.
        Use this when you already have specific incident IDs and need their full details.
        For searching/discovering incidents, use the `falcon_search_incidents` tool instead.
        """
        incidents = self._base_get_by_ids(
            operation="GetIncidents",
            ids=ids,
        )

        if self._is_error(incidents):
            return [incidents]

        return incidents

    def search_behaviors(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit the results. IMPORTANT: use the `falcon://incidents/behaviors/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="Maximum number of records to return. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return ids.",
        ),
        sort: str | None = Field(
            default=None,
            description="The property to sort by. (Ex: modified_timestamp.desc)",
        ),
    ) -> list[dict[str, Any]]:
        """Find and analyze behaviors to understand suspicious activity in your environment.

        Use this when you need to find behaviors matching certain criteria rather than retrieving specific behaviors by ID.
        For retrieving details of known behavior IDs, use falcon_get_behavior_details instead.

        IMPORTANT: You must use the `falcon://incidents/behaviors/fql-guide` resource when you need to use the `filter` parameter.
        This resource contains the guide on how to build the FQL `filter` parameter for the `falcon_search_behaviors` tool.
        """
        behavior_ids = self.query_behavior_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(behavior_ids):
            return [behavior_ids]

        # If we have behavior IDs, get the details for each one
        if behavior_ids:
            return self.get_behavior_details(behavior_ids)

        return []

    def query_behavior_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL Syntax formatted string used to limit behavior IDs. IMPORTANT: use the `falcon://incidents/behaviors/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=500,
            description="Maximum number of IDs to return. (Max: 500)",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="The property to sort by. (Ex: modified_timestamp.desc)",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query behavior IDs by FQL criteria."""
        return self._base_query(
            operation="QueryBehaviors",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    def get_behavior_details(
        self,
        ids: list[str] = Field(description="Behavior ID(s) to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get detailed behavior information to understand attack techniques and tactics.

        Use this when you already know the specific behavior ID(s) and need to retrieve their details.
        For searching behaviors based on criteria, use the `falcon_search_behaviors` tool instead.
        """
        behaviors = self._base_get_by_ids(
            operation="GetBehaviors",
            ids=ids,
        )

        if self._is_error(behaviors):
            return [behaviors]

        return behaviors

    def perform_incident_action(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Incident ID(s) to update. Required when `body` is not provided.",
        ),
        action_parameters: list[dict[str, str]] | None = Field(
            default=None,
            description="Explicit action parameter list. Overrides individual action fields when provided.",
        ),
        add_comment: str | None = Field(
            default=None,
            description="Add a comment to incidents.",
        ),
        add_tag: str | None = Field(
            default=None,
            description="Add a tag to incidents.",
        ),
        delete_tag: str | None = Field(
            default=None,
            description="Delete a tag from incidents.",
        ),
        update_name: str | None = Field(
            default=None,
            description="Update incident name.",
        ),
        update_description: str | None = Field(
            default=None,
            description="Update incident description.",
        ),
        update_assigned_to_v2: str | None = Field(
            default=None,
            description="Assign incident owner by Falcon user UUID.",
        ),
        update_status: int | None = Field(
            default=None,
            description="Update incident status. Valid values: 20 (new), 25 (reopened), 30 (in_progress), 40 (closed).",
        ),
        unassign: bool | None = Field(
            default=None,
            description="When true, unassign current incident owner.",
        ),
        update_detects: bool | None = Field(
            default=None,
            description="Also update associated detection assignment/status.",
        ),
        overwrite_detects: bool | None = Field(
            default=None,
            description="When updating detections, overwrite existing values.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full PerformIncidentAction request body override.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform incident update actions using PerformIncidentAction."""
        ids = self._resolve_field_default(ids)
        action_parameters = self._resolve_field_default(action_parameters)
        add_comment = self._resolve_field_default(add_comment)
        add_tag = self._resolve_field_default(add_tag)
        delete_tag = self._resolve_field_default(delete_tag)
        update_name = self._resolve_field_default(update_name)
        update_description = self._resolve_field_default(update_description)
        update_assigned_to_v2 = self._resolve_field_default(update_assigned_to_v2)
        update_status = self._resolve_field_default(update_status)
        unassign = self._resolve_field_default(unassign)
        update_detects = self._resolve_field_default(update_detects)
        overwrite_detects = self._resolve_field_default(overwrite_detects)
        body = self._resolve_field_default(body)

        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="PerformIncidentAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="PerformIncidentAction",
                    )
                ]

            resolved_action_parameters = self._resolve_action_parameters(
                action_parameters=action_parameters,
                add_comment=add_comment,
                add_tag=add_tag,
                delete_tag=delete_tag,
                update_name=update_name,
                update_description=update_description,
                update_assigned_to_v2=update_assigned_to_v2,
                update_status=update_status,
                unassign=unassign,
            )
            if not resolved_action_parameters:
                return [
                    _format_error_response(
                        "At least one action must be specified via `action_parameters` or action fields.",
                        operation="PerformIncidentAction",
                    )
                ]

            request_body = {"ids": ids, "action_parameters": resolved_action_parameters}

        response = self.client.command(
            "PerformIncidentAction",
            parameters=prepare_api_parameters(
                {
                    "update_detects": update_detects,
                    "overwrite_detects": overwrite_detects,
                }
            ),
            body=prepare_api_parameters(request_body),
        )
        result = handle_api_response(
            response,
            operation="PerformIncidentAction",
            error_message="Failed to perform incident action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    @staticmethod
    def _resolve_action_parameters(
        action_parameters: list[dict[str, str]] | None,
        add_comment: str | None,
        add_tag: str | None,
        delete_tag: str | None,
        update_name: str | None,
        update_description: str | None,
        update_assigned_to_v2: str | None,
        update_status: int | None,
        unassign: bool | None,
    ) -> list[dict[str, str]]:
        if action_parameters:
            return action_parameters

        resolved: list[dict[str, str]] = []
        if add_comment is not None:
            resolved.append({"name": "add_comment", "value": add_comment})
        if add_tag is not None:
            resolved.append({"name": "add_tag", "value": add_tag})
        if delete_tag is not None:
            resolved.append({"name": "delete_tag", "value": delete_tag})
        if update_name is not None:
            resolved.append({"name": "update_name", "value": update_name})
        if update_description is not None:
            resolved.append({"name": "update_description", "value": update_description})
        if update_assigned_to_v2 is not None:
            resolved.append({"name": "update_assigned_to_v2", "value": update_assigned_to_v2})
        if update_status is not None:
            resolved.append({"name": "update_status", "value": str(update_status)})
        if unassign:
            resolved.append({"name": "unassign", "value": ""})

        return resolved

    @staticmethod
    def _resolve_field_default(value: Any) -> Any:
        if isinstance(value, FieldInfo):
            if value.default is ...:
                return None
            return value.default
        return value

    def _base_query(
        self,
        operation: str,
        filter: str | None = None,
        limit: int = 100,
        offset: int | None = None,
        sort: str | None = None,
    ) -> list[str] | dict[str, Any]:
        return self._base_search_api_call(
            operation=operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to perform operation",
        )
