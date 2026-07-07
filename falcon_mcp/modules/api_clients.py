"""
API Clients module for Falcon MCP Server.

This module wraps FalconPy's API Clients service collection. It is intentionally
limited to listing, retrieving, and updating API client scopes.
"""

from __future__ import annotations

from typing import Any

from falconpy.api_clients import APIClients  # type: ignore[import-untyped]
from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule

API_CLIENTS_USAGE_GUIDE = """
# API Clients Usage Guide

This module uses FalconPy's API Clients service collection.

Read operations:
- `falcon_list_api_client_ids`
- `falcon_get_api_clients`
- `falcon_find_api_clients`

Write operation:
- `falcon_update_api_client_scopes`
- `falcon_copy_api_client_scopes_to_matching_clients`

Write tools require `confirm_execution=true`.

For Flight Control child CIDs, pass `member_cid` to a single-CID tool or
`target_member_cids` to the copy tool. This module does not expose MSSP tools
or enumerate child CIDs.
"""

READ_SCOPES = ["api-client-mgmt:read"]
WRITE_SCOPES = ["api-client-mgmt:write"]

OPERATION_SCOPES = {
    "GetAccessibleScopes": READ_SCOPES,
    "GetAllAPIClientIdsForCustomer": READ_SCOPES,
    "GetAPIClients": READ_SCOPES,
    "UpdateAPIClient": WRITE_SCOPES,
}

WRITE_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


