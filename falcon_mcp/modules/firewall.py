"""
Firewall Management module for Falcon MCP Server.

This module provides full Falcon Firewall Management service collection coverage:
query/get/aggregate operations for rules, rule groups, policy rules, events, fields,
platforms, policy containers, and network locations, plus write lifecycle operations.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.firewall import (
    FIREWALL_MANAGEMENT_SAFETY_GUIDE,
    SEARCH_FIREWALL_EVENTS_FQL_DOCUMENTATION,
    SEARCH_FIREWALL_NETWORK_LOCATIONS_FQL_DOCUMENTATION,
    SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
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


class FirewallModule(BaseModule):
    """Module for Falcon Firewall Management operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_firewall_rules, name="search_firewall_rules")
        self._add_tool(
            server=server,
            method=self.search_firewall_rule_groups,
            name="search_firewall_rule_groups",
        )
        self._add_tool(
            server=server,
            method=self.search_firewall_policy_rules,
            name="search_firewall_policy_rules",
        )
        self._add_tool(server=server, method=self.query_firewall_rule_ids, name="query_firewall_rule_ids")
        self._add_tool(
            server=server,
            method=self.query_firewall_rule_group_ids,
            name="query_firewall_rule_group_ids",
        )
        self._add_tool(
            server=server,
            method=self.query_firewall_policy_rule_ids,
            name="query_firewall_policy_rule_ids",
        )
        self._add_tool(server=server, method=self.get_firewall_rules, name="get_firewall_rules")
        self._add_tool(server=server, method=self.get_firewall_rule_groups, name="get_firewall_rule_groups")
        self._add_tool(server=server, method=self.aggregate_firewall_rules, name="aggregate_firewall_rules")
        self._add_tool(
            server=server,
            method=self.aggregate_firewall_rule_groups,
            name="aggregate_firewall_rule_groups",
        )
        self._add_tool(
            server=server,
            method=self.aggregate_firewall_policy_rules,
            name="aggregate_firewall_policy_rules",
        )
        self._add_tool(server=server, method=self.aggregate_firewall_events, name="aggregate_firewall_events")
        self._add_tool(server=server, method=self.query_firewall_event_ids, name="query_firewall_event_ids")
        self._add_tool(server=server, method=self.get_firewall_events, name="get_firewall_events")
        self._add_tool(server=server, method=self.query_firewall_field_ids, name="query_firewall_field_ids")
        self._add_tool(server=server, method=self.get_firewall_fields, name="get_firewall_fields")
        self._add_tool(server=server, method=self.query_firewall_platform_ids, name="query_firewall_platform_ids")
        self._add_tool(server=server, method=self.get_firewall_platforms, name="get_firewall_platforms")
        self._add_tool(
            server=server,
            method=self.get_firewall_policy_containers,
            name="get_firewall_policy_containers",
        )
        self._add_tool(
            server=server,
            method=self.create_firewall_rule_group,
            name="create_firewall_rule_group",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_firewall_rule_group,
            name="update_firewall_rule_group",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_firewall_rule_groups,
            name="delete_firewall_rule_groups",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.validate_firewall_rule_group_create,
            name="validate_firewall_rule_group_create",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.validate_firewall_rule_group_update,
            name="validate_firewall_rule_group_update",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_firewall_policy_container,
            name="update_firewall_policy_container",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_firewall_policy_container_v1,
            name="update_firewall_policy_container_v1",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.query_firewall_network_location_ids,
            name="query_firewall_network_location_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_firewall_network_locations,
            name="get_firewall_network_locations",
        )
        self._add_tool(
            server=server,
            method=self.get_firewall_network_location_details,
            name="get_firewall_network_location_details",
        )
        self._add_tool(
            server=server,
            method=self.create_firewall_network_locations,
            name="create_firewall_network_locations",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.upsert_firewall_network_locations,
            name="upsert_firewall_network_locations",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_firewall_network_locations,
            name="update_firewall_network_locations",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_firewall_network_locations_metadata,
            name="update_firewall_network_locations_metadata",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_firewall_network_locations_precedence,
            name="update_firewall_network_locations_precedence",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_firewall_network_locations,
            name="delete_firewall_network_locations",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.validate_firewall_filepath_pattern,
            name="validate_firewall_filepath_pattern",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        rules_fql_resource = TextResource(
            uri=AnyUrl("falcon://firewall/rules/fql-guide"),
            name="falcon_search_firewall_rules_fql_guide",
            description="FQL guidance for firewall rules, rule groups, and policy-rule query tools.",
            text=SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
        )

        events_fql_resource = TextResource(
            uri=AnyUrl("falcon://firewall/events/fql-guide"),
            name="falcon_search_firewall_events_fql_guide",
            description="FQL guidance for firewall events query tools.",
            text=SEARCH_FIREWALL_EVENTS_FQL_DOCUMENTATION,
        )

        network_locations_fql_resource = TextResource(
            uri=AnyUrl("falcon://firewall/network-locations/fql-guide"),
            name="falcon_search_firewall_network_locations_fql_guide",
            description="FQL guidance for firewall network location query tools.",
            text=SEARCH_FIREWALL_NETWORK_LOCATIONS_FQL_DOCUMENTATION,
        )

        safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://firewall/safety-guide"),
            name="falcon_firewall_management_safety_guide",
            description="Safety and operational guidance for firewall management write tools.",
            text=FIREWALL_MANAGEMENT_SAFETY_GUIDE,
        )

        self._add_resource(server, rules_fql_resource)
        self._add_resource(server, events_fql_resource)
        self._add_resource(server, network_locations_fql_resource)
        self._add_resource(server, safety_guide_resource)

    def search_firewall_rules(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall rule search. IMPORTANT: use `falcon://firewall/rules/fql-guide` for filter construction.",
        ),
        limit: int = Field(default=20, ge=1, le=5000, description="Maximum number of records. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression. Example: `modified_on.desc`."),
        q: str | None = Field(default=None, description="Free-text query string."),
        after: str | None = Field(default=None, description="Pagination token from a previous response."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search firewall rules and return full details."""
        rule_ids = self.query_firewall_rule_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            q=q,
            after=after,
        )
        if self._is_error(rule_ids):
            return [rule_ids]
        if isinstance(rule_ids, dict):
            return rule_ids
        if not rule_ids:
            if filter:
                return self._format_fql_error_response(
                    [],
                    filter,
                    SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
                )
            return []
        return self.get_firewall_rules(ids=rule_ids)

    def search_firewall_rule_groups(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall rule-group search. IMPORTANT: use `falcon://firewall/rules/fql-guide` for filter construction.",
        ),
        limit: int = Field(default=20, ge=1, le=5000, description="Maximum number of records. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression. Example: `modified_on.desc`."),
        q: str | None = Field(default=None, description="Free-text query string."),
        after: str | None = Field(default=None, description="Pagination token from a previous response."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search firewall rule groups and return full details."""
        group_ids = self.query_firewall_rule_group_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            q=q,
            after=after,
        )
        if self._is_error(group_ids):
            return [group_ids]
        if isinstance(group_ids, dict):
            return group_ids
        if not group_ids:
            if filter:
                return self._format_fql_error_response(
                    [],
                    filter,
                    SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
                )
            return []
        return self.get_firewall_rule_groups(ids=group_ids)

    def search_firewall_policy_rules(
        self,
        policy_id: str = Field(description="Firewall policy container ID."),
        filter: str | None = Field(
            default=None,
            description="FQL filter for policy-rule search. IMPORTANT: use `falcon://firewall/rules/fql-guide` for filter construction.",
        ),
        limit: int = Field(default=20, ge=1, le=5000, description="Maximum number of records. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression. Example: `modified_on.desc`."),
        q: str | None = Field(default=None, description="Free-text query string."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search rules within a specific policy container and return full details."""
        rule_ids = self.query_firewall_policy_rule_ids(
            policy_id=policy_id,
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            q=q,
        )
        if self._is_error(rule_ids):
            return [rule_ids]
        if isinstance(rule_ids, dict):
            return rule_ids
        if not rule_ids:
            if filter:
                return self._format_fql_error_response(
                    [],
                    filter,
                    SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
                )
            return []
        return self.get_firewall_rules(ids=rule_ids)

    def query_firewall_rule_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall rule ID query. IMPORTANT: use `falcon://firewall/rules/fql-guide`.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query string."),
        after: str | None = Field(default=None, description="Pagination token."),
    ) -> list[str] | dict[str, Any]:
        """Query firewall rule IDs."""
        return self._query_ids_with_fql_guide(
            operation="query_rules",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "after": after,
            },
            error_message="Failed to query firewall rule IDs",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
        )

    def query_firewall_rule_group_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall rule-group ID query. IMPORTANT: use `falcon://firewall/rules/fql-guide`.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query string."),
        after: str | None = Field(default=None, description="Pagination token."),
    ) -> list[str] | dict[str, Any]:
        """Query firewall rule-group IDs."""
        return self._query_ids_with_fql_guide(
            operation="query_rule_groups",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "after": after,
            },
            error_message="Failed to query firewall rule-group IDs",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
        )

    def query_firewall_policy_rule_ids(
        self,
        policy_id: str = Field(description="Firewall policy container ID."),
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall policy-rule ID query. IMPORTANT: use `falcon://firewall/rules/fql-guide`.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query string."),
    ) -> list[str] | dict[str, Any]:
        """Query firewall policy-rule IDs."""
        return self._query_ids_with_fql_guide(
            operation="query_policy_rules",
            search_params={
                "id": policy_id,
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to query firewall policy-rule IDs",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_RULES_FQL_DOCUMENTATION,
        )

    def get_firewall_rules(
        self,
        ids: list[str] | None = Field(default=None, description="Firewall rule IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get firewall rules by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall rules.",
                    operation="get_rules",
                )
            ]
        result = self._base_get_by_ids(
            operation="get_rules",
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def get_firewall_rule_groups(
        self,
        ids: list[str] | None = Field(default=None, description="Firewall rule-group IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get firewall rule groups by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall rule groups.",
                    operation="get_rule_groups",
                )
            ]
        result = self._base_get_by_ids(
            operation="get_rule_groups",
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def aggregate_firewall_rules(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Aggregate request body for `aggregate_rules`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate query against firewall rules."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for aggregate firewall rule queries.",
                    operation="aggregate_rules",
                )
            ]
        result = self._call_firewall_api(
            operation="aggregate_rules",
            body_params=body,
            error_message="Failed to aggregate firewall rules",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def aggregate_firewall_rule_groups(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Aggregate request body for `aggregate_rule_groups`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate query against firewall rule groups."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for aggregate firewall rule-group queries.",
                    operation="aggregate_rule_groups",
                )
            ]
        result = self._call_firewall_api(
            operation="aggregate_rule_groups",
            body_params=body,
            error_message="Failed to aggregate firewall rule groups",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def aggregate_firewall_policy_rules(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Aggregate request body for `aggregate_policy_rules`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate query against firewall policy rules."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for aggregate firewall policy-rule queries.",
                    operation="aggregate_policy_rules",
                )
            ]
        result = self._call_firewall_api(
            operation="aggregate_policy_rules",
            body_params=body,
            error_message="Failed to aggregate firewall policy rules",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def aggregate_firewall_events(
        self,
        body: list[dict[str, Any]] | None = Field(
            default=None,
            description="Aggregate request body for `aggregate_events`.",
        ),
    ) -> list[dict[str, Any]]:
        """Run aggregate query against firewall events."""
        if not body:
            return [
                _format_error_response(
                    "`body` is required for aggregate firewall events queries.",
                    operation="aggregate_events",
                )
            ]
        result = self._call_firewall_api(
            operation="aggregate_events",
            body_params=body,
            error_message="Failed to aggregate firewall events",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def query_firewall_event_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for firewall event ID query. IMPORTANT: use `falcon://firewall/events/fql-guide`.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query string."),
        after: str | None = Field(default=None, description="Pagination token."),
    ) -> list[str] | dict[str, Any]:
        """Query firewall event IDs."""
        return self._query_ids_with_fql_guide(
            operation="query_events",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "after": after,
            },
            error_message="Failed to query firewall event IDs",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_EVENTS_FQL_DOCUMENTATION,
        )

    def get_firewall_events(
        self,
        ids: list[str] | None = Field(default=None, description="Firewall event IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get firewall events by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall events.",
                    operation="get_events",
                )
            ]
        result = self._base_get_by_ids(
            operation="get_events",
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def query_firewall_field_ids(
        self,
        filter: str | None = Field(default=None, description="FQL filter for firewall field ID query."),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query string."),
        after: str | None = Field(default=None, description="Pagination token."),
    ) -> list[str] | dict[str, Any]:
        """Query firewall field IDs."""
        result = self._base_search_api_call(
            operation="query_firewall_fields",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "after": after,
            },
            error_message="Failed to query firewall field IDs",
        )
        if self._is_error(result):
            return result
        return result

    def get_firewall_fields(
        self,
        ids: list[str] | None = Field(default=None, description="Firewall field IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get firewall fields by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall fields.",
                    operation="get_firewall_fields",
                )
            ]
        result = self._base_get_by_ids(
            operation="get_firewall_fields",
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def query_firewall_platform_ids(
        self,
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
    ) -> list[str] | dict[str, Any]:
        """Query firewall platform IDs."""
        result = self._base_search_api_call(
            operation="query_platforms",
            search_params={
                "limit": limit,
                "offset": offset,
            },
            error_message="Failed to query firewall platform IDs",
        )
        if self._is_error(result):
            return result
        return result

    def get_firewall_platforms(
        self,
        ids: list[str] | None = Field(default=None, description="Firewall platform IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get firewall platforms by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall platforms.",
                    operation="get_platforms",
                )
            ]
        result = self._base_get_by_ids(
            operation="get_platforms",
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def get_firewall_policy_containers(
        self,
        ids: list[str] | None = Field(default=None, description="Firewall policy-container IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get firewall policy containers by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall policy containers.",
                    operation="get_policy_containers",
                )
            ]
        result = self._base_get_by_ids(
            operation="get_policy_containers",
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def create_firewall_rule_group(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body for `create_rule_group`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `create_rule_group` (e.g., clone_id, library, comment).",
        ),
    ) -> list[dict[str, Any]]:
        """Create a firewall rule group."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="create_rule_group",
            query_params=parameters,
            body_params=body,
            error_message="Failed to create firewall rule group",
        )

    def update_firewall_rule_group(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Full request body for `update_rule_group`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `update_rule_group`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update a firewall rule group."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="update_rule_group",
            query_params=parameters,
            body_params=body,
            error_message="Failed to update firewall rule group",
        )

    def delete_firewall_rule_groups(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(default=None, description="Firewall rule-group IDs to delete."),
        comment: str | None = Field(default=None, description="Optional audit comment."),
    ) -> list[dict[str, Any]]:
        """Delete firewall rule groups."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete firewall rule groups.",
                    operation="delete_rule_groups",
                )
            ]
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="delete_rule_groups",
            query_params={"ids": ids, "comment": comment},
            error_message="Failed to delete firewall rule groups",
        )

    def validate_firewall_rule_group_create(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this validation operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Validation request body for `create_rule_group_validation`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `create_rule_group_validation`.",
        ),
    ) -> list[dict[str, Any]]:
        """Validate a create-rule-group payload."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="create_rule_group_validation",
            query_params=parameters,
            body_params=body,
            error_message="Failed to validate firewall rule-group create payload",
        )

    def validate_firewall_rule_group_update(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this validation operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Validation request body for `update_rule_group_validation`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `update_rule_group_validation`.",
        ),
    ) -> list[dict[str, Any]]:
        """Validate an update-rule-group payload."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="update_rule_group_validation",
            query_params=parameters,
            body_params=body,
            error_message="Failed to validate firewall rule-group update payload",
        )

    def update_firewall_policy_container(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `update_policy_container`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `update_policy_container`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update firewall policy container (v2)."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="update_policy_container",
            query_params=parameters,
            body_params=body,
            error_message="Failed to update firewall policy container",
        )

    def update_firewall_policy_container_v1(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `update_policy_container_v1`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `update_policy_container_v1`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update firewall policy container (v1)."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="update_policy_container_v1",
            query_params=parameters,
            body_params=body,
            error_message="Failed to update firewall policy container v1",
        )

    def query_firewall_network_location_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for network-location ID query. IMPORTANT: use `falcon://firewall/network-locations/fql-guide`.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum number of IDs. [1-5000]"),
        offset: int = Field(default=0, ge=0, description="Starting index for pagination."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query string."),
        after: str | None = Field(default=None, description="Pagination token."),
    ) -> list[str] | dict[str, Any]:
        """Query firewall network-location IDs."""
        return self._query_ids_with_fql_guide(
            operation="query_network_locations",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "after": after,
            },
            error_message="Failed to query firewall network-location IDs",
            filter_used=filter,
            fql_guide=SEARCH_FIREWALL_NETWORK_LOCATIONS_FQL_DOCUMENTATION,
        )

    def get_firewall_network_locations(
        self,
        ids: list[str] | None = Field(default=None, description="Firewall network-location IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get firewall network locations by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall network locations.",
                    operation="get_network_locations",
                )
            ]
        result = self._base_get_by_ids(
            operation="get_network_locations",
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def get_firewall_network_location_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Firewall network-location IDs to retrieve details for.",
        ),
    ) -> list[dict[str, Any]]:
        """Get detailed firewall network-location entities by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve firewall network location details.",
                    operation="get_network_locations_details",
                )
            ]
        result = self._base_get_by_ids(
            operation="get_network_locations_details",
            ids=ids,
            use_params=True,
        )
        if self._is_error(result):
            return [result]
        return result

    def create_firewall_network_locations(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `create_network_locations`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `create_network_locations`.",
        ),
    ) -> list[dict[str, Any]]:
        """Create firewall network locations."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="create_network_locations",
            query_params=parameters,
            body_params=body,
            error_message="Failed to create firewall network locations",
        )

    def upsert_firewall_network_locations(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `upsert_network_locations`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `upsert_network_locations`.",
        ),
    ) -> list[dict[str, Any]]:
        """Upsert firewall network locations."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="upsert_network_locations",
            query_params=parameters,
            body_params=body,
            error_message="Failed to upsert firewall network locations",
        )

    def update_firewall_network_locations(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `update_network_locations`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `update_network_locations`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update firewall network locations."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="update_network_locations",
            query_params=parameters,
            body_params=body,
            error_message="Failed to update firewall network locations",
        )

    def update_firewall_network_locations_metadata(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `update_network_locations_metadata`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `update_network_locations_metadata`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update firewall network-location metadata."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="update_network_locations_metadata",
            query_params=parameters,
            body_params=body,
            error_message="Failed to update firewall network-location metadata",
        )

    def update_firewall_network_locations_precedence(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Request body for `update_network_locations_precedence`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional query parameters for `update_network_locations_precedence`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update firewall network-location precedence."""
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="update_network_locations_precedence",
            query_params=parameters,
            body_params=body,
            error_message="Failed to update firewall network-location precedence",
        )

    def delete_firewall_network_locations(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Firewall network-location IDs to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete firewall network locations."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete firewall network locations.",
                    operation="delete_network_locations",
                )
            ]
        return self._write_operation(
            confirm_execution=confirm_execution,
            operation="delete_network_locations",
            query_params={"ids": ids},
            error_message="Failed to delete firewall network locations",
        )

    def validate_firewall_filepath_pattern(
        self,
        filepath_pattern: str | None = Field(
            default=None,
            description="File path pattern to validate against firewall path validation rules.",
        ),
    ) -> list[dict[str, Any]]:
        """Validate firewall file path pattern syntax."""
        if not filepath_pattern:
            return [
                _format_error_response(
                    "`filepath_pattern` is required.",
                    operation="validate_filepath_pattern",
                )
            ]
        result = self._call_firewall_api(
            operation="validate_filepath_pattern",
            query_params={"filepath_pattern": filepath_pattern},
            error_message="Failed to validate firewall filepath pattern",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
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

    def _write_operation(
        self,
        confirm_execution: bool,
        operation: str,
        error_message: str,
        query_params: dict[str, Any] | None = None,
        body_params: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation=operation,
                )
            ]

        result = self._call_firewall_api(
            operation=operation,
            query_params=query_params,
            body_params=body_params,
            error_message=error_message,
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def _call_firewall_api(
        self,
        operation: str,
        error_message: str,
        query_params: dict[str, Any] | None = None,
        body_params: dict[str, Any] | list[dict[str, Any]] | None = None,
        default_result: Any | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        call_args: dict[str, Any] = {}

        if query_params is not None:
            prepared_params = prepare_api_parameters(query_params)
            if prepared_params:
                call_args["parameters"] = prepared_params

        if body_params is not None:
            if isinstance(body_params, list):
                call_args["body"] = body_params
            else:
                call_args["body"] = prepare_api_parameters(body_params)

        response = self.client.command(operation, **call_args)
        return handle_api_response(
            response,
            operation=operation,
            error_message=error_message,
            default_result=default_result if default_result is not None else [],
        )
