"""
Prevention Policies module for Falcon MCP Server.

This module provides full Falcon Prevention Policies service collection coverage:
search, query, get, create, update, delete, action, and precedence operations.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.prevention_policies import (
    PREVENTION_POLICIES_SAFETY_GUIDE,
    SEARCH_PREVENTION_POLICIES_FQL_DOCUMENTATION,
    SEARCH_PREVENTION_POLICY_MEMBERS_FQL_DOCUMENTATION,
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


class PreventionPoliciesModule(BaseModule):
    """Module for Falcon Prevention Policies operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_prevention_policies,
            name="search_prevention_policies",
        )
        self._add_tool(
            server=server,
            method=self.search_prevention_policy_members,
            name="search_prevention_policy_members",
        )
        self._add_tool(
            server=server,
            method=self.query_prevention_policy_ids,
            name="query_prevention_policy_ids",
        )
        self._add_tool(
            server=server,
            method=self.query_prevention_policy_member_ids,
            name="query_prevention_policy_member_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_prevention_policy_details,
            name="get_prevention_policy_details",
        )
        self._add_tool(
            server=server,
            method=self.create_prevention_policies,
            name="create_prevention_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_prevention_policies,
            name="update_prevention_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_prevention_policies,
            name="delete_prevention_policies",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.perform_prevention_policies_action,
            name="perform_prevention_policies_action",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.set_prevention_policies_precedence,
            name="set_prevention_policies_precedence",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_prevention_policies_fql_resource = TextResource(
            uri=AnyUrl("falcon://prevention-policies/policies/fql-guide"),
            name="falcon_search_prevention_policies_fql_guide",
            description="Contains FQL guidance for prevention policy search tools.",
            text=SEARCH_PREVENTION_POLICIES_FQL_DOCUMENTATION,
        )

        search_prevention_policy_members_fql_resource = TextResource(
            uri=AnyUrl("falcon://prevention-policies/members/fql-guide"),
            name="falcon_search_prevention_policy_members_fql_guide",
            description="Contains FQL guidance for prevention policy member search tools.",
            text=SEARCH_PREVENTION_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

        prevention_policies_safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://prevention-policies/safety-guide"),
            name="falcon_prevention_policies_safety_guide",
            description="Safety and operational guidance for prevention policy write tools.",
            text=PREVENTION_POLICIES_SAFETY_GUIDE,
        )

        self._add_resource(server, search_prevention_policies_fql_resource)
        self._add_resource(server, search_prevention_policy_members_fql_resource)
        self._add_resource(server, prevention_policies_safety_guide_resource)

    def search_prevention_policies(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for prevention policy search. IMPORTANT: use the `falcon://prevention-policies/policies/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of prevention policy records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort policies. Example: `name.desc,precedence.asc`.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search prevention policies and return combined details."""
        return self._search_with_fql_guide(
            operation="queryCombinedPreventionPolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search prevention policies",
            filter_used=filter,
            fql_guide=SEARCH_PREVENTION_POLICIES_FQL_DOCUMENTATION,
        )

    def search_prevention_policy_members(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Prevention policy ID to search members for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for prevention policy member search. IMPORTANT: use the `falcon://prevention-policies/members/fql-guide` resource when building this filter parameter.",
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
        """Search members of a prevention policy and return combined details."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to search prevention policy members.",
                    operation="queryCombinedPreventionPolicyMembers",
                )
            ]

        return self._search_with_fql_guide(
            operation="queryCombinedPreventionPolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search prevention policy members",
            filter_used=filter,
            fql_guide=SEARCH_PREVENTION_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def query_prevention_policy_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for prevention policy ID query. IMPORTANT: use the `falcon://prevention-policies/policies/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=5000,
            description="Maximum number of prevention policy IDs to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort policies. Example: `name.desc,precedence.asc`.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query prevention policy IDs."""
        return self._query_ids_with_fql_guide(
            operation="queryPreventionPolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query prevention policy IDs",
            filter_used=filter,
            fql_guide=SEARCH_PREVENTION_POLICIES_FQL_DOCUMENTATION,
        )

    def query_prevention_policy_member_ids(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Prevention policy ID to query member IDs for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for prevention policy member ID query. IMPORTANT: use the `falcon://prevention-policies/members/fql-guide` resource when building this filter parameter.",
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
        """Query prevention policy member IDs."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to query prevention policy member IDs.",
                    operation="queryPreventionPolicyMembers",
                )
            ]

        return self._query_ids_with_fql_guide(
            operation="queryPreventionPolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query prevention policy member IDs",
            filter_used=filter,
            fql_guide=SEARCH_PREVENTION_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def get_prevention_policy_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Prevention policy IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Get prevention policy details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve prevention policy details.",
                    operation="getPreventionPolicies",
                )
            ]

        result = self._base_get_by_ids(
            operation="getPreventionPolicies",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def create_prevention_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `createPreventionPolicies`.",
        ),
        clone_id: str | None = Field(
            default=None,
            description="Prevention policy ID to clone.",
        ),
        description: str | None = Field(
            default=None,
            description="Policy description.",
        ),
        name: str | None = Field(
            default=None,
            description="Policy name.",
        ),
        platform_name: Literal["Windows", "Mac", "Linux", "iOS", "Android"] | None = Field(
            default=None,
            description="Target operating system platform name.",
        ),
        settings: list[dict[str, Any]] | None = Field(
            default=None,
            description="Policy settings payload list.",
        ),
    ) -> list[dict[str, Any]]:
        """Create prevention policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="createPreventionPolicies",
                )
            ]

        request_body = body
        if request_body is None:
            if not name or not platform_name:
                return [
                    _format_error_response(
                        "`name` and `platform_name` are required when `body` is not provided.",
                        operation="createPreventionPolicies",
                    )
                ]

            resource = {
                "name": name,
                "platform_name": platform_name,
            }
            if clone_id:
                resource["clone_id"] = clone_id
            if description:
                resource["description"] = description
            if settings:
                resource["settings"] = settings

            request_body = {"resources": [resource]}

        result = self._base_query_api_call(
            operation="createPreventionPolicies",
            body_params=request_body,
            error_message="Failed to create prevention policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_prevention_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `updatePreventionPolicies`.",
        ),
        id: str | None = Field(
            default=None,
            description="Prevention policy ID to update when `body` is not provided.",
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
        """Update prevention policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="updatePreventionPolicies",
                )
            ]

        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided.",
                        operation="updatePreventionPolicies",
                    )
                ]
            if not any(value is not None for value in [description, name, settings]):
                return [
                    _format_error_response(
                        "Provide at least one update field (`name`, `description`, `settings`) when `body` is not provided.",
                        operation="updatePreventionPolicies",
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
            operation="updatePreventionPolicies",
            body_params=request_body,
            error_message="Failed to update prevention policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_prevention_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Prevention policy IDs to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete prevention policies by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="deletePreventionPolicies",
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete prevention policies.",
                    operation="deletePreventionPolicies",
                )
            ]

        result = self._base_query_api_call(
            operation="deletePreventionPolicies",
            query_params={"ids": ids},
            error_message="Failed to delete prevention policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def perform_prevention_policies_action(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        action_name: Literal[
            "add-host-group",
            "add-rule-group",
            "disable",
            "enable",
            "remove-host-group",
            "remove-rule-group",
        ]
        | None = Field(
            default=None,
            description="Action to perform on prevention policies.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Target prevention policy IDs.",
        ),
        group_id: str | None = Field(
            default=None,
            description="Group ID used for add/remove host/rule-group actions.",
        ),
        action_parameters: list[dict[str, Any]] | None = Field(
            default=None,
            description="Action parameters list. Overrides `group_id` when provided.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `performPreventionPoliciesAction`.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action against prevention policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="performPreventionPoliciesAction",
                )
            ]

        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required for prevention policy action.",
                    operation="performPreventionPoliciesAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="performPreventionPoliciesAction",
                    )
                ]
            request_body = {"ids": ids}

            effective_action_parameters = action_parameters
            if effective_action_parameters is None and group_id:
                effective_action_parameters = [{"name": "group_id", "value": group_id}]
            if effective_action_parameters:
                request_body["action_parameters"] = effective_action_parameters

        result = self._base_query_api_call(
            operation="performPreventionPoliciesAction",
            query_params={"action_name": action_name},
            body_params=request_body,
            error_message="Failed to perform prevention policy action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def set_prevention_policies_precedence(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `setPreventionPoliciesPrecedence`.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Ordered policy IDs from highest to lowest precedence.",
        ),
        platform_name: Literal["Windows", "Mac", "Linux", "iOS", "Android"] | None = Field(
            default=None,
            description="Target platform name for precedence update.",
        ),
    ) -> list[dict[str, Any]]:
        """Set prevention policy precedence order."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="setPreventionPoliciesPrecedence",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids or not platform_name:
                return [
                    _format_error_response(
                        "`ids` and `platform_name` are required when `body` is not provided.",
                        operation="setPreventionPoliciesPrecedence",
                    )
                ]
            request_body = {"ids": ids, "platform_name": platform_name}

        result = self._base_query_api_call(
            operation="setPreventionPoliciesPrecedence",
            body_params=request_body,
            error_message="Failed to set prevention policy precedence",
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
