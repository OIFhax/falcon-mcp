"""
Firewall Policies module for Falcon MCP Server.

This module provides full Falcon Firewall Policies service collection coverage:
search, query, get, create, update, delete, action, and precedence operations.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.firewall_policies import (
    FIREWALL_POLICIES_SAFETY_GUIDE,
    SEARCH_FIREWALL_POLICIES_FQL_DOCUMENTATION,
    SEARCH_FIREWALL_POLICY_MEMBERS_FQL_DOCUMENTATION,
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


class FirewallPoliciesModule(BaseModule):
    """Module for Falcon Firewall Policies operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_firewall_policy_members,
            name="search_firewall_policy_members",
        )
        self._add_tool(
            server=server,
            method=self.search_firewall_policies,
            name="search_firewall_policies",
        )
        self._add_tool(
            server=server,
            method=self.perform_firewall_policies_action,
            name="perform_firewall_policies_action",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.set_firewall_policies_precedence,
            name="set_firewall_policies_precedence",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_firewall_policy_details,
            name="get_firewall_policy_details",
        )
        self._add_tool(
            server=server,
            method=self.create_firewall_policies,
            name="create_firewall_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_firewall_policies,
            name="update_firewall_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_firewall_policies,
            name="delete_firewall_policies",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.query_firewall_policy_member_ids,
            name="query_firewall_policy_member_ids",
        )
        self._add_tool(
            server=server,
            method=self.query_firewall_policy_ids,
            name="query_firewall_policy_ids",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_firewall_policies_fql_resource = TextResource(
            uri=AnyUrl("falcon://firewall-policies/policies/fql-guide"),
            name="falcon_search_firewall_policies_fql_guide",
            description="Contains FQL guidance for firewall policy search tools.",
            text=SEARCH_FIREWALL_POLICIES_FQL_DOCUMENTATION,
        )

        search_firewall_policy_members_fql_resource = TextResource(
            uri=AnyUrl("falcon://firewall-policies/members/fql-guide"),
            name="falcon_search_firewall_policy_members_fql_guide",
            description="Contains FQL guidance for firewall policy member search tools.",
            text=SEARCH_FIREWALL_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

        firewall_policies_safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://firewall-policies/safety-guide"),
            name="falcon_firewall_policies_safety_guide",
            description="Safety and operational guidance for firewall policy write tools.",
            text=FIREWALL_POLICIES_SAFETY_GUIDE,
        )

        self._add_resource(server, search_firewall_policies_fql_resource)
        self._add_resource(server, search_firewall_policy_members_fql_resource)
        self._add_resource(server, firewall_policies_safety_guide_resource)

    def search_firewall_policy_members(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Firewall policy ID to search members for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall policy member search. IMPORTANT: use the `falcon://firewall-policies/members/fql-guide` resource when building this filter parameter.",
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
        """Search members of a firewall policy and return combined details."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to search firewall policy members.",
                    operation="queryCombinedFirewallPolicyMembers",
                )
            ]

        return self._search_with_fql_guide(
            operation="queryCombinedFirewallPolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search firewall policy members",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def search_firewall_policies(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall policy search. IMPORTANT: use the `falcon://firewall-policies/policies/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of policy records to return. [1-5000]",
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
        """Search firewall policies and return combined details."""
        return self._search_with_fql_guide(
            operation="queryCombinedFirewallPolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search firewall policies",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_POLICIES_FQL_DOCUMENTATION,
        )

    def perform_firewall_policies_action(
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
            description="Action to perform on firewall policies.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Target firewall policy IDs.",
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
            description="Optional full body override for `performFirewallPoliciesAction`.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action against firewall policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="performFirewallPoliciesAction",
                )
            ]

        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required for firewall policy action.",
                    operation="performFirewallPoliciesAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="performFirewallPoliciesAction",
                    )
                ]
            request_body = {"ids": ids}

            effective_action_parameters = action_parameters
            if effective_action_parameters is None and group_id:
                effective_action_parameters = [{"name": "group_id", "value": group_id}]
            if effective_action_parameters:
                request_body["action_parameters"] = effective_action_parameters

        result = self._base_query_api_call(
            operation="performFirewallPoliciesAction",
            query_params={"action_name": action_name},
            body_params=request_body,
            error_message="Failed to perform firewall policy action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def set_firewall_policies_precedence(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `setFirewallPoliciesPrecedence`.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Ordered policy IDs from highest to lowest precedence.",
        ),
        platform_name: Literal["Windows", "Mac", "Linux"] | None = Field(
            default=None,
            description="Target platform name for precedence update.",
        ),
    ) -> list[dict[str, Any]]:
        """Set firewall policy precedence order."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="setFirewallPoliciesPrecedence",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids or not platform_name:
                return [
                    _format_error_response(
                        "`ids` and `platform_name` are required when `body` is not provided.",
                        operation="setFirewallPoliciesPrecedence",
                    )
                ]
            request_body = {"ids": ids, "platform_name": platform_name}

        result = self._base_query_api_call(
            operation="setFirewallPoliciesPrecedence",
            body_params=request_body,
            error_message="Failed to set firewall policy precedence",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_firewall_policy_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Firewall policy IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Get firewall policy details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall policy details.",
                    operation="getFirewallPolicies",
                )
            ]

        result = self._base_get_by_ids(
            operation="getFirewallPolicies",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def create_firewall_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `createFirewallPolicies`.",
        ),
        clone_id: str | None = Field(
            default=None,
            description="Firewall policy ID to clone from.",
        ),
        name: str | None = Field(
            default=None,
            description="Policy name.",
        ),
        platform_name: Literal["Windows", "Mac", "Linux"] | None = Field(
            default=None,
            description="Target operating system platform name.",
        ),
        description: str | None = Field(
            default=None,
            description="Policy description.",
        ),
        settings: dict[str, Any] | None = Field(
            default=None,
            description="Policy settings dictionary.",
        ),
    ) -> list[dict[str, Any]]:
        """Create firewall policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="createFirewallPolicies",
                )
            ]

        request_body = body
        if request_body is None:
            if not name or not platform_name:
                return [
                    _format_error_response(
                        "`name` and `platform_name` are required when `body` is not provided.",
                        operation="createFirewallPolicies",
                    )
                ]
            if not settings:
                return [
                    _format_error_response(
                        "`settings` is required when `body` is not provided.",
                        operation="createFirewallPolicies",
                    )
                ]

            resource = {
                "name": name,
                "platform_name": platform_name,
                "settings": settings,
            }
            if description:
                resource["description"] = description

            request_body = {"resources": [resource]}

        result = self._base_query_api_call(
            operation="createFirewallPolicies",
            query_params={"clone_id": clone_id},
            body_params=request_body,
            error_message="Failed to create firewall policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_firewall_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `updateFirewallPolicies`.",
        ),
        id: str | None = Field(
            default=None,
            description="Policy ID to update when `body` is not provided.",
        ),
        name: str | None = Field(
            default=None,
            description="Updated policy name.",
        ),
        description: str | None = Field(
            default=None,
            description="Updated policy description.",
        ),
        settings: dict[str, Any] | None = Field(
            default=None,
            description="Updated policy settings dictionary.",
        ),
    ) -> list[dict[str, Any]]:
        """Update firewall policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="updateFirewallPolicies",
                )
            ]

        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided.",
                        operation="updateFirewallPolicies",
                    )
                ]
            if not any(value is not None for value in [name, description, settings]):
                return [
                    _format_error_response(
                        "Provide at least one update field (`name`, `description`, `settings`) when `body` is not provided.",
                        operation="updateFirewallPolicies",
                    )
                ]

            resource = {"id": id}
            if name is not None:
                resource["name"] = name
            if description is not None:
                resource["description"] = description
            if settings is not None:
                resource["settings"] = settings
            request_body = {"resources": [resource]}

        result = self._base_query_api_call(
            operation="updateFirewallPolicies",
            body_params=request_body,
            error_message="Failed to update firewall policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_firewall_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Firewall policy IDs to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete firewall policies by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="deleteFirewallPolicies",
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete firewall policies.",
                    operation="deleteFirewallPolicies",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteFirewallPolicies",
            query_params={"ids": ids},
            error_message="Failed to delete firewall policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def query_firewall_policy_member_ids(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Firewall policy ID to query member IDs for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall policy member ID query. IMPORTANT: use the `falcon://firewall-policies/members/fql-guide` resource when building this filter parameter.",
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
        """Query firewall policy member IDs."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to query firewall policy member IDs.",
                    operation="queryFirewallPolicyMembers",
                )
            ]

        return self._query_ids_with_fql_guide(
            operation="queryFirewallPolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query firewall policy member IDs",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def query_firewall_policy_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall policy ID query. IMPORTANT: use the `falcon://firewall-policies/policies/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=5000,
            description="Maximum number of policy IDs to return. [1-5000]",
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
        """Query firewall policy IDs."""
        return self._query_ids_with_fql_guide(
            operation="queryFirewallPolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query firewall policy IDs",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_POLICIES_FQL_DOCUMENTATION,
        )

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
