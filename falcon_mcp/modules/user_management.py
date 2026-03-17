"""
User Management module for Falcon MCP Server.

This module provides tools for searching users/roles and performing controlled
user and role assignment changes through Falcon User Management APIs.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.user_management import (
    SEARCH_USERS_FQL_DOCUMENTATION,
    USER_MANAGEMENT_SAFETY_GUIDE,
    USER_ROLE_GRANTS_FQL_DOCUMENTATION,
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


class UserManagementModule(BaseModule):
    """Module for Falcon User Management operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.aggregate_users,
            name="aggregate_users",
        )
        self._add_tool(
            server=server,
            method=self.search_users,
            name="search_users",
        )
        self._add_tool(
            server=server,
            method=self.get_user_details,
            name="get_user_details",
        )
        self._add_tool(
            server=server,
            method=self.search_user_roles,
            name="search_user_roles",
        )
        self._add_tool(
            server=server,
            method=self.get_user_role_details,
            name="get_user_role_details",
        )
        self._add_tool(
            server=server,
            method=self.get_user_role_details_v1,
            name="get_user_role_details_v1",
        )
        self._add_tool(
            server=server,
            method=self.get_user_role_grants,
            name="get_user_role_grants",
        )
        self._add_tool(
            server=server,
            method=self.create_user,
            name="create_user",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_user,
            name="update_user",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_user,
            name="delete_user",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.perform_user_action,
            name="perform_user_action",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.grant_user_roles,
            name="grant_user_roles",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.revoke_user_roles,
            name="revoke_user_roles",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_users_fql_resource = TextResource(
            uri=AnyUrl("falcon://user-management/users/fql-guide"),
            name="falcon_search_users_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_users` tool.",
            text=SEARCH_USERS_FQL_DOCUMENTATION,
        )

        user_role_grants_fql_resource = TextResource(
            uri=AnyUrl("falcon://user-management/user-role-grants/fql-guide"),
            name="falcon_user_role_grants_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_get_user_role_grants` tool.",
            text=USER_ROLE_GRANTS_FQL_DOCUMENTATION,
        )

        user_management_safety_resource = TextResource(
            uri=AnyUrl("falcon://user-management/safety-guide"),
            name="falcon_user_management_safety_guide",
            description="Safety and operational guidance for User Management write tools.",
            text=USER_MANAGEMENT_SAFETY_GUIDE,
        )

        self._add_resource(server, search_users_fql_resource)
        self._add_resource(server, user_role_grants_fql_resource)
        self._add_resource(server, user_management_safety_resource)

    def aggregate_users(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Aggregation specification body for `aggregateUsersV1`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate analysis over user-management records."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for user aggregation.",
                    operation="aggregateUsersV1",
                )
            ]

        command_response = self.client.command("aggregateUsersV1", body=body)
        result = handle_api_response(
            command_response,
            operation="aggregateUsersV1",
            error_message="Failed to aggregate users",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_users(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit user search results. IMPORTANT: use the `falcon://user-management/users/fql-guide` resource when building this filter parameter.",
            examples={"uid:'analyst@example.com'", "status:'active'"},
        ),
        limit: int = Field(
            default=20,
            ge=1,
            le=500,
            description="Maximum number of user UUIDs to return from search. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return user UUIDs.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort users using FQL sort syntax.

                Common fields include:
                cid_name, created_at, first_name, has_temporary_roles, last_login_at,
                last_name, name, status, temporarily_assigned_cids, uid

                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
                Examples: 'last_login_at.desc', 'uid|asc'
            """).strip(),
            examples={"last_login_at.desc", "uid|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search users and return full user details."""
        user_ids = self._base_search_api_call(
            operation="queryUserV1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search users",
        )

        if self._is_error(user_ids):
            return self._format_fql_error_response(
                [user_ids], filter, SEARCH_USERS_FQL_DOCUMENTATION
            )

        if not user_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_USERS_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="retrieveUsersGETV1",
            ids=user_ids,
            id_key="ids",
            use_params=False,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_user_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="User UUIDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve user records by user UUID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve user details.",
                    operation="retrieveUsersGETV1",
                )
            ]

        result = self._base_get_by_ids(
            operation="retrieveUsersGETV1",
            ids=ids,
            id_key="ids",
            use_params=False,
        )

        if self._is_error(result):
            return [result]

        return result

    def search_user_roles(
        self,
        user_uuid: str | None = Field(
            default=None,
            description="Optional user UUID to return roles relevant to one user.",
        ),
        cid: str | None = Field(
            default=None,
            description="Optional CID for Flight Control role queries.",
        ),
        action: str = Field(
            default="grant",
            description="Action context for role query (usually `grant`).",
            examples={"grant"},
        ),
    ) -> list[dict[str, Any]]:
        """Search roles and return full role details."""
        role_ids = self._base_search_api_call(
            operation="queriesRolesV1",
            search_params={
                "user_uuid": user_uuid,
                "cid": cid,
                "action": action,
            },
            error_message="Failed to search user roles",
        )

        if self._is_error(role_ids):
            return [role_ids]

        if not role_ids:
            return []

        result = self.get_user_role_details(
            ids=role_ids,
            cid=cid,
        )

        return result

    def get_user_role_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Role IDs to retrieve using `entitiesRolesGETV2`.",
        ),
        cid: str | None = Field(
            default=None,
            description="Optional CID for Flight Control role detail retrieval.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve role records by role ID using entitiesRolesGETV2."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve role details.",
                    operation="entitiesRolesGETV2",
                )
            ]

        result = self._base_query_api_call(
            operation="entitiesRolesGETV2",
            query_params={"cid": cid},
            body_params={"ids": ids},
            error_message="Failed to retrieve role details",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_user_role_details_v1(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Role IDs to retrieve using legacy `entitiesRolesV1`.",
        ),
        cid: str | None = Field(
            default=None,
            description="Optional CID for Flight Control role detail retrieval.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve role records by role ID using entitiesRolesV1."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve role details.",
                    operation="entitiesRolesV1",
                )
            ]

        result = self._base_query_api_call(
            operation="entitiesRolesV1",
            query_params={"ids": ids, "cid": cid},
            error_message="Failed to retrieve role details (v1)",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_user_role_grants(
        self,
        user_uuid: str | None = Field(
            default=None,
            description="User UUID to retrieve grants for.",
        ),
        cid: str | None = Field(
            default=None,
            description="Optional CID for Flight Control role-grant view.",
        ),
        direct_only: bool | None = Field(
            default=None,
            description="If true, return direct grants only.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter for role grants. IMPORTANT: use the `falcon://user-management/user-role-grants/fql-guide` resource when building this filter parameter.",
            examples={"role_name:'Falcon Administrator'", "role_id:'abcd1234'"},
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="Maximum number of role grants to return. [1-500]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return role grants.",
        ),
        sort: str | None = Field(
            default=None,
            description="FQL sort expression for role grants (for example, `expires_at|asc`).",
            examples={"expires_at|asc", "role_name|desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve user role grants for a specific user UUID."""
        if not user_uuid:
            return _format_error_response(
                "`user_uuid` is required to retrieve user role grants.",
                operation="CombinedUserRolesV2",
            )

        result = self._base_query_api_call(
            operation="CombinedUserRolesV2",
            query_params={
                "user_uuid": user_uuid,
                "cid": cid,
                "direct_only": direct_only,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to get user role grants",
            default_result=[],
        )

        if self._is_error(result):
            if filter:
                return self._format_fql_error_response(
                    [result], filter, USER_ROLE_GRANTS_FQL_DOCUMENTATION
                )
            return [result]

        if not result and filter:
            return self._format_fql_error_response(
                [], filter, USER_ROLE_GRANTS_FQL_DOCUMENTATION
            )

        return result

    def create_user(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        uid: str | None = Field(
            default=None,
            description="User login identifier (typically email). Required.",
        ),
        first_name: str | None = Field(
            default=None,
            description="First name for the user account.",
        ),
        last_name: str | None = Field(
            default=None,
            description="Last name for the user account.",
        ),
        password: str | None = Field(
            default=None,
            description="Optional initial password. Omit when using activation or SSO workflows.",
        ),
        cid: str | None = Field(
            default=None,
            description="Optional CID for Flight Control user creation.",
        ),
        validate_only: bool = Field(
            default=False,
            description="When true, validates payload but does not create the user.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a user (or validate the creation payload)."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="createUserV1",
                )
            ]

        if not uid:
            return [
                _format_error_response(
                    "`uid` is required to create a user.",
                    operation="createUserV1",
                )
            ]

        result = self._base_query_api_call(
            operation="createUserV1",
            query_params={"validate_only": validate_only},
            body_params={
                "uid": uid,
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
                "cid": cid,
            },
            error_message="Failed to create user",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_user(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        user_uuid: str | None = Field(
            default=None,
            description="User UUID to update.",
        ),
        first_name: str | None = Field(
            default=None,
            description="Updated first name. Required with `last_name`.",
        ),
        last_name: str | None = Field(
            default=None,
            description="Updated last name. Required with `first_name`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update a user's first and last name."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="updateUserV1",
                )
            ]

        if not user_uuid:
            return [
                _format_error_response(
                    "`user_uuid` is required to update a user.",
                    operation="updateUserV1",
                )
            ]

        if not first_name or not last_name:
            return [
                _format_error_response(
                    "`first_name` and `last_name` are required to update a user.",
                    operation="updateUserV1",
                )
            ]

        result = self._base_query_api_call(
            operation="updateUserV1",
            query_params={"user_uuid": user_uuid},
            body_params={"first_name": first_name, "last_name": last_name},
            error_message="Failed to update user",
            default_result=[
                {
                    "user_uuid": user_uuid,
                    "first_name": first_name,
                    "last_name": last_name,
                    "status": "submitted",
                }
            ],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_user(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this destructive operation.",
        ),
        user_uuid: str | None = Field(
            default=None,
            description="User UUID to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete a user by user UUID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="deleteUserV1",
                )
            ]

        if not user_uuid:
            return [
                _format_error_response(
                    "`user_uuid` is required to delete a user.",
                    operation="deleteUserV1",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteUserV1",
            query_params={"user_uuid": user_uuid},
            error_message="Failed to delete user",
            default_result=[{"user_uuid": user_uuid, "status": "submitted"}],
        )

        if self._is_error(result):
            return [result]

        return result

    def perform_user_action(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this destructive operation.",
        ),
        action_name: str | None = Field(
            default=None,
            description="Action to apply. Supported values: `reset_2fa`, `reset_password`.",
            examples={"reset_password", "reset_2fa"},
        ),
        user_uuids: list[str] | None = Field(
            default=None,
            description="User UUIDs to apply the action to.",
        ),
        action_value: str | None = Field(
            default=None,
            description="Optional action value parameter.",
        ),
    ) -> list[dict[str, Any]]:
        """Apply user actions such as password or 2FA reset."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="userActionV1",
                )
            ]

        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required to perform a user action.",
                    operation="userActionV1",
                )
            ]

        if action_name not in {"reset_2fa", "reset_password"}:
            return [
                _format_error_response(
                    "`action_name` must be one of: `reset_2fa`, `reset_password`.",
                    operation="userActionV1",
                )
            ]

        if not user_uuids:
            return [
                _format_error_response(
                    "`user_uuids` is required to perform a user action.",
                    operation="userActionV1",
                )
            ]

        action_payload: dict[str, Any] = {"action_name": action_name}
        if action_value is not None:
            action_payload["action_value"] = action_value

        result = self._base_query_api_call(
            operation="userActionV1",
            body_params={"ids": user_uuids, "action": action_payload},
            error_message="Failed to perform user action",
            default_result=[
                {
                    "action_name": action_name,
                    "user_uuids": user_uuids,
                    "status": "submitted",
                }
            ],
        )

        if self._is_error(result):
            return [result]

        return result

    def grant_user_roles(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        user_uuid: str | None = Field(
            default=None,
            description="User UUID to grant roles to.",
        ),
        role_ids: list[str] | None = Field(
            default=None,
            description="Role IDs to grant.",
        ),
        cid: str | None = Field(
            default=None,
            description="Optional CID for Flight Control role grant actions.",
        ),
    ) -> list[dict[str, Any]]:
        """Grant one or more roles to a user."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="userRolesActionV1",
                )
            ]

        if not user_uuid:
            return [
                _format_error_response(
                    "`user_uuid` is required to grant roles.",
                    operation="userRolesActionV1",
                )
            ]

        if not role_ids:
            return [
                _format_error_response(
                    "`role_ids` is required to grant roles.",
                    operation="userRolesActionV1",
                )
            ]

        request_body: dict[str, Any] = {
            "action": "grant",
            "uuid": user_uuid,
            "role_ids": role_ids,
        }
        if cid:
            request_body["cid"] = cid

        result = self._base_query_api_call(
            operation="userRolesActionV1",
            body_params=request_body,
            error_message="Failed to grant user roles",
            default_result=[
                {
                    "action": "grant",
                    "uuid": user_uuid,
                    "role_ids": role_ids,
                    "status": "submitted",
                }
            ],
        )

        if self._is_error(result):
            return [result]

        return result

    def revoke_user_roles(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this destructive operation.",
        ),
        user_uuid: str | None = Field(
            default=None,
            description="User UUID to revoke roles from.",
        ),
        role_ids: list[str] | None = Field(
            default=None,
            description="Role IDs to revoke.",
        ),
        cid: str | None = Field(
            default=None,
            description="Optional CID for Flight Control role revoke actions.",
        ),
    ) -> list[dict[str, Any]]:
        """Revoke one or more roles from a user."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="userRolesActionV1",
                )
            ]

        if not user_uuid:
            return [
                _format_error_response(
                    "`user_uuid` is required to revoke roles.",
                    operation="userRolesActionV1",
                )
            ]

        if not role_ids:
            return [
                _format_error_response(
                    "`role_ids` is required to revoke roles.",
                    operation="userRolesActionV1",
                )
            ]

        request_body: dict[str, Any] = {
            "action": "revoke",
            "uuid": user_uuid,
            "role_ids": role_ids,
        }
        if cid:
            request_body["cid"] = cid

        result = self._base_query_api_call(
            operation="userRolesActionV1",
            body_params=request_body,
            error_message="Failed to revoke user roles",
            default_result=[
                {
                    "action": "revoke",
                    "uuid": user_uuid,
                    "role_ids": role_ids,
                    "status": "submitted",
                }
            ],
        )

        if self._is_error(result):
            return [result]

        return result
