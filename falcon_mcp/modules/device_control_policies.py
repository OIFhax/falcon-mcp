"""
Device Control Policies module for Falcon MCP Server.

This module provides full Falcon Device Control Policies service collection
coverage, including policy lifecycle operations, default/class configuration
operations, policy actions, precedence updates, and member/policy searches.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.device_control_policies import (
    DEVICE_CONTROL_DEFAULTS_GUIDE,
    DEVICE_CONTROL_POLICIES_SAFETY_GUIDE,
    SEARCH_DEVICE_CONTROL_POLICIES_FQL_DOCUMENTATION,
    SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_FQL_DOCUMENTATION,
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


class DeviceControlPoliciesModule(BaseModule):
    """Module for Falcon Device Control Policies operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_device_control_policy_members,
            name="search_device_control_policy_members",
        )
        self._add_tool(
            server=server,
            method=self.search_device_control_policies,
            name="search_device_control_policies",
        )
        self._add_tool(
            server=server,
            method=self.get_default_device_control_policies,
            name="get_default_device_control_policies",
        )
        self._add_tool(
            server=server,
            method=self.update_default_device_control_policies,
            name="update_default_device_control_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.perform_device_control_policies_action,
            name="perform_device_control_policies_action",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_device_control_policies_classes,
            name="update_device_control_policies_classes",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_default_device_control_settings,
            name="get_default_device_control_settings",
        )
        self._add_tool(
            server=server,
            method=self.update_default_device_control_settings,
            name="update_default_device_control_settings",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.set_device_control_policies_precedence,
            name="set_device_control_policies_precedence",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_device_control_policy_details,
            name="get_device_control_policy_details",
        )
        self._add_tool(
            server=server,
            method=self.create_device_control_policies,
            name="create_device_control_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_device_control_policies,
            name="update_device_control_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_device_control_policies,
            name="delete_device_control_policies",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_device_control_policy_details_v2,
            name="get_device_control_policy_details_v2",
        )
        self._add_tool(
            server=server,
            method=self.create_device_control_policies_v2,
            name="create_device_control_policies_v2",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_device_control_policies_v2,
            name="update_device_control_policies_v2",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.query_device_control_policy_member_ids,
            name="query_device_control_policy_member_ids",
        )
        self._add_tool(
            server=server,
            method=self.query_device_control_policy_ids,
            name="query_device_control_policy_ids",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_device_control_policies_fql_resource = TextResource(
            uri=AnyUrl("falcon://device-control-policies/policies/fql-guide"),
            name="falcon_search_device_control_policies_fql_guide",
            description="Contains FQL guidance for device control policy search tools.",
            text=SEARCH_DEVICE_CONTROL_POLICIES_FQL_DOCUMENTATION,
        )

        search_device_control_policy_members_fql_resource = TextResource(
            uri=AnyUrl("falcon://device-control-policies/members/fql-guide"),
            name="falcon_search_device_control_policy_members_fql_guide",
            description="Contains FQL guidance for device control policy member search tools.",
            text=SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

        device_control_defaults_guide_resource = TextResource(
            uri=AnyUrl("falcon://device-control-policies/defaults/guide"),
            name="falcon_device_control_defaults_guide",
            description="Guidance for default and class-level device control operations.",
            text=DEVICE_CONTROL_DEFAULTS_GUIDE,
        )

        device_control_policies_safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://device-control-policies/safety-guide"),
            name="falcon_device_control_policies_safety_guide",
            description="Safety and operational guidance for device control policy write tools.",
            text=DEVICE_CONTROL_POLICIES_SAFETY_GUIDE,
        )

        self._add_resource(server, search_device_control_policies_fql_resource)
        self._add_resource(server, search_device_control_policy_members_fql_resource)
        self._add_resource(server, device_control_defaults_guide_resource)
        self._add_resource(server, device_control_policies_safety_guide_resource)

    def search_device_control_policy_members(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Device control policy ID to search members for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for device control policy member search. IMPORTANT: use the `falcon://device-control-policies/members/fql-guide` resource when building this filter parameter.",
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
        """Search members of a device control policy and return combined details."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to search device control policy members.",
                    operation="queryCombinedDeviceControlPolicyMembers",
                )
            ]

        return self._search_with_fql_guide(
            operation="queryCombinedDeviceControlPolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search device control policy members",
            filter_used=filter,
            fql_guide=SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def search_device_control_policies(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for device control policy search. IMPORTANT: use the `falcon://device-control-policies/policies/fql-guide` resource when building this filter parameter.",
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
        """Search device control policies and return combined details."""
        return self._search_with_fql_guide(
            operation="queryCombinedDeviceControlPolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search device control policies",
            filter_used=filter,
            fql_guide=SEARCH_DEVICE_CONTROL_POLICIES_FQL_DOCUMENTATION,
        )

    def get_default_device_control_policies(self) -> list[dict[str, Any]]:
        """Get default device control policies."""
        result = self._base_query_api_call(
            operation="getDefaultDeviceControlPolicies",
            error_message="Failed to get default device control policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_default_device_control_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body for `updateDefaultDeviceControlPolicies`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update default device control policies."""
        return self._update_body_required_operation(
            operation="updateDefaultDeviceControlPolicies",
            confirm_execution=confirm_execution,
            body=body,
            error_message="Failed to update default device control policies",
        )

    def perform_device_control_policies_action(
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
            description="Action to perform on device control policies.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Target device control policy IDs.",
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
            description="Optional full body override for `performDeviceControlPoliciesAction`.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action against device control policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="performDeviceControlPoliciesAction",
                )
            ]

        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required for device control policy action.",
                    operation="performDeviceControlPoliciesAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="performDeviceControlPoliciesAction",
                    )
                ]
            request_body = {"ids": ids}

            effective_action_parameters = action_parameters
            if effective_action_parameters is None and group_id:
                effective_action_parameters = [{"name": "group_id", "value": group_id}]
            if effective_action_parameters:
                request_body["action_parameters"] = effective_action_parameters

        result = self._base_query_api_call(
            operation="performDeviceControlPoliciesAction",
            query_params={"action_name": action_name},
            body_params=request_body,
            error_message="Failed to perform device control policy action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_device_control_policies_classes(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body for `patchDeviceControlPoliciesClassesV1`.",
        ),
    ) -> list[dict[str, Any]]:
        """Patch device control policy classes."""
        return self._update_body_required_operation(
            operation="patchDeviceControlPoliciesClassesV1",
            confirm_execution=confirm_execution,
            body=body,
            error_message="Failed to update device control policy classes",
        )

    def get_default_device_control_settings(self) -> list[dict[str, Any]]:
        """Get default device control settings."""
        result = self._base_query_api_call(
            operation="getDefaultDeviceControlSettings",
            error_message="Failed to get default device control settings",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_default_device_control_settings(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body for `updateDefaultDeviceControlSettings`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update default device control settings."""
        return self._update_body_required_operation(
            operation="updateDefaultDeviceControlSettings",
            confirm_execution=confirm_execution,
            body=body,
            error_message="Failed to update default device control settings",
        )

    def set_device_control_policies_precedence(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `setDeviceControlPoliciesPrecedence`.",
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
        """Set device control policy precedence order."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="setDeviceControlPoliciesPrecedence",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids or not platform_name:
                return [
                    _format_error_response(
                        "`ids` and `platform_name` are required when `body` is not provided.",
                        operation="setDeviceControlPoliciesPrecedence",
                    )
                ]
            request_body = {"ids": ids, "platform_name": platform_name}

        result = self._base_query_api_call(
            operation="setDeviceControlPoliciesPrecedence",
            body_params=request_body,
            error_message="Failed to set device control policy precedence",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_device_control_policy_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Device control policy IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Get device control policy details by ID (v1 endpoint)."""
        return self._get_policy_details(
            operation="getDeviceControlPolicies",
            ids=ids,
        )

    def create_device_control_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `createDeviceControlPolicies`.",
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
        """Create device control policies (v1 endpoint)."""
        return self._create_device_control_policies_common(
            operation="createDeviceControlPolicies",
            confirm_execution=confirm_execution,
            body=body,
            name=name,
            platform_name=platform_name,
            description=description,
            settings=settings,
        )

    def update_device_control_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `updateDeviceControlPolicies`.",
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
        """Update device control policies (v1 endpoint)."""
        return self._update_device_control_policies_common(
            operation="updateDeviceControlPolicies",
            confirm_execution=confirm_execution,
            body=body,
            id=id,
            name=name,
            description=description,
            settings=settings,
        )

    def delete_device_control_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Device control policy IDs to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete device control policies by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="deleteDeviceControlPolicies",
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete device control policies.",
                    operation="deleteDeviceControlPolicies",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteDeviceControlPolicies",
            query_params={"ids": ids},
            error_message="Failed to delete device control policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_device_control_policy_details_v2(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Device control policy IDs to retrieve (v2 endpoint).",
        ),
    ) -> list[dict[str, Any]]:
        """Get device control policy details by ID (v2 endpoint)."""
        return self._get_policy_details(
            operation="getDeviceControlPoliciesV2",
            ids=ids,
        )

    def create_device_control_policies_v2(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `postDeviceControlPoliciesV2`.",
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
        """Create device control policies (v2 endpoint)."""
        return self._create_device_control_policies_common(
            operation="postDeviceControlPoliciesV2",
            confirm_execution=confirm_execution,
            body=body,
            name=name,
            platform_name=platform_name,
            description=description,
            settings=settings,
        )

    def update_device_control_policies_v2(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `patchDeviceControlPoliciesV2`.",
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
        """Update device control policies (v2 endpoint)."""
        return self._update_device_control_policies_common(
            operation="patchDeviceControlPoliciesV2",
            confirm_execution=confirm_execution,
            body=body,
            id=id,
            name=name,
            description=description,
            settings=settings,
        )

    def query_device_control_policy_member_ids(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Device control policy ID to query member IDs for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for device control policy member ID query. IMPORTANT: use the `falcon://device-control-policies/members/fql-guide` resource when building this filter parameter.",
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
        """Query device control policy member IDs."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to query device control policy member IDs.",
                    operation="queryDeviceControlPolicyMembers",
                )
            ]

        return self._query_ids_with_fql_guide(
            operation="queryDeviceControlPolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query device control policy member IDs",
            filter_used=filter,
            fql_guide=SEARCH_DEVICE_CONTROL_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def query_device_control_policy_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for device control policy ID query. IMPORTANT: use the `falcon://device-control-policies/policies/fql-guide` resource when building this filter parameter.",
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
        """Query device control policy IDs."""
        return self._query_ids_with_fql_guide(
            operation="queryDeviceControlPolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query device control policy IDs",
            filter_used=filter,
            fql_guide=SEARCH_DEVICE_CONTROL_POLICIES_FQL_DOCUMENTATION,
        )

    def _get_policy_details(
        self,
        operation: str,
        ids: list[str] | None,
    ) -> list[dict[str, Any]]:
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve device control policy details.",
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

    def _create_device_control_policies_common(
        self,
        operation: str,
        confirm_execution: bool,
        body: dict[str, Any] | None,
        name: str | None,
        platform_name: str | None,
        description: str | None,
        settings: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation=operation,
                )
            ]

        request_body = body
        if request_body is None:
            if not name or not platform_name:
                return [
                    _format_error_response(
                        "`name` and `platform_name` are required when `body` is not provided.",
                        operation=operation,
                    )
                ]
            if not settings:
                return [
                    _format_error_response(
                        "`settings` is required when `body` is not provided.",
                        operation=operation,
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
            operation=operation,
            body_params=request_body,
            error_message="Failed to create device control policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _update_device_control_policies_common(
        self,
        operation: str,
        confirm_execution: bool,
        body: dict[str, Any] | None,
        id: str | None,
        name: str | None,
        description: str | None,
        settings: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation=operation,
                )
            ]

        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided.",
                        operation=operation,
                    )
                ]
            if not any(value is not None for value in [name, description, settings]):
                return [
                    _format_error_response(
                        "Provide at least one update field (`name`, `description`, `settings`) when `body` is not provided.",
                        operation=operation,
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
            operation=operation,
            body_params=request_body,
            error_message="Failed to update device control policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _update_body_required_operation(
        self,
        operation: str,
        confirm_execution: bool,
        body: dict[str, Any] | None,
        error_message: str,
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation=operation,
                )
            ]

        if not body:
            return [
                _format_error_response(
                    "`body` is required for this operation.",
                    operation=operation,
                )
            ]

        result = self._base_query_api_call(
            operation=operation,
            body_params=body,
            error_message=error_message,
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
