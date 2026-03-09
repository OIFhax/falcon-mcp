"""
Hosts module for Falcon MCP Server.

This module provides tools for Hosts, Host Groups, and Host Migration.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.hosts import (
    SEARCH_HOSTS_FQL_DOCUMENTATION,
    SEARCH_HOST_GROUPS_FQL_DOCUMENTATION,
    SEARCH_HOST_MIGRATIONS_FQL_DOCUMENTATION,
    SEARCH_MIGRATIONS_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


MUTATING_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)

DESTRUCTIVE_TOOL_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=True,
)


class HostsModule(BaseModule):
    """Module for managing Falcon hosts, host groups, and host migrations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(server=server, method=self.search_hosts, name="search_hosts")
        self._add_tool(server=server, method=self.get_host_details, name="get_host_details")

        self._add_tool(server=server, method=self.search_host_groups, name="search_host_groups")
        self._add_tool(
            server=server,
            method=self.search_host_group_members,
            name="search_host_group_members",
        )
        self._add_tool(
            server=server,
            method=self.add_host_group,
            name="add_host_group",
            annotations=MUTATING_TOOL_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_host_group,
            name="update_host_group",
            annotations=MUTATING_TOOL_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.remove_host_groups,
            name="remove_host_groups",
            annotations=DESTRUCTIVE_TOOL_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.perform_host_group_action,
            name="perform_host_group_action",
            annotations=MUTATING_TOOL_ANNOTATIONS,
        )

        self._add_tool(server=server, method=self.search_migrations, name="search_migrations")
        self._add_tool(
            server=server,
            method=self.search_host_migrations,
            name="search_host_migrations",
        )
        self._add_tool(
            server=server,
            method=self.create_migration,
            name="create_migration",
            annotations=MUTATING_TOOL_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.get_migration_destinations,
            name="get_migration_destinations",
        )
        self._add_tool(
            server=server,
            method=self.perform_migration_action,
            name="perform_migration_action",
            annotations=MUTATING_TOOL_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.perform_host_migration_action,
            name="perform_host_migration_action",
            annotations=MUTATING_TOOL_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://hosts/search/fql-guide"),
                name="falcon_search_hosts_fql_guide",
                description="Contains the guide for the `filter` parameter of the `falcon_search_hosts` tool.",
                text=SEARCH_HOSTS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://hosts/groups/fql-guide"),
                name="falcon_search_host_groups_fql_guide",
                description="Contains the guide for the `filter` parameter of host group search tools.",
                text=SEARCH_HOST_GROUPS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://hosts/migrations/fql-guide"),
                name="falcon_search_migrations_fql_guide",
                description="Contains the guide for the `filter` parameter of the `falcon_search_migrations` tool.",
                text=SEARCH_MIGRATIONS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://hosts/host-migrations/fql-guide"),
                name="falcon_search_host_migrations_fql_guide",
                description="Contains the guide for the `filter` parameter of the `falcon_search_host_migrations` tool.",
                text=SEARCH_HOST_MIGRATIONS_FQL_DOCUMENTATION,
            ),
        )

    def search_hosts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit host search results. IMPORTANT: use the `falcon://hosts/search/fql-guide` resource when building this filter parameter.",
            examples={"platform_name:'Windows'", "hostname:'PC*'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="The maximum records to return. [1-5000]",
        ),
        offset: int | None = Field(
            default=None,
            description="The offset to start retrieving records from.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort hosts using FQL syntax.

                Supported formats: `field.asc`, `field.desc`, `field|asc`, `field|desc`.
                Common fields: hostname, last_seen, first_seen, modified_timestamp,
                platform_name, agent_version, os_version, external_ip.
            """).strip(),
            examples={"hostname.asc", "last_seen.desc"},
        ),
    ) -> list[dict[str, Any]]:
        """Search for hosts and return full host details."""
        device_ids = self._base_search_api_call(
            operation="QueryDevicesByFilter",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search hosts",
        )

        if self._is_error(device_ids):
            return [device_ids]

        if not device_ids:
            return []

        details = self._base_get_by_ids(
            operation="PostDeviceDetailsV2",
            ids=device_ids,
            id_key="ids",
        )

        if self._is_error(details):
            return [details]

        return details

    def get_host_details(
        self,
        ids: list[str] = Field(
            description="Host device IDs to retrieve details for. You can get IDs from search results, Falcon console, or Streaming API. Maximum: 5000 IDs per request."
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Retrieve detailed information for specific host device IDs."""
        logger.debug("Getting host details for IDs: %s", ids)
        if not ids:
            return []

        return self._base_get_by_ids(
            operation="PostDeviceDetailsV2",
            ids=ids,
            id_key="ids",
        )

    def search_host_groups(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit host group search results. IMPORTANT: use the `falcon://hosts/groups/fql-guide` resource when building this filter parameter.",
            examples={"group_type:'static'", "name:'Server*'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of host group IDs to return. [1-5000]",
        ),
        offset: int | None = Field(
            default=None,
            description="Offset in the overall result set.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort host groups using FQL syntax.

                Supported fields: created_by, created_timestamp, group_type,
                modified_by, modified_timestamp, name.

                Supported formats: `field.asc`, `field.desc`, `field|asc`, `field|desc`.
            """).strip(),
            examples={"modified_timestamp.desc", "name|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search host groups and return full host group details."""
        host_group_ids = self._base_search_api_call(
            operation="queryHostGroups",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search host groups",
        )

        if self._is_error(host_group_ids):
            if filter:
                return self._format_fql_error_response(
                    [host_group_ids], filter, SEARCH_HOST_GROUPS_FQL_DOCUMENTATION
                )
            return [host_group_ids]

        if not host_group_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_HOST_GROUPS_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="getHostGroups",
            ids=host_group_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_host_group_members(
        self,
        group_id: str = Field(
            description="Host group ID to search members within.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit host group member search results. IMPORTANT: use the `falcon://hosts/groups/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=5000,
            description="Maximum number of host group members to return. [1-5000]",
        ),
        offset: int | None = Field(
            default=None,
            description="Offset in the overall result set.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression in FQL syntax.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search members in a host group and return full host details."""
        members = self._base_search_api_call(
            operation="queryCombinedGroupMembers",
            search_params={
                "id": group_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search host group members",
        )

        if self._is_error(members):
            if filter:
                return self._format_fql_error_response(
                    [members], filter, SEARCH_HOST_GROUPS_FQL_DOCUMENTATION
                )
            return [members]

        if not members and filter:
            return self._format_fql_error_response([], filter, SEARCH_HOST_GROUPS_FQL_DOCUMENTATION)

        return members

    def add_host_group(
        self,
        name: str | None = Field(
            default=None,
            description="Host group name. Required when `body` is not provided.",
        ),
        group_type: str = Field(
            default="static",
            description="Host group type. Common values: static, dynamic.",
        ),
        description: str | None = Field(
            default=None,
            description="Host group description.",
        ),
        assignment_rule: str | None = Field(
            default=None,
            description="Assignment rule for dynamic host groups.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a host group."""
        request_body = body
        if request_body is None:
            if not name:
                return [
                    _format_error_response(
                        "`name` is required when `body` is not provided.",
                        operation="createHostGroups",
                    )
                ]

            host_group = {
                "name": name,
                "group_type": group_type,
            }
            if description:
                host_group["description"] = description
            if assignment_rule:
                host_group["assignment_rule"] = assignment_rule

            request_body = {"resources": [host_group]}

        result = self._base_query_api_call(
            operation="createHostGroups",
            body_params=request_body,
            error_message="Failed to create host group",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_host_group(
        self,
        id: str | None = Field(
            default=None,
            description="Host group ID to update. Required when `body` is not provided.",
        ),
        name: str | None = Field(
            default=None,
            description="Updated host group name.",
        ),
        group_type: str | None = Field(
            default=None,
            description="Updated host group type.",
        ),
        description: str | None = Field(
            default=None,
            description="Updated host group description.",
        ),
        assignment_rule: str | None = Field(
            default=None,
            description="Updated assignment rule for dynamic host groups.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Update a host group."""
        request_body = body
        if request_body is None:
            if not id:
                return [
                    _format_error_response(
                        "`id` is required when `body` is not provided.",
                        operation="updateHostGroups",
                    )
                ]

            host_group = {"id": id}
            optional_values = {
                "name": name,
                "group_type": group_type,
                "description": description,
                "assignment_rule": assignment_rule,
            }
            for key, value_ in optional_values.items():
                if value_ is not None:
                    host_group[key] = value_

            if len(host_group) == 1:
                return [
                    _format_error_response(
                        "Provide at least one host group field to update alongside `id`.",
                        operation="updateHostGroups",
                    )
                ]

            request_body = {"resources": [host_group]}

        result = self._base_query_api_call(
            operation="updateHostGroups",
            body_params=request_body,
            error_message="Failed to update host group",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def remove_host_groups(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Host group IDs to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete host groups by IDs."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required when deleting host groups.",
                    operation="deleteHostGroups",
                )
            ]

        result = self._base_query_api_call(
            operation="deleteHostGroups",
            query_params={
                "ids": ids,
            },
            error_message="Failed to delete host groups",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def perform_host_group_action(
        self,
        action_name: str | None = Field(
            default=None,
            description="Host group action to perform. Supported values: add-hosts, remove-hosts.",
        ),
        group_ids: list[str] | None = Field(
            default=None,
            description="Host group IDs to target with this action.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter that selects hosts for add/remove operations.",
        ),
        action_parameters: list[dict[str, str]] | None = Field(
            default=None,
            description="Optional action parameter objects. Overrides `filter` when provided.",
        ),
        disable_hostname_check: bool | None = Field(
            default=None,
            description="Disable hostname validation before action execution.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action against one or more host groups."""
        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required to perform a host group action.",
                    operation="performGroupAction",
                )
            ]

        request_body = body
        if request_body is None:
            if not group_ids:
                return [
                    _format_error_response(
                        "`group_ids` is required when `body` is not provided.",
                        operation="performGroupAction",
                    )
                ]

            if not filter and not action_parameters:
                return [
                    _format_error_response(
                        "Provide either `filter` or `action_parameters` when `body` is not provided.",
                        operation="performGroupAction",
                    )
                ]

            request_body = {"ids": group_ids}
            if action_parameters:
                request_body["action_parameters"] = action_parameters
            else:
                request_body["action_parameters"] = [{"name": "filter", "value": filter}]

        result = self._base_query_api_call(
            operation="performGroupAction",
            query_params={
                "action_name": action_name,
                "disable_hostname_check": disable_hostname_check,
            },
            body_params=request_body,
            error_message="Failed to perform host group action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_migrations(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit migration job search results. IMPORTANT: use the `falcon://hosts/migrations/fql-guide` resource when building this filter parameter.",
            examples={"status:'pending'", "target_cid:'0123456789ABCDEF0123456789ABCDEF'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=10000,
            description="Maximum number of migration IDs to return. [1-10000]",
        ),
        offset: int | None = Field(
            default=None,
            description="Offset in the overall result set.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort migration jobs using FQL syntax.

                Common fields: status, migration_status, created_by, created_time,
                name, id, migration_id, target_cid.
            """).strip(),
            examples={"created_time.desc", "name|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search migration jobs and return full migration details."""
        migration_ids = self._base_search_api_call(
            operation="GetMigrationIDsV1",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search migrations",
        )

        if self._is_error(migration_ids):
            if filter:
                return self._format_fql_error_response(
                    [migration_ids], filter, SEARCH_MIGRATIONS_FQL_DOCUMENTATION
                )
            return [migration_ids]

        if not migration_ids:
            if filter:
                return self._format_fql_error_response([], filter, SEARCH_MIGRATIONS_FQL_DOCUMENTATION)
            return []

        details = self._base_get_by_ids(
            operation="GetMigrationsV1",
            ids=migration_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def search_host_migrations(
        self,
        migration_id: str = Field(
            description="Migration job ID to search host migration entities for.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter to limit host migration search results. IMPORTANT: use the `falcon://hosts/host-migrations/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=10000,
            description="Maximum number of host migration IDs to return. [1-10000]",
        ),
        offset: int | None = Field(
            default=None,
            description="Offset in the overall result set.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression in FQL syntax.",
            examples={"hostname|asc", "created_time.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search host migration entities and return full host migration details."""
        host_migration_ids = self._base_search_api_call(
            operation="GetHostMigrationIDsV1",
            search_params={
                "id": migration_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search host migrations",
        )

        if self._is_error(host_migration_ids):
            if filter:
                return self._format_fql_error_response(
                    [host_migration_ids], filter, SEARCH_HOST_MIGRATIONS_FQL_DOCUMENTATION
                )
            return [host_migration_ids]

        if not host_migration_ids:
            if filter:
                return self._format_fql_error_response(
                    [], filter, SEARCH_HOST_MIGRATIONS_FQL_DOCUMENTATION
                )
            return []

        details = self._base_get_by_ids(
            operation="GetHostMigrationsV1",
            ids=host_migration_ids,
        )

        if self._is_error(details):
            return [details]

        return details

    def create_migration(
        self,
        target_cid: str | None = Field(
            default=None,
            description="Target CID to migrate hosts to. Required when `body` is not provided.",
        ),
        name: str | None = Field(
            default=None,
            description="Migration job name.",
        ),
        device_ids: list[str] | None = Field(
            default=None,
            description="Device IDs to include in the migration job.",
        ),
        filter: str | None = Field(
            default=None,
            description="FQL filter used to select hosts for migration.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Create a host migration job."""
        request_body = body
        if request_body is None:
            if not target_cid:
                return [
                    _format_error_response(
                        "`target_cid` is required when `body` is not provided.",
                        operation="CreateMigrationV1",
                    )
                ]

            if not device_ids and not filter:
                return [
                    _format_error_response(
                        "Provide either `device_ids` or `filter` when `body` is not provided.",
                        operation="CreateMigrationV1",
                    )
                ]

            request_body = {
                "target_cid": target_cid,
            }
            if name:
                request_body["name"] = name
            if device_ids:
                request_body["device_ids"] = device_ids
            if filter:
                request_body["filter"] = filter

        result = self._base_query_api_call(
            operation="CreateMigrationV1",
            body_params=request_body,
            error_message="Failed to create migration",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def get_migration_destinations(
        self,
        device_ids: list[str] | None = Field(
            default=None,
            description="Optional host device IDs used to resolve migration destinations.",
        ),
        filter: str | None = Field(
            default=None,
            description="Optional FQL filter used to resolve migration destinations.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Get available migration destinations for selected hosts."""
        request_body = body
        if request_body is None:
            if not device_ids and not filter:
                return [
                    _format_error_response(
                        "Provide `body`, `device_ids`, or `filter` to get migration destinations.",
                        operation="GetMigrationDestinationsV1",
                    )
                ]
            request_body = {}
            if device_ids:
                request_body["device_ids"] = device_ids
            if filter:
                request_body["filter"] = filter

        result = self._base_query_api_call(
            operation="GetMigrationDestinationsV1",
            body_params=request_body,
            error_message="Failed to get migration destinations",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def perform_migration_action(
        self,
        action_name: str | None = Field(
            default=None,
            description="Migration action to perform. Supported values: start_migration, cancel_migration, rename_migration, delete_migration.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Migration IDs targeted by this action.",
        ),
        filter: str | None = Field(
            default=None,
            description="Optional FQL filter used to target migration IDs.",
        ),
        action_parameters: list[dict[str, str]] | None = Field(
            default=None,
            description="Optional action parameter objects (for example, rename payload).",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action on migration jobs."""
        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required to perform a migration action.",
                    operation="MigrationsActionsV1",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids and not filter:
                return [
                    _format_error_response(
                        "Provide either `ids` or `filter` when `body` is not provided.",
                        operation="MigrationsActionsV1",
                    )
                ]

            request_body = {}
            if ids:
                request_body["ids"] = ids
            if filter:
                request_body["filter"] = filter
            if action_parameters:
                request_body["action_parameters"] = action_parameters

        result = self._base_query_api_call(
            operation="MigrationsActionsV1",
            query_params={"action_name": action_name},
            body_params=request_body,
            error_message="Failed to perform migration action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def perform_host_migration_action(
        self,
        migration_id: str | None = Field(
            default=None,
            description="Migration job ID to perform host migration actions within.",
        ),
        action_name: str | None = Field(
            default=None,
            description="Host migration action to perform. Supported values: remove_hosts, remove_host_groups, add_host_groups.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Host migration entity IDs targeted by this action.",
        ),
        filter: str | None = Field(
            default=None,
            description="Optional FQL filter used to target host migration entities.",
        ),
        action_parameters: list[dict[str, str]] | None = Field(
            default=None,
            description="Optional action parameter objects (for example, host_group bindings).",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body override. If provided, convenience fields are ignored.",
        ),
    ) -> list[dict[str, Any]]:
        """Perform an action on host migration entities."""
        if not migration_id:
            return [
                _format_error_response(
                    "`migration_id` is required to perform a host migration action.",
                    operation="HostMigrationsActionsV1",
                )
            ]
        if not action_name:
            return [
                _format_error_response(
                    "`action_name` is required to perform a host migration action.",
                    operation="HostMigrationsActionsV1",
                )
            ]

        request_body = body
        if request_body is None:
            if not ids and not filter:
                return [
                    _format_error_response(
                        "Provide either `ids` or `filter` when `body` is not provided.",
                        operation="HostMigrationsActionsV1",
                    )
                ]

            request_body = {}
            if ids:
                request_body["ids"] = ids
            if filter:
                request_body["filter"] = filter
            if action_parameters:
                request_body["action_parameters"] = action_parameters

        result = self._base_query_api_call(
            operation="HostMigrationsActionsV1",
            query_params={
                "id": migration_id,
                "action_name": action_name,
            },
            body_params=request_body,
            error_message="Failed to perform host migration action",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
