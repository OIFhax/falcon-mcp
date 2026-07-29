"""Detections module for Falcon MCP Server."""

from textwrap import dedent
from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field
from pydantic.fields import FieldInfo

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.detections import (
    DETECTIONS_AGGREGATION_GUIDE,
    DETECTIONS_UPDATE_ACTIONS_GUIDE,
    EMBEDDED_FQL_SYNTAX,
    SEARCH_DETECTIONS_FQL_DOCUMENTATION,
)

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

logger = get_logger(__name__)

DETECTION_DETAIL_BATCH_SIZE = 500


class DetectionsModule(BaseModule):
    """Module for accessing and managing CrowdStrike Falcon detections."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_detections, name="search_detections")
        self._add_tool(
            server=server,
            method=self.search_detections_combined,
            name="search_detections_combined",
        )
        self._add_tool(
            server=server, method=self.query_detection_ids_v1, name="query_detection_ids_v1"
        )
        self._add_tool(
            server=server, method=self.query_detection_ids_v2, name="query_detection_ids_v2"
        )
        self._add_tool(
            server=server, method=self.get_detection_details, name="get_detection_details"
        )
        self._add_tool(
            server=server,
            method=self.get_detection_details_v1,
            name="get_detection_details_v1",
        )
        self._add_tool(
            server=server,
            method=self.get_detection_details_v2,
            name="get_detection_details_v2",
        )
        self._add_tool(
            server=server,
            method=self.aggregate_detections_v1,
            name="aggregate_detections_v1",
        )
        self._add_tool(
            server=server,
            method=self.aggregate_detections_v2,
            name="aggregate_detections_v2",
        )
        self._add_tool(
            server=server,
            method=self.update_detections_v1,
            name="update_detections_v1",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_detections_v2,
            name="update_detections_v2",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_detections_v3,
            name="update_detections_v3",
            annotations=WRITE_ANNOTATIONS,
        )

        self._add_tool(
            server=server,
            method=self.update_detections,
            name="update_detections",
            annotations=ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_detections_fql_resource = TextResource(
            uri=AnyUrl("falcon://detections/search/fql-guide"),
            name="falcon_search_detections_fql_guide",
            description="Contains the guide for the `filter` param used by detections query/search tools.",
            text=SEARCH_DETECTIONS_FQL_DOCUMENTATION,
        )
        detections_aggregation_resource = TextResource(
            uri=AnyUrl("falcon://detections/aggregation/guide"),
            name="falcon_detections_aggregation_guide",
            description="Guidance and body examples for detections aggregate tools.",
            text=DETECTIONS_AGGREGATION_GUIDE,
        )
        detections_update_actions_resource = TextResource(
            uri=AnyUrl("falcon://detections/update-actions/guide"),
            name="falcon_detections_update_actions_guide",
            description="Safety and action-parameter guidance for detections update tools.",
            text=DETECTIONS_UPDATE_ACTIONS_GUIDE,
        )

        self._add_resource(server, search_detections_fql_resource)
        self._add_resource(server, detections_aggregation_resource)
        self._add_resource(server, detections_update_actions_resource)

    def search_detections(
        self,
        filter: str | None = Field(
            default=None,
            description=(
                "FQL filter expression. See `falcon://detections/search/fql-guide` for syntax.\n\n"
                + EMBEDDED_FQL_SYNTAX
            ),
            examples=["status:'new'+severity_name:'High'", "device.hostname:'DC*'"],
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=10000,
            description="Maximum number of detection IDs to retrieve before fetching details. [1-10000]",
        ),
        offset: int | None = Field(
            default=None,
            ge=0,
            description="The first detection to return where 0 is the latest detection.",
        ),
        q: str | None = Field(
            default=None,
            description="Search all detection metadata for the provided string.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort detections using these options:
                timestamp, created_timestamp, updated_timestamp, severity, confidence, agent_id.

                Both formats are supported: `severity.desc` or `severity|desc`.
                Examples: `severity.desc`, `timestamp.desc`.
            """).strip(),
            examples=["severity.desc", "timestamp.desc"],
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether to include hidden detections when querying and fetching details.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Find detections by criteria and return their complete details."""
        detection_ids, pagination = self._base_search_with_meta(
            operation="GetQueriesAlertsV2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "q": q,
                "sort": sort,
                "include_hidden": include_hidden,
            },
            error_message="Failed to search detections",
        )

        if self._is_error(detection_ids):
            return self._format_fql_error_response(
                [detection_ids], filter, SEARCH_DETECTIONS_FQL_DOCUMENTATION
            )
        if not detection_ids:
            return self._build_pagination_envelope([], pagination, filter)

        details = []
        for start in range(0, len(detection_ids), DETECTION_DETAIL_BATCH_SIZE):
            detail_batch = self._base_get_by_ids(
                operation="PostEntitiesAlertsV2",
                ids=detection_ids[start : start + DETECTION_DETAIL_BATCH_SIZE],
                id_key="composite_ids",
                include_hidden=include_hidden,
            )
            if self._is_error(detail_batch):
                return [detail_batch]
            details.extend(detail_batch)

        details = self._reorder_by_ids(detection_ids, details, id_field="composite_id")
        return self._build_pagination_envelope(details, pagination, filter)

    def search_detections_combined(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for combined detections query. IMPORTANT: use `falcon://detections/search/fql-guide` when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of combined detections to return. [1-1000]",
        ),
        after: str | None = Field(
            default=None,
            description="Cursor token for paging PostCombinedAlertsV1 results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression in `<field|direction>` format.",
            examples={"created_timestamp|desc", "severity|desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search detections using PostCombinedAlertsV1."""
        request_body = prepare_api_parameters(
            {
                "filter": filter,
                "limit": limit,
                "after": after,
                "sort": sort,
            }
        )
        response = self.client.command("PostCombinedAlertsV1", body=request_body)
        detections = handle_api_response(
            response,
            operation="PostCombinedAlertsV1",
            error_message="Failed to search detections using combined endpoint",
            default_result=[],
        )

        if self._is_error(detections):
            return self._format_fql_error_response(
                [detections],
                filter,
                SEARCH_DETECTIONS_FQL_DOCUMENTATION,
            )

        if not detections and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_DETECTIONS_FQL_DOCUMENTATION,
            )

        return detections

    def query_detection_ids_v1(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for detection ID query. IMPORTANT: use `falcon://detections/search/fql-guide` when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=10000,
            description="Maximum number of detection IDs to return. [1-10000]",
        ),
        offset: int | None = Field(
            default=None,
            ge=0,
            description="The first detection to return where 0 is the latest detection.",
        ),
        q: str | None = Field(
            default=None,
            description="Search all detection metadata for the provided string.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression in `<field|direction>` format.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query detection IDs using GetQueriesAlertsV1."""
        result = self._base_search_api_call(
            operation="GetQueriesAlertsV1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "q": q,
                "sort": sort,
            },
            error_message="Failed to query detection IDs (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_DETECTIONS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_DETECTIONS_FQL_DOCUMENTATION,
            )

        return result

    def query_detection_ids_v2(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for detection ID query. IMPORTANT: use `falcon://detections/search/fql-guide` when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=10000,
            description="Maximum number of detection IDs to return. [1-10000]",
        ),
        offset: int | None = Field(
            default=None,
            ge=0,
            description="The first detection to return where 0 is the latest detection.",
        ),
        q: str | None = Field(
            default=None,
            description="Search all detection metadata for the provided string.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression in `<field|direction>` format.",
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether to include hidden detections in query results.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query detection IDs using GetQueriesAlertsV2."""
        result = self._base_search_api_call(
            operation="GetQueriesAlertsV2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "q": q,
                "sort": sort,
                "include_hidden": include_hidden,
            },
            error_message="Failed to query detection IDs (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_DETECTIONS_FQL_DOCUMENTATION,
            )

        if not result and filter:
            return self._format_fql_error_response(
                [],
                filter,
                SEARCH_DETECTIONS_FQL_DOCUMENTATION,
            )

        return result

    def get_detection_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Composite ID(s) for detections to retrieve via PostEntitiesAlertsV2.",
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether to include hidden detections in the response.",
        ),
    ) -> list[dict[str, Any]]:
        """Backward-compatible alias for PostEntitiesAlertsV2 details retrieval."""
        return self.get_detection_details_v2(
            composite_ids=ids,
            include_hidden=include_hidden,
        )

    def get_detection_details_v1(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Detection ID(s) to retrieve via PostEntitiesAlertsV1.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve detection details using PostEntitiesAlertsV1."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve detection details.",
                    operation="PostEntitiesAlertsV1",
                )
            ]

        details = self._base_get_by_ids(
            operation="PostEntitiesAlertsV1",
            ids=ids,
            id_key="ids",
        )

        if self._is_error(details):
            return [details]

        return details

    def get_detection_details_v2(
        self,
        composite_ids: list[str] | None = Field(
            default=None,
            description="Composite detection ID(s) to retrieve via PostEntitiesAlertsV2.",
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether to include hidden detections in the response.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve detection details using PostEntitiesAlertsV2."""
        if not composite_ids:
            return [
                _format_error_response(
                    "`composite_ids` is required to retrieve detection details.",
                    operation="PostEntitiesAlertsV2",
                )
            ]

        details = self._base_get_by_ids(
            operation="PostEntitiesAlertsV2",
            ids=composite_ids,
            id_key="composite_ids",
            include_hidden=include_hidden,
        )

        if self._is_error(details):
            return [details]

        return details

    def aggregate_detections_v1(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="List-based aggregation payload for PostAggregatesAlertsV1.",
        ),
    ) -> list[dict[str, Any]]:
        """Run detection aggregation queries using PostAggregatesAlertsV1."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for detections aggregation.",
                    operation="PostAggregatesAlertsV1",
                )
            ]

        response = self.client.command("PostAggregatesAlertsV1", body=body)
        result = handle_api_response(
            response,
            operation="PostAggregatesAlertsV1",
            error_message="Failed to aggregate detections (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def aggregate_detections_v2(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="List-based aggregation payload for PostAggregatesAlertsV2.",
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether to include hidden detections in aggregate processing.",
        ),
    ) -> list[dict[str, Any]]:
        """Run detection aggregation queries using PostAggregatesAlertsV2."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for detections aggregation.",
                    operation="PostAggregatesAlertsV2",
                )
            ]

        response = self.client.command(
            "PostAggregatesAlertsV2",
            parameters=prepare_api_parameters({"include_hidden": include_hidden}),
            body=body,
        )
        result = handle_api_response(
            response,
            operation="PostAggregatesAlertsV2",
            error_message="Failed to aggregate detections (v2)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_detections_v1(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Detection IDs targeted by this operation.",
        ),
        action_parameters: list[dict[str, str]] | None = Field(
            default=None,
            description="Explicit action parameter objects. Overrides convenience action fields when provided.",
        ),
        update_status: Literal["new", "in_progress", "reopened", "closed"] | None = Field(
            default=None,
            description="Set the detection status.",
        ),
        add_tag: str | None = Field(default=None, description="Add a tag."),
        remove_tag: str | None = Field(default=None, description="Remove a tag."),
        remove_tags_by_prefix: str | None = Field(
            default=None,
            description="Remove tags matching a prefix.",
        ),
        append_comment: str | None = Field(default=None, description="Append a comment."),
        assign_to_name: str | None = Field(default=None, description="Assign to Falcon username."),
        assign_to_user_id: str | None = Field(
            default=None, description="Assign to Falcon user ID."
        ),
        assign_to_uuid: str | None = Field(default=None, description="Assign to Falcon user UUID."),
        new_behavior_processed: str | None = Field(
            default=None,
            description="Associate newly processed behavior metadata.",
        ),
        show_in_ui: bool | None = Field(
            default=None, description="Show or hide detections in Falcon UI."
        ),
        unassign: bool | None = Field(
            default=None,
            description="Set true to clear any current assignment.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full request body override for PatchEntitiesAlertsV1.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform detection update actions using PatchEntitiesAlertsV1."""
        return self._update_detections(
            operation="PatchEntitiesAlertsV1",
            id_key="ids",
            confirm_execution=confirm_execution,
            ids=ids,
            action_parameters=action_parameters,
            update_status=update_status,
            add_tag=add_tag,
            remove_tag=remove_tag,
            remove_tags_by_prefix=remove_tags_by_prefix,
            append_comment=append_comment,
            assign_to_name=assign_to_name,
            assign_to_user_id=assign_to_user_id,
            assign_to_uuid=assign_to_uuid,
            new_behavior_processed=new_behavior_processed,
            show_in_ui=show_in_ui,
            unassign=unassign,
            body=body,
            include_hidden=None,
        )

    def update_detections_v2(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Detection IDs targeted by this operation.",
        ),
        action_parameters: list[dict[str, str]] | None = Field(
            default=None,
            description="Explicit action parameter objects. Overrides convenience action fields when provided.",
        ),
        update_status: Literal["new", "in_progress", "reopened", "closed"] | None = Field(
            default=None,
            description="Set the detection status.",
        ),
        add_tag: str | None = Field(default=None, description="Add a tag."),
        remove_tag: str | None = Field(default=None, description="Remove a tag."),
        remove_tags_by_prefix: str | None = Field(
            default=None,
            description="Remove tags matching a prefix.",
        ),
        append_comment: str | None = Field(default=None, description="Append a comment."),
        assign_to_name: str | None = Field(default=None, description="Assign to Falcon username."),
        assign_to_user_id: str | None = Field(
            default=None, description="Assign to Falcon user ID."
        ),
        assign_to_uuid: str | None = Field(default=None, description="Assign to Falcon user UUID."),
        new_behavior_processed: str | None = Field(
            default=None,
            description="Associate newly processed behavior metadata.",
        ),
        show_in_ui: bool | None = Field(
            default=None, description="Show or hide detections in Falcon UI."
        ),
        unassign: bool | None = Field(
            default=None,
            description="Set true to clear any current assignment.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full request body override for PatchEntitiesAlertsV2.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform detection update actions using PatchEntitiesAlertsV2."""
        return self._update_detections(
            operation="PatchEntitiesAlertsV2",
            id_key="ids",
            confirm_execution=confirm_execution,
            ids=ids,
            action_parameters=action_parameters,
            update_status=update_status,
            add_tag=add_tag,
            remove_tag=remove_tag,
            remove_tags_by_prefix=remove_tags_by_prefix,
            append_comment=append_comment,
            assign_to_name=assign_to_name,
            assign_to_user_id=assign_to_user_id,
            assign_to_uuid=assign_to_uuid,
            new_behavior_processed=new_behavior_processed,
            show_in_ui=show_in_ui,
            unassign=unassign,
            body=body,
            include_hidden=None,
        )

    def update_detections_v3(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Must be set to `true` to execute this write operation.",
        ),
        composite_ids: list[str] | None = Field(
            default=None,
            description="Composite detection IDs targeted by this operation.",
        ),
        action_parameters: list[dict[str, str]] | None = Field(
            default=None,
            description="Explicit action parameter objects. Overrides convenience action fields when provided.",
        ),
        update_status: Literal["new", "in_progress", "reopened", "closed"] | None = Field(
            default=None,
            description="Set the detection status.",
        ),
        add_tag: str | None = Field(default=None, description="Add a tag."),
        remove_tag: str | None = Field(default=None, description="Remove a tag."),
        remove_tags_by_prefix: str | None = Field(
            default=None,
            description="Remove tags matching a prefix.",
        ),
        append_comment: str | None = Field(default=None, description="Append a comment."),
        assign_to_name: str | None = Field(default=None, description="Assign to Falcon username."),
        assign_to_user_id: str | None = Field(
            default=None, description="Assign to Falcon user ID."
        ),
        assign_to_uuid: str | None = Field(default=None, description="Assign to Falcon user UUID."),
        new_behavior_processed: str | None = Field(
            default=None,
            description="Associate newly processed behavior metadata.",
        ),
        show_in_ui: bool | None = Field(
            default=None, description="Show or hide detections in Falcon UI."
        ),
        unassign: bool | None = Field(
            default=None,
            description="Set true to clear any current assignment.",
        ),
        include_hidden: bool = Field(
            default=True,
            description="Whether hidden detections are included in update context.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full request body override for PatchEntitiesAlertsV3.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform detection update actions using PatchEntitiesAlertsV3."""
        return self._update_detections(
            operation="PatchEntitiesAlertsV3",
            id_key="composite_ids",
            confirm_execution=confirm_execution,
            ids=composite_ids,
            action_parameters=action_parameters,
            update_status=update_status,
            add_tag=add_tag,
            remove_tag=remove_tag,
            remove_tags_by_prefix=remove_tags_by_prefix,
            append_comment=append_comment,
            assign_to_name=assign_to_name,
            assign_to_user_id=assign_to_user_id,
            assign_to_uuid=assign_to_uuid,
            new_behavior_processed=new_behavior_processed,
            show_in_ui=show_in_ui,
            unassign=unassign,
            body=body,
            include_hidden=include_hidden,
        )

    def _update_detections(
        self,
        operation: str,
        id_key: Literal["ids", "composite_ids"],
        confirm_execution: bool,
        ids: list[str] | None,
        action_parameters: list[dict[str, str]] | None,
        update_status: str | None,
        add_tag: str | None,
        remove_tag: str | None,
        remove_tags_by_prefix: str | None,
        append_comment: str | None,
        assign_to_name: str | None,
        assign_to_user_id: str | None,
        assign_to_uuid: str | None,
        new_behavior_processed: str | None,
        show_in_ui: bool | None,
        unassign: bool | None,
        body: dict[str, Any] | None,
        include_hidden: bool | None,
    ) -> list[dict[str, Any]]:
        ids = self._resolve_field_default(ids)
        action_parameters = self._resolve_field_default(action_parameters)
        update_status = self._resolve_field_default(update_status)
        add_tag = self._resolve_field_default(add_tag)
        remove_tag = self._resolve_field_default(remove_tag)
        remove_tags_by_prefix = self._resolve_field_default(remove_tags_by_prefix)
        append_comment = self._resolve_field_default(append_comment)
        assign_to_name = self._resolve_field_default(assign_to_name)
        assign_to_user_id = self._resolve_field_default(assign_to_user_id)
        assign_to_uuid = self._resolve_field_default(assign_to_uuid)
        new_behavior_processed = self._resolve_field_default(new_behavior_processed)
        show_in_ui = self._resolve_field_default(show_in_ui)
        unassign = self._resolve_field_default(unassign)
        body = self._resolve_field_default(body)
        include_hidden = self._resolve_field_default(include_hidden)

        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation=operation,
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        f"`{id_key}` is required when `body` is not provided.",
                        operation=operation,
                    )
                ]

            resolved_action_parameters = self._resolve_action_parameters(
                action_parameters=action_parameters,
                update_status=update_status,
                add_tag=add_tag,
                remove_tag=remove_tag,
                remove_tags_by_prefix=remove_tags_by_prefix,
                append_comment=append_comment,
                assign_to_name=assign_to_name,
                assign_to_user_id=assign_to_user_id,
                assign_to_uuid=assign_to_uuid,
                new_behavior_processed=new_behavior_processed,
                show_in_ui=show_in_ui,
                unassign=unassign,
            )
            if not resolved_action_parameters:
                return [
                    _format_error_response(
                        "At least one action must be specified via `action_parameters` or action fields.",
                        operation=operation,
                    )
                ]

            request_body = {
                id_key: ids,
                "action_parameters": resolved_action_parameters,
            }

        call_kwargs: dict[str, Any] = {
            "body": prepare_api_parameters(request_body),
        }

        if include_hidden is not None:
            call_kwargs["parameters"] = prepare_api_parameters({"include_hidden": include_hidden})

        response = self.client.command(operation, **call_kwargs)
        result = handle_api_response(
            response,
            operation=operation,
            error_message="Failed to update detections",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    @staticmethod
    def _resolve_action_parameters(
        action_parameters: list[dict[str, str]] | None,
        update_status: str | None,
        add_tag: str | None,
        remove_tag: str | None,
        remove_tags_by_prefix: str | None,
        append_comment: str | None,
        assign_to_name: str | None,
        assign_to_user_id: str | None,
        assign_to_uuid: str | None,
        new_behavior_processed: str | None,
        show_in_ui: bool | None,
        unassign: bool | None,
    ) -> list[dict[str, str]]:
        if action_parameters:
            return action_parameters

        resolved: list[dict[str, str]] = []
        if update_status is not None:
            resolved.append({"name": "update_status", "value": update_status})
        if add_tag is not None:
            resolved.append({"name": "add_tag", "value": add_tag})
        if remove_tag is not None:
            resolved.append({"name": "remove_tag", "value": remove_tag})
        if remove_tags_by_prefix is not None:
            resolved.append({"name": "remove_tags_by_prefix", "value": remove_tags_by_prefix})
        if append_comment is not None:
            resolved.append({"name": "append_comment", "value": append_comment})
        if assign_to_name is not None:
            resolved.append({"name": "assign_to_name", "value": assign_to_name})
        if assign_to_user_id is not None:
            resolved.append({"name": "assign_to_user_id", "value": assign_to_user_id})
        if assign_to_uuid is not None:
            resolved.append({"name": "assign_to_uuid", "value": assign_to_uuid})
        if new_behavior_processed is not None:
            resolved.append({"name": "new_behavior_processed", "value": new_behavior_processed})
        if show_in_ui is not None:
            resolved.append({"name": "show_in_ui", "value": str(show_in_ui).lower()})
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

    def update_detections(
        self,
        ids: list[str] = Field(
            description="Composite ID(s) of the detection(s) to update.",
        ),
        status: str | None = Field(
            default=None,
            description=(
                "New status for the detection(s). Allowed values: new, in_progress, "
                "reopened, closed."
            ),
        ),
        assign_to_uuid: str | None = Field(
            default=None,
            description=(
                "UUID of the user to assign the detection(s) to. "
                "Example: '00000000-0000-0000-0000-000000000000'."
            ),
        ),
        assign_to_user_id: str | None = Field(
            default=None,
            description=(
                "Email address of the user to assign the detection(s) to. "
                "Example: 'analyst@example.com'."
            ),
        ),
        assign_to_name: str | None = Field(
            default=None,
            description=(
                "Full name of the user to assign the detection(s) to. Example: 'Jane Smith'."
            ),
        ),
        unassign: bool | None = Field(
            default=None,
            description=(
                "Pass True to remove the current assignee. False is a no-op; "
                "only True has any effect."
            ),
        ),
        append_comment: str | None = Field(
            default=None,
            description=(
                "Comment to append to the detection(s). Comments are visible in the Falcon "
                "console. Must be a non-empty, non-whitespace string."
            ),
        ),
        show_in_ui: bool | None = Field(
            default=None,
            description="Whether to show the detection(s) in the Falcon UI. Set to False to hide.",
        ),
        add_tags: list[str] | None = Field(
            default=None,
            description=(
                "Tags to add to the detection(s). Tags are free-form strings; any value is "
                "accepted. "
                "true_positive, false_positive, and ignored are the conventional resolution "
                "tags the "
                "Falcon console surfaces in its Resolution column — use them when recording "
                "a resolution, "
                "but they are guidance, not an enforced set."
            ),
        ),
        remove_tags: list[str] | None = Field(
            default=None,
            description=(
                "Tags to remove from the detection(s). Each value must match an existing "
                "tag exactly."
            ),
        ),
        remove_tags_by_prefix: str | None = Field(
            default=None,
            description=(
                "Remove all tags on the detection(s) that start with this prefix (e.g. 'fc/')."
            ),
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Update the status, assignment, visibility, comments, and tags of one or more detections.

        Use to change status (new, in_progress, reopened, closed), assign to a user by UUID,
        email address, or full name, unassign, append a comment, hide/show detections in the UI,
        or add/remove tags. Resolution is tag-based: applying the conventional tags true_positive,
        false_positive, or ignored is what populates the console's Resolution view. At least one
        update parameter must be provided. Returns `[]` (empty list) on success, or
        `{"result": [], "hint": "..."}` when closing without adding a resolution tag in this call;
        returns an error dict on failure.
        """
        # Validate mutually exclusive assignment parameters
        assignment_params = [assign_to_uuid, assign_to_user_id, assign_to_name]
        if sum(p is not None for p in assignment_params) > 1:
            return {
                "error": (
                    "Provide at most one of assign_to_uuid, assign_to_user_id, assign_to_name."
                )
            }

        if unassign is True and any(p is not None for p in assignment_params):
            return {"error": "Cannot combine unassign with an assignment parameter."}

        if append_comment is not None and append_comment.strip() == "":
            return {"error": "append_comment must not be empty."}

        for tag in add_tags or []:
            if tag.strip() == "":
                return {"error": "add_tags must not contain empty or whitespace-only strings."}

        for tag in remove_tags or []:
            if tag.strip() == "":
                return {"error": "remove_tags must not contain empty or whitespace-only strings."}

        if remove_tags_by_prefix is not None and remove_tags_by_prefix.strip() == "":
            return {"error": "remove_tags_by_prefix must not be empty or whitespace-only."}

        _valid_statuses = {"new", "in_progress", "reopened", "closed"}
        if status is not None and status not in _valid_statuses:
            return {"error": f"status must be one of: {', '.join(sorted(_valid_statuses))}."}

        if not ids:
            return {"error": "At least one detection ID must be provided."}

        action_parameters: list[dict[str, Any]] = []

        str_params = {
            "update_status": status,
            "assign_to_uuid": assign_to_uuid,
            "assign_to_user_id": assign_to_user_id,
            "assign_to_name": assign_to_name,
            "append_comment": append_comment,
        }
        for name, value in str_params.items():
            if value is not None:
                action_parameters.append({"name": name, "value": value})

        # show_in_ui and unassign must be sent as strings — the API rejects JSON booleans
        if show_in_ui is not None:
            action_parameters.append({"name": "show_in_ui", "value": str(show_in_ui).lower()})
        if unassign is True:
            action_parameters.append({"name": "unassign", "value": "true"})

        for tag in add_tags or []:
            action_parameters.append({"name": "add_tag", "value": tag})
        for tag in remove_tags or []:
            action_parameters.append({"name": "remove_tag", "value": tag})
        if remove_tags_by_prefix is not None:
            action_parameters.append(
                {"name": "remove_tags_by_prefix", "value": remove_tags_by_prefix}
            )

        if not action_parameters:
            return {"error": "At least one update parameter must be provided."}

        body = {
            "composite_ids": ids,
            "action_parameters": action_parameters,
        }

        result = self._base_query_api_call(
            operation="PatchEntitiesAlertsV3",
            body_params=body,
            error_message="Failed to update detections",
            default_result=[],
        )

        # Soft hint: closing without adding a resolution tag in this call may leave the
        # detection out of the console's Resolution view. Non-fatal — only wraps the success
        # case. We only know this call's add_tags, not any resolution tag set previously.
        _resolution_tags = {"true_positive", "false_positive", "ignored"}
        if (
            not self._is_error(result)
            and status == "closed"
            and not _resolution_tags.intersection(add_tags or [])
        ):
            return {
                "result": result,
                "hint": (
                    "No resolution tag was added in this update call. The console convention is to "
                    "add true_positive, false_positive, or ignored when closing a detection so it "
                    "appears in the Resolution view (skip if a resolution tag was already set)."
                ),
            }

        return result
