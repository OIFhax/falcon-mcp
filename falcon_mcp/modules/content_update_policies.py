"""
Content Update Policies module for Falcon MCP Server.

This module provides full Falcon Content Update Policies service collection coverage:
search, query, get, create, update, delete, action, and precedence operations.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.content_update_policies import (
    CONTENT_UPDATE_PINNABLE_VERSIONS_GUIDE,
    CONTENT_UPDATE_POLICIES_SAFETY_GUIDE,
    SEARCH_CONTENT_UPDATE_POLICIES_FQL_DOCUMENTATION,
    SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION,
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


class ContentUpdatePoliciesModule(BaseModule):
    """Module for Falcon Content Update Policies operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_content_update_policies,
            name="search_content_update_policies",
        )
        self._add_tool(
            server=server,
            method=self.search_content_update_policy_members,
            name="search_content_update_policy_members",
        )
        self._add_tool(
            server=server,
            method=self.query_content_update_policy_ids,
            name="query_content_update_policy_ids",
        )
        self._add_tool(
            server=server,
            method=self.query_content_update_policy_member_ids,
            name="query_content_update_policy_member_ids",
        )
        self._add_tool(
            server=server,
            method=self.query_content_update_pinnable_versions,
            name="query_content_update_pinnable_versions",
        )
        self._add_tool(
            server=server,
            method=self.get_content_update_policy_details,
            name="get_content_update_policy_details",
        )
        self._add_tool(
            server=server,
            method=self.create_content_update_policies,
            name="create_content_update_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_content_update_policies,
            name="update_content_update_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_content_update_policies,
            name="delete_content_update_policies",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.perform_content_update_policies_action,
            name="perform_content_update_policies_action",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.set_content_update_policies_precedence,
            name="set_content_update_policies_precedence",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_policies_resource = TextResource(
            uri=AnyUrl("falcon://content-update-policies/policies/fql-guide"),
            name="falcon_search_content_update_policies_fql_guide",
            description="Contains FQL guidance for content update policy search tools.",
            text=SEARCH_CONTENT_UPDATE_POLICIES_FQL_DOCUMENTATION,
        )

        search_members_resource = TextResource(
            uri=AnyUrl("falcon://content-update-policies/members/fql-guide"),
            name="falcon_search_content_update_policy_members_fql_guide",
            description="Contains FQL guidance for content update policy member search tools.",
            text=SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

        pinnable_versions_resource = TextResource(
            uri=AnyUrl("falcon://content-update-policies/pinnable-versions/guide"),
            name="falcon_content_update_policies_pinnable_versions_guide",
            description="Guidance for querying pinnable content versions.",
            text=CONTENT_UPDATE_PINNABLE_VERSIONS_GUIDE,
        )

        safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://content-update-policies/safety-guide"),
            name="falcon_content_update_policies_safety_guide",
            description="Safety and operational guidance for content update policy write tools.",
            text=CONTENT_UPDATE_POLICIES_SAFETY_GUIDE,
        )

        self._add_resource(server, search_policies_resource)
        self._add_resource(server, search_members_resource)
        self._add_resource(server, pinnable_versions_resource)
        self._add_resource(server, safety_guide_resource)

    def search_content_update_policies(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for content update policy search. IMPORTANT: use the `falcon://content-update-policies/policies/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of content update policy records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort policies. Example: `name.asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search content update policies and return combined details."""
        return self._search_with_fql_guide(
            operation="queryCombinedContentUpdatePolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search content update policies",
            filter_used=filter,
            fql_guide=SEARCH_CONTENT_UPDATE_POLICIES_FQL_DOCUMENTATION,
        )

    def search_content_update_policy_members(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Content update policy ID to search members for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for content update policy member search. IMPORTANT: use the `falcon://content-update-policies/members/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of member records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort policy members. Example: `hostname.asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search members of a content update policy and return combined details."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to search content update policy members.",
                    operation="queryCombinedContentUpdatePolicyMembers",
                )
            ]

        return self._search_with_fql_guide(
            operation="queryCombinedContentUpdatePolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search content update policy members",
            filter_used=filter,
            fql_guide=SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def query_content_update_policy_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for content update policy ID query. IMPORTANT: use the `falcon://content-update-policies/policies/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=5000,
            description="Maximum number of content update policy IDs to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort policies. Example: `name.asc`.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query content update policy IDs."""
        return self._query_ids_with_fql_guide(
            operation="queryContentUpdatePolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query content update policy IDs",
            filter_used=filter,
            fql_guide=SEARCH_CONTENT_UPDATE_POLICIES_FQL_DOCUMENTATION,
        )

    def query_content_update_policy_member_ids(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Content update policy ID to query member IDs for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for content update policy member ID query. IMPORTANT: use the `falcon://content-update-policies/members/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=5000,
            description="Maximum number of member IDs to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort member IDs. Example: `hostname.asc`.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query content update policy member IDs."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to query content update policy member IDs.",
                    operation="queryContentUpdatePolicyMembers",
                )
            ]

        return self._query_ids_with_fql_guide(
            operation="queryContentUpdatePolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query content update policy member IDs",
            filter_used=filter,
            fql_guide=SEARCH_CONTENT_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def query_content_update_pinnable_versions(
        self,
        category: Literal[
            "rapid_response_al_bl_listing",
            "sensor_operations",
            "system_critical",
            "vulnerability_management",
        ]
        | None = Field(
            default=None,
            description="Content category. IMPORTANT: use the `falcon://content-update-policies/pinnable-versions/guide` resource when building this parameter.",
        ),
        sort: str | None = Field(
            default="deployed_timestamp.desc",
            description="Sort order for returned content versions.",
        ),
    ) -> list[Any]:
        """Query pinnable content versions for a category."""
        if not category:
            return [
                _format_error_response(
                    "`category` is required to query pinnable content versions.",
                    operation="queryPinnableContentVersions",
                )
            ]

        result = self._base_search_api_call(
            operation="queryPinnableContentVersions",
            search_params={
                "category": category,
                "sort": sort,
            },
            error_message="Failed to query pinnable content versions",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_content_update_policy_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Content update policy IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Get content update policy details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve content update policy details.",
                    operation="getContentUpdatePolicies",
                )
            ]

        result = self._base_get_by_ids(
            operation="getContentUpdatePolicies",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def create_content_update_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `createContentUpdatePolicies`.",
        ),
        clone_id: str | None = Field(
            default=None,
            description="Content update policy ID to clone.",
        ),
        description: str | None = Field(
            default=None,
            description="Policy description.",
        ),
        name: str | None = Field(
            default=None,
            description="Policy name.",
        ),
        platform_name: str | None = Field(
            default=None,
            description="Target operating system platform name.",
        ),
        settings: list[dict[str, Any]] | None = Field(
            default=None,
            description="Policy settings payload list.",
        ),
    ) -> list[dict[str, Any]]:
        """Create content update policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="createContentUpdatePolicies",
                )
            ]

        request_body = body
        if request_body is None:
            if not name or not platform_name:
                return [
                    _format_error_response(
                        "`name` and `platform_name` are required when `body` is not provided.",
                        operation="createContentUpdatePolicies",
                    )
                ]

            resource = {
                "name": name,
                "platform_name": platform_name,
            }
            if clone_id is not None:
                resource["clone_id"] = clone_id
            if description is not None:
                resource["description"] = description
            if settings is not None:
                resource["settings"] = settings

            request_body = {"resources": [resource]}

        result = self._base_query_api_call(
            operation="createContentUpdatePolicies",
            body_params=request_body,
            error_message="Failed to create content update policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_content_update_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `updateContentUpdatePolicies`.",
        ),
        id: str | None = Field(
            default=None,
            description="Content update policy ID to update when `body` is not provided.",
        ),
        description: str | None = Field(
            default=None,
            description="Updated policy description.",
        ),
        name: str | None = Field(
            default=None,
            description="Updated policy name.",
        ),
        settings: list[dict[str, Any]] | None = Field(
            default=None,
            description="Updated policy settings payload list.",
        ),
    ) -> list[dict[str, Any]]:
        """Update content update policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="updateContentUpdatePolicies",
                )
            ]

        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided.",
                        operation="updateContentUpdatePolicies",
                    )
                ]
            if not any(value is not None for value in [description, name, settings]):
                return [
                    _format_error_response(
                        "Provide at least one update field (`name`, `description`, `settings`) when `body` is not provided.",
                        operation="updateContentUpdatePolicies",
                    )
                ]

            resource = {"id": id}
            if description is not None:
                resource["description"] = description
            if name is not None:
                resource["name"] = name
            if settings is not None:
                resource["settings"] = settings
            request_body = {"resources": [resource]}

        result = self._base_query_api_call(
            operation="updateContentUpdatePolicies",
            body_params=request_body,
            error_message="Failed to update content update policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_content_update_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Content update policy IDs to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete content update policies by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="deleteContentUpdatePolicies",
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete content update policies.",
                    operation="deleteContentUpdatePolicies",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteContentUpdatePolicies",
            query_params={"ids": ids},
            error_message="Failed to delete content update policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def perform_content_update_policies_action(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        action_name: Literal[
            "add-host-group",
            "disable",
            "enable",
            "override-allow",
            "override-pause",
            "override-revert",
            "remove-host-group",
            "remove-pinned-content-version",
            "set-pinned-content-version",
        ]
        | None = Field(
            default=None,
            description="Action to perform on content update policies.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Target content update policy IDs.",
        ),
        group_id: str | None = Field(
            default=None,
            description="Group ID used for add/remove host-group actions.",
        ),
        action_parameters: list[dict[str, Any]] | None = Field(
            default=None,
            description="Action parameters list. Overrides `group_id` when provided.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `performContentUpdatePoliciesAction`.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action against content update policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="performContentUpdatePoliciesAction",
                )
            ]

        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required for content update policy action.",
                    operation="performContentUpdatePoliciesAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="performContentUpdatePoliciesAction",
                    )
                ]
            request_body = {"ids": ids}

            effective_action_parameters = action_parameters
            if effective_action_parameters is None and group_id:
                effective_action_parameters = [{"name": "group_id", "value": group_id}]
            if effective_action_parameters:
                request_body["action_parameters"] = effective_action_parameters

        result = self._base_query_api_call(
            operation="performContentUpdatePoliciesAction",
            query_params={"action_name": action_name},
            body_params=request_body,
            error_message="Failed to perform content update policy action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def set_content_update_policies_precedence(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `setContentUpdatePoliciesPrecedence`.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Ordered policy IDs from highest to lowest precedence.",
        ),
    ) -> list[dict[str, Any]]:
        """Set content update policy precedence order."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="setContentUpdatePoliciesPrecedence",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="setContentUpdatePoliciesPrecedence",
                    )
                ]
            request_body = {"ids": ids}

        result = self._base_query_api_call(
            operation="setContentUpdatePoliciesPrecedence",
            body_params=request_body,
            error_message="Failed to set content update policy precedence",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _search_with_fql_guide(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str,
        filter_used: str | None,
        fql_guide: str,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params=search_params,
            error_message=error_message,
        )

        if self._is_error(result):
            return self._format_fql_error_response([result], filter_used, fql_guide)

        if not result and filter_used:
            return self._format_fql_error_response([], filter_used, fql_guide)

        return result

    def _query_ids_with_fql_guide(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str,
        filter_used: str | None,
        fql_guide: str,
    ) -> list[str] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params=search_params,
            error_message=error_message,
        )

        if self._is_error(result):
            return self._format_fql_error_response([result], filter_used, fql_guide)

        if not result and filter_used:
            return self._format_fql_error_response([], filter_used, fql_guide)

        return result
