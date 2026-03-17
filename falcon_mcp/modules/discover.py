"""
Discover module for Falcon MCP Server.

This module provides full read coverage for Falcon Discover applications, hosts,
accounts, IoT hosts, and login entities.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.discover import (
    SEARCH_APPLICATIONS_FQL_DOCUMENTATION,
    SEARCH_UNMANAGED_ASSETS_FQL_DOCUMENTATION,
)


class DiscoverModule(BaseModule):
    """Module for Falcon Discover operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_applications, name="search_applications")
        self._add_tool(server=server, method=self.query_application_ids, name="query_application_ids")
        self._add_tool(server=server, method=self.get_application_details, name="get_application_details")
        self._add_tool(server=server, method=self.search_hosts_combined, name="search_hosts_combined")
        self._add_tool(server=server, method=self.query_host_ids, name="query_host_ids")
        self._add_tool(server=server, method=self.get_host_details, name="get_host_details")
        self._add_tool(server=server, method=self.search_hosts, name="search_hosts")
        self._add_tool(
            server=server,
            method=self.search_unmanaged_assets,
            name="search_unmanaged_assets",
        )
        self._add_tool(server=server, method=self.query_account_ids, name="query_account_ids")
        self._add_tool(server=server, method=self.get_account_details, name="get_account_details")
        self._add_tool(server=server, method=self.search_accounts, name="search_accounts")
        self._add_tool(server=server, method=self.query_login_ids, name="query_login_ids")
        self._add_tool(server=server, method=self.get_login_details, name="get_login_details")
        self._add_tool(server=server, method=self.search_logins, name="search_logins")
        self._add_tool(server=server, method=self.query_iot_host_ids, name="query_iot_host_ids")
        self._add_tool(server=server, method=self.query_iot_host_ids_v2, name="query_iot_host_ids_v2")
        self._add_tool(server=server, method=self.get_iot_host_details, name="get_iot_host_details")
        self._add_tool(server=server, method=self.search_iot_hosts, name="search_iot_hosts")

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_applications_fql_resource = TextResource(
            uri=AnyUrl("falcon://discover/applications/fql-guide"),
            name="falcon_search_applications_fql_guide",
            description="Contains the guide for the `filter` parameter of application search/query tools.",
            text=SEARCH_APPLICATIONS_FQL_DOCUMENTATION,
        )

        search_hosts_fql_resource = TextResource(
            uri=AnyUrl("falcon://discover/hosts/fql-guide"),
            name="falcon_search_unmanaged_assets_fql_guide",
            description="Contains the guide for the `filter` parameter of host and unmanaged asset search/query tools.",
            text=SEARCH_UNMANAGED_ASSETS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_applications_fql_resource)
        self._add_resource(server, search_hosts_fql_resource)

    def search_applications(
        self,
        filter: str = Field(
            description="FQL filter expression used to limit results. IMPORTANT: use `falcon://discover/applications/fql-guide` when building this parameter.",
            examples={"name:'Chrome'", "vendor:'Microsoft Corporation'"},
        ),
        facet: str | list[str] | None = Field(
            default=None,
            description=dedent("""
                Optional facet detail blocks for application entities.

                Supported values:
                - browser_extension
                - host_info
                - install_usage
                - package
                - ide_extension
            """).strip(),
            examples={"host_info", "install_usage"},
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of records to return. [1-1000]",
        ),
        after: str | None = Field(
            default=None,
            description="Cursor token for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression for applications.",
            examples={"name.asc", "last_updated_timestamp.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search applications using the combined applications endpoint."""
        return self._combined_discover_search(
            operation="combined_applications",
            filter=filter,
            limit=limit,
            sort=sort,
            after=after,
            facet=facet,
            error_message="Failed to search applications",
            fql_documentation=SEARCH_APPLICATIONS_FQL_DOCUMENTATION,
        )

    def query_application_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit application IDs. IMPORTANT: use `falcon://discover/applications/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query application IDs."""
        return self._discover_query_ids(
            operation="query_applications",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to query application IDs",
            fql_documentation=SEARCH_APPLICATIONS_FQL_DOCUMENTATION,
        )

    def get_application_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Application IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve application details by ID."""
        return self._discover_get_by_ids(
            operation="get_applications",
            ids=ids,
            id_description="application IDs",
        )

    def search_hosts_combined(
        self,
        filter: str = Field(
            description="FQL filter expression used to limit host results. IMPORTANT: use `falcon://discover/hosts/fql-guide` when building this parameter.",
            examples={"entity_type:'managed'", "platform_name:'Windows'"},
        ),
        facet: str | list[str] | None = Field(
            default=None,
            description="Optional host facet details. Supported values: system_insights, third_party, risk_factors.",
            examples={"system_insights", "risk_factors"},
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of records to return. [1-1000]",
        ),
        after: str | None = Field(
            default=None,
            description="Cursor token for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression for hosts.",
            examples={"hostname.asc", "last_seen_timestamp.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search host assets using the combined hosts endpoint."""
        return self._combined_discover_search(
            operation="combined_hosts",
            filter=filter,
            limit=limit,
            sort=sort,
            after=after,
            facet=facet,
            error_message="Failed to search hosts",
            fql_documentation=SEARCH_UNMANAGED_ASSETS_FQL_DOCUMENTATION,
        )

    def query_host_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit host IDs. IMPORTANT: use `falcon://discover/hosts/fql-guide` when building this parameter.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query host IDs."""
        return self._discover_query_ids(
            operation="query_hosts",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to query host IDs",
            fql_documentation=SEARCH_UNMANAGED_ASSETS_FQL_DOCUMENTATION,
        )

    def get_host_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Host asset IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve host asset details by ID."""
        return self._discover_get_by_ids(
            operation="get_hosts",
            ids=ids,
            id_description="host IDs",
        )

    def search_hosts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit host IDs before retrieving details.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search hosts using query + get-by-ids workflow."""
        host_ids = self.query_host_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(host_ids):
            return [host_ids]
        if isinstance(host_ids, dict):
            return host_ids
        if not host_ids:
            return []

        return self.get_host_details(ids=host_ids)

    def search_unmanaged_assets(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression for unmanaged assets. IMPORTANT: use `falcon://discover/hosts/fql-guide` when building this parameter. `entity_type:'unmanaged'` is always applied automatically.",
            examples={"platform_name:'Windows'", "criticality:'Critical'"},
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of records to return. [1-1000]",
        ),
        after: str | None = Field(
            default=None,
            description="Cursor token for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression for unmanaged hosts.",
            examples={"hostname.asc", "last_seen_timestamp.desc"},
        ),
        facet: str | list[str] | None = Field(
            default=None,
            description="Optional host facet details. Supported values: system_insights, third_party, risk_factors.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search unmanaged assets using combined hosts with enforced unmanaged filter."""
        base_filter = "entity_type:'unmanaged'"
        combined_filter = f"{base_filter}+{filter}" if filter else base_filter

        return self._combined_discover_search(
            operation="combined_hosts",
            filter=combined_filter,
            limit=limit,
            sort=sort,
            after=after,
            facet=facet,
            error_message="Failed to search unmanaged assets",
            fql_documentation=SEARCH_UNMANAGED_ASSETS_FQL_DOCUMENTATION,
        )

    def query_account_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit account IDs.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query account IDs."""
        return self._discover_query_ids(
            operation="query_accounts",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to query account IDs",
        )

    def get_account_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Account IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve account details by ID."""
        return self._discover_get_by_ids(
            operation="get_accounts",
            ids=ids,
            id_description="account IDs",
        )

    def search_accounts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit account IDs before retrieving details.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[dict[str, Any]]:
        """Search accounts using query + get-by-ids workflow."""
        account_ids = self.query_account_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(account_ids):
            return [account_ids]
        if not account_ids:
            return []

        return self.get_account_details(ids=account_ids)

    def query_login_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit login IDs.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query login IDs."""
        return self._discover_query_ids(
            operation="query_logins",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to query login IDs",
        )

    def get_login_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Login IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve login details by ID."""
        return self._discover_get_by_ids(
            operation="get_logins",
            ids=ids,
            id_description="login IDs",
        )

    def search_logins(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit login IDs before retrieving details.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[dict[str, Any]]:
        """Search logins using query + get-by-ids workflow."""
        login_ids = self.query_login_ids(
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
        )

        if self._is_error(login_ids):
            return [login_ids]
        if not login_ids:
            return []

        return self.get_login_details(ids=login_ids)

    def query_iot_host_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit IoT host IDs.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Offset for paginated results.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query IoT host IDs using v1 endpoint."""
        return self._discover_query_ids(
            operation="query_iot_hosts",
            filter=filter,
            limit=limit,
            offset=offset,
            sort=sort,
            error_message="Failed to query IoT host IDs",
        )

    def query_iot_host_ids_v2(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit IoT host IDs using v2 cursor pagination.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        after: str | None = Field(
            default=None,
            description="Cursor token for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[str] | dict[str, Any]:
        """Query IoT host IDs using v2 endpoint."""
        return self._base_search_api_call(
            operation="query_iot_hostsV2",
            search_params={
                "filter": filter,
                "limit": limit,
                "after": after,
                "sort": sort,
            },
            error_message="Failed to query IoT host IDs (v2)",
        )

    def get_iot_host_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="IoT host IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve IoT host details by ID."""
        return self._discover_get_by_ids(
            operation="get_iot_hosts",
            ids=ids,
            id_description="IoT host IDs",
        )

    def search_iot_hosts(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter expression used to limit IoT host IDs before retrieving details.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=100,
            description="Maximum number of IDs to return. [1-100]",
        ),
        after: str | None = Field(
            default=None,
            description="Cursor token for pagination.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression.",
        ),
    ) -> list[dict[str, Any]]:
        """Search IoT hosts using v2 query + get-by-ids workflow."""
        iot_host_ids = self.query_iot_host_ids_v2(
            filter=filter,
            limit=limit,
            after=after,
            sort=sort,
        )

        if self._is_error(iot_host_ids):
            return [iot_host_ids]
        if not iot_host_ids:
            return []

        return self.get_iot_host_details(ids=iot_host_ids)

    def _combined_discover_search(
        self,
        operation: str,
        filter: str,
        limit: int,
        sort: str | None,
        after: str | None,
        facet: str | list[str] | None,
        error_message: str,
        fql_documentation: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "sort": sort,
                "after": after,
                "facet": facet,
            },
            error_message=error_message,
        )

        if self._is_error(result) and fql_documentation:
            return self._format_fql_error_response(
                [result],
                filter,
                fql_documentation,
            )

        if not result and filter and fql_documentation:
            return self._format_fql_error_response(
                [],
                filter,
                fql_documentation,
            )

        return result

    def _discover_query_ids(
        self,
        operation: str,
        filter: str | None,
        limit: int,
        offset: int,
        sort: str | None,
        error_message: str,
        fql_documentation: str | None = None,
    ) -> list[str] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message=error_message,
        )

        if self._is_error(result) and fql_documentation:
            return self._format_fql_error_response(
                [result],
                filter,
                fql_documentation,
            )

        if not result and filter and fql_documentation:
            return self._format_fql_error_response(
                [],
                filter,
                fql_documentation,
            )

        return result

    def _discover_get_by_ids(
        self,
        operation: str,
        ids: list[str] | None,
        id_description: str,
    ) -> list[dict[str, Any]]:
        if not ids:
            return [
                _format_error_response(
                    f"`ids` is required to retrieve {id_description}.",
                    operation=operation,
                )
            ]

        result = self._base_get_by_ids(
            operation=operation,
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result
