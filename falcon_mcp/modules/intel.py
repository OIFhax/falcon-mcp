"""
Intel module for Falcon MCP Server.

Provides full FalconPy Intel service collection coverage for actors, indicators,
reports, rules, malware, MITRE ATT&CK, and vulnerability intelligence data.
"""

from typing import Any

from mcp.server import FastMCP
from mcp.server.fastmcp.resources import TextResource
from pydantic import AnyUrl, Field

from falcon_mcp.common.errors import _format_error_response, handle_api_response
from falcon_mcp.common.logging import get_logger
from falcon_mcp.common.utils import prepare_api_parameters
from falcon_mcp.modules.base import BaseModule
from falcon_mcp.resources.intel import (
    QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION,
    QUERY_INDICATOR_ENTITIES_FQL_DOCUMENTATION,
    QUERY_REPORT_ENTITIES_FQL_DOCUMENTATION,
)

logger = get_logger(__name__)


INTEL_RULE_TYPE_HELP = """
Accepted values:
- common-event-format
- netwitness
- snort-suricata-master
- snort-suricata-update
- snort-suricata-changelog
- yara-master
- yara-update
- yara-changelog
- cql-master
- cql-update
- cql-changelog
""".strip()


class IntelModule(BaseModule):
    """Module for CrowdStrike Falcon Intel operations."""

    def register_tools(self, server: FastMCP) -> None:
        """Register tools with the MCP server."""
        self._add_tool(server=server, method=self.search_actors, name="search_actors")
        self._add_tool(server=server, method=self.query_actor_ids, name="query_actor_ids")
        self._add_tool(server=server, method=self.get_actor_details, name="get_actor_details")

        self._add_tool(server=server, method=self.search_indicators, name="search_indicators")
        self._add_tool(server=server, method=self.query_indicator_ids, name="query_indicator_ids")
        self._add_tool(server=server, method=self.get_indicator_details, name="get_indicator_details")

        self._add_tool(server=server, method=self.search_reports, name="search_reports")
        self._add_tool(server=server, method=self.query_report_ids, name="query_report_ids")
        self._add_tool(server=server, method=self.get_report_details, name="get_report_details")
        self._add_tool(server=server, method=self.download_report_pdf, name="download_report_pdf")

        self._add_tool(server=server, method=self.query_rule_ids, name="query_rule_ids")
        self._add_tool(server=server, method=self.get_rule_details, name="get_rule_details")
        self._add_tool(server=server, method=self.download_rule_file, name="download_rule_file")
        self._add_tool(
            server=server,
            method=self.download_latest_rule_file,
            name="download_latest_rule_file",
        )

        self._add_tool(server=server, method=self.query_malware_ids, name="query_malware_ids")
        self._add_tool(server=server, method=self.search_malware, name="search_malware")
        self._add_tool(server=server, method=self.get_malware_details, name="get_malware_details")
        self._add_tool(
            server=server,
            method=self.get_malware_mitre_report,
            name="get_malware_mitre_report",
        )

        self._add_tool(server=server, method=self.query_mitre_attacks, name="query_mitre_attacks")
        self._add_tool(
            server=server,
            method=self.query_mitre_attacks_for_malware,
            name="query_mitre_attacks_for_malware",
        )
        self._add_tool(server=server, method=self.get_mitre_attack_details, name="get_mitre_attack_details")
        self._add_tool(server=server, method=self.get_mitre_report, name="get_mitre_report")

        self._add_tool(
            server=server,
            method=self.query_vulnerability_ids,
            name="query_vulnerability_ids",
        )
        self._add_tool(
            server=server,
            method=self.get_vulnerability_details,
            name="get_vulnerability_details",
        )

    def register_resources(self, server: FastMCP) -> None:
        """Register resources with the MCP server."""
        search_actors_fql_resource = TextResource(
            uri=AnyUrl("falcon://intel/actors/fql-guide"),
            name="falcon_search_actors_fql_guide",
            description="Contains the guide for the `filter` parameter of actor tools.",
            text=QUERY_ACTOR_ENTITIES_FQL_DOCUMENTATION,
        )

        search_indicators_fql_resource = TextResource(
            uri=AnyUrl("falcon://intel/indicators/fql-guide"),
            name="falcon_search_indicators_fql_guide",
            description="Contains the guide for the `filter` parameter of indicator tools.",
            text=QUERY_INDICATOR_ENTITIES_FQL_DOCUMENTATION,
        )

        search_reports_fql_resource = TextResource(
            uri=AnyUrl("falcon://intel/reports/fql-guide"),
            name="falcon_search_reports_fql_guide",
            description="Contains the guide for the `filter` parameter of report tools.",
            text=QUERY_REPORT_ENTITIES_FQL_DOCUMENTATION,
        )

        self._add_resource(server, search_actors_fql_resource)
        self._add_resource(server, search_indicators_fql_resource)
        self._add_resource(server, search_reports_fql_resource)

    def search_actors(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression. IMPORTANT: use `falcon://intel/actors/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of records."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(
            default=None,
            description="Sort expression. Example: `created_date|desc`.",
        ),
        q: str | None = Field(default=None, description="Free-text search across indexed fields."),
        fields: list[str] | None = Field(
            default=None,
            description="Specific fields to return (or collection alias such as `__full__`).",
        ),
    ) -> list[dict[str, Any]]:
        """Query actor entities (QueryIntelActorEntities)."""
        return self._run_search(
            operation="QueryIntelActorEntities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "fields": fields,
            },
            error_message="Failed to search actors",
        )

    def query_actor_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression. IMPORTANT: use `falcon://intel/actors/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of IDs."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text search."),
    ) -> list[Any]:
        """Query actor IDs (QueryIntelActorIds)."""
        return self._run_search(
            operation="QueryIntelActorIds",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to query actor IDs",
        )

    def get_actor_details(
        self,
        ids: list[str] | None = Field(default=None, description="Actor IDs to retrieve."),
        fields: list[str] | None = Field(
            default=None,
            description="Optional list of actor fields to include.",
        ),
    ) -> list[dict[str, Any]]:
        """Get actor entities by ID (GetIntelActorEntities)."""
        return self._run_get_by_ids(
            operation="GetIntelActorEntities",
            ids=ids,
            validation_message="`ids` is required to retrieve actor details.",
            use_params=True,
            fields=fields,
        )

    def search_indicators(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression. IMPORTANT: use `falcon://intel/indicators/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=10, ge=1, le=10000, description="Maximum number of records."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text search."),
        include_deleted: bool = Field(
            default=False,
            description="Include both published and deleted indicators.",
        ),
        include_relations: bool = Field(
            default=False,
            description="Include related indicators.",
        ),
        fields: list[str] | None = Field(
            default=None,
            description="Specific fields to return (or collection alias such as `__full__`).",
        ),
    ) -> list[dict[str, Any]]:
        """Query indicator entities (QueryIntelIndicatorEntities)."""
        return self._run_search(
            operation="QueryIntelIndicatorEntities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "include_deleted": include_deleted,
                "include_relations": include_relations,
                "fields": fields,
            },
            error_message="Failed to search indicators",
        )

    def query_indicator_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression. IMPORTANT: use `falcon://intel/indicators/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=10, ge=1, le=10000, description="Maximum number of IDs."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text search."),
        include_deleted: bool = Field(
            default=False,
            description="Include both published and deleted indicators.",
        ),
        include_relations: bool = Field(
            default=False,
            description="Include related indicators.",
        ),
    ) -> list[Any]:
        """Query indicator IDs (QueryIntelIndicatorIds)."""
        return self._run_search(
            operation="QueryIntelIndicatorIds",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "include_deleted": include_deleted,
                "include_relations": include_relations,
            },
            error_message="Failed to query indicator IDs",
        )

    def get_indicator_details(
        self,
        ids: list[str] | None = Field(default=None, description="Indicator IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get indicator entities by ID (GetIntelIndicatorEntities)."""
        return self._run_get_by_ids(
            operation="GetIntelIndicatorEntities",
            ids=ids,
            validation_message="`ids` is required to retrieve indicator details.",
            use_params=False,
        )

    def search_reports(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression. IMPORTANT: use `falcon://intel/reports/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of records."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text search."),
        fields: list[str] | None = Field(
            default=None,
            description="Specific fields to return (or collection alias such as `__full__`).",
        ),
    ) -> list[dict[str, Any]]:
        """Query report entities (QueryIntelReportEntities)."""
        return self._run_search(
            operation="QueryIntelReportEntities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "fields": fields,
            },
            error_message="Failed to search reports",
        )

    def query_report_ids(
        self,
        filter: str | None = Field(
            default=None,
            description="FQL query expression. IMPORTANT: use `falcon://intel/reports/fql-guide` when building this parameter.",
        ),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of IDs."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text search."),
    ) -> list[Any]:
        """Query report IDs (QueryIntelReportIds)."""
        return self._run_search(
            operation="QueryIntelReportIds",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to query report IDs",
        )

    def get_report_details(
        self,
        ids: list[str] | None = Field(default=None, description="Report IDs to retrieve."),
        fields: list[str] | None = Field(default=None, description="Optional list of report fields."),
    ) -> list[dict[str, Any]]:
        """Get report entities by ID (GetIntelReportEntities)."""
        return self._run_get_by_ids(
            operation="GetIntelReportEntities",
            ids=ids,
            validation_message="`ids` is required to retrieve report details.",
            use_params=True,
            fields=fields,
        )

    def download_report_pdf(
        self,
        report_id: str = Field(description="Report ID to download as PDF."),
    ) -> list[dict[str, Any]]:
        """Download report PDF metadata (GetIntelReportPDF)."""
        result = self._run_binary_operation(
            operation="GetIntelReportPDF",
            api_params={"id": report_id},
            error_message="Failed to download report PDF",
            binary_mode="pdf",
        )
        if isinstance(result, str):
            return [{"content": result}]
        return result

    def query_rule_ids(
        self,
        rule_type: str = Field(
            description=f"Rule feed type. {INTEL_RULE_TYPE_HELP}",
        ),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of IDs."),
        offset: int = Field(default=0, ge=0, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        name: list[str] | None = Field(default=None, description="Rule title filter list."),
        description: list[str] | None = Field(default=None, description="Description substring filters."),
        tags: list[str] | None = Field(default=None, description="Rule tag filters."),
        min_created_date: int | None = Field(
            default=None,
            description="Filter results created on or after this timestamp.",
        ),
        max_created_date: str | None = Field(
            default=None,
            description="Filter results created on or before this timestamp/date string.",
        ),
        q: str | None = Field(default=None, description="Free-text search."),
    ) -> list[Any]:
        """Query rule IDs (QueryIntelRuleIds)."""
        return self._run_search(
            operation="QueryIntelRuleIds",
            search_params={
                "type": rule_type,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "name": name,
                "description": description,
                "tags": tags,
                "min_created_date": min_created_date,
                "max_created_date": max_created_date,
                "q": q,
            },
            error_message="Failed to query rule IDs",
        )

    def get_rule_details(
        self,
        ids: list[str] | None = Field(default=None, description="Rule IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get rule entities by ID (GetIntelRuleEntities)."""
        return self._run_get_by_ids(
            operation="GetIntelRuleEntities",
            ids=ids,
            validation_message="`ids` is required to retrieve rule details.",
            use_params=True,
        )

    def download_rule_file(
        self,
        rule_id: int = Field(description="Rule set ID to download."),
        format: str = Field(default="zip", description="Archive format (`zip` or `gzip`)."),
    ) -> list[dict[str, Any]]:
        """Download rule archive metadata (GetIntelRuleFile)."""
        result = self._run_binary_operation(
            operation="GetIntelRuleFile",
            api_params={"id": rule_id, "format": format},
            error_message="Failed to download rule file",
            binary_mode="archive",
        )
        if isinstance(result, str):
            return [{"content": result}]
        return result

    def download_latest_rule_file(
        self,
        rule_type: str = Field(description=f"Rule feed type. {INTEL_RULE_TYPE_HELP}"),
        format: str = Field(default="zip", description="Archive format (`zip` or `gzip`)."),
        if_none_match: str | None = Field(
            default=None,
            description="Optional ETag value for conditional retrieval.",
        ),
        if_modified_since: str | None = Field(
            default=None,
            description="Optional date for conditional retrieval.",
        ),
    ) -> list[dict[str, Any]]:
        """Download latest rule archive metadata (GetLatestIntelRuleFile)."""
        result = self._run_binary_operation(
            operation="GetLatestIntelRuleFile",
            api_params={
                "type": rule_type,
                "format": format,
                "if_none_match": if_none_match,
                "if_modified_since": if_modified_since,
            },
            error_message="Failed to download latest rule file",
            binary_mode="archive",
        )
        if isinstance(result, str):
            return [{"content": result}]
        return result

    def query_malware_ids(
        self,
        filter: str | None = Field(default=None, description="FQL query expression."),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of IDs."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text search."),
    ) -> list[Any]:
        """Query malware family IDs/names (QueryMalware)."""
        return self._run_search(
            operation="QueryMalware",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to query malware IDs",
        )

    def search_malware(
        self,
        filter: str | None = Field(default=None, description="FQL query expression."),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of records."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text search."),
        fields: list[str] | None = Field(default=None, description="Specific malware fields to return."),
    ) -> list[dict[str, Any]]:
        """Query malware entities (QueryMalwareEntities)."""
        return self._run_search(
            operation="QueryMalwareEntities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
                "fields": fields,
            },
            error_message="Failed to search malware",
        )

    def get_malware_details(
        self,
        ids: list[str] | None = Field(default=None, description="Malware family IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get malware entities by ID (GetMalwareEntities)."""
        result = self._run_binary_operation(
            operation="GetMalwareEntities",
            api_params={"ids": ids},
            error_message="Failed to get malware details",
            binary_mode="text",
            required_ids=ids,
            required_message="`ids` is required to retrieve malware details.",
        )
        if isinstance(result, str):
            return [{"content": result}]
        return result

    def get_malware_mitre_report(
        self,
        malware_id: str = Field(
            description="Malware family name (lowercase slug) to retrieve MITRE ATT&CK report for.",
        ),
        format: str = Field(
            default="JSON",
            description="Report format: `CSV`, `JSON`, or `JSON_NAVIGATOR`.",
        ),
    ) -> str | list[dict[str, Any]]:
        """Get malware MITRE ATT&CK report (GetMalwareMitreReport)."""
        return self._run_binary_operation(
            operation="GetMalwareMitreReport",
            api_params={"id": malware_id, "format": format},
            error_message="Failed to get malware MITRE report",
            binary_mode="text",
        )

    def query_mitre_attacks(
        self,
        id: str | None = Field(
            default=None,
            description="Single actor slug ID for MITRE lookup.",
        ),
        ids: list[str] | None = Field(
            default=None,
            description="One or more actor slug IDs for MITRE lookup.",
        ),
    ) -> list[Any]:
        """Query MITRE tactics/techniques by actor (QueryMitreAttacks)."""
        if not id and not ids:
            return [
                _format_error_response(
                    "Either `id` or `ids` is required to query MITRE attacks.",
                    operation="QueryMitreAttacks",
                )
            ]

        return self._run_search(
            operation="QueryMitreAttacks",
            search_params={
                "id": id,
                "ids": ids,
            },
            error_message="Failed to query MITRE attacks",
        )

    def query_mitre_attacks_for_malware(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="Malware family slugs to query MITRE ATT&CK techniques for.",
        ),
    ) -> str | list[dict[str, Any]] | list[Any]:
        """Query MITRE tactics/techniques by malware (QueryMitreAttacksForMalware)."""
        return self._run_binary_operation(
            operation="QueryMitreAttacksForMalware",
            api_params={"ids": ids},
            error_message="Failed to query malware MITRE attacks",
            binary_mode="text",
            required_ids=ids,
            required_message="`ids` is required to query malware MITRE attacks.",
        )

    def get_mitre_attack_details(
        self,
        ids: list[str] | None = Field(
            default=None,
            description="MITRE attack IDs from `query_mitre_attacks` to retrieve report/observable detail.",
        ),
    ) -> list[dict[str, Any]]:
        """Retrieve report and observable detail by MITRE attack IDs (PostMitreAttacks)."""
        if not ids:
            return [
                _format_error_response(
                    "`ids` is required to retrieve MITRE attack details.",
                    operation="PostMitreAttacks",
                )
            ]

        api_response = self._base_query_api_call(
            operation="PostMitreAttacks",
            body_params={"ids": ids},
            error_message="Failed to retrieve MITRE attack details",
            default_result=[],
        )

        if self._is_error(api_response):
            return [api_response]

        return api_response

    def get_mitre_report(
        self,
        actor: str = Field(
            description="Threat actor name or numeric actor ID.",
            examples={"WARP PANDA", "234987"},
        ),
        format: str = Field(
            default="json",
            description="Report format (`csv` or `json`).",
            examples={"json", "csv"},
        ),
    ) -> str | list[dict[str, Any]]:
        """Generate MITRE ATT&CK report for a threat actor (GetMitreReport)."""
        actor_id = actor.strip()

        if not actor_id.isdigit():
            escaped_actor = actor.replace("'", "\\'")
            search_results = self._run_search(
                operation="QueryIntelActorEntities",
                search_params={
                    "filter": f"name:'{escaped_actor}'",
                    "limit": 1,
                },
                error_message="Failed to search for actor by name",
            )

            if search_results and isinstance(search_results[0], dict) and "error" in search_results[0]:
                return search_results

            if not search_results or not isinstance(search_results[0], dict):
                return [
                    {
                        "error": "Actor not found",
                        "message": f"No actor found with name: {actor}",
                    }
                ]

            resolved_id = search_results[0].get("id")
            if not resolved_id:
                return [
                    {
                        "error": "Invalid actor data",
                        "message": (
                            f"Found actor '{search_results[0].get('name', 'unknown')}' "
                            "but no ID was returned."
                        ),
                        "actor_data": search_results[0],
                    }
                ]

            actor_id = str(resolved_id)
            logger.debug("Resolved actor '%s' to ID %s", actor, actor_id)

        return self._run_binary_operation(
            operation="GetMitreReport",
            api_params={
                "actor_id": actor_id,
                "format": format,
            },
            error_message="Failed to get MITRE report",
            binary_mode="text",
        )

    def query_vulnerability_ids(
        self,
        filter: str | None = Field(default=None, description="FQL query expression."),
        limit: int = Field(default=10, ge=1, le=5000, description="Maximum number of IDs."),
        offset: int | None = Field(default=None, description="Result set offset."),
        sort: str | None = Field(default=None, description="Sort expression."),
        q: str | None = Field(default=None, description="Free-text query."),
    ) -> list[Any]:
        """Query vulnerability IDs (QueryVulnerabilities)."""
        return self._run_search(
            operation="QueryVulnerabilities",
            search_params={
                "filter": filter,
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "q": q,
            },
            error_message="Failed to query vulnerability IDs",
        )

    def get_vulnerability_details(
        self,
        ids: list[str] | None = Field(default=None, description="Vulnerability IDs to retrieve."),
    ) -> list[dict[str, Any]]:
        """Get vulnerability entities by ID (GetVulnerabilities)."""
        return self._run_get_by_ids(
            operation="GetVulnerabilities",
            ids=ids,
            validation_message="`ids` is required to retrieve vulnerability details.",
            use_params=False,
        )

    def _run_search(
        self,
        operation: str,
        search_params: dict[str, Any],
        error_message: str,
    ) -> list[Any]:
        """Run a search/query operation and normalize errors."""
        api_response = self._base_search_api_call(
            operation=operation,
            search_params=search_params,
            error_message=error_message,
        )

        if self._is_error(api_response):
            return [api_response]

        return api_response

    def _run_get_by_ids(
        self,
        operation: str,
        ids: list[str] | None,
        validation_message: str,
        use_params: bool,
        **additional_params: Any,
    ) -> list[dict[str, Any]]:
        """Run a get-by-ids operation and normalize errors."""
        if not ids:
            return [_format_error_response(validation_message, operation=operation)]

        api_response = self._base_get_by_ids(
            operation=operation,
            ids=ids,
            use_params=use_params,
            **additional_params,
        )

        if self._is_error(api_response):
            return [api_response]

        return api_response

    def _run_binary_operation(
        self,
        operation: str,
        api_params: dict[str, Any],
        error_message: str,
        binary_mode: str,
        required_ids: list[str] | None = None,
        required_message: str | None = None,
    ) -> str | list[dict[str, Any]] | list[Any]:
        """Run an operation that may return binary data."""
        if required_message is not None and not required_ids:
            return [_format_error_response(required_message, operation=operation)]

        prepared_params = prepare_api_parameters(api_params)
        command_response = self.client.command(
            operation,
            parameters=prepared_params,
        )

        return self._normalize_binary_response(
            operation=operation,
            command_response=command_response,
            error_message=error_message,
            binary_mode=binary_mode,
        )

    def _normalize_binary_response(
        self,
        operation: str,
        command_response: Any,
        error_message: str,
        binary_mode: str,
    ) -> str | list[dict[str, Any]] | list[Any]:
        """Normalize FalconPy responses that may be bytes or dict."""
        if isinstance(command_response, (bytes, bytearray)):
            return self._format_binary_payload(
                payload=bytes(command_response),
                operation=operation,
                binary_mode=binary_mode,
            )

        if not isinstance(command_response, dict):
            return [
                _format_error_response(
                    f"Unexpected response type: {type(command_response).__name__}",
                    operation=operation,
                )
            ]

        status_code = command_response.get("status_code")
        body = command_response.get("body")

        if status_code is not None and status_code >= 300:
            error_result = handle_api_response(
                command_response,
                operation=operation,
                error_message=error_message,
                default_result=[],
            )
            return [error_result] if self._is_error(error_result) else error_result

        if isinstance(body, (bytes, bytearray)):
            return self._format_binary_payload(
                payload=bytes(body),
                operation=operation,
                binary_mode=binary_mode,
            )

        if isinstance(body, str):
            return body

        if isinstance(body, list):
            return body

        parsed_response = handle_api_response(
            command_response,
            operation=operation,
            error_message=error_message,
            default_result=[],
        )

        if self._is_error(parsed_response):
            return [parsed_response]

        return parsed_response

    def _format_binary_payload(
        self,
        payload: bytes,
        operation: str,
        binary_mode: str,
    ) -> str | list[dict[str, Any]]:
        """Format binary endpoint results for MCP responses."""
        if binary_mode == "text":
            try:
                return payload.decode("utf-8")
            except UnicodeDecodeError:
                return [
                    _format_error_response(
                        "Endpoint returned non-text binary content that cannot be displayed inline.",
                        details={"operation": operation, "size_bytes": len(payload)},
                        operation=operation,
                    )
                ]

        if binary_mode == "pdf":
            return [
                {
                    "message": (
                        "PDF content is binary and is not rendered inline by this MCP tool. "
                        "Use a file download-capable client to save and open the PDF."
                    ),
                    "operation": operation,
                    "size_bytes": len(payload),
                }
            ]

        return [
            {
                "message": (
                    "Archive content is binary and is not rendered inline by this MCP tool. "
                    "Use a file download-capable client to save and extract it."
                ),
                "operation": operation,
                "size_bytes": len(payload),
            }
        ]
