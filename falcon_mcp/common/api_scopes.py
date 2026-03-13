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
    # Exposure Management operations
    "query_external_assets_v2": ["Exposure Management:read"],
    "get_external_assets": ["Exposure Management:read"],
    "aggregate_external_assets": ["Exposure Management:read"],
    "post_external_assets_inventory_v1": ["Exposure Management:write"],
    "patch_external_assets": ["Exposure Management:write"],
    "delete_external_assets": ["Exposure Management:write"],
    # CAO Hunting operations
    "AggregateHuntingGuides": ["CAO Hunting:read"],
    "AggregateIntelligenceQueries": ["CAO Hunting:read"],
    "GetArchiveExport": ["CAO Hunting:read"],
    "GetHuntingGuides": ["CAO Hunting:read"],
    "GetIntelligenceQueries": ["CAO Hunting:read"],
    "SearchHuntingGuides": ["CAO Hunting:read"],
    "SearchIntelligenceQueries": ["CAO Hunting:read"],
    # Zero Trust Assessment operations
    "getAssessmentV1": ["Zero Trust Assessment:read"],
    "getAuditV1": ["Zero Trust Assessment:read"],
    "getAssessmentsByScoreV1": ["Zero Trust Assessment:read"],
    "getCombinedAssessmentsQuery": ["Zero Trust Assessment:read"],
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
    # User Management operations
    "queryUserV1": ["User Management:read"],
    "retrieveUsersGETV1": ["User Management:read"],
    "queriesRolesV1": ["User Management:read"],
    "entitiesRolesGETV2": ["User Management:read"],
    "CombinedUserRolesV2": ["User Management:read"],
    "createUserV1": ["User Management:write"],
    "deleteUserV1": ["User Management:write"],
    "userRolesActionV1": ["User Management:write"],
    # Sensor Usage operations
    "GetSensorUsageWeekly": ["Sensor Usage:read"],
    # Sensor Download operations
    "GetCombinedSensorInstallersByQuery": ["Sensor Download:read"],
    "GetCombinedSensorInstallersByQueryV2": ["Sensor Download:read"],
    "DownloadSensorInstallerById": ["Sensor Download:read"],
    "DownloadSensorInstallerByIdV2": ["Sensor Download:read"],
    "GetSensorInstallersEntities": ["Sensor Download:read"],
    "GetSensorInstallersEntitiesV2": ["Sensor Download:read"],
    "GetSensorInstallersCCIDByQuery": ["Sensor Download:read"],
    "GetSensorInstallersByQuery": ["Sensor Download:read"],
    "GetSensorInstallersByQueryV2": ["Sensor Download:read"],
    # Installation Tokens operations
    "audit_events_read": ["Installation Tokens:read"],
    "customer_settings_read": ["Installation Tokens:read"],
    "tokens_read": ["Installation Tokens:read"],
    "audit_events_query": ["Installation Tokens:read"],
    "tokens_query": ["Installation Tokens:read"],
    "tokens_create": ["Installation Tokens:write"],
    "tokens_delete": ["Installation Tokens:write"],
    "tokens_update": ["Installation Tokens:write"],
    "customer_settings_update": ["Installation Tokens Settings:write"],
    # Prevention Policies operations
    "queryCombinedPreventionPolicyMembers": ["Prevention Policies:read"],
    "queryCombinedPreventionPolicies": ["Prevention Policies:read"],
    "getPreventionPolicies": ["Prevention Policies:read"],
    "queryPreventionPolicyMembers": ["Prevention Policies:read"],
    "queryPreventionPolicies": ["Prevention Policies:read"],
    "performPreventionPoliciesAction": ["Prevention Policies:write"],
    "setPreventionPoliciesPrecedence": ["Prevention Policies:write"],
    "createPreventionPolicies": ["Prevention Policies:write"],
    "updatePreventionPolicies": ["Prevention Policies:write"],
    "deletePreventionPolicies": ["Prevention Policies:write"],
    # Workflows operations
    "WorkflowActivitiesCombined": ["Workflow:read"],
    "WorkflowActivitiesContentCombined": ["Workflow:read"],
    "WorkflowDefinitionsCombined": ["Workflow:read"],
    "WorkflowExecutionsCombined": ["Workflow:read"],
    "WorkflowTriggersCombined": ["Workflow:read"],
    "WorkflowDefinitionsExport": ["Workflow:read"],
    "WorkflowExecutionResults": ["Workflow:read"],
    "WorkflowGetHumanInputV1": ["Workflow:read"],
    "WorkflowDefinitionsAction": ["Workflow:write"],
    "WorkflowDefinitionsImport": ["Workflow:write"],
    "WorkflowDefinitionsUpdate": ["Workflow:write"],
    "WorkflowExecute": ["Workflow:write"],
    "WorkflowExecuteInternal": ["Workflow:write"],
    "WorkflowMockExecute": ["Workflow:write"],
    "WorkflowExecutionsAction": ["Workflow:write"],
    "WorkflowUpdateHumanInputV1": ["Workflow:write"],
    "WorkflowSystemDefinitionsDeProvision": ["Workflow:write"],
    "WorkflowSystemDefinitionsPromote": ["Workflow:write"],
    "WorkflowSystemDefinitionsProvision": ["Workflow:write"],
    # Quarantine operations
    "ActionUpdateCount": ["Quarantined Files:read"],
    "GetAggregateFiles": ["Quarantined Files:read"],
    "GetQuarantineFiles": ["Quarantined Files:read"],
    "QueryQuarantineFiles": ["Quarantined Files:read"],
    "UpdateQfByQuery": ["Quarantined Files:write"],
    "UpdateQuarantinedDetectsByIds": ["Quarantined Files:write"],
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
    # Custom IOA operations
    "query_rule_groups_full": ["Custom IOA Rules:read"],
    "query_platformsMixin0": ["Custom IOA Rules:read"],
    "get_platformsMixin0": ["Custom IOA Rules:read"],
    "query_rule_types": ["Custom IOA Rules:read"],
    "get_rule_types": ["Custom IOA Rules:read"],
    "create_rule_groupMixin0": ["Custom IOA Rules:write"],
    "update_rule_groupMixin0": ["Custom IOA Rules:write"],
    "delete_rule_groupsMixin0": ["Custom IOA Rules:write"],
    "create_rule": ["Custom IOA Rules:write"],
    "update_rules_v2": ["Custom IOA Rules:write"],
    "delete_rules": ["Custom IOA Rules:write"],
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
