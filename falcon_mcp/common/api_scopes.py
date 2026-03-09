"""
API scope definitions and utilities for Falcon MCP Server

This module provides API scope definitions and related utilities for the Falcon MCP server.
"""

from .logging import get_logger

logger = get_logger(__name__)

# Map of API operations to required scopes
# This can be expanded as more modules and operations are added
API_SCOPE_REQUIREMENTS = {
    # Alerts operations (migrated from detections)
    "GetQueriesAlertsV2": ["Alerts:read"],
    "PostEntitiesAlertsV2": ["Alerts:read"],
    # Hosts operations
    "QueryDevicesByFilter": ["Hosts:read"],
    "PostDeviceDetailsV2": ["Hosts:read"],
    # Host Groups operations
    "queryHostGroups": ["Host Groups:read"],
    "getHostGroups": ["Host Groups:read"],
    "queryCombinedGroupMembers": ["Host Groups:read"],
    "createHostGroups": ["Host Groups:write"],
    "updateHostGroups": ["Host Groups:write"],
    "deleteHostGroups": ["Host Groups:write"],
    "performGroupAction": ["Host Groups:write"],
    # Host Migration operations
    "GetMigrationIDsV1": ["Host Migration:read"],
    "GetMigrationsV1": ["Host Migration:read"],
    "GetHostMigrationIDsV1": ["Host Migration:read"],
    "GetHostMigrationsV1": ["Host Migration:read"],
    "GetMigrationDestinationsV1": ["Host Migration:read"],
    "CreateMigrationV1": ["Host Migration:write"],
    "MigrationsActionsV1": ["Host Migration:write"],
    "HostMigrationsActionsV1": ["Host Migration:write"],
    # IT Automation operations
    "ITAutomationGetTaskExecutionsByQuery": ["IT Automation:read"],
    "ITAutomationGetTaskExecution": ["IT Automation:read"],
    "ITAutomationGetTaskExecutionHostStatus": ["IT Automation:read"],
    "ITAutomationStartExecutionResultsSearch": ["IT Automation:read"],
    "ITAutomationGetExecutionResultsSearchStatus": ["IT Automation:read"],
    "ITAutomationGetExecutionResults": ["IT Automation:read"],
    "ITAutomationStartTaskExecution": ["IT Automation:write"],
    "ITAutomationRunLiveQuery": ["IT Automation:write"],
    "ITAutomationCancelTaskExecution": ["IT Automation:write"],
    "ITAutomationRerunTaskExecution": ["IT Automation:write"],
    # Incidents operations
    "QueryIncidents": ["Incidents:read"],
    "CrowdScore": ["Incidents:read"],
    "GetIncidents": ["Incidents:read"],
    "GetBehaviors": ["Incidents:read"],
    "QueryBehaviors": ["Incidents:read"],
    # Intel operations
    "QueryIntelActorEntities": ["Actors (Falcon Intelligence):read"],
    "QueryIntelIndicatorEntities": ["Indicators (Falcon Intelligence):read"],
    "QueryIntelReportEntities": ["Reports (Falcon Intelligence):read"],
    "GetMitreReport": ["Actors (Falcon Intelligence):read"],
    # IOC operations
    "indicator_search_v1": ["IOC Management:read"],
    "indicator_get_v1": ["IOC Management:read"],
    "indicator_create_v1": ["IOC Management:write"],
    "indicator_delete_v1": ["IOC Management:write"],
    # IOA Exclusions operations
    "queryIOAExclusionsV1": ["IOA Exclusions:read"],
    "getIOAExclusionsV1": ["IOA Exclusions:read"],
    "createIOAExclusionsV1": ["IOA Exclusions:write"],
    "updateIOAExclusionsV1": ["IOA Exclusions:write"],
    "deleteIOAExclusionsV1": ["IOA Exclusions:write"],
    # Firewall Management operations
    "query_rules": ["Firewall Management:read"],
    "get_rules": ["Firewall Management:read"],
    "query_rule_groups": ["Firewall Management:read"],
    "get_rule_groups": ["Firewall Management:read"],
    "query_policy_rules": ["Firewall Management:read"],
    "create_rule_group": ["Firewall Management:write"],
    "delete_rule_groups": ["Firewall Management:write"],
    # Real Time Response operations
    "RTR_ListAllSessions": ["Real Time Response:read"],
    "RTR_ListSessions": ["Real Time Response:read"],
    "RTR_InitSession": ["Real Time Response:read"],
    "RTR_ExecuteCommand": ["Real Time Response:read"],
    "RTR_CheckCommandStatus": ["Real Time Response:read"],
    "RTR_DeleteSession": ["Real Time Response:read"],
    "RTR_DeleteQueuedSession": ["Real Time Response:read"],
    # Real Time Response Admin operations
    "RTR_ListScripts": ["Real Time Response Admin:write"],
    "RTR_GetScripts": ["Real Time Response Admin:write"],
    "RTR_ListPut_Files": ["Real Time Response Admin:write"],
    "RTR_GetPut_Files": ["Real Time Response Admin:write"],
    "RTR_ExecuteAdminCommand": ["Real Time Response Admin:write"],
    "RTR_CheckAdminCommandStatus": ["Real Time Response Admin:write"],
    "BatchAdminCmd": ["Real Time Response Admin:write"],
    # Real Time Response Audit operations
    "RTRAuditSessions": ["Real Time Response Audit:read"],
    # Spotlight operations
    "combinedQueryVulnerabilities": ["Vulnerabilities:read"],
    # Discover operations
    "combined_applications": ["Assets:read"],
    "combined_hosts": ["Assets:read"],
    # Cloud operations
    "ReadContainerCombined": ["Falcon Container Image:read"],
    "ReadContainerCount": ["Falcon Container Image:read"],
    "ReadCombinedVulnerabilities": ["Falcon Container Image:read"],
    # Identity Protection operations
    "api_preempt_proxy_post_graphql": [
        "Identity Protection Entities:read",
        "Identity Protection Timeline:read",
        "Identity Protection Detections:read",
        "Identity Protection Assessment:read",
        "Identity Protection GraphQL:write",
    ],
    # Sensor Usage operations
    "GetSensorUsageWeekly": ["Sensor Usage:read"],
    # Serverless operations
    "GetCombinedVulnerabilitiesSARIF": ["Falcon Container Image:read"],
    # Scheduled Reports operations
    "scheduled_reports_query": ["Scheduled Reports:read"],
    "scheduled_reports_get": ["Scheduled Reports:read"],
    "scheduled_reports_launch": ["Scheduled Reports:read"],
    # Report Executions operations (same scope as Scheduled Reports)
    "report_executions_query": ["Scheduled Reports:read"],
    "report_executions_get": ["Scheduled Reports:read"],
    "report_executions_download_get": ["Scheduled Reports:read"],
    # NGSIEM operations
    "StartSearchV1": ["NGSIEM:write"],
    "GetSearchStatusV1": ["NGSIEM:read"],
    "StopSearchV1": ["NGSIEM:write"],
    # Add more mappings as needed
}


def get_required_scopes(operation: str | None) -> list[str]:
    """Get the required API scopes for a specific operation.

    Args:
        operation: The API operation name

    Returns:
        List[str]: List of required API scopes
    """
    if operation is None:
        return []
    return API_SCOPE_REQUIREMENTS.get(operation, [])
