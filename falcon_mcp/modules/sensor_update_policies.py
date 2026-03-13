"""
Sensor Update Policies module for Falcon MCP Server.

This module provides full Falcon Sensor Update Policies service collection
coverage, including v1/v2 policy lifecycle operations, build and kernel
discovery, member searches, actions, precedence updates, and uninstall token
reveal operations.
"""

from typing import Any, Literal

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.sensor_update_policies import (
    SEARCH_SENSOR_UPDATE_KERNELS_FQL_DOCUMENTATION,
    SEARCH_SENSOR_UPDATE_POLICIES_FQL_DOCUMENTATION,
    SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION,
    SENSOR_UPDATE_BUILDS_GUIDE,
    SENSOR_UPDATE_POLICIES_SAFETY_GUIDE,
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


class SensorUpdatePoliciesModule(BaseModule):
    """Module for Falcon Sensor Update Policies operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.reveal_sensor_uninstall_token,
            name="reveal_sensor_uninstall_token",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.search_sensor_update_builds,
            name="search_sensor_update_builds",
        )
        self._add_tool(
            server=server,
            method=self.search_sensor_update_kernels,
            name="search_sensor_update_kernels",
        )
        self._add_tool(
            server=server,
            method=self.search_sensor_update_policy_members,
            name="search_sensor_update_policy_members",
        )
        self._add_tool(
            server=server,
            method=self.search_sensor_update_policies,
            name="search_sensor_update_policies",
        )
        self._add_tool(
            server=server,
            method=self.search_sensor_update_policies_v2,
            name="search_sensor_update_policies_v2",
        )
        self._add_tool(
            server=server,
            method=self.perform_sensor_update_policies_action,
            name="perform_sensor_update_policies_action",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.set_sensor_update_policies_precedence,
            name="set_sensor_update_policies_precedence",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_sensor_update_policy_details,
            name="get_sensor_update_policy_details",
        )
        self._add_tool(
            server=server,
            method=self.create_sensor_update_policies,
            name="create_sensor_update_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_sensor_update_policies,
            name="update_sensor_update_policies",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_sensor_update_policies,
            name="delete_sensor_update_policies",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_sensor_update_policy_details_v2,
            name="get_sensor_update_policy_details_v2",
        )
        self._add_tool(
            server=server,
            method=self.create_sensor_update_policies_v2,
            name="create_sensor_update_policies_v2",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_sensor_update_policies_v2,
            name="update_sensor_update_policies_v2",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.query_sensor_update_kernel_distinct,
            name="query_sensor_update_kernel_distinct",
        )
        self._add_tool(
            server=server,
            method=self.query_sensor_update_policy_member_ids,
            name="query_sensor_update_policy_member_ids",
        )
        self._add_tool(
            server=server,
            method=self.query_sensor_update_policy_ids,
            name="query_sensor_update_policy_ids",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_sensor_update_policies_fql_resource = TextResource(
            uri=AnyUrl("falcon://sensor-update-policies/policies/fql-guide"),
            name="falcon_search_sensor_update_policies_fql_guide",
            description="Contains FQL guidance for sensor update policy search tools.",
            text=SEARCH_SENSOR_UPDATE_POLICIES_FQL_DOCUMENTATION,
        )

        search_sensor_update_policy_members_fql_resource = TextResource(
            uri=AnyUrl("falcon://sensor-update-policies/members/fql-guide"),
            name="falcon_search_sensor_update_policy_members_fql_guide",
            description="Contains FQL guidance for sensor update policy member search tools.",
            text=SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

        search_sensor_update_kernels_fql_resource = TextResource(
            uri=AnyUrl("falcon://sensor-update-policies/kernels/fql-guide"),
            name="falcon_search_sensor_update_kernels_fql_guide",
            description="Contains FQL guidance for sensor update kernel search tools.",
            text=SEARCH_SENSOR_UPDATE_KERNELS_FQL_DOCUMENTATION,
        )

        sensor_update_builds_guide_resource = TextResource(
            uri=AnyUrl("falcon://sensor-update-policies/builds/guide"),
            name="falcon_sensor_update_builds_guide",
            description="Guidance for available sensor update build queries.",
            text=SENSOR_UPDATE_BUILDS_GUIDE,
        )

        sensor_update_policies_safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://sensor-update-policies/safety-guide"),
            name="falcon_sensor_update_policies_safety_guide",
            description="Safety and operational guidance for sensor update policy write tools.",
            text=SENSOR_UPDATE_POLICIES_SAFETY_GUIDE,
        )

        self._add_resource(server, search_sensor_update_policies_fql_resource)
        self._add_resource(server, search_sensor_update_policy_members_fql_resource)
        self._add_resource(server, search_sensor_update_kernels_fql_resource)
        self._add_resource(server, sensor_update_builds_guide_resource)
        self._add_resource(server, sensor_update_policies_safety_guide_resource)

    def reveal_sensor_uninstall_token(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this sensitive operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `revealUninstallToken`.",
        ),
        device_id: str | None = Field(
            default=None,
            description="Device ID to retrieve uninstall token for. Use `MAINTENANCE` for bulk maintenance token.",
        ),
        audit_message: str | None = Field(
            default=None,
            description="Audit message for token reveal action.",
        ),
    ) -> list[dict[str, Any]]:
        """Reveal an uninstall token for a specific device."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="revealUninstallToken",
                )
            ]

        request_body = body
        if request_body is None:
            if not device_id:
                return [
                    _format_error_response(
                        "`device_id` is required when `body` is not provided.",
                        operation="revealUninstallToken",
                    )
                ]
            request_body = {"device_id": device_id}
            if audit_message is not None:
                request_body["audit_message"] = audit_message

        result = self._base_query_api_call(
            operation="revealUninstallToken",
            body_params=request_body,
            error_message="Failed to reveal uninstall token",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_sensor_update_builds(
        self,
        platform: Literal["linux", "linuxarm64", "mac", "windows", "zlinux"] | None = Field(
            default=None,
            description="Platform to return sensor update builds for.",
        ),
        stage: str | list[str] | None = Field(
            default=None,
            description="Optional rollout stage selector (string or list of strings).",
        ),
    ) -> list[dict[str, Any]]:
        """Search available sensor update builds."""
        if not platform:
            return [
                _format_error_response(
                    "`platform` is required to search sensor update builds.",
                    operation="queryCombinedSensorUpdateBuilds",
                )
            ]

        result = self._base_search_api_call(
            operation="queryCombinedSensorUpdateBuilds",
            search_params={"platform": platform, "stage": stage},
            error_message="Failed to search sensor update builds",
        )

        if self._is_error(result):
            return [result]

        return result

    def search_sensor_update_kernels(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor update kernel search. IMPORTANT: use the `falcon://sensor-update-policies/kernels/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of kernel compatibility records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search sensor update kernel compatibility records."""
        return self._search_with_fql_guide(
            operation="queryCombinedSensorUpdateKernels",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to search sensor update kernels",
            filter_used=filter,
            fql_guide=SEARCH_SENSOR_UPDATE_KERNELS_FQL_DOCUMENTATION,
        )

    def search_sensor_update_policy_members(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Sensor update policy ID to search members for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor update policy member search. IMPORTANT: use the `falcon://sensor-update-policies/members/fql-guide` resource when building this filter parameter.",
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
        """Search members of a sensor update policy and return combined details."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to search sensor update policy members.",
                    operation="queryCombinedSensorUpdatePolicyMembers",
                )
            ]

        return self._search_with_fql_guide(
            operation="queryCombinedSensorUpdatePolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search sensor update policy members",
            filter_used=filter,
            fql_guide=SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def search_sensor_update_policies(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor update policy search. IMPORTANT: use the `falcon://sensor-update-policies/policies/fql-guide` resource when building this filter parameter.",
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
        """Search sensor update policies (v1 combined endpoint)."""
        return self._search_with_fql_guide(
            operation="queryCombinedSensorUpdatePolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search sensor update policies",
            filter_used=filter,
            fql_guide=SEARCH_SENSOR_UPDATE_POLICIES_FQL_DOCUMENTATION,
        )

    def search_sensor_update_policies_v2(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor update policy v2 search. IMPORTANT: use the `falcon://sensor-update-policies/policies/fql-guide` resource when building this filter parameter.",
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
        """Search sensor update policies (v2 combined endpoint)."""
        return self._search_with_fql_guide(
            operation="queryCombinedSensorUpdatePoliciesV2",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search sensor update policies v2",
            filter_used=filter,
            fql_guide=SEARCH_SENSOR_UPDATE_POLICIES_FQL_DOCUMENTATION,
        )

    def perform_sensor_update_policies_action(
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
            description="Action to perform on sensor update policies.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Target sensor update policy IDs.",
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
            description="Optional full body override for `performSensorUpdatePoliciesAction`.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action against sensor update policies."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="performSensorUpdatePoliciesAction",
                )
            ]

        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required for sensor update policy action.",
                    operation="performSensorUpdatePoliciesAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `body` is not provided.",
                        operation="performSensorUpdatePoliciesAction",
                    )
                ]
            request_body = {"ids": ids}

            effective_action_parameters = action_parameters
            if effective_action_parameters is None and group_id:
                effective_action_parameters = [{"name": "group_id", "value": group_id}]
            if effective_action_parameters:
                request_body["action_parameters"] = effective_action_parameters

        result = self._base_query_api_call(
            operation="performSensorUpdatePoliciesAction",
            query_params={"action_name": action_name},
            body_params=request_body,
            error_message="Failed to perform sensor update policy action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def set_sensor_update_policies_precedence(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full body override for `setSensorUpdatePoliciesPrecedence`.",
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
        """Set sensor update policy precedence order."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="setSensorUpdatePoliciesPrecedence",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids or not platform_name:
                return [
                    _format_error_response(
                        "`ids` and `platform_name` are required when `body` is not provided.",
                        operation="setSensorUpdatePoliciesPrecedence",
                    )
                ]
            request_body = {"ids": ids, "platform_name": platform_name}

        result = self._base_query_api_call(
            operation="setSensorUpdatePoliciesPrecedence",
            body_params=request_body,
            error_message="Failed to set sensor update policy precedence",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_sensor_update_policy_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Sensor update policy IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Get sensor update policy details by ID (v1 endpoint)."""
        return self._get_policy_details(
            operation="getSensorUpdatePolicies",
            ids=ids,
        )

    def create_sensor_update_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `createSensorUpdatePolicies`.",
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
        build: str | None = Field(
            default=None,
            description="Sensor build identifier for v1 policy settings.",
        ),
        settings: dict[str, Any] | None = Field(
            default=None,
            description="Policy settings dictionary. Overrides `build` when provided.",
        ),
    ) -> list[dict[str, Any]]:
        """Create sensor update policies (v1 endpoint)."""
        return self._create_sensor_update_policies_common(
            operation="createSensorUpdatePolicies",
            confirm_execution=confirm_execution,
            body=body,
            name=name,
            platform_name=platform_name,
            description=description,
            settings_override=settings,
            fallback_settings=self._build_v1_settings(build=build),
        )

    def update_sensor_update_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `updateSensorUpdatePolicies`.",
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
        build: str | None = Field(
            default=None,
            description="Updated build identifier for v1 settings.",
        ),
        settings: dict[str, Any] | None = Field(
            default=None,
            description="Updated settings dictionary. Overrides `build` when provided.",
        ),
    ) -> list[dict[str, Any]]:
        """Update sensor update policies (v1 endpoint)."""
        return self._update_sensor_update_policies_common(
            operation="updateSensorUpdatePolicies",
            confirm_execution=confirm_execution,
            body=body,
            id=id,
            name=name,
            description=description,
            settings_override=settings,
            fallback_settings=self._build_v1_settings(build=build),
        )

    def delete_sensor_update_policies(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Sensor update policy IDs to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete sensor update policies by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="deleteSensorUpdatePolicies",
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete sensor update policies.",
                    operation="deleteSensorUpdatePolicies",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteSensorUpdatePolicies",
            query_params={"ids": ids},
            error_message="Failed to delete sensor update policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_sensor_update_policy_details_v2(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Sensor update policy IDs to retrieve (v2 endpoint).",
        ),
    ) -> list[dict[str, Any]]:
        """Get sensor update policy details by ID (v2 endpoint)."""
        return self._get_policy_details(
            operation="getSensorUpdatePoliciesV2",
            ids=ids,
        )

    def create_sensor_update_policies_v2(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `createSensorUpdatePoliciesV2`.",
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
        build: str | None = Field(
            default=None,
            description="Sensor build identifier for policy settings.",
        ),
        scheduler: dict[str, Any] | None = Field(
            default=None,
            description="Scheduler settings payload.",
        ),
        show_early_adopter_builds: bool | None = Field(
            default=None,
            description="Whether to allow early adopter builds.",
        ),
        uninstall_protection: str | None = Field(
            default=None,
            description="Uninstall protection state (for example ENABLED or DISABLED).",
        ),
        variants: list[dict[str, Any]] | None = Field(
            default=None,
            description="Variant build settings payload list.",
        ),
        settings: dict[str, Any] | None = Field(
            default=None,
            description="Policy settings dictionary. Overrides convenience settings fields when provided.",
        ),
    ) -> list[dict[str, Any]]:
        """Create sensor update policies (v2 endpoint)."""
        return self._create_sensor_update_policies_common(
            operation="createSensorUpdatePoliciesV2",
            confirm_execution=confirm_execution,
            body=body,
            name=name,
            platform_name=platform_name,
            description=description,
            settings_override=settings,
            fallback_settings=self._build_v2_settings(
                build=build,
                scheduler=scheduler,
                show_early_adopter_builds=show_early_adopter_builds,
                uninstall_protection=uninstall_protection,
                variants=variants,
            ),
        )

    def update_sensor_update_policies_v2(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override for `updateSensorUpdatePoliciesV2`.",
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
        build: str | None = Field(
            default=None,
            description="Updated build identifier for policy settings.",
        ),
        scheduler: dict[str, Any] | None = Field(
            default=None,
            description="Updated scheduler settings payload.",
        ),
        show_early_adopter_builds: bool | None = Field(
            default=None,
            description="Updated early adopter builds flag.",
        ),
        uninstall_protection: str | None = Field(
            default=None,
            description="Updated uninstall protection state.",
        ),
        variants: list[dict[str, Any]] | None = Field(
            default=None,
            description="Updated variant build settings payload list.",
        ),
        settings: dict[str, Any] | None = Field(
            default=None,
            description="Updated settings dictionary. Overrides convenience settings fields when provided.",
        ),
    ) -> list[dict[str, Any]]:
        """Update sensor update policies (v2 endpoint)."""
        return self._update_sensor_update_policies_common(
            operation="updateSensorUpdatePoliciesV2",
            confirm_execution=confirm_execution,
            body=body,
            id=id,
            name=name,
            description=description,
            settings_override=settings,
            fallback_settings=self._build_v2_settings(
                build=build,
                scheduler=scheduler,
                show_early_adopter_builds=show_early_adopter_builds,
                uninstall_protection=uninstall_protection,
                variants=variants,
            ),
        )

    def query_sensor_update_kernel_distinct(
        self,
        distinct_field: str = Field(
            default="id",
            description="Field name to return distinct values for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for kernel distinct queries. IMPORTANT: use the `falcon://sensor-update-policies/kernels/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=5000,
            description="Maximum number of records to return. [1-5000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return records.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Query distinct kernel compatibility values."""
        return self._search_with_fql_guide(
            operation="querySensorUpdateKernelsDistinct",
            search_params={
                "distinct-field": distinct_field,
                "filter": filter,
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to query distinct sensor update kernels",
            filter_used=filter,
            fql_guide=SEARCH_SENSOR_UPDATE_KERNELS_FQL_DOCUMENTATION,
        )

    def query_sensor_update_policy_member_ids(
        self,
        policy_id: str | None = Field(
            default=None,
            description="Sensor update policy ID to query member IDs for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor update policy member ID query. IMPORTANT: use the `falcon://sensor-update-policies/members/fql-guide` resource when building this filter parameter.",
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
        """Query sensor update policy member IDs."""
        if not policy_id:
            return [
                _format_error_response(
                    "`policy_id` is required to query sensor update policy member IDs.",
                    operation="querySensorUpdatePolicyMembers",
                )
            ]

        return self._query_ids_with_fql_guide(
            operation="querySensorUpdatePolicyMembers",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query sensor update policy member IDs",
            filter_used=filter,
            fql_guide=SEARCH_SENSOR_UPDATE_POLICY_MEMBERS_FQL_DOCUMENTATION,
        )

    def query_sensor_update_policy_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for sensor update policy ID query. IMPORTANT: use the `falcon://sensor-update-policies/policies/fql-guide` resource when building this filter parameter.",
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
        """Query sensor update policy IDs."""
        return self._query_ids_with_fql_guide(
            operation="querySensorUpdatePolicies",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to query sensor update policy IDs",
            filter_used=filter,
            fql_guide=SEARCH_SENSOR_UPDATE_POLICIES_FQL_DOCUMENTATION,
        )

    def _get_policy_details(
        self,
        operation: str,
        ids: list[str] | None,
    ) -> list[dict[str, Any]]:
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve sensor update policy details.",
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

    def _create_sensor_update_policies_common(
        self,
        operation: str,
        confirm_execution: bool,
        body: dict[str, Any] | None,
        name: str | None,
        platform_name: str | None,
        description: str | None,
        settings_override: dict[str, Any] | None,
        fallback_settings: dict[str, Any] | None,
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

            effective_settings = settings_override or fallback_settings
            if not effective_settings:
                return [
                    _format_error_response(
                        "Provide `settings` (or convenience setting fields) when `body` is not provided.",
                        operation=operation,
                    )
                ]

            resource = {
                "name": name,
                "platform_name": platform_name,
                "settings": effective_settings,
            }
            if description:
                resource["description"] = description

            request_body = {"resources": [resource]}

        result = self._base_query_api_call(
            operation=operation,
            body_params=request_body,
            error_message="Failed to create sensor update policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _update_sensor_update_policies_common(
        self,
        operation: str,
        confirm_execution: bool,
        body: dict[str, Any] | None,
        id: str | None,
        name: str | None,
        description: str | None,
        settings_override: dict[str, Any] | None,
        fallback_settings: dict[str, Any] | None,
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

            effective_settings = settings_override or fallback_settings
            if not any(value is not None for value in [name, description, effective_settings]):
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
            if effective_settings is not None:
                resource["settings"] = effective_settings

            request_body = {"resources": [resource]}

        result = self._base_query_api_call(
            operation=operation,
            body_params=request_body,
            error_message="Failed to update sensor update policies",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    @staticmethod
    def _build_v1_settings(build: str | None) -> dict[str, Any] | None:
        if build is None:
            return None
        return {"build": build}

    @staticmethod
    def _build_v2_settings(
        build: str | None,
        scheduler: dict[str, Any] | None,
        show_early_adopter_builds: bool | None,
        uninstall_protection: str | None,
        variants: list[dict[str, Any]] | None,
    ) -> dict[str, Any] | None:
        settings: dict[str, Any] = {}
        if build is not None:
            settings["build"] = build
        if scheduler is not None:
            settings["scheduler"] = scheduler
        if show_early_adopter_builds is not None:
            settings["show_early_adopter_builds"] = show_early_adopter_builds
        if uninstall_protection is not None:
            settings["uninstall_protection"] = uninstall_protection
        if variants is not None:
            settings["variants"] = variants
        return settings or None

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
