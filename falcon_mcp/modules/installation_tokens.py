"""
Installation Tokens module for Falcon MCP Server.

This module provides tools for querying and managing installation tokens,
reviewing token audit events, and reading/updating token customer settings.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.installation_tokens import (
    INSTALLATION_TOKENS_SAFETY_GUIDE,
    SEARCH_INSTALLATION_TOKEN_AUDIT_FQL_DOCUMENTATION,
    SEARCH_INSTALLATION_TOKENS_FQL_DOCUMENTATION,
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


class InstallationTokensModule(BaseModule):
    """Module for Installation Tokens operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_installation_tokens,
            name="search_installation_tokens",
        )
        self._add_tool(
            server=server,
            method=self.get_installation_token_details,
            name="get_installation_token_details",
        )
        self._add_tool(
            server=server,
            method=self.create_installation_token,
            name="create_installation_token",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_installation_tokens,
            name="update_installation_tokens",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_installation_tokens,
            name="delete_installation_tokens",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.search_installation_token_audit_events,
            name="search_installation_token_audit_events",
        )
        self._add_tool(
            server=server,
            method=self.get_installation_token_audit_event_details,
            name="get_installation_token_audit_event_details",
        )
        self._add_tool(
            server=server,
            method=self.get_installation_token_customer_settings,
            name="get_installation_token_customer_settings",
        )
        self._add_tool(
            server=server,
            method=self.update_installation_token_customer_settings,
            name="update_installation_token_customer_settings",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_installation_tokens_fql_resource = TextResource(
            uri=AnyUrl("falcon://installation-tokens/tokens/fql-guide"),
            name="falcon_search_installation_tokens_fql_guide",
            description="Contains the guide for the `filter` parameter of `falcon_search_installation_tokens`.",
            text=SEARCH_INSTALLATION_TOKENS_FQL_DOCUMENTATION,
        )

        search_installation_token_audit_fql_resource = TextResource(
            uri=AnyUrl("falcon://installation-tokens/audit/fql-guide"),
            name="falcon_search_installation_token_audit_fql_guide",
            description="Contains the guide for the `filter` parameter of `falcon_search_installation_token_audit_events`.",
            text=SEARCH_INSTALLATION_TOKEN_AUDIT_FQL_DOCUMENTATION,
        )

        installation_tokens_safety_guide_resource = TextResource(
            uri=AnyUrl("falcon://installation-tokens/safety-guide"),
            name="falcon_installation_tokens_safety_guide",
            description="Safety and operational guidance for installation token write tools.",
            text=INSTALLATION_TOKENS_SAFETY_GUIDE,
        )

        self._add_resource(server, search_installation_tokens_fql_resource)
        self._add_resource(server, search_installation_token_audit_fql_resource)
        self._add_resource(server, installation_tokens_safety_guide_resource)

    def search_installation_tokens(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for installation token search. IMPORTANT: use the `falcon://installation-tokens/tokens/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=1000,
            description="Maximum number of token IDs to return. [1-1000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort token results using FQL sort syntax.",
            examples={"created_timestamp|desc", "expires_timestamp.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search installation tokens and return full token details."""
        token_ids = self._base_search_api_call(
            operation="tokens_query",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search installation tokens",
        )

        if self._is_error(token_ids):
            return self._format_fql_error_response(
                [token_ids], filter, SEARCH_INSTALLATION_TOKENS_FQL_DOCUMENTATION
            )

        if not token_ids:
            if filter:
                return self._format_fql_error_response(
                    [],
                    filter,
                    SEARCH_INSTALLATION_TOKENS_FQL_DOCUMENTATION,
                )
            return []

        details = self._base_get_by_ids(
            operation="tokens_read",
            ids=token_ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_installation_token_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Installation token IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve installation token details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve installation token details.",
                    operation="tokens_read",
                )
            ]

        result = self._base_get_by_ids(
            operation="tokens_read",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def create_installation_token(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        label: str | None = Field(
            default=None,
            description="Token label.",
        ),
        expires_timestamp: str | None = Field(
            default=None,
            description="Token expiration timestamp in UTC (RFC3339 format).",
        ),
        type: str | None = Field(
            default=None,
            description="Optional token type.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full request body override for `tokens_create`.",
        ),
    ) -> list[dict[str, Any]]:
        """Create an installation token."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="tokens_create",
                )
            ]

        request_body = body
        if request_body is None:
            if not label:
                return [
                    _format_error_response(
                        "`label` is required when `body` is not provided.",
                        operation="tokens_create",
                    )
                ]
            if not expires_timestamp:
                return [
                    _format_error_response(
                        "`expires_timestamp` is required when `body` is not provided.",
                        operation="tokens_create",
                    )
                ]
            request_body = {
                "label": label,
                "expires_timestamp": expires_timestamp,
            }
            if type:
                request_body["type"] = type

        prepared_body = prepare_api_parameters(request_body)
        command_response = self.client.command("tokens_create", body=prepared_body)
        result = handle_api_response(
            command_response,
            operation="tokens_create",
            error_message="Failed to create installation token",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_installation_tokens(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Installation token IDs to update.",
        ),
        label: str | None = Field(
            default=None,
            description="Updated token label.",
        ),
        expires_timestamp: str | None = Field(
            default=None,
            description="Updated expiration timestamp in UTC (RFC3339 format).",
        ),
        revoked: bool | None = Field(
            default=None,
            description="Set to true to revoke token, false to restore.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full request body override for `tokens_update`.",
        ),
        parameters: dict[str, Any] | None = Field(
            default=None,
            description="Optional full query parameter override for `tokens_update`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update installation tokens by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="tokens_update",
                )
            ]

        request_body = body
        request_parameters = parameters

        if request_parameters is None:
            if not ids:
                return [
                    _format_error_response(
                        "`ids` is required when `parameters` is not provided.",
                        operation="tokens_update",
                    )
                ]
            request_parameters = {"ids": ids}

        if request_body is None:
            if label is None and expires_timestamp is None and revoked is None:
                return [
                    _format_error_response(
                        "At least one update field (`label`, `expires_timestamp`, or `revoked`) is required when `body` is not provided.",
                        operation="tokens_update",
                    )
                ]
            request_body = {}
            if label is not None:
                request_body["label"] = label
            if expires_timestamp is not None:
                request_body["expires_timestamp"] = expires_timestamp
            if revoked is not None:
                request_body["revoked"] = revoked

        prepared_body = prepare_api_parameters(request_body)
        prepared_params = prepare_api_parameters(request_parameters)
        command_response = self.client.command(
            "tokens_update",
            parameters=prepared_params,
            body=prepared_body,
        )
        result = handle_api_response(
            command_response,
            operation="tokens_update",
            error_message="Failed to update installation tokens",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def delete_installation_tokens(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="Installation token IDs to delete.",
        ),
    ) -> list[dict[str, Any]]:
        """Delete installation tokens by ID."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="tokens_delete",
                )
            ]

        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete installation tokens.",
                    operation="tokens_delete",
                )
            ]

        prepared_params = prepare_api_parameters({"ids": ids})
        command_response = self.client.command("tokens_delete", parameters=prepared_params)
        result = handle_api_response(
            command_response,
            operation="tokens_delete",
            error_message="Failed to delete installation tokens",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def search_installation_token_audit_events(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for installation token audit event search. IMPORTANT: use the `falcon://installation-tokens/audit/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(
            default=50,
            ge=1,
            le=1000,
            description="Maximum number of audit event IDs to return. [1-1000]",
        ),
        offset: int = Field(
            default=0,
            ge=0,
            description="Starting index of overall result set from which to return IDs.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort audit events using FQL sort syntax.",
            examples={"timestamp|desc", "action.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search installation token audit events and return full event details."""
        audit_event_ids = self._base_search_api_call(
            operation="audit_events_query",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
            },
            error_message="Failed to search installation token audit events",
        )

        if self._is_error(audit_event_ids):
            return self._format_fql_error_response(
                [audit_event_ids],
                filter,
                SEARCH_INSTALLATION_TOKEN_AUDIT_FQL_DOCUMENTATION,
            )

        if not audit_event_ids:
            if filter:
                return self._format_fql_error_response(
                    [],
                    filter,
                    SEARCH_INSTALLATION_TOKEN_AUDIT_FQL_DOCUMENTATION,
                )
            return []

        details = self._base_get_by_ids(
            operation="audit_events_read",
            ids=audit_event_ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def get_installation_token_audit_event_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Audit event IDs to retrieve.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve installation token audit event details by ID."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve audit event details.",
                    operation="audit_events_read",
                )
            ]

        result = self._base_get_by_ids(
            operation="audit_events_read",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def get_installation_token_customer_settings(self) -> list[dict[str, Any]]:
        """Retrieve installation token customer settings."""
        command_response = self.client.command("customer_settings_read")
        result = handle_api_response(
            command_response,
            operation="customer_settings_read",
            error_message="Failed to retrieve installation token customer settings",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def update_installation_token_customer_settings(
        self,
        confirm_execution: bool = Field(
            default=False,
            description="Explicit safety confirmation. Must be set to `true` to execute this write operation.",
        ),
        max_active_tokens: int | None = Field(
            default=None,
            ge=0,
            description="Maximum number of active tokens within the tenant.",
        ),
        tokens_required: bool | None = Field(
            default=None,
            description="Whether sensor installation tokens are required.",
        ),
        body: dict[str, Any] | None = Field(
            default=None,
            description="Optional full request body override for `customer_settings_update`.",
        ),
    ) -> list[dict[str, Any]]:
        """Update installation token customer settings."""
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="customer_settings_update",
                )
            ]

        request_body = body
        if request_body is None:
            if max_active_tokens is None and tokens_required is None:
                return [
                    _format_error_response(
                        "At least one setting (`max_active_tokens` or `tokens_required`) is required when `body` is not provided.",
                        operation="customer_settings_update",
                    )
                ]
            request_body = {}
            if max_active_tokens is not None:
                request_body["max_active_tokens"] = max_active_tokens
            if tokens_required is not None:
                request_body["tokens_required"] = tokens_required

        prepared_body = prepare_api_parameters(request_body)
        command_response = self.client.command("customer_settings_update", body=prepared_body)
        result = handle_api_response(
            command_response,
            operation="customer_settings_update",
            error_message="Failed to update installation token customer settings",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
