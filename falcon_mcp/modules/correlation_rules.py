"""
Correlation Rules module for Falcon MCP Server.

This module provides full Falcon Correlation Rules coverage across query, get, aggregate,
version lifecycle, and rule lifecycle workflows.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from mcp.types import ToolAnnotations
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.correlation_rules import (
    CORRELATION_RULES_FQL_GUIDE,
    CORRELATION_RULES_SAFETY_GUIDE,
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


class CorrelationRulesModule(BaseModule):
    """Module for Falcon Correlation Rules operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_correlation_rules_v1, name="search_correlation_rules_v1")
        self._add_tool(server=server, method=self.search_correlation_rules_v2, name="search_correlation_rules_v2")
        self._add_tool(server=server, method=self.query_correlation_rule_ids, name="query_correlation_rule_ids")
        self._add_tool(server=server, method=self.query_correlation_rule_version_ids, name="query_correlation_rule_version_ids")
        self._add_tool(server=server, method=self.get_correlation_rules, name="get_correlation_rules")
        self._add_tool(server=server, method=self.get_correlation_rule_versions, name="get_correlation_rule_versions")
        self._add_tool(server=server, method=self.get_latest_correlation_rule_versions, name="get_latest_correlation_rule_versions")
        self._add_tool(server=server, method=self.aggregate_correlation_rule_versions, name="aggregate_correlation_rule_versions")
        self._add_tool(server=server, method=self.create_correlation_rule, name="create_correlation_rule", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.update_correlation_rule, name="update_correlation_rule", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.delete_correlation_rules, name="delete_correlation_rules", annotations=DESTRUCTIVE_WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.export_correlation_rule_versions, name="export_correlation_rule_versions", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.import_correlation_rule, name="import_correlation_rule", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.publish_correlation_rule_version, name="publish_correlation_rule_version", annotations=WRITE_ANNOTATIONS)
        self._add_tool(server=server, method=self.delete_correlation_rule_versions, name="delete_correlation_rule_versions", annotations=DESTRUCTIVE_WRITE_ANNOTATIONS)

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://correlation-rules/fql-guide"),
                name="falcon_correlation_rules_fql_guide",
                description="FQL guidance for Correlation Rules search tools.",
                text=CORRELATION_RULES_FQL_GUIDE,
            ),
        )
        self._add_resource(
            server,
            TextResource(
                uri=AnyUrl("falcon://correlation-rules/safety-guide"),
                name="falcon_correlation_rules_safety_guide",
                description="Safety guidance for Correlation Rules write tools.",
                text=CORRELATION_RULES_SAFETY_GUIDE,
            ),
        )

    def search_correlation_rules_v1(self, filter: str | None = Field(default=None, description="FQL filter for v1 combined rule search. IMPORTANT: use `falcon://correlation-rules/fql-guide` when building this parameter."), q: str | None = Field(default=None), sort: str | None = Field(default=None), offset: int = Field(default=0, ge=0), limit: int = Field(default=100, ge=1, le=5000)) -> list[dict[str, Any]] | dict[str, Any]:
        """Search correlation rules using the v1 combined endpoint."""
        return self._search_with_guide(operation="combined_rules_get_v1", filter=filter, q=q, sort=sort, offset=offset, limit=limit)

    def search_correlation_rules_v2(self, filter: str | None = Field(default=None, description="FQL filter for v2 combined rule search. IMPORTANT: use `falcon://correlation-rules/fql-guide` when building this parameter."), q: str | None = Field(default=None), sort: str | None = Field(default=None), offset: int = Field(default=0, ge=0), limit: int = Field(default=100, ge=1, le=5000)) -> list[dict[str, Any]] | dict[str, Any]:
        """Search correlation rules using the v2 combined endpoint."""
        return self._search_with_guide(operation="combined_rules_get_v2", filter=filter, q=q, sort=sort, offset=offset, limit=limit)

    def query_correlation_rule_ids(self, filter: str | None = Field(default=None, description="FQL filter for correlation rule ID query. IMPORTANT: use `falcon://correlation-rules/fql-guide` when building this parameter."), q: str | None = Field(default=None), sort: str | None = Field(default=None), offset: int = Field(default=0, ge=0), limit: int = Field(default=100, ge=1, le=5000)) -> list[str] | dict[str, Any]:
        """Query correlation rule IDs."""
        return self._query_ids_with_guide(operation="queries_rules_get_v1", filter=filter, q=q, sort=sort, offset=offset, limit=limit)

    def query_correlation_rule_version_ids(self, filter: str | None = Field(default=None, description="FQL filter for correlation rule version ID query. IMPORTANT: use `falcon://correlation-rules/fql-guide` when building this parameter."), q: str | None = Field(default=None), sort: str | None = Field(default=None), offset: int = Field(default=0, ge=0), limit: int = Field(default=100, ge=1, le=5000)) -> list[str] | dict[str, Any]:
        """Query correlation rule version IDs."""
        return self._query_ids_with_guide(operation="queries_rules_get_v2", filter=filter, q=q, sort=sort, offset=offset, limit=limit)

    def get_correlation_rules(self, ids: list[str] | None = Field(default=None, description="Correlation rule IDs to retrieve.")) -> list[dict[str, Any]]:
        """Retrieve correlation rules by ID."""
        return self._get_ids_or_error(operation="entities_rules_get_v1", ids=ids, message="`ids` is required to retrieve correlation rules.")

    def get_correlation_rule_versions(self, ids: list[str] | None = Field(default=None, description="Correlation rule version IDs to retrieve.")) -> list[dict[str, Any]]:
        """Retrieve correlation rule versions by ID."""
        return self._get_ids_or_error(operation="entities_rules_get_v2", ids=ids, message="`ids` is required to retrieve correlation rule versions.")

    def get_latest_correlation_rule_versions(self, rule_ids: list[str] | None = Field(default=None, description="Correlation rule IDs to resolve to latest versions.")) -> list[dict[str, Any]]:
        """Retrieve latest rule versions by rule ID."""
        return self._get_ids_or_error(operation="entities_latest_rules_get_v1", ids=rule_ids, message="`rule_ids` is required to retrieve latest correlation rule versions.", id_key="rule_ids")

    def aggregate_correlation_rule_versions(self, body: dict[str, Any] | None = None, filter: str | None = None, ids: list[str] | None = None) -> list[dict[str, Any]]:
        """Aggregate correlation rule versions."""
        request_body = body or {
            key: value
            for key, value in {"filter": filter, "ids": ids}.items()
            if value is not None
        }
        if not request_body:
            return [
                _format_error_response(
                    "Provide `body`, `filter`, or `ids` to aggregate correlation rule versions.",
                    operation="aggregates_rule_versions_post_v1",
                )
            ]
        result = self._base_query_api_call(
            operation="aggregates_rule_versions_post_v1",
            body_params=request_body,
            error_message="Failed to aggregate correlation rule versions",
            default_result=[],
        )
        if self._is_error(result):
            return [result]
        return result

    def create_correlation_rule(self, confirm_execution: bool = Field(default=False), body: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Create a correlation rule."""
        return self._run_body_write(operation="entities_rules_post_v1", confirm_execution=confirm_execution, body=body, validation_message="Provide `body` to create a correlation rule.", error_message="Failed to create correlation rule")

    def update_correlation_rule(self, confirm_execution: bool = Field(default=False), body: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Update a correlation rule."""
        return self._run_body_write(operation="entities_rules_patch_v1", confirm_execution=confirm_execution, body=body, validation_message="Provide `body` to update a correlation rule.", error_message="Failed to update correlation rule")

    def delete_correlation_rules(self, confirm_execution: bool = Field(default=False), ids: list[str] | None = Field(default=None, description="Correlation rule IDs to delete.")) -> list[dict[str, Any]]:
        """Delete correlation rules by ID."""
        return self._run_delete_ids(operation="entities_rules_delete_v1", confirm_execution=confirm_execution, ids=ids, validation_message="`ids` is required to delete correlation rules.", error_message="Failed to delete correlation rules")

    def export_correlation_rule_versions(self, confirm_execution: bool = Field(default=False), body: dict[str, Any] | None = None, filter: str | None = None, sort: str | None = None, get_latest: bool | None = None, report_format: str | None = None, search: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Export correlation rule versions."""
        payload = body or {
            key: value
            for key, value in {
                "get_latest": get_latest,
                "report_format": report_format,
                "search": search or (
                    {k: v for k, v in {"filter": filter, "sort": sort}.items() if v is not None}
                    if filter or sort else None
                ),
            }.items()
            if value is not None
        }
        return self._run_body_write(operation="entities_rule_versions_export_post_v1", confirm_execution=confirm_execution, body=payload, validation_message="Provide `body` or export fields to export correlation rule versions.", error_message="Failed to export correlation rule versions")

    def import_correlation_rule(self, confirm_execution: bool = Field(default=False), body: dict[str, Any] | None = None, rule: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Import a correlation rule version."""
        payload = body or rule
        return self._run_body_write(operation="entities_rule_versions_import_post_v1", confirm_execution=confirm_execution, body=payload, validation_message="Provide `body` or `rule` to import a correlation rule.", error_message="Failed to import correlation rule")

    def publish_correlation_rule_version(self, confirm_execution: bool = Field(default=False), body: dict[str, Any] | None = None, id: str | None = None) -> list[dict[str, Any]]:
        """Publish a correlation rule version."""
        payload = body or ({"id": id} if id else None)
        return self._run_body_write(operation="entities_rule_versions_publish_patch_v1", confirm_execution=confirm_execution, body=payload, validation_message="Provide `body` or `id` to publish a correlation rule version.", error_message="Failed to publish correlation rule version")

    def delete_correlation_rule_versions(self, confirm_execution: bool = Field(default=False), ids: list[str] | None = Field(default=None, description="Correlation rule version IDs to delete.")) -> list[dict[str, Any]]:
        """Delete correlation rule versions by ID."""
        return self._run_delete_ids(operation="entities_rule_versions_delete_v1", confirm_execution=confirm_execution, ids=ids, validation_message="`ids` is required to delete correlation rule versions.", error_message="Failed to delete correlation rule versions")

    def _search_with_guide(self, operation: str, filter: str | None, q: str | None, sort: str | None, offset: int, limit: int) -> list[dict[str, Any]] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params={"filter": filter, "q": q, "sort": sort, "offset": offset, "limit": limit},
            error_message="Failed to search correlation rules",
            default_result=[],
        )
        if self._is_error(result):
            return self._format_fql_error_response([result], filter or q, CORRELATION_RULES_FQL_GUIDE)
        if not result and (filter or q):
            return self._format_fql_error_response([], filter or q, CORRELATION_RULES_FQL_GUIDE)
        return result

    def _query_ids_with_guide(self, operation: str, filter: str | None, q: str | None, sort: str | None, offset: int, limit: int) -> list[str] | dict[str, Any]:
        result = self._base_search_api_call(
            operation=operation,
            search_params={"filter": filter, "q": q, "sort": sort, "offset": offset, "limit": limit},
            error_message="Failed to query correlation rule IDs",
            default_result=[],
        )
        if self._is_error(result):
            return self._format_fql_error_response([result], filter or q, CORRELATION_RULES_FQL_GUIDE)
        if not result and (filter or q):
            return self._format_fql_error_response([], filter or q, CORRELATION_RULES_FQL_GUIDE)
        return result

    def _get_ids_or_error(self, operation: str, ids: list[str] | None, message: str, id_key: str = "ids") -> list[dict[str, Any]]:
        if not ids:
            return [_format_error_response(message, operation=operation)]
        result = self._base_get_by_ids(operation=operation, ids=ids, id_key=id_key, use_params=True)
        if self._is_error(result):
            return [result]
        return result

    def _run_body_write(self, operation: str, confirm_execution: bool, body: dict[str, Any] | None, validation_message: str, error_message: str) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [_format_error_response("This operation requires `confirm_execution=true`.", operation=operation)]
        if body is None:
            return [_format_error_response(validation_message, operation=operation)]
        result = self._base_query_api_call(operation=operation, body_params=body, error_message=error_message, default_result=[])
        if self._is_error(result):
            return [result]
        return result

    def _run_delete_ids(self, operation: str, confirm_execution: bool, ids: list[str] | None, validation_message: str, error_message: str) -> list[dict[str, Any]]:
        if not confirm_execution:
            return [_format_error_response("This operation requires `confirm_execution=true`.", operation=operation)]
        if not ids:
            return [_format_error_response(validation_message, operation=operation)]
        result = self._base_query_api_call(operation=operation, query_params={"ids": ids}, error_message=error_message, default_result=[])
        if self._is_error(result):
            return [result]
        return result