class APIClientsModule(BaseModule):
    """Module for Falcon API client management."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server,
            self.get_accessible_api_client_scopes,
            "get_accessible_api_client_scopes",
        )
        self._add_tool(server, self.list_api_client_ids, "list_api_client_ids")
        self._add_tool(server, self.get_api_clients, "get_api_clients")
        self._add_tool(server, self.find_api_clients, "find_api_clients")
        self._add_tool(
            server,
            self.update_api_client_scopes,
            "update_api_client_scopes",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server,
            self.copy_api_client_scopes_to_matching_clients,
            "copy_api_client_scopes_to_matching_clients",
            annotations=WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://api-clients/usage-guide"),
                name="falcon_api_clients_usage_guide",
                description="Operational guidance for API client management tools.",
                text=API_CLIENTS_USAGE_GUIDE,
            ),
        )

    def get_accessible_api_client_scopes(
        self,
        member_cid: str | None = Field(
            default=None,
            description="Optional Flight Control child CID to run the API Clients request against.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get all API client scopes available to the target CID."""
        service = self._service(member_cid)
        response = service.get_accessible_scopes()
        return self._handle_response(
            response,
            operation="GetAccessibleScopes",
            error_message="Failed to get accessible API client scopes",
        )

    def list_api_client_ids(
        self,
        member_cid: str | None = Field(
            default=None, description="Optional Flight Control child CID."
        ),
        limit: int = Field(default=500, ge=1, le=500),
        offset: int = Field(default=0, ge=0),
        sort: str = Field(default="created_timestamp|desc"),
    ) -> list[str] | dict[str, Any]:
        """List API client IDs for the target CID."""
        service = self._service(member_cid)
        response = service.get_all_api_client_ids_for_customer(
            parameters={"limit": limit, "offset": offset, "sort": sort}
        )
        return self._handle_response(
            response,
            operation="GetAllAPIClientIdsForCustomer",
            error_message="Failed to list API client IDs",
        )

    def get_api_clients(
        self,
        ids: list[str] = Field(description="API client IDs to retrieve."),
        member_cid: str | None = Field(
            default=None, description="Optional Flight Control child CID."
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get API client definitions by ID."""
        if not ids:
            return _format_error_response("`ids` is required.", operation="GetAPIClients")
        service = self._service(member_cid)
        response = service.get_api_clients(ids=ids)
        result = self._handle_response(
            response,
            operation="GetAPIClients",
            error_message="Failed to get API clients",
        )
        return self._sanitize(result)

    def find_api_clients(
        self,
        name_contains: str = Field(
            default="Intezer", description="Case-insensitive name substring."
        ),
        member_cid: str | None = Field(
            default=None, description="Optional Flight Control child CID."
        ),
        max_clients: int = Field(default=1000, ge=1, le=5000),
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Find API clients by name substring."""
        clients = self._list_all_clients(member_cid=member_cid, max_clients=max_clients)
        if self._is_error(clients):
            return clients
        needle = name_contains.lower()
        matches = [client for client in clients if needle in str(client.get("name", "")).lower()]
        return {
            "member_cid": member_cid,
            "name_contains": name_contains,
            "matched_count": len(matches),
            "clients": self._sanitize(matches),
        }

    def update_api_client_scopes(
        self,
        id: str = Field(description="API client ID to update."),
        scopes: list[str] = Field(description="Complete replacement scope list."),
        member_cid: str | None = Field(
            default=None, description="Optional Flight Control child CID."
        ),
        name: str | None = Field(
            default=None, description="Existing or replacement API client name."
        ),
        description: str | None = Field(
            default=None, description="Existing or replacement description."
        ),
        confirm_execution: bool = Field(default=False),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Replace an API client's scope list."""
        if not confirm_execution:
            return _format_error_response(
                "This operation requires `confirm_execution=true`.",
                operation="UpdateAPIClient",
            )
        if not scopes:
            return _format_error_response("`scopes` is required.", operation="UpdateAPIClient")

        body = self._client_update_body(name=name, description=description, scopes=scopes)
        service = self._service(member_cid)
        response = service.update_api_client(parameters={"ids": id}, body=body)
        return self._handle_response(
            response,
            operation="UpdateAPIClient",
            error_message=f"Failed to update API client {id}",
        )

    def copy_api_client_scopes_to_matching_clients(
        self,
        source_client_id: str = Field(
            default="27a5a57909fc4bef9120fe7c17b10c46",
            description="Source API client ID whose scopes should be copied.",
        ),
        target_name_contains: str = Field(
            default="Intezer",
            description="Case-insensitive target name substring.",
        ),
        source_member_cid: str | None = Field(
            default=None,
            description="Optional child CID for the source client. Defaults to the current CID.",
        ),
        target_member_cids: list[str] | None = Field(
            default=None,
            description="Child CIDs to process. If omitted, only the current CID is processed.",
        ),
        max_clients_per_cid: int = Field(default=1000, ge=1, le=5000),
        exclude_source_client: bool = Field(default=True),
        filter_unavailable_scopes: bool = Field(
            default=False,
            description="Remove source scopes that Falcon reports as unavailable in each target CID before updating.",
        ),
        confirm_execution: bool = Field(default=False),
    ) -> dict[str, Any]:
        """Copy the source API client's scopes to matching API clients."""
        source_result = self.get_api_clients(ids=[source_client_id], member_cid=source_member_cid)
        if self._is_error(source_result):
            return {
                "error": "Unable to retrieve source API client.",
                "source_client_id": source_client_id,
                "details": source_result,
            }
        if not source_result:
            return {
                "error": "Source API client was not found.",
                "source_client_id": source_client_id,
                "source_member_cid": source_member_cid,
            }

        source_client = source_result[0]
        source_scopes = source_client.get("scopes")
        if not isinstance(source_scopes, list) or not source_scopes:
            return {
                "error": "Source API client does not include a non-empty `scopes` list.",
                "source_client": self._sanitize(source_client),
            }

        target_cids = target_member_cids if target_member_cids is not None else [None]
        report: dict[str, Any] = {
            "source_client": self._sanitize(source_client),
            "target_name_contains": target_name_contains,
            "target_member_cids": target_cids,
            "source_scope_count": len(source_scopes),
            "filter_unavailable_scopes": filter_unavailable_scopes,
            "dry_run": not confirm_execution,
            "processed": [],
            "errors": [],
        }

        for member_cid in target_cids:
            target_scopes = list(source_scopes)
            unavailable_source_scopes: list[str] = []
            if filter_unavailable_scopes:
                service = self._service(member_cid)
                response = service.get_accessible_scopes()
                accessible = self._handle_response(
                    response,
                    operation="GetAccessibleScopes",
                    error_message="Failed to get accessible API client scopes",
                    default_result=[],
                )
                if self._is_error(accessible):
                    report["errors"].append(
                        {
                            "member_cid": member_cid,
                            "stage": "accessible_scopes",
                            "error": accessible,
                        }
                    )
                    continue
                accessible_ids = {
                    item.get("id")
                    for item in accessible
                    if isinstance(item, dict) and item.get("id")
                }
                unavailable_source_scopes = [
                    scope for scope in source_scopes if scope not in accessible_ids
                ]
                target_scopes = [scope for scope in source_scopes if scope in accessible_ids]

            clients = self._list_all_clients(member_cid=member_cid, max_clients=max_clients_per_cid)
            if self._is_error(clients):
                report["errors"].append({"member_cid": member_cid, "error": clients})
                continue

            matches = []
            for client in clients:
                client_id = self._client_id(client)
                if exclude_source_client and client_id == source_client_id:
                    continue
                if target_name_contains.lower() in str(client.get("name", "")).lower():
                    matches.append(client)

            cid_report = {
                "member_cid": member_cid,
                "matched_count": len(matches),
                "targets": [],
            }

            for target in matches:
                target_id = self._client_id(target)
                if not target_id:
                    cid_report["targets"].append(
                        {
                            "client": self._sanitize(target),
                            "error": "Target client ID was not found.",
                        }
                    )
                    continue

                update_body = self._client_update_body(
                    name=target.get("name"),
                    description=target.get("description"),
                    scopes=target_scopes,
                )
                target_entry: dict[str, Any] = {
                    "id": target_id,
                    "name": target.get("name"),
                    "current_scope_count": len(target.get("scopes", []) or []),
                    "new_scope_count": len(target_scopes),
                    "unavailable_source_scopes": unavailable_source_scopes,
                }

                if confirm_execution:
                    service = self._service(member_cid)
                    response = service.update_api_client(
                        parameters={"ids": target_id}, body=update_body
                    )
                    result = self._handle_response(
                        response,
                        operation="UpdateAPIClient",
                        error_message=f"Failed to update API client {target_id}",
                    )
                    if self._is_error(result):
                        target_entry["error"] = result
                    else:
                        target_entry["updated"] = True
                        target_entry["result"] = self._sanitize(result)
                else:
                    target_entry["planned_update"] = True

                cid_report["targets"].append(target_entry)

            report["processed"].append(cid_report)

        return report

    def _service(self, member_cid: str | None = None) -> APIClients:
        params: dict[str, Any] = {
            "client_id": self.client.client_id,
            "client_secret": self.client.client_secret,
            "base_url": self.client.base_url,
            "debug": self.client.debug,
            "user_agent": self.client.get_user_agent(),
        }
        if member_cid:
            params["member_cid"] = member_cid
        proxy = getattr(self.client, "proxy", None)
        if proxy:
            params["proxy"] = {"https": proxy}
        http_timeout = getattr(self.client, "http_timeout", None)
        if http_timeout:
            params["timeout"] = http_timeout
        return APIClients(**params)

    def _list_all_clients(
        self,
        *,
        member_cid: str | None,
        max_clients: int,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        service = self._service(member_cid)
        all_ids: list[str] = []
        offset = 0
        page_size = min(500, max_clients)

        while len(all_ids) < max_clients:
            response = service.get_all_api_client_ids_for_customer(
                parameters={"limit": page_size, "offset": offset, "sort": "created_timestamp|desc"}
            )
            page = self._handle_response(
                response,
                operation="GetAllAPIClientIdsForCustomer",
                error_message="Failed to list API client IDs",
                default_result=[],
            )
            if self._is_error(page):
                return page
            if not page:
                break
            all_ids.extend(str(item) for item in page)
            if len(page) < page_size:
                break
            offset += len(page)

        all_ids = all_ids[:max_clients]
        clients: list[dict[str, Any]] = []
        for index in range(0, len(all_ids), 500):
            chunk = all_ids[index : index + 500]
            response = service.get_api_clients(ids=chunk)
            details = self._handle_response(
                response,
                operation="GetAPIClients",
                error_message="Failed to get API clients",
                default_result=[],
            )
            if self._is_error(details):
                return details
            clients.extend(details)
        return clients

    def _handle_response(
        self,
        response: Any,
        operation: str,
        error_message: str,
        default_result: Any = None,
    ) -> Any:
        if not isinstance(response, dict):
            return _format_error_response(
                f"{error_message}: unexpected response type {type(response).__name__}",
                operation=operation,
            )

        status_code = response.get("status_code")
        if status_code is None or status_code >= 300:
            details = response
            message = f"{error_message}: request failed with status code {status_code}"
            error = _format_error_response(message, details=details, operation=operation)
            required_scopes = OPERATION_SCOPES.get(operation)
            if status_code == 403 and required_scopes:
                error["required_scopes"] = required_scopes
                error["resolution"] = (
                    "Grant the API client these Falcon scopes before retrying: "
                    + ", ".join(required_scopes)
                )
            return error

        resources = response.get("body", {}).get("resources", [])
        if not resources and default_result is not None:
            return default_result
        return resources

    @staticmethod
    def _client_id(client: dict[str, Any]) -> str | None:
        for key in ("id", "client_id", "clientId", "clientID"):
            value = client.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def _client_update_body(
        *,
        name: Any,
        description: Any,
        scopes: list[str],
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"scopes": scopes}
        if name is not None:
            body["name"] = str(name)
        if description is not None:
            body["description"] = str(description)
        return body

    @classmethod
    def _sanitize(cls, value: Any) -> Any:
        if isinstance(value, list):
            return [cls._sanitize(item) for item in value]
        if isinstance(value, dict):
            redacted_keys = {"secret", "client_secret", "clientSecret", "api_key", "apiKey"}
            return {
                key: "<redacted>" if key in redacted_keys else cls._sanitize(item)
                for key, item in value.items()
            }
        return value
