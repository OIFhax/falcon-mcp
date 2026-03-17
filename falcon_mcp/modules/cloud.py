"""
Cloud module for Falcon MCP Server.

This module provides tools for Falcon Kubernetes container inventory and full
Container Vulnerabilities service collection coverage.
"""

from textwrap import dedent
from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.cloud import (
    IMAGES_VULNERABILITIES_FQL_DOCUMENTATION,
    KUBERNETES_CONTAINERS_FQL_DOCUMENTATION,
)


class CloudModule(BaseModule):
    """Module for Falcon cloud container inventory and vulnerabilities."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(
            server=server,
            method=self.search_kubernetes_containers,
            name="search_kubernetes_containers",
        )
        self._add_tool(
            server=server,
            method=self.count_kubernetes_containers,
            name="count_kubernetes_containers",
        )
        self._add_tool(
            server=server,
            method=self.search_images_vulnerabilities,
            name="search_images_vulnerabilities",
        )
        self._add_tool(
            server=server,
            method=self.get_image_vulnerability_details,
            name="get_image_vulnerability_details",
        )
        self._add_tool(
            server=server,
            method=self.get_image_vulnerability_info,
            name="get_image_vulnerability_info",
        )
        self._add_tool(
            server=server,
            method=self.count_image_vulnerabilities,
            name="count_image_vulnerabilities",
        )
        self._add_tool(
            server=server,
            method=self.count_image_vulnerabilities_by_severity,
            name="count_image_vulnerabilities_by_severity",
        )
        self._add_tool(
            server=server,
            method=self.count_image_vulnerabilities_by_cps_rating,
            name="count_image_vulnerabilities_by_cps_rating",
        )
        self._add_tool(
            server=server,
            method=self.count_image_vulnerabilities_by_cvss_score,
            name="count_image_vulnerabilities_by_cvss_score",
        )
        self._add_tool(
            server=server,
            method=self.count_image_vulnerabilities_by_actively_exploited,
            name="count_image_vulnerabilities_by_actively_exploited",
        )
        self._add_tool(
            server=server,
            method=self.get_top_vulnerabilities_by_image_count,
            name="get_top_vulnerabilities_by_image_count",
        )
        self._add_tool(
            server=server,
            method=self.get_recent_vulnerabilities_by_publication_date,
            name="get_recent_vulnerabilities_by_publication_date",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        kubernetes_containers_fql_resource = TextResource(
            uri=AnyUrl("falcon://cloud/kubernetes-containers/fql-guide"),
            name="falcon_kubernetes_containers_fql_filter_guide",
            description="Contains the guide for the `filter` parameter of Kubernetes container inventory tools.",
            text=KUBERNETES_CONTAINERS_FQL_DOCUMENTATION,
        )

        images_vulnerabilities_fql_resource = TextResource(
            uri=AnyUrl("falcon://cloud/images-vulnerabilities/fql-guide"),
            name="falcon_images_vulnerabilities_fql_filter_guide",
            description="Contains the guide for the `filter` parameter of image vulnerability tools.",
            text=IMAGES_VULNERABILITIES_FQL_DOCUMENTATION,
        )

        self._add_resource(server, kubernetes_containers_fql_resource)
        self._add_resource(server, images_vulnerabilities_fql_resource)

    def search_kubernetes_containers(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for container inventory search. IMPORTANT: use `falcon://cloud/kubernetes-containers/fql-guide` when building this parameter.",
            examples={"cloud_name:'AWS'", "cluster_name:'prod'"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=9999,
            description="Maximum number of containers to return. [1-9999]",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description=dedent(
                """
                Sort containers by inventory fields (for example `last_seen.desc`, `container_name|asc`).
            """
            ).strip(),
            examples={"container_name.desc", "last_seen.desc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search Kubernetes containers (ReadContainerCombined)."""
        return self._cloud_search(
            operation="ReadContainerCombined",
            params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search Kubernetes containers",
        )

    def count_kubernetes_containers(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for container count. IMPORTANT: use `falcon://cloud/kubernetes-containers/fql-guide` when building this parameter.",
            examples={"cloud_name:'Azure'", "container_name:'service'"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Count Kubernetes containers (ReadContainerCount)."""
        return self._cloud_search(
            operation="ReadContainerCount",
            params={"filter": filter},
            error_message="Failed to count Kubernetes containers",
        )

    def search_images_vulnerabilities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for image vulnerabilities. IMPORTANT: use `falcon://cloud/images-vulnerabilities/fql-guide` when building this parameter.",
            examples={"cve_id:*'*2025*'", "cvss_score:>5"},
        ),
        limit: int = Field(
            default=10,
            ge=1,
            le=9999,
            description="Maximum number of vulnerability records to return. [1-9999]",
        ),
        offset: int | None = Field(
            default=None,
            description="Starting index from which to return records.",
        ),
        sort: str | None = Field(
            default=None,
            description="Sort expression for vulnerabilities.",
            examples={"cvss_score.desc", "cps_current_rating.asc"},
        ),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Search image vulnerabilities (ReadCombinedVulnerabilities)."""
        return self._cloud_search(
            operation="ReadCombinedVulnerabilities",
            params={"filter": filter, "limit": limit, "offset": offset, "sort": sort},
            error_message="Failed to search image vulnerabilities",
        )

    def get_image_vulnerability_details(
        self,
        image_id: str | None = Field(
            default=None,
            description="Image UUID to retrieve vulnerability details for.",
        ),
        filter: str | None = Field(
            default=None,
            description="Optional FQL vulnerability filter.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]]:
        """Get vulnerability details for a specific image (ReadCombinedVulnerabilitiesDetails)."""
        if not image_id:
            return [
                _format_error_response(
                    "`image_id` is required to retrieve image vulnerability details.",
                    operation="ReadCombinedVulnerabilitiesDetails",
                )
            ]

        result = self._cloud_search(
            operation="ReadCombinedVulnerabilitiesDetails",
            params={"id": image_id, "filter": filter, "limit": limit, "offset": offset},
            error_message="Failed to retrieve image vulnerability details",
        )

        if self._is_error(result):
            return [result]
        return result

    def get_image_vulnerability_info(
        self,
        cve_id: str | None = Field(
            default=None,
            description="CVE ID to retrieve package and vulnerability info for.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]]:
        """Get package/vulnerability info by CVE (ReadCombinedVulnerabilitiesInfo)."""
        if not cve_id:
            return [
                _format_error_response(
                    "`cve_id` is required to retrieve vulnerability info.",
                    operation="ReadCombinedVulnerabilitiesInfo",
                )
            ]

        result = self._cloud_search(
            operation="ReadCombinedVulnerabilitiesInfo",
            params={"cve_id": cve_id, "limit": limit, "offset": offset},
            error_message="Failed to retrieve vulnerability info",
        )

        if self._is_error(result):
            return [result]
        return result

    def count_image_vulnerabilities(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for vulnerability count aggregation.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Aggregate vulnerability counts (ReadVulnerabilityCount)."""
        return self._cloud_search(
            operation="ReadVulnerabilityCount",
            params={"filter": filter, "limit": limit, "offset": offset},
            error_message="Failed to retrieve vulnerability counts",
        )

    def count_image_vulnerabilities_by_severity(
        self,
        filter: str | None = Field(default=None, description="FQL filter for severity aggregation."),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Aggregate vulnerability counts by severity (ReadVulnerabilityCountBySeverity)."""
        return self._cloud_search(
            operation="ReadVulnerabilityCountBySeverity",
            params={"filter": filter, "limit": limit, "offset": offset},
            error_message="Failed to retrieve vulnerability counts by severity",
        )

    def count_image_vulnerabilities_by_cps_rating(
        self,
        filter: str | None = Field(default=None, description="FQL filter for CPS rating aggregation."),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Aggregate vulnerability counts by CPS rating (ReadVulnerabilityCountByCPSRating)."""
        return self._cloud_search(
            operation="ReadVulnerabilityCountByCPSRating",
            params={"filter": filter, "limit": limit, "offset": offset},
            error_message="Failed to retrieve vulnerability counts by CPS rating",
        )

    def count_image_vulnerabilities_by_cvss_score(
        self,
        filter: str | None = Field(default=None, description="FQL filter for CVSS score aggregation."),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Aggregate vulnerability counts by CVSS score (ReadVulnerabilityCountByCVSSScore)."""
        return self._cloud_search(
            operation="ReadVulnerabilityCountByCVSSScore",
            params={"filter": filter, "limit": limit, "offset": offset},
            error_message="Failed to retrieve vulnerability counts by CVSS score",
        )

    def count_image_vulnerabilities_by_actively_exploited(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL filter for actively exploited aggregation.",
        ),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Aggregate vulnerability counts by actively exploited status (ReadVulnerabilityCountByActivelyExploited)."""
        return self._cloud_search(
            operation="ReadVulnerabilityCountByActivelyExploited",
            params={"filter": filter, "limit": limit, "offset": offset},
            error_message="Failed to retrieve vulnerability counts by actively exploited status",
        )

    def get_top_vulnerabilities_by_image_count(
        self,
        filter: str | None = Field(default=None, description="FQL filter for vulnerability ranking."),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get vulnerabilities with the highest image impact (ReadVulnerabilitiesByImageCount)."""
        return self._cloud_search(
            operation="ReadVulnerabilitiesByImageCount",
            params={"filter": filter, "limit": limit, "offset": offset},
            error_message="Failed to retrieve vulnerabilities by image impact",
        )

    def get_recent_vulnerabilities_by_publication_date(
        self,
        filter: str | None = Field(default=None, description="FQL filter for publication-date ranking."),
        limit: int = Field(default=100, ge=1, le=5000, description="Maximum records to return."),
        offset: int | None = Field(default=None, description="Starting index from which to return records."),
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Get vulnerabilities ordered by publication date (ReadVulnerabilitiesPublicationDate)."""
        return self._cloud_search(
            operation="ReadVulnerabilitiesPublicationDate",
            params={"filter": filter, "limit": limit, "offset": offset},
            error_message="Failed to retrieve vulnerabilities by publication date",
        )

    def _cloud_search(
        self,
        operation: str,
        params: dict[str, Any],
        error_message: str,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        return self._base_search_api_call(
            operation=operation,
            search_params=params,
            error_message=error_message,
        )
