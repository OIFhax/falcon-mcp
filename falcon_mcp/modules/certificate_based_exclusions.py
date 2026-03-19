"""
Certificate Based Exclusions module for Falcon MCP Server.

This module provides tools for searching, retrieving, creating, updating,
and deleting Falcon certificate based exclusions, plus certificate lookup.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.certificate_based_exclusions import (
    CERTIFICATE_BASED_EXCLUSIONS_CERT_GUIDE,
    CERTIFICATE_BASED_EXCLUSIONS_SAFETY_GUIDE,
    SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_DOCUMENTATION,
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


class CertificateBasedExclusionsModule(BaseModule):
    """Module for Falcon Certificate Based Exclusions operations."""

    def register_tools(self, server: FastMCP) -> None:
        self._add_tool(
            server=server,
            method=self.search_certificate_based_exclusions,
            name="search_certificate_based_exclusions",
        )
        self._add_tool(
            server=server,
            method=self.query_certificate_based_exclusion_ids,
            name="query_certificate_based_exclusion_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_certificate_based_exclusion_details,
            name="get_certificate_based_exclusion_details",
        )
        self._add_tool(
            server=server,
            method=self.get_certificate_signing_info,
            name="get_certificate_signing_info",
        )
        self._add_tool(
            server=server,
            method=self.create_certificate_based_exclusions,
            name="create_certificate_based_exclusions",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.update_certificate_based_exclusions,
            name="update_certificate_based_exclusions",
            annotations=WRITE_ANNOTATIONS,
        )
        self._add_tool(
            server=server,
            method=self.delete_certificate_based_exclusions,
            name="delete_certificate_based_exclusions",
            annotations=DESTRUCTIVE_WRITE_ANNOTATIONS,
        )

    def register_resources(self, server: FastMCP) -> None:
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://certificate-based-exclusions/search/fql-guide"),
                name="falcon_search_certificate_based_exclusions_fql_guide",
                description="FQL guidance for certificate based exclusions search tools.",
                text=SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_DOCUMENTATION,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://certificate-based-exclusions/certificates/guide"),
                name="falcon_certificate_based_exclusions_certificates_guide",
                description="Usage guidance for certificate signing lookups.",
                text=CERTIFICATE_BASED_EXCLUSIONS_CERT_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://certificate-based-exclusions/safety-guide"),
                name="falcon_certificate_based_exclusions_safety_guide",
                description="Safety and operational guidance for certificate based exclusion write tools.",
                text=CERTIFICATE_BASED_EXCLUSIONS_SAFETY_GUIDE,
            ),
        )

    def search_certificate_based_exclusions(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for certificate based exclusion search. IMPORTANT: use the `falcon://certificate-based-exclusions/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=100),
        offset: int | None = Field(default=None),
        sort: str | None = Field(default=None),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        exclusion_ids = self._base_search_api_call(
            operation="cb_exclusions_query_v1",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search certificate based exclusions",
        )

        if self._is_error(exclusion_ids):
            if filter:
                return self._format_fql_error_response(
                    [exclusion_ids],
                    filter,
                    SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_DOCUMENTATION,
                )
            return [exclusion_ids]

        if not exclusion_ids:
            if filter:
                return self._format_fql_error_response(
                    [],
                    filter,
                    SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_DOCUMENTATION,
                )
            return []

        details = self._base_get_by_ids(
            operation="cb_exclusions_get_v1",
            ids=exclusion_ids,
            use_params=True,
        )

        if self._is_error(details):
            return [details]

        return details

    def query_certificate_based_exclusion_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for certificate based exclusion ID query. IMPORTANT: use the `falcon://certificate-based-exclusions/search/fql-guide` resource when building this filter parameter.",
        ),
        limit: int = Field(default=100, ge=1, le=100),
        offset: int | None = Field(default=None),
        sort: str | None = Field(default=None),
    ) -> list[str] | dict[str, Any]:
        result = self._base_search_api_call(
            operation="cb_exclusions_query_v1",
            search_params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to query certificate based exclusion IDs",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result], filter, SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_DOCUMENTATION
            )

        if not result and filter:
            return self._format_fql_error_response(
                [], filter, SEARCH_CERTIFICATE_BASED_EXCLUSIONS_FQL_DOCUMENTATION
            )

        return result

    def get_certificate_based_exclusion_details(
        self,
        ids: list[str] | None = Field(default=None, description="Certificate based exclusion IDs."),
    ) -> list[dict[str, Any]]:
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve certificate based exclusion details.",
                    operation="cb_exclusions_get_v1",
                )
            ]

        result = self._base_get_by_ids(
            operation="cb_exclusions_get_v1",
            ids=ids,
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def get_certificate_signing_info(
        self,
        sha256: str | None = Field(
            default=None,
            description="SHA256 hash of the file to retrieve certificate signing information for. IMPORTANT: use the `falcon://certificate-based-exclusions/certificates/guide` resource for guidance.",
        ),
    ) -> list[dict[str, Any]]:
        if not sha256:
            return [
                _format_error_response(
                    "`sha256` is required to retrieve certificate signing information.",
                    operation="certificates_get_v1",
                )
            ]

        result = self._base_query_api_call(
            operation="certificates_get_v1",
            query_params={"ids": sha256},
            error_message="Failed to retrieve certificate signing information",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result

    def create_certificate_based_exclusions(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = Field(default=None),
        applied_globally: bool | None = Field(default=None),
        certificate: dict[str, Any] | None = Field(default=None),
        issuer: str | None = Field(default=None),
        serial: str | None = Field(default=None),
        subject: str | None = Field(default=None),
        thumbprint: str | None = Field(default=None),
        valid_from: str | None = Field(default=None),
        valid_to: str | None = Field(default=None),
        children_cids: list[str] | None = Field(default=None),
        comment: str | None = Field(default=None),
        created_by: str | None = Field(default=None),
        created_on: str | None = Field(default=None),
        description: str | None = Field(default=None),
        host_groups: list[str] | None = Field(default=None),
        modified_by: str | None = Field(default=None),
        modified_on: str | None = Field(default=None),
        name: str | None = Field(default=None),
        status: str | None = Field(default=None),
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="cb_exclusions_create_v1",
                )
            ]

        request_body = body
        if request_body is None:
            if not any(
                value is not None
                for value in [
                    certificate,
                    issuer,
                    serial,
                    subject,
                    thumbprint,
                    valid_from,
                    valid_to,
                    name,
                ]
            ):
                return [
                    _format_error_response(
                        "Provide `body` or certificate/name fields to create a certificate based exclusion.",
                        operation="cb_exclusions_create_v1",
                    )
                ]

            exclusion: dict[str, Any] = {}
            if applied_globally is not None:
                exclusion["applied_globally"] = applied_globally
            if certificate is not None:
                exclusion["certificate"] = certificate
            else:
                certificate_fields = {
                    "issuer": issuer,
                    "serial": serial,
                    "subject": subject,
                    "thumbprint": thumbprint,
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                }
                cert = {key: value for key, value in certificate_fields.items() if value is not None}
                if cert:
                    exclusion["certificate"] = cert
            for key, value in {
                "children_cids": children_cids,
                "comment": comment,
                "created_by": created_by,
                "created_on": created_on,
                "description": description,
                "host_groups": host_groups,
                "modified_by": modified_by,
                "modified_on": modified_on,
                "name": name,
                "status": status,
            }.items():
                if value is not None:
                    exclusion[key] = value
            request_body = {"exclusions": [exclusion]}

        result = self._base_query_api_call(
            operation="cb_exclusions_create_v1",
            body_params=request_body,
            error_message="Failed to create certificate based exclusions",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def update_certificate_based_exclusions(
        self,
        confirm_execution: bool = Field(default=False),
        body: dict[str, Any] | None = Field(default=None),
        applied_globally: bool | None = Field(default=None),
        certificate: dict[str, Any] | None = Field(default=None),
        issuer: str | None = Field(default=None),
        serial: str | None = Field(default=None),
        subject: str | None = Field(default=None),
        thumbprint: str | None = Field(default=None),
        valid_from: str | None = Field(default=None),
        valid_to: str | None = Field(default=None),
        children_cids: list[str] | None = Field(default=None),
        comment: str | None = Field(default=None),
        created_by: str | None = Field(default=None),
        created_on: str | None = Field(default=None),
        description: str | None = Field(default=None),
        host_groups: list[str] | None = Field(default=None),
        modified_by: str | None = Field(default=None),
        modified_on: str | None = Field(default=None),
        name: str | None = Field(default=None),
        status: str | None = Field(default=None),
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="cb_exclusions_update_v1",
                )
            ]

        request_body = body
        if request_body is None:
            if not any(
                value is not None
                for value in [
                    certificate,
                    issuer,
                    serial,
                    subject,
                    thumbprint,
                    valid_from,
                    valid_to,
                    name,
                    description,
                    status,
                ]
            ):
                return [
                    _format_error_response(
                        "Provide `body` or update fields to modify certificate based exclusions.",
                        operation="cb_exclusions_update_v1",
                    )
                ]
            exclusion: dict[str, Any] = {}
            if applied_globally is not None:
                exclusion["applied_globally"] = applied_globally
            if certificate is not None:
                exclusion["certificate"] = certificate
            else:
                certificate_fields = {
                    "issuer": issuer,
                    "serial": serial,
                    "subject": subject,
                    "thumbprint": thumbprint,
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                }
                cert = {key: value for key, value in certificate_fields.items() if value is not None}
                if cert:
                    exclusion["certificate"] = cert
            for key, value in {
                "children_cids": children_cids,
                "comment": comment,
                "created_by": created_by,
                "created_on": created_on,
                "description": description,
                "host_groups": host_groups,
                "modified_by": modified_by,
                "modified_on": modified_on,
                "name": name,
                "status": status,
            }.items():
                if value is not None:
                    exclusion[key] = value
            request_body = {"exclusions": [exclusion]}

        result = self._base_query_api_call(
            operation="cb_exclusions_update_v1",
            body_params=request_body,
            error_message="Failed to update certificate based exclusions",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def delete_certificate_based_exclusions(
        self,
        confirm_execution: bool = Field(default=False),
        ids: list[str] | None = Field(default=None),
        comment: str | None = Field(default=None),
    ) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [
                _format_error_response(
                    "This operation requires `confirm_execution=true`.",
                    operation="cb_exclusions_delete_v1",
                )
            ]
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to delete certificate based exclusions.",
                    operation="cb_exclusions_delete_v1",
                )
            ]

        result = self._base_query_api_call(
            operation="cb_exclusions_delete_v1",
            query_params={"ids": ids, "comment": comment},
            error_message="Failed to delete certificate based exclusions",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result
