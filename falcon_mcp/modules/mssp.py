"""
MSSP (Flight Control) module for Falcon MCP Server.

This module provides full Falcon Flight Control coverage using generated wrappers around
the official operation IDs.
"""

from collections.abc import Callable
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.mssp import MSSP_SAFETY_GUIDE, MSSP_USAGE_GUIDE

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


class MSSPModule(BaseModule):
    """Module for Falcon MSSP (Flight Control) operations."""

    TOOL_SPECS = [
        ("query_mssp_children", "queryChildren", "params_read", None),
        ("get_mssp_children", "getChildren", "params_read", None),
        ("get_mssp_children_v2", "getChildrenV2", "body_read", None),
        ("query_mssp_cid_groups", "queryCIDGroups", "params_read", None),
        ("get_mssp_cid_group_by_id", "getCIDGroupById", "params_read", None),
        ("get_mssp_cid_group_by_id_v1", "getCIDGroupByIdV1", "params_read", None),
        ("get_mssp_cid_group_by_id_v2", "getCIDGroupByIdV2", "params_read", None),
        ("create_mssp_cid_groups", "createCIDGroups", "body_write", WRITE_ANNOTATIONS),
        ("update_mssp_cid_groups", "updateCIDGroups", "body_write", WRITE_ANNOTATIONS),
        ("delete_mssp_cid_groups", "deleteCIDGroups", "params_write", DESTRUCTIVE_WRITE_ANNOTATIONS),
        ("query_mssp_cid_group_members", "queryCIDGroupMembers", "params_read", None),
        ("get_mssp_cid_group_members", "getCIDGroupMembersBy", "params_read", None),
        ("get_mssp_cid_group_members_v1", "getCIDGroupMembersByV1", "params_read", None),
        ("get_mssp_cid_group_members_v2", "getCIDGroupMembersByV2", "params_read", None),
        ("add_mssp_cid_group_members", "addCIDGroupMembers", "body_write", WRITE_ANNOTATIONS),
        ("delete_mssp_cid_group_members", "deleteCIDGroupMembers", "body_write", DESTRUCTIVE_WRITE_ANNOTATIONS),
        ("delete_mssp_cid_group_members_v1", "deleteCIDGroupMembersV1", "body_write", DESTRUCTIVE_WRITE_ANNOTATIONS),
        ("delete_mssp_cid_group_members_v2", "deleteCIDGroupMembersV2", "body_write", DESTRUCTIVE_WRITE_ANNOTATIONS),
        ("query_mssp_roles", "queryRoles", "params_read", None),
        ("get_mssp_roles_by_id", "getRolesByID", "params_read", None),
        ("add_mssp_role", "addRole", "body_write", WRITE_ANNOTATIONS),
        ("delete_mssp_roles", "deletedRoles", "body_write", DESTRUCTIVE_WRITE_ANNOTATIONS),
        ("query_mssp_user_groups", "queryUserGroups", "params_read", None),
        ("get_mssp_user_groups_by_id", "getUserGroupsByID", "params_read", None),
        ("get_mssp_user_groups_by_id_v1", "getUserGroupsByIDV1", "params_read", None),
        ("get_mssp_user_groups_by_id_v2", "getUserGroupsByIDV2", "params_read", None),
        ("create_mssp_user_groups", "createUserGroups", "body_write", WRITE_ANNOTATIONS),
        ("update_mssp_user_groups", "updateUserGroups", "body_write", WRITE_ANNOTATIONS),
        ("delete_mssp_user_groups", "deleteUserGroups", "params_write", DESTRUCTIVE_WRITE_ANNOTATIONS),
        ("query_mssp_user_group_members", "queryUserGroupMembers", "params_read", None),
        ("get_mssp_user_group_members_by_id", "getUserGroupMembersByID", "params_read", None),
        ("get_mssp_user_group_members_by_id_v1", "getUserGroupMembersByIDV1", "params_read", None),
        ("get_mssp_user_group_members_by_id_v2", "getUserGroupMembersByIDV2", "params_read", None),
        ("add_mssp_user_group_members", "addUserGroupMembers", "body_write", WRITE_ANNOTATIONS),
        ("delete_mssp_user_group_members", "deleteUserGroupMembers", "body_write", DESTRUCTIVE_WRITE_ANNOTATIONS),
    ]

    def __init__(self, client):
        super().__init__(client)
        self._generated_tool_names: list[str] = []
        self._build_generated_tools()

    def _build_generated_tools(self) -> None:
        for attr_name, operation, kind, _annotations in self.TOOL_SPECS:
            if kind == "params_read":
                method = self._make_params_read_tool(operation)
            elif kind == "body_read":
                method = self._make_body_read_tool(operation)
            elif kind == "body_write":
                method = self._make_body_write_tool(operation)
            elif kind == "params_write":
                method = self._make_params_write_tool(operation)
            else:
                raise ValueError(f"Unsupported tool kind: {kind}")
            setattr(self, attr_name, method)
            self._generated_tool_names.append(attr_name)

    def register_tools(self, server: FastMCP) -> None:
        for attr_name, _operation, _kind, annotations in self.TOOL_SPECS:
            self._add_tool(server=server, method=getattr(self, attr_name), name=attr_name, annotations=annotations)

    def register_resources(self, server: FastMCP) -> None:
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://mssp/usage-guide"),
                name="falcon_mssp_usage_guide",
                description="Usage guidance for MSSP (Flight Control) tools.",
                text=MSSP_USAGE_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://mssp/safety-guide"),
                name="falcon_mssp_safety_guide",
                description="Safety guidance for MSSP (Flight Control) write tools.",
                text=MSSP_SAFETY_GUIDE,
            ),
        )

    def _make_params_read_tool(self, operation: str) -> Callable[..., list[dict[str, Any]]]:
        def tool(parameters: dict[str, Any] | None = Field(default=None, description="Full query parameters payload.")) -> list[dict[str, Any]]:
            result = self._base_query_api_call(
                operation=operation,
                query_params=parameters or {},
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_body_read_tool(self, operation: str) -> Callable[..., list[dict[str, Any]]]:
        def tool(body: dict[str, Any] | None = None) -> list[dict[str, Any]]:
            if body is None:
                return [_format_error_response("Provide `body` to execute this Flight Control operation.", operation=operation)]
            result = self._base_query_api_call(
                operation=operation,
                body_params=body,
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_body_write_tool(self, operation: str) -> Callable[..., list[dict[str, Any]]]:
        def tool(confirm_execution: bool = Field(default=False), body: dict[str, Any] | None = None) -> list[dict[str, Any]]:
            if not confirm_execution:
                return [_format_error_response("This operation requires `confirm_execution=true`.", operation=operation)]
            if body is None:
                return [_format_error_response("Provide `body` to execute this Flight Control write operation.", operation=operation)]
            result = self._base_query_api_call(
                operation=operation,
                body_params=body,
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool

    def _make_params_write_tool(self, operation: str) -> Callable[..., list[dict[str, Any]]]:
        def tool(confirm_execution: bool = Field(default=False), parameters: dict[str, Any] | None = Field(default=None, description="Full query parameters payload.")) -> list[dict[str, Any]]:
            if not confirm_execution:
                return [_format_error_response("This operation requires `confirm_execution=true`.", operation=operation)]
            if parameters is None:
                return [_format_error_response("Provide `parameters` to execute this Flight Control write operation.", operation=operation)]
            result = self._base_query_api_call(
                operation=operation,
                query_params=parameters,
                error_message=f"Failed to execute {operation}",
                default_result=[],
            )
            if self._is_error(result):
                return [result]
            return result

        tool.__name__ = f"{operation}_tool"
        return tool
