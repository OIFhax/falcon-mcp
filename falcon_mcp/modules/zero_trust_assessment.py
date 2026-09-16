"""
Zero Trust Assessment module for Falcon MCP Server.

This module provides tools for querying host Zero Trust scores and retrieving
assessment details and tenant audit metrics.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.utils import unwrap_field_default
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.zero_trust_assessment import (
    SEARCH_ZTA_ASSESSMENTS_FQL_DOCUMENTATION,
    SEARCH_ZTA_COMBINED_ASSESSMENTS_FQL_DOCUMENTATION,
)

SORT_ORDERS = ("asc", "desc")


def _build_score_filter(min_score: int | None, max_score: int | None) -> str:
    """Build the score filter required by the assessment query endpoint."""
    parts = []
    if min_score is not None:
        parts.append(f"score:>={min_score}")
    if max_score is not None:
        parts.append(f"score:<={max_score}")
    return "+".join(parts) if parts else "score:>=0"


def _missing_aids(requested: list[str], records: list[dict[str, Any]]) -> list[str]:
    """Return requested AIDs with no assessment, preserving request order."""
    found = {record.get("aid") for record in records}
    return [aid for aid in requested if aid not in found]


class ZeroTrustAssessmentModule(BaseModule):
    """Module for Zero Trust Assessment operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server.

        Args:
            server: MCP server instance
        """
        self._add_tool(
            server=server,
            method=self.search_zta_assessments,
            name="search_zta_assessments",
        )
        self._add_tool(
            server=server,
            method=self.search_zta_assessments_by_score,
            name="search_zta_assessments_by_score",
        )
        self._add_tool(
            server=server,
            method=self.search_zta_combined_assessments,
            name="search_zta_combined_assessments",
        )
        self._add_tool(
            server=server,
            method=self.get_zta_assessment_details,
            name="get_zta_assessment_details",
        )
        self._add_tool(
            server=server,
            method=self.get_zta_audit_report,
            name="get_zta_audit_report",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server.

        Args:
            server: MCP server instance
        """
        search_zta_assessments_fql_resource = TextResource(
            uri=AnyUrl("falcon://zero-trust-assessment/assessments/fql-guide"),
            name="falcon_search_zta_assessments_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_zta_assessments_by_score` tool.",
            text=SEARCH_ZTA_ASSESSMENTS_FQL_DOCUMENTATION,
        )

        search_zta_combined_assessments_fql_resource = TextResource(
            uri=AnyUrl("falcon://zero-trust-assessment/combined-assessments/fql-guide"),
            name="falcon_search_zta_combined_assessments_fql_guide",
            description="Contains the guide for the `filter` parameter of the `falcon_search_zta_combined_assessments` tool.",
            text=SEARCH_ZTA_COMBINED_ASSESSMENTS_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_zta_assessments_fql_resource)
        self._add_resource(server, search_zta_combined_assessments_fql_resource)

    def search_zta_assessments(
        self,
        min_score: int | None = Field(
            default=None,
            ge=0,
            le=100,
            description="Lowest Zero Trust score to include (0-100). Omit for no lower bound.",
        ),
        max_score: int | None = Field(
            default=None,
            ge=0,
            le=100,
            description=(
                "Highest Zero Trust score to include (0-100). Combine with `min_score` "
                "to select a range."
            ),
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of hosts to return. (Max: 1000)",
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token from a previous response's `pagination.next`.",
        ),
        sort_order: str = Field(
            default="asc",
            description="'asc' for weakest first, 'desc' for strongest first.",
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Zero Trust scores and return full assessment details."""
        min_score = unwrap_field_default(min_score)
        max_score = unwrap_field_default(max_score)
        limit = unwrap_field_default(limit)
        after = unwrap_field_default(after)
        sort_order = unwrap_field_default(sort_order)

        if sort_order not in SORT_ORDERS:
            return _format_error_response(
                f"Invalid sort_order '{sort_order}'. Valid values are: {', '.join(SORT_ORDERS)}."
            )
        if min_score is not None and max_score is not None and min_score > max_score:
            return _format_error_response(
                f"min_score ({min_score}) is greater than max_score ({max_score}), "
                "so no host can match."
            )

        score_filter = _build_score_filter(min_score, max_score)
        assessments, pagination = self._base_search_with_meta(
            operation="getAssessmentsByScoreV1",
            search_params={
                "filter": score_filter,
                "limit": limit,
                "after": after,
                "sort": f"score|{sort_order}",
            },
            error_message="Failed to search Zero Trust Assessment scores",
        )
        if self._is_error(assessments):
            return [assessments]

        aids = [aid for record in assessments if (aid := record.get("aid"))]
        if not aids:
            return self._build_pagination_envelope([], pagination, score_filter)

        details = self._base_get_by_ids(
            operation="getAssessmentV1",
            ids=aids,
            use_params=True,
        )
        if self._is_error(details):
            return [details]

        details = self._reorder_by_ids(aids, details, id_field="aid")
        envelope = self._build_pagination_envelope(details, pagination, score_filter)
        missing = _missing_aids(aids, details)
        if missing:
            envelope["not_found"] = missing
        return envelope

    def search_zta_assessments_by_score(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL score filter for Zero Trust Assessment search. IMPORTANT: use the `falcon://zero-trust-assessment/assessments/fql-guide` resource when building this filter parameter.",
            examples={"score:>=80", "score:<50"},
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of score assessment records to return. [1-1000]",
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token from previous response.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort assessments by score.

                Supported formats: 'score.asc', 'score.desc', 'score|asc', 'score|desc'
            """).strip(),
            examples={"score|desc", "score.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for host Zero Trust assessments by score filter."""
        if not filter:
            return [
                _format_error_response(
                    "`filter` is required for score-based ZTA search.",
                    operation="getAssessmentsByScoreV1",
                )
            ]

        result = self._base_search_api_call(
            operation="getAssessmentsByScoreV1",
            search_params={
                "filter": filter,
                "limit": limit,
                "after": after,
                "sort": sort,
            },
            error_message="Failed to search Zero Trust assessments by score",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_ZTA_ASSESSMENTS_FQL_DOCUMENTATION,
            )

        return result

    def search_zta_combined_assessments(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for combined Zero Trust assessments. IMPORTANT: use the `falcon://zero-trust-assessment/combined-assessments/fql-guide` resource when building this filter parameter.",
            examples={"updated_timestamp:>'now-7d'", "aid:'0123456789abcdef0123456789abcdef'"},
        ),
        facet: list[str] | None = Field(
            default=None,
            description="Optional facet blocks to include. Supported values: `host`, `finding.rule`.",
        ),
        limit: int = Field(
            default=100,
            ge=1,
            le=5000,
            description="Maximum number of combined assessment records to return. [1-5000]",
        ),
        after: str | None = Field(
            default=None,
            description="Pagination token from previous response.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent("""
                Sort combined assessments.

                Common options: created_timestamp|desc, updated_timestamp|asc
                Supported formats: 'field.asc', 'field.desc', 'field|asc', 'field|desc'
            """).strip(),
            examples={"updated_timestamp.desc", "created_timestamp|asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search for combined Zero Trust assessments with host/finding facets."""
        if not filter:
            return [
                _format_error_response(
                    "`filter` is required for combined ZTA assessment search.",
                    operation="getCombinedAssessmentsQuery",
                )
            ]

        result = self._base_search_api_call(
            operation="getCombinedAssessmentsQuery",
            search_params={
                "filter": filter,
                "facet": facet,
                "limit": limit,
                "after": after,
                "sort": sort,
            },
            error_message="Failed to search combined Zero Trust assessments",
        )

        if self._is_error(result):
            return self._format_fql_error_response(
                [result],
                filter,
                SEARCH_ZTA_COMBINED_ASSESSMENTS_FQL_DOCUMENTATION,
            )

        return result

    def get_zta_assessment_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Host agent IDs (AIDs) to retrieve Zero Trust assessments for.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve Zero Trust assessment details for specific host agent IDs."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve Zero Trust assessment details.",
                    operation="getAssessmentV1",
                )
            ]

        result = self._base_get_by_ids(
            operation="getAssessmentV1",
            ids=ids,
            id_key="ids",
            use_params=True,
        )

        if self._is_error(result):
            return [result]

        return result

    def get_zta_audit_report(self) -> list[dict[str, Any]]:
        """Retrieve tenant-wide Zero Trust Assessment audit metrics."""
        command_response = self.client.command("getAuditV1")
        result = handle_api_response(
            command_response,
            operation="getAuditV1",
            error_message="Failed to retrieve Zero Trust audit report",
            default_result=[],
        )

        if self._is_error(result):
            return [result]

        return result
