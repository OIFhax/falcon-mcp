"""
Tests for the API scope utilities.
"""

import re
import unittest
import warnings
from pathlib import Path

from falcon_mcp.common.api_scopes import API_SCOPE_REQUIREMENTS, get_required_scopes


class TestApiScopes(unittest.TestCase):
    """Test cases for the API scope utilities."""

    @staticmethod
    def _extract_operations_from_modules() -> set[str]:
        """Extract all operation names used in module files.

        Returns:
            set[str]: Set of operation names found in modules
        """
        operations = set()

        # Get the modules directory
        modules_path = Path(__file__).parent.parent.parent / "falcon_mcp" / "modules"

        # Pattern to match operation= statements
        operation_pattern = re.compile(r'operation\s*=\s*["\']([^"\']+)["\']')

        # Search through all Python module files
        for module_file in modules_path.glob("*.py"):
            if module_file.name in ["__init__.py", "base.py"]:
                continue

            try:
                content = module_file.read_text()
                matches = operation_pattern.findall(content)
                operations.update(matches)
            except (OSError, UnicodeDecodeError):
                # Skip files that can't be read or decoded
                continue

        return operations

    def test_api_scope_requirements_structure(self):
        """Test API_SCOPE_REQUIREMENTS dictionary structure."""
        # Verify it's a dictionary
        self.assertIsInstance(API_SCOPE_REQUIREMENTS, dict)

        # Verify it has entries
        self.assertGreater(len(API_SCOPE_REQUIREMENTS), 0)

        # Verify structure of entries (keys are strings, values are lists of strings)
        for operation, scopes in API_SCOPE_REQUIREMENTS.items():
            self.assertIsInstance(operation, str)
            self.assertIsInstance(scopes, list)
            for scope in scopes:
                self.assertIsInstance(scope, str)

    def test_get_required_scopes(self):
        """Test get_required_scopes function."""
        # Test with known operations
        self.assertEqual(get_required_scopes("GetQueriesAlertsV1"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("GetQueriesAlertsV2"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("PostCombinedAlertsV1"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("PostAggregatesAlertsV1"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("PostAggregatesAlertsV2"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("PostEntitiesAlertsV1"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("PostEntitiesAlertsV2"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("PatchEntitiesAlertsV1"), ["Alerts:write"])
        self.assertEqual(get_required_scopes("PatchEntitiesAlertsV2"), ["Alerts:write"])
        self.assertEqual(get_required_scopes("PatchEntitiesAlertsV3"), ["Alerts:write"])
        self.assertEqual(get_required_scopes("QueryIncidents"), ["Incidents:read"])
        self.assertEqual(get_required_scopes("PerformIncidentAction"), ["Incidents:write"])
        self.assertEqual(get_required_scopes("combined_applications"), ["Assets:read"])
        self.assertEqual(get_required_scopes("query_accounts"), ["Assets:read"])
        self.assertEqual(get_required_scopes("query_iot_hostsV2"), ["Assets:read"])
        self.assertEqual(get_required_scopes("get_iot_hosts"), ["Assets:read"])
        self.assertEqual(get_required_scopes("RTR_ListAllSessions"), ["Real Time Response:read"])
        self.assertEqual(get_required_scopes("queryHostGroups"), ["Host Groups:read"])
        self.assertEqual(get_required_scopes("createHostGroups"), ["Host Groups:write"])
        self.assertEqual(get_required_scopes("GetMigrationIDsV1"), ["Host Migration:read"])
        self.assertEqual(get_required_scopes("CreateMigrationV1"), ["Host Migration:write"])
        self.assertEqual(
            get_required_scopes("ITAutomationGetTaskExecution"),
            ["IT Automation:read"],
        )
        self.assertEqual(
            get_required_scopes("ITAutomationGetTasksByQuery"),
            ["IT Automation:read"],
        )
        self.assertEqual(
            get_required_scopes("ITAutomationGetPolicies"),
            ["IT Automation:read"],
        )
        self.assertEqual(
            get_required_scopes("ITAutomationRunLiveQuery"),
            ["IT Automation:write"],
        )
        self.assertEqual(
            get_required_scopes("ITAutomationCreateTask"),
            ["IT Automation:write"],
        )
        self.assertEqual(
            get_required_scopes("ITAutomationDeleteTaskGroups"),
            ["IT Automation:write"],
        )
        self.assertEqual(get_required_scopes("getMLExclusionsV1"), ["ml-exclusions:read"])
        self.assertEqual(get_required_scopes("createMLExclusionsV1"), ["ml-exclusions:write"])
        self.assertEqual(get_required_scopes("deleteMLExclusionsV1"), ["ml-exclusions:write"])
        self.assertEqual(get_required_scopes("updateMLExclusionsV1"), ["ml-exclusions:write"])
        self.assertEqual(get_required_scopes("queryMLExclusionsV1"), ["ml-exclusions:read"])
        self.assertEqual(
            get_required_scopes("getSensorVisibilityExclusionsV1"),
            ["sensor-visibility-exclusions:read"],
        )
        self.assertEqual(
            get_required_scopes("createSVExclusionsV1"),
            ["sensor-visibility-exclusions:write"],
        )
        self.assertEqual(
            get_required_scopes("deleteSensorVisibilityExclusionsV1"),
            ["sensor-visibility-exclusions:write"],
        )
        self.assertEqual(
            get_required_scopes("updateSensorVisibilityExclusionsV1"),
            ["sensor-visibility-exclusions:write"],
        )
        self.assertEqual(
            get_required_scopes("querySensorVisibilityExclusionsV1"),
            ["sensor-visibility-exclusions:read"],
        )
        self.assertEqual(get_required_scopes("cb_exclusions_get_v1"), ["ml-exclusions:read"])
        self.assertEqual(get_required_scopes("cb_exclusions_create_v1"), ["ml-exclusions:write"])
        self.assertEqual(get_required_scopes("cb_exclusions_delete_v1"), ["ml-exclusions:write"])
        self.assertEqual(get_required_scopes("cb_exclusions_update_v1"), ["ml-exclusions:write"])
        self.assertEqual(get_required_scopes("certificates_get_v1"), ["ml-exclusions:read"])
        self.assertEqual(get_required_scopes("cb_exclusions_query_v1"), ["ml-exclusions:read"])
        self.assertEqual(get_required_scopes("queryIOAExclusionsV1"), ["IOA Exclusions:read"])
        self.assertEqual(get_required_scopes("createIOAExclusionsV1"), ["IOA Exclusions:write"])
        self.assertEqual(get_required_scopes("query_rules"), ["Firewall Management:read"])
        self.assertEqual(get_required_scopes("create_rule_group"), ["Firewall Management:write"])
        self.assertEqual(get_required_scopes("GetDashboardTemplate"), ["NGSIEM:read"])
        self.assertEqual(get_required_scopes("CreateDashboardFromTemplate"), ["NGSIEM:write"])
        self.assertEqual(get_required_scopes("queryVulnerabilities"), ["Vulnerabilities:read"])
        self.assertEqual(get_required_scopes("getVulnerabilities"), ["Vulnerabilities:read"])
        self.assertEqual(get_required_scopes("getRemediations"), ["Vulnerabilities:read"])
        self.assertEqual(get_required_scopes("getRemediationsV2"), ["Vulnerabilities:read"])
        self.assertEqual(
            get_required_scopes("query_external_assets_v2"),
            ["Exposure Management:read"],
        )
        self.assertEqual(
            get_required_scopes("delete_external_assets"),
            ["Exposure Management:write"],
        )
        self.assertEqual(
            get_required_scopes("listAvailableStreamsOAuth2"),
            ["event-streams:read"],
        )
        self.assertEqual(
            get_required_scopes("refreshActiveStreamSession"),
            ["event-streams:read"],
        )
        self.assertEqual(
            get_required_scopes("fdrschema_combined_event_get"),
            ["falcon-data-replicator:read"],
        )
        self.assertEqual(
            get_required_scopes("fdrschema_entities_event_get"),
            ["falcon-data-replicator:read"],
        )
        self.assertEqual(
            get_required_scopes("fdrschema_queries_event_get"),
            ["falcon-data-replicator:read"],
        )
        self.assertEqual(
            get_required_scopes("fdrschema_entities_field_get"),
            ["falcon-data-replicator:read"],
        )
        self.assertEqual(
            get_required_scopes("fdrschema_queries_field_get"),
            ["falcon-data-replicator:read"],
        )
        self.assertEqual(
            get_required_scopes("FetchFilesDownloadInfo"),
            ["infrastructure-as-code:read"],
        )
        self.assertEqual(
            get_required_scopes("FetchFilesDownloadInfoV2"),
            ["infrastructure-as-code:read"],
        )
        self.assertEqual(
            get_required_scopes("DownloadFile"),
            ["infrastructure-as-code:read"],
        )
        self.assertEqual(
            get_required_scopes("EnumerateFile"),
            ["infrastructure-as-code:read"],
        )
        self.assertEqual(
            get_required_scopes("GetDeliverySettings"),
            ["delivery-settings:read"],
        )
        self.assertEqual(
            get_required_scopes("PostDeliverySettings"),
            ["delivery-settings:write"],
        )
        self.assertEqual(
            get_required_scopes("entities_states_v1"),
            ["device-content:read"],
        )
        self.assertEqual(
            get_required_scopes("queries_states_v1"),
            ["device-content:read"],
        )
        self.assertEqual(
            get_required_scopes("CombinedReleaseNotesV1"),
            ["deployment-coordinator:read"],
        )
        self.assertEqual(
            get_required_scopes("CombinedReleasesV1Mixin0"),
            ["deployment-coordinator:read"],
        )
        self.assertEqual(
            get_required_scopes("GetDeploymentsExternalV1"),
            ["deployment-coordinator:read"],
        )
        self.assertEqual(
            get_required_scopes("GetEntityIDsByQueryPOST"),
            ["deployment-coordinator:read"],
        )
        self.assertEqual(
            get_required_scopes("GetEntityIDsByQueryPOSTV2"),
            ["deployments:read"],
        )
        self.assertEqual(
            get_required_scopes("QueryReleaseNotesV1"),
            ["deployment-coordinator:read"],
        )
        self.assertEqual(
            get_required_scopes("DownloadFeedArchive"),
            ["indicator-graph:read"],
        )
        self.assertEqual(
            get_required_scopes("ListFeedTypes"),
            ["indicator-graph:read"],
        )
        self.assertEqual(
            get_required_scopes("QueryFeedArchives"),
            ["indicator-graph:read"],
        )
        self.assertEqual(
            get_required_scopes("GetCombinedPluginConfigs"),
            ["api-integrations:read"],
        )
        self.assertEqual(
            get_required_scopes("ExecuteCommandProxy"),
            ["api-integrations:write"],
        )
        self.assertEqual(
            get_required_scopes("ExecuteCommand"),
            ["api-integrations:write"],
        )
        self.assertEqual(
            get_required_scopes("GetScansAggregates"),
            ["quick-scan:read"],
        )
        self.assertEqual(
            get_required_scopes("GetScans"),
            ["quick-scan:read"],
        )
        self.assertEqual(
            get_required_scopes("ScanSamples"),
            ["quick-scan:write"],
        )
        self.assertEqual(
            get_required_scopes("QuerySubmissionsMixin0"),
            ["quick-scan:read"],
        )
        self.assertEqual(
            get_required_scopes("combined_edges_get"),
            ["threatgraph:read"],
        )
        self.assertEqual(
            get_required_scopes("combined_ran_on_get"),
            ["threatgraph:read"],
        )
        self.assertEqual(
            get_required_scopes("combined_summary_get"),
            ["threatgraph:read"],
        )
        self.assertEqual(
            get_required_scopes("entities_vertices_get"),
            ["threatgraph:read"],
        )
        self.assertEqual(
            get_required_scopes("entities_vertices_getv2"),
            ["threatgraph:read"],
        )
        self.assertEqual(
            get_required_scopes("queries_edgetypes_get"),
            ["threatgraph:read"],
        )
        self.assertEqual(
            get_required_scopes("GetMalQueryQuotasV1"),
            ["malquery:read"],
        )
        self.assertEqual(
            get_required_scopes("PostMalQueryFuzzySearchV1"),
            ["malquery:write"],
        )
        self.assertEqual(
            get_required_scopes("GetMalQueryDownloadV1"),
            ["malquery:read"],
        )
        self.assertEqual(
            get_required_scopes("GetMalQueryMetadataV1"),
            ["malquery:read"],
        )
        self.assertEqual(
            get_required_scopes("GetMalQueryRequestV1"),
            ["malquery:read"],
        )
        self.assertEqual(
            get_required_scopes("GetMalQueryEntitiesSamplesFetchV1"),
            ["malquery:read"],
        )
        self.assertEqual(
            get_required_scopes("PostMalQueryEntitiesSamplesMultidownloadV1"),
            ["malquery:write"],
        )
        self.assertEqual(
            get_required_scopes("PostMalQueryExactSearchV1"),
            ["malquery:write"],
        )
        self.assertEqual(
            get_required_scopes("PostMalQueryHuntV1"),
            ["malquery:write"],
        )
        self.assertEqual(
            get_required_scopes("aggregates_rule_versions_post_v1"),
            ["correlation-rules:write"],
        )
        self.assertEqual(
            get_required_scopes("combined_rules_get_v1"),
            ["correlation-rules:read"],
        )
        self.assertEqual(
            get_required_scopes("combined_rules_get_v2"),
            ["correlation-rules:read"],
        )
        self.assertEqual(
            get_required_scopes("entities_latest_rules_get_v1"),
            ["correlation-rules:read"],
        )
        self.assertEqual(
            get_required_scopes("entities_rule_versions_export_post_v1"),
            ["correlation-rules:write"],
        )
        self.assertEqual(
            get_required_scopes("entities_rule_versions_import_post_v1"),
            ["correlation-rules:write"],
        )
        self.assertEqual(
            get_required_scopes("entities_rule_versions_publish_patch_v1"),
            ["correlation-rules:write"],
        )
        self.assertEqual(
            get_required_scopes("entities_rule_versions_delete_v1"),
            ["correlation-rules:write"],
        )
        self.assertEqual(
            get_required_scopes("entities_rules_get_v1"),
            ["correlation-rules:read"],
        )
        self.assertEqual(
            get_required_scopes("entities_rules_post_v1"),
            ["correlation-rules:write"],
        )
        self.assertEqual(
            get_required_scopes("entities_rules_patch_v1"),
            ["correlation-rules:write"],
        )
        self.assertEqual(
            get_required_scopes("entities_rules_delete_v1"),
            ["correlation-rules:write"],
        )
        self.assertEqual(
            get_required_scopes("entities_rules_get_v2"),
            ["correlation-rules:read"],
        )
        self.assertEqual(
            get_required_scopes("queries_rules_get_v1"),
            ["correlation-rules:read"],
        )
        self.assertEqual(
            get_required_scopes("queries_rules_get_v2"),
            ["correlation-rules:read"],
        )
        self.assertEqual(
            get_required_scopes("AggregateCases"),
            ["message-center:read"],
        )
        self.assertEqual(
            get_required_scopes("GetCaseActivityByIds"),
            ["message-center:read"],
        )
        self.assertEqual(
            get_required_scopes("CaseAddActivity"),
            ["message-center:write"],
        )
        self.assertEqual(
            get_required_scopes("CaseDownloadAttachment"),
            ["message-center:read"],
        )
        self.assertEqual(
            get_required_scopes("CaseAddAttachment"),
            ["message-center:write"],
        )
        self.assertEqual(
            get_required_scopes("CreateCaseV2"),
            ["message-center:write"],
        )
        self.assertEqual(
            get_required_scopes("GetCaseEntitiesByIDs"),
            ["message-center:read"],
        )
        self.assertEqual(
            get_required_scopes("QueryActivityByCaseID"),
            ["message-center:read"],
        )
        self.assertEqual(
            get_required_scopes("QueryCasesIdsByFilter"),
            ["message-center:read"],
        )
        case_management_scopes = {
            "aggregates_file_details_post_v1": "case-templates:read",
            "combined_file_details_get_v1": "case-templates:read",
            "entities_file_details_get_v1": "case-templates:read",
            "entities_file_details_patch_v1": "case-templates:write",
            "entities_files_bulk_download_post_v1": "case-templates:read",
            "entities_files_download_get_v1": "case-templates:read",
            "entities_files_upload_post_v1": "case-templates:write",
            "entities_files_delete_v1": "case-templates:write",
            "entities_retrieve_rtr_file_post_v1": "case-templates:write",
            "queries_file_details_get_v1": "case-templates:read",
            "aggregates_notification_groups_post_v1": "case-templates:read",
            "aggregates_notification_groups_post_v2": "case-templates:read",
            "aggregates_slas_post_v1": "case-templates:read",
            "aggregates_templates_post_v1": "case-templates:read",
            "entities_fields_get_v1": "case-templates:read",
            "entities_notification_groups_get_v1": "case-templates:read",
            "entities_notification_groups_post_v1": "case-templates:write",
            "entities_notification_groups_patch_v1": "case-templates:write",
            "entities_notification_groups_delete_v1": "case-templates:write",
            "entities_notification_groups_get_v2": "case-templates:read",
            "entities_notification_groups_post_v2": "case-templates:write",
            "entities_notification_groups_patch_v2": "case-templates:write",
            "entities_notification_groups_delete_v2": "case-templates:write",
            "entities_slas_get_v1": "case-templates:read",
            "entities_slas_post_v1": "case-templates:write",
            "entities_slas_patch_v1": "case-templates:write",
            "entities_slas_delete_v1": "case-templates:write",
            "entities_template_snapshots_get_v1": "case-templates:read",
            "entities_templates_export_get_v1": "case-templates:read",
            "entities_templates_import_post_v1": "case-templates:write",
            "entities_templates_get_v1": "case-templates:read",
            "entities_templates_post_v1": "case-templates:write",
            "entities_templates_patch_v1": "case-templates:write",
            "entities_templates_delete_v1": "case-templates:write",
            "queries_fields_get_v1": "case-templates:read",
            "queries_notification_groups_get_v1": "case-templates:read",
            "queries_notification_groups_get_v2": "case-templates:read",
            "queries_slas_get_v1": "case-templates:read",
            "queries_template_snapshots_get_v1": "case-templates:read",
            "queries_templates_get_v1": "case-templates:read",
            "entities_alert_evidence_post_v1": "case-templates:write",
            "entities_case_tags_post_v1": "case-templates:write",
            "entities_case_tags_delete_v1": "case-templates:write",
            "entities_cases_put_v2": "case-templates:write",
            "entities_cases_post_v2": "case-templates:read",
            "entities_cases_patch_v2": "case-templates:write",
            "entities_event_evidence_post_v1": "case-templates:write",
            "queries_cases_get_v1": "case-templates:read",
        }
        for operation, scope in case_management_scopes.items():
            self.assertEqual(get_required_scopes(operation), [scope])
        self.assertEqual(get_required_scopes("getChildrenV2"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("getChildren"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("getCIDGroupMembersByV1"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("addCIDGroupMembers"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("deleteCIDGroupMembersV1"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("getCIDGroupMembersBy"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("deleteCIDGroupMembers"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("getCIDGroupMembersByV2"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("deleteCIDGroupMembersV2"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("getCIDGroupByIdV1"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("createCIDGroups"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("deleteCIDGroups"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("updateCIDGroups"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("getCIDGroupById"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("getCIDGroupByIdV2"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("getRolesByID"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("addRole"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("deletedRoles"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("getUserGroupMembersByIDV1"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("addUserGroupMembers"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("deleteUserGroupMembers"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("getUserGroupMembersByID"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("getUserGroupMembersByIDV2"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("getUserGroupsByIDV1"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("createUserGroups"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("deleteUserGroups"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("updateUserGroups"), ["flight-control:write"])
        self.assertEqual(get_required_scopes("getUserGroupsByID"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("getUserGroupsByIDV2"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("queryChildren"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("queryCIDGroupMembers"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("queryCIDGroups"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("queryRoles"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("queryUserGroupMembers"), ["flight-control:read"])
        self.assertEqual(get_required_scopes("queryUserGroups"), ["flight-control:read"])
        self.assertEqual(
            get_required_scopes("GetDriftIndicatorsValuesByDate"),
            ["drift-indicators:read"],
        )
        self.assertEqual(
            get_required_scopes("ReadDriftIndicatorsCount"),
            ["drift-indicators:read"],
        )
        self.assertEqual(
            get_required_scopes("SearchAndReadDriftIndicatorEntities"),
            ["drift-indicators:read"],
        )
        self.assertEqual(
            get_required_scopes("ReadDriftIndicatorEntities"),
            ["drift-indicators:read"],
        )
        self.assertEqual(
            get_required_scopes("SearchDriftIndicators"),
            ["drift-indicators:read"],
        )
        self.assertEqual(
            get_required_scopes("SearchHuntingGuides"),
            ["CAO Hunting:read"],
        )
        self.assertEqual(
            get_required_scopes("GetArchiveExport"),
            ["CAO Hunting:read"],
        )
        self.assertEqual(
            get_required_scopes("getAssessmentV1"),
            ["Zero Trust Assessment:read"],
        )
        self.assertEqual(
            get_required_scopes("getCombinedAssessmentsQuery"),
            ["Zero Trust Assessment:read"],
        )
        self.assertEqual(
            get_required_scopes("queryCombinedContentUpdatePolicies"),
            ["Content Update Policies:read"],
        )
        self.assertEqual(
            get_required_scopes("performContentUpdatePoliciesAction"),
            ["Content Update Policies:write"],
        )
        self.assertEqual(
            get_required_scopes("GetSensorInstallersByQueryV2"),
            ["Sensor Download:read"],
        )
        self.assertEqual(
            get_required_scopes("QueryQuarantineFiles"),
            ["Quarantined Files:read"],
        )
        self.assertEqual(
            get_required_scopes("report_executions_retry"),
            ["Scheduled Reports:read"],
        )
        self.assertEqual(
            get_required_scopes("tokens_query"),
            ["Installation Tokens:read"],
        )
        self.assertEqual(
            get_required_scopes("queryCombinedPreventionPolicies"),
            ["Prevention Policies:read"],
        )
        self.assertEqual(
            get_required_scopes("performPreventionPoliciesAction"),
            ["Prevention Policies:write"],
        )
        self.assertEqual(
            get_required_scopes("queryCombinedRTResponsePolicies"),
            ["Response Policies:read"],
        )
        self.assertEqual(
            get_required_scopes("performRTResponsePoliciesAction"),
            ["Response Policies:write"],
        )
        self.assertEqual(
            get_required_scopes("queryCombinedSensorUpdatePolicies"),
            ["Sensor Update Policies:read"],
        )
        self.assertEqual(
            get_required_scopes("performSensorUpdatePoliciesAction"),
            ["Sensor Update Policies:write"],
        )
        self.assertEqual(
            get_required_scopes("queryCombinedDeviceControlPolicies"),
            ["Device Control Policies:read"],
        )
        self.assertEqual(
            get_required_scopes("performDeviceControlPoliciesAction"),
            ["Device Control Policies:write"],
        )
        self.assertEqual(
            get_required_scopes("queryCombinedFirewallPolicies"),
            ["Firewall Policies:read"],
        )
        self.assertEqual(
            get_required_scopes("performFirewallPoliciesAction"),
            ["Firewall Policies:write"],
        )
        self.assertEqual(
            get_required_scopes("WorkflowDefinitionsCombined"),
            ["Workflow:read"],
        )
        self.assertEqual(
            get_required_scopes("WorkflowExecute"),
            ["Workflow:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_AggregateSessions"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("BatchActiveResponderCmd"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("BatchGetCmd"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("BatchGetCmdStatus"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("BatchInitSessions"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("BatchRefreshSessions"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("RTR_ExecuteActiveResponderCommand"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("RTR_CheckActiveResponderCommandStatus"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("RTR_GetExtractedFileContents"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("RTR_ListFilesV2"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("RTR_DeleteFileV2"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("RTR_ListQueuedSessions"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("RTR_PulseSession"),
            ["Real Time Response:read"],
        )
        self.assertEqual(
            get_required_scopes("RTR_ExecuteAdminCommand"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_GetFalconScripts"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_ListFalconScripts"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_GetPutFileContents"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_GetPut_FilesV2"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_CreatePut_FilesV2"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_GetScriptsV2"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_CreateScriptsV2"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_UpdateScriptsV2"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTRAuditSessions"),
            ["Real Time Response Audit:read"],
        )
        self.assertEqual(get_required_scopes("aggregateUsersV1"), ["User Management:read"])
        self.assertEqual(get_required_scopes("queryUserV1"), ["User Management:read"])
        self.assertEqual(get_required_scopes("entitiesRolesV1"), ["User Management:read"])
        self.assertEqual(get_required_scopes("userActionV1"), ["User Management:write"])
        self.assertEqual(get_required_scopes("updateUserV1"), ["User Management:write"])
        self.assertEqual(get_required_scopes("userRolesActionV1"), ["User Management:write"])

        # Test with unknown operation
        self.assertEqual(get_required_scopes("UnknownOperation"), [])

        # Test with empty string
        self.assertEqual(get_required_scopes(""), [])

        # Test with None (should handle gracefully)
        self.assertEqual(get_required_scopes(None), [])

    def test_all_operations_have_scope_mappings(self):
        """Test that all operations used in modules have scope mappings defined."""
        # Extract all operations from module files
        operations_in_modules = self._extract_operations_from_modules()

        # Get operations that have scope mappings
        mapped_operations = set(API_SCOPE_REQUIREMENTS.keys())

        # Find operations without scope mappings
        unmapped_operations = operations_in_modules - mapped_operations

        # Assert that all operations have scope mappings
        self.assertEqual(
            len(unmapped_operations),
            0,
            f"The following operations are missing scope mappings: {sorted(unmapped_operations)}"
        )

    def test_no_unused_scope_mappings(self):
        """Test that all scope mappings correspond to operations actually used in modules."""
        # Extract all operations from module files
        operations_in_modules = self._extract_operations_from_modules()

        # Get operations that have scope mappings
        mapped_operations = set(API_SCOPE_REQUIREMENTS.keys())

        # Find scope mappings for operations not in modules (potentially unused)
        unused_mappings = mapped_operations - operations_in_modules

        # This is a warning test - we allow some unused mappings for backward compatibility
        # but we want to be aware of them
        if unused_mappings:
            warnings.warn(
                f"The following scope mappings may be unused: {sorted(unused_mappings)}",
                UserWarning,
                stacklevel=2
            )

    def test_scope_format_validation(self):
        """Test that all scopes follow the expected format."""
        for operation, scopes in API_SCOPE_REQUIREMENTS.items():
            for scope in scopes:
                # Test that scope is non-empty
                self.assertGreater(len(scope), 0, f"Empty scope found for operation {operation}")

                # Test that scope contains a colon (standard format: "Resource:permission")
                # Note: Some scopes like "Identity Protection GraphQL:write" have spaces and are valid
                self.assertIn(
                    ":", scope, f"Invalid scope format '{scope}' for operation {operation}"
                )

                # Test that scope doesn't start or end with whitespace
                self.assertEqual(
                    scope, scope.strip(), f"Scope '{scope}' has leading/trailing whitespace"
                )

                # Test that scope has both parts (before and after colon)
                parts = scope.split(":")
                self.assertEqual(
                    len(parts), 2, f"Invalid scope format '{scope}' - should have exactly one colon"
                )
                self.assertGreater(
                    len(parts[0]), 0, f"Empty resource name in scope '{scope}'"
                )
                self.assertGreater(
                    len(parts[1]), 0, f"Empty permission name in scope '{scope}'"
                )

    def test_error_handling_integration(self):
        """Test that get_required_scopes integrates properly with error handling."""
        # Test with multiple known operations to ensure consistency
        test_cases = [
            ("GetQueriesAlertsV1", ["Alerts:read"]),
            ("GetQueriesAlertsV2", ["Alerts:read"]),
            ("PostCombinedAlertsV1", ["Alerts:read"]),
            ("PostAggregatesAlertsV1", ["Alerts:read"]),
            ("PostAggregatesAlertsV2", ["Alerts:read"]),
            ("PostEntitiesAlertsV1", ["Alerts:read"]),
            ("PostEntitiesAlertsV2", ["Alerts:read"]),
            ("PatchEntitiesAlertsV1", ["Alerts:write"]),
            ("PatchEntitiesAlertsV2", ["Alerts:write"]),
            ("PatchEntitiesAlertsV3", ["Alerts:write"]),
            ("QueryIncidents", ["Incidents:read"]),
            ("PerformIncidentAction", ["Incidents:write"]),
            ("combined_applications", ["Assets:read"]),
            ("query_accounts", ["Assets:read"]),
            ("query_iot_hostsV2", ["Assets:read"]),
            ("get_iot_hosts", ["Assets:read"]),
            ("QueryIntelActorEntities", ["Actors (Falcon Intelligence):read"]),
            ("QueryIntelActorIds", ["Actors (Falcon Intelligence):read"]),
            ("GetIntelActorEntities", ["Actors (Falcon Intelligence):read"]),
            ("QueryIntelIndicatorEntities", ["Indicators (Falcon Intelligence):read"]),
            ("GetIntelIndicatorEntities", ["Indicators (Falcon Intelligence):read"]),
            ("QueryIntelReportEntities", ["Reports (Falcon Intelligence):read"]),
            ("GetIntelReportEntities", ["Reports (Falcon Intelligence):read"]),
            ("QueryIntelRuleIds", ["Reports (Falcon Intelligence):read"]),
            ("QueryMalwareEntities", ["Reports (Falcon Intelligence):read"]),
            ("QueryVulnerabilities", ["Indicators (Falcon Intelligence):read"]),
            ("PostMitreAttacks", ["Actors (Falcon Intelligence):read"]),
            ("GetMitreReport", ["Actors (Falcon Intelligence):read"]),
            ("ReadContainerCombined", ["Falcon Container Image:read"]),
            ("ReadContainerCount", ["Falcon Container Image:read"]),
            ("ReadCombinedVulnerabilities", ["Falcon Container Image:read"]),
            ("ReadCombinedVulnerabilitiesDetails", ["Falcon Container Image:read"]),
            ("ReadCombinedVulnerabilitiesInfo", ["Falcon Container Image:read"]),
            ("ReadVulnerabilityCount", ["Falcon Container Image:read"]),
            ("ReadVulnerabilityCountBySeverity", ["Falcon Container Image:read"]),
            ("ReadVulnerabilityCountByCPSRating", ["Falcon Container Image:read"]),
            ("ReadVulnerabilityCountByCVSSScore", ["Falcon Container Image:read"]),
            ("ReadVulnerabilityCountByActivelyExploited", ["Falcon Container Image:read"]),
            ("ReadVulnerabilitiesByImageCount", ["Falcon Container Image:read"]),
            ("ReadVulnerabilitiesPublicationDate", ["Falcon Container Image:read"]),
            ("queryHostGroups", ["Host Groups:read"]),
            ("createHostGroups", ["Host Groups:write"]),
            ("GetMigrationIDsV1", ["Host Migration:read"]),
            ("CreateMigrationV1", ["Host Migration:write"]),
            ("ITAutomationGetTaskExecution", ["IT Automation:read"]),
            ("ITAutomationGetTasksByQuery", ["IT Automation:read"]),
            ("ITAutomationGetPolicies", ["IT Automation:read"]),
            ("ITAutomationRunLiveQuery", ["IT Automation:write"]),
            ("ITAutomationCreateTask", ["IT Automation:write"]),
            ("ITAutomationDeleteTaskGroups", ["IT Automation:write"]),
            ("getMLExclusionsV1", ["ml-exclusions:read"]),
            ("createMLExclusionsV1", ["ml-exclusions:write"]),
            ("deleteMLExclusionsV1", ["ml-exclusions:write"]),
            ("updateMLExclusionsV1", ["ml-exclusions:write"]),
            ("queryMLExclusionsV1", ["ml-exclusions:read"]),
            ("getSensorVisibilityExclusionsV1", ["sensor-visibility-exclusions:read"]),
            ("createSVExclusionsV1", ["sensor-visibility-exclusions:write"]),
            ("deleteSensorVisibilityExclusionsV1", ["sensor-visibility-exclusions:write"]),
            ("updateSensorVisibilityExclusionsV1", ["sensor-visibility-exclusions:write"]),
            ("querySensorVisibilityExclusionsV1", ["sensor-visibility-exclusions:read"]),
            ("cb_exclusions_get_v1", ["ml-exclusions:read"]),
            ("cb_exclusions_create_v1", ["ml-exclusions:write"]),
            ("cb_exclusions_delete_v1", ["ml-exclusions:write"]),
            ("cb_exclusions_update_v1", ["ml-exclusions:write"]),
            ("certificates_get_v1", ["ml-exclusions:read"]),
            ("cb_exclusions_query_v1", ["ml-exclusions:read"]),
            ("queryIOAExclusionsV1", ["IOA Exclusions:read"]),
            ("createIOAExclusionsV1", ["IOA Exclusions:write"]),
            ("query_rules", ["Firewall Management:read"]),
            ("create_rule_group", ["Firewall Management:write"]),
            ("GetDashboardTemplate", ["NGSIEM:read"]),
            ("CreateDashboardFromTemplate", ["NGSIEM:write"]),
            ("queryVulnerabilities", ["Vulnerabilities:read"]),
            ("getVulnerabilities", ["Vulnerabilities:read"]),
            ("getRemediations", ["Vulnerabilities:read"]),
            ("getRemediationsV2", ["Vulnerabilities:read"]),
            ("query_external_assets_v2", ["Exposure Management:read"]),
            ("delete_external_assets", ["Exposure Management:write"]),
            ("listAvailableStreamsOAuth2", ["event-streams:read"]),
            ("refreshActiveStreamSession", ["event-streams:read"]),
            ("fdrschema_combined_event_get", ["falcon-data-replicator:read"]),
            ("fdrschema_entities_event_get", ["falcon-data-replicator:read"]),
            ("fdrschema_queries_event_get", ["falcon-data-replicator:read"]),
            ("fdrschema_entities_field_get", ["falcon-data-replicator:read"]),
            ("fdrschema_queries_field_get", ["falcon-data-replicator:read"]),
            ("FetchFilesDownloadInfo", ["infrastructure-as-code:read"]),
            ("FetchFilesDownloadInfoV2", ["infrastructure-as-code:read"]),
            ("DownloadFile", ["infrastructure-as-code:read"]),
            ("EnumerateFile", ["infrastructure-as-code:read"]),
            ("GetDeliverySettings", ["delivery-settings:read"]),
            ("PostDeliverySettings", ["delivery-settings:write"]),
            ("entities_states_v1", ["device-content:read"]),
            ("queries_states_v1", ["device-content:read"]),
            ("CombinedReleaseNotesV1", ["deployment-coordinator:read"]),
            ("CombinedReleasesV1Mixin0", ["deployment-coordinator:read"]),
            ("GetDeploymentsExternalV1", ["deployment-coordinator:read"]),
            ("GetEntityIDsByQueryPOST", ["deployment-coordinator:read"]),
            ("GetEntityIDsByQueryPOSTV2", ["deployments:read"]),
            ("QueryReleaseNotesV1", ["deployment-coordinator:read"]),
            ("DownloadFeedArchive", ["indicator-graph:read"]),
            ("ListFeedTypes", ["indicator-graph:read"]),
            ("QueryFeedArchives", ["indicator-graph:read"]),
            ("GetCombinedPluginConfigs", ["api-integrations:read"]),
            ("ExecuteCommandProxy", ["api-integrations:write"]),
            ("ExecuteCommand", ["api-integrations:write"]),
            ("GetScansAggregates", ["quick-scan:read"]),
            ("GetScans", ["quick-scan:read"]),
            ("ScanSamples", ["quick-scan:write"]),
            ("QuerySubmissionsMixin0", ["quick-scan:read"]),
            ("combined_edges_get", ["threatgraph:read"]),
            ("combined_ran_on_get", ["threatgraph:read"]),
            ("combined_summary_get", ["threatgraph:read"]),
            ("entities_vertices_get", ["threatgraph:read"]),
            ("entities_vertices_getv2", ["threatgraph:read"]),
            ("queries_edgetypes_get", ["threatgraph:read"]),
            ("GetMalQueryQuotasV1", ["malquery:read"]),
            ("PostMalQueryFuzzySearchV1", ["malquery:write"]),
            ("GetMalQueryDownloadV1", ["malquery:read"]),
            ("GetMalQueryMetadataV1", ["malquery:read"]),
            ("GetMalQueryRequestV1", ["malquery:read"]),
            ("GetMalQueryEntitiesSamplesFetchV1", ["malquery:read"]),
            ("PostMalQueryEntitiesSamplesMultidownloadV1", ["malquery:write"]),
            ("PostMalQueryExactSearchV1", ["malquery:write"]),
            ("PostMalQueryHuntV1", ["malquery:write"]),
            ("aggregates_rule_versions_post_v1", ["correlation-rules:write"]),
            ("combined_rules_get_v1", ["correlation-rules:read"]),
            ("combined_rules_get_v2", ["correlation-rules:read"]),
            ("entities_latest_rules_get_v1", ["correlation-rules:read"]),
            ("entities_rule_versions_export_post_v1", ["correlation-rules:write"]),
            ("entities_rule_versions_import_post_v1", ["correlation-rules:write"]),
            ("entities_rule_versions_publish_patch_v1", ["correlation-rules:write"]),
            ("entities_rule_versions_delete_v1", ["correlation-rules:write"]),
            ("entities_rules_get_v1", ["correlation-rules:read"]),
            ("entities_rules_post_v1", ["correlation-rules:write"]),
            ("entities_rules_patch_v1", ["correlation-rules:write"]),
            ("entities_rules_delete_v1", ["correlation-rules:write"]),
            ("entities_rules_get_v2", ["correlation-rules:read"]),
            ("queries_rules_get_v1", ["correlation-rules:read"]),
            ("queries_rules_get_v2", ["correlation-rules:read"]),
            ("AggregateCases", ["message-center:read"]),
            ("GetCaseActivityByIds", ["message-center:read"]),
            ("CaseAddActivity", ["message-center:write"]),
            ("CaseDownloadAttachment", ["message-center:read"]),
            ("CaseAddAttachment", ["message-center:write"]),
            ("CreateCaseV2", ["message-center:write"]),
            ("GetCaseEntitiesByIDs", ["message-center:read"]),
            ("QueryActivityByCaseID", ["message-center:read"]),
            ("QueryCasesIdsByFilter", ["message-center:read"]),
            ("getChildrenV2", ["flight-control:read"]),
            ("getChildren", ["flight-control:read"]),
            ("getCIDGroupMembersByV1", ["flight-control:read"]),
            ("addCIDGroupMembers", ["flight-control:write"]),
            ("deleteCIDGroupMembersV1", ["flight-control:write"]),
            ("getCIDGroupMembersBy", ["flight-control:read"]),
            ("deleteCIDGroupMembers", ["flight-control:write"]),
            ("getCIDGroupMembersByV2", ["flight-control:read"]),
            ("deleteCIDGroupMembersV2", ["flight-control:write"]),
            ("getCIDGroupByIdV1", ["flight-control:read"]),
            ("createCIDGroups", ["flight-control:write"]),
            ("deleteCIDGroups", ["flight-control:write"]),
            ("updateCIDGroups", ["flight-control:write"]),
            ("getCIDGroupById", ["flight-control:read"]),
            ("getCIDGroupByIdV2", ["flight-control:read"]),
            ("getRolesByID", ["flight-control:read"]),
            ("addRole", ["flight-control:write"]),
            ("deletedRoles", ["flight-control:write"]),
            ("getUserGroupMembersByIDV1", ["flight-control:read"]),
            ("addUserGroupMembers", ["flight-control:write"]),
            ("deleteUserGroupMembers", ["flight-control:write"]),
            ("getUserGroupMembersByID", ["flight-control:read"]),
            ("getUserGroupMembersByIDV2", ["flight-control:read"]),
            ("getUserGroupsByIDV1", ["flight-control:read"]),
            ("createUserGroups", ["flight-control:write"]),
            ("deleteUserGroups", ["flight-control:write"]),
            ("updateUserGroups", ["flight-control:write"]),
            ("getUserGroupsByID", ["flight-control:read"]),
            ("getUserGroupsByIDV2", ["flight-control:read"]),
            ("queryChildren", ["flight-control:read"]),
            ("queryCIDGroupMembers", ["flight-control:read"]),
            ("queryCIDGroups", ["flight-control:read"]),
            ("queryRoles", ["flight-control:read"]),
            ("queryUserGroupMembers", ["flight-control:read"]),
            ("queryUserGroups", ["flight-control:read"]),
            ("GetDriftIndicatorsValuesByDate", ["drift-indicators:read"]),
            ("ReadDriftIndicatorsCount", ["drift-indicators:read"]),
            ("SearchAndReadDriftIndicatorEntities", ["drift-indicators:read"]),
            ("ReadDriftIndicatorEntities", ["drift-indicators:read"]),
            ("SearchDriftIndicators", ["drift-indicators:read"]),
            ("SearchHuntingGuides", ["CAO Hunting:read"]),
            ("GetArchiveExport", ["CAO Hunting:read"]),
            ("getAssessmentV1", ["Zero Trust Assessment:read"]),
            ("getCombinedAssessmentsQuery", ["Zero Trust Assessment:read"]),
            ("queryCombinedContentUpdatePolicies", ["Content Update Policies:read"]),
            ("performContentUpdatePoliciesAction", ["Content Update Policies:write"]),
            ("GetSensorInstallersByQueryV2", ["Sensor Download:read"]),
            ("QueryQuarantineFiles", ["Quarantined Files:read"]),
            ("report_executions_retry", ["Scheduled Reports:read"]),
            ("tokens_query", ["Installation Tokens:read"]),
            ("queryCombinedPreventionPolicies", ["Prevention Policies:read"]),
            ("performPreventionPoliciesAction", ["Prevention Policies:write"]),
            ("queryCombinedRTResponsePolicies", ["Response Policies:read"]),
            ("performRTResponsePoliciesAction", ["Response Policies:write"]),
            ("queryCombinedSensorUpdatePolicies", ["Sensor Update Policies:read"]),
            ("performSensorUpdatePoliciesAction", ["Sensor Update Policies:write"]),
            ("queryCombinedDeviceControlPolicies", ["Device Control Policies:read"]),
            ("performDeviceControlPoliciesAction", ["Device Control Policies:write"]),
            ("queryCombinedFirewallPolicies", ["Firewall Policies:read"]),
            ("performFirewallPoliciesAction", ["Firewall Policies:write"]),
            ("WorkflowDefinitionsCombined", ["Workflow:read"]),
            ("WorkflowExecute", ["Workflow:write"]),
            ("RTR_AggregateSessions", ["Real Time Response:read"]),
            ("BatchActiveResponderCmd", ["Real Time Response:read"]),
            ("BatchGetCmd", ["Real Time Response:read"]),
            ("BatchGetCmdStatus", ["Real Time Response:read"]),
            ("BatchInitSessions", ["Real Time Response:read"]),
            ("BatchRefreshSessions", ["Real Time Response:read"]),
            ("RTR_ExecuteActiveResponderCommand", ["Real Time Response:read"]),
            ("RTR_CheckActiveResponderCommandStatus", ["Real Time Response:read"]),
            ("RTR_GetExtractedFileContents", ["Real Time Response:read"]),
            ("RTR_ListFilesV2", ["Real Time Response:read"]),
            ("RTR_DeleteFileV2", ["Real Time Response:read"]),
            ("RTR_ListQueuedSessions", ["Real Time Response:read"]),
            ("RTR_PulseSession", ["Real Time Response:read"]),
            ("RTR_ExecuteCommand", ["Real Time Response:read"]),
            ("RTR_ExecuteAdminCommand", ["Real Time Response Admin:write"]),
            ("RTR_GetFalconScripts", ["Real Time Response Admin:write"]),
            ("RTR_ListFalconScripts", ["Real Time Response Admin:write"]),
            ("RTR_GetPutFileContents", ["Real Time Response Admin:write"]),
            ("RTR_GetPut_FilesV2", ["Real Time Response Admin:write"]),
            ("RTR_CreatePut_FilesV2", ["Real Time Response Admin:write"]),
            ("RTR_GetScriptsV2", ["Real Time Response Admin:write"]),
            ("RTR_CreateScriptsV2", ["Real Time Response Admin:write"]),
            ("RTR_UpdateScriptsV2", ["Real Time Response Admin:write"]),
            ("RTRAuditSessions", ["Real Time Response Audit:read"]),
            ("aggregateUsersV1", ["User Management:read"]),
            ("queryUserV1", ["User Management:read"]),
            ("entitiesRolesV1", ["User Management:read"]),
            ("userActionV1", ["User Management:write"]),
            ("updateUserV1", ["User Management:write"]),
            ("userRolesActionV1", ["User Management:write"]),
            ("api_preempt_proxy_post_graphql", [
                "Identity Protection Entities:read",
                "Identity Protection Timeline:read",
                "Identity Protection Detections:read",
                "Identity Protection Assessment:read",
                "Identity Protection GraphQL:write"
            ])
        ]

        for operation, expected_scopes in test_cases:
            with self.subTest(operation=operation):
                result = get_required_scopes(operation)
                self.assertEqual(result, expected_scopes)
                self.assertIsInstance(result, list)
                for scope in result:
                    self.assertIsInstance(scope, str)

    def test_graceful_fallback_behavior(self):
        """Test that unmapped operations handle gracefully without breaking error handling."""
        # Test edge cases that should return empty list
        edge_cases = [
            None,
            "",
            "NonExistentOperation",
            "malformed operation name",
            "operation:with:colons",
        ]

        for test_case in edge_cases:
            with self.subTest(operation=test_case):
                result = get_required_scopes(test_case)
                self.assertEqual(result, [])
                self.assertIsInstance(result, list)

    def test_scope_mapping_consistency(self):
        """Test that scope mappings are internally consistent and follow patterns."""
        # Collect scopes by category to validate consistency
        scope_patterns = {}
        for operation, scopes in API_SCOPE_REQUIREMENTS.items():
            for scope in scopes:
                resource = scope.split(":")[0]
                permission = scope.split(":")[1]

                if resource not in scope_patterns:
                    scope_patterns[resource] = set()
                scope_patterns[resource].add(permission)

        # Validate that most resources use consistent permission patterns
        read_only_resources = [
            "Hosts", "Vulnerabilities",
            "Assets", "Sensor Usage", "Scheduled Reports",
            "Real Time Response", "Real Time Response Audit", "CAO Hunting",
            "Zero Trust Assessment", "Sensor Download", "event-streams",
            "falcon-data-replicator", "infrastructure-as-code",
            "drift-indicators",
        ]

        for resource in read_only_resources:
            if resource in scope_patterns:
                self.assertEqual(
                    scope_patterns[resource],
                    {"read"},
                    f"Resource '{resource}' should only use 'read' permission"
                )

        read_write_resources = [
            "Alerts",
            "Incidents",
            "Host Groups",
            "Host Migration",
            "IT Automation",
            "IOC Management",
            "ml-exclusions",
            "sensor-visibility-exclusions",
            "IOA Exclusions",
            "Firewall Management",
            "Exposure Management",
            "NGSIEM",
            "User Management",
            "Quarantined Files",
            "Installation Tokens",
            "Prevention Policies",
            "Response Policies",
            "Sensor Update Policies",
            "Device Control Policies",
            "Firewall Policies",
            "Content Update Policies",
            "Workflow",
        ]

        for resource in read_write_resources:
            if resource in scope_patterns:
                self.assertEqual(
                    scope_patterns[resource],
                    {"read", "write"},
                    f"Resource '{resource}' should use both 'read' and 'write' permissions"
                )

    def test_comprehensive_module_coverage(self):
        """Test that we have reasonable coverage across expected modules."""
        # Count operations by likely module based on operation patterns
        module_patterns = {
            "alerts": ["GetQueriesAlertsV2", "PostEntitiesAlertsV2"],
            "hosts": ["QueryDevicesByFilter", "PostDeviceDetailsV2"],
            "host_groups": [
                "queryHostGroups",
                "getHostGroups",
                "queryCombinedGroupMembers",
                "createHostGroups",
                "updateHostGroups",
                "deleteHostGroups",
                "performGroupAction",
            ],
            "host_migration": [
                "GetMigrationIDsV1",
                "GetMigrationsV1",
                "GetHostMigrationIDsV1",
                "GetHostMigrationsV1",
                "GetMigrationDestinationsV1",
                "CreateMigrationV1",
                "MigrationsActionsV1",
                "HostMigrationsActionsV1",
            ],
            "it_automation": [
                "ITAutomationGetAssociatedTasks",
                "ITAutomationCombinedScheduledTasks",
                "ITAutomationGetTaskExecutionsByQuery",
                "ITAutomationGetTaskGroupsByQuery",
                "ITAutomationGetTasksByQuery",
                "ITAutomationGetUserGroup",
                "ITAutomationCreateUserGroup",
                "ITAutomationUpdateUserGroup",
                "ITAutomationDeleteUserGroup",
                "ITAutomationUpdatePolicyHostGroups",
                "ITAutomationUpdatePoliciesPrecedence",
                "ITAutomationGetPolicies",
                "ITAutomationCreatePolicy",
                "ITAutomationUpdatePolicies",
                "ITAutomationDeletePolicy",
                "ITAutomationGetScheduledTasks",
                "ITAutomationCreateScheduledTask",
                "ITAutomationUpdateScheduledTask",
                "ITAutomationDeleteScheduledTasks",
                "ITAutomationGetTaskExecution",
                "ITAutomationGetTaskExecutionHostStatus",
                "ITAutomationStartExecutionResultsSearch",
                "ITAutomationGetExecutionResultsSearchStatus",
                "ITAutomationGetExecutionResults",
                "ITAutomationGetTaskGroups",
                "ITAutomationCreateTaskGroup",
                "ITAutomationUpdateTaskGroup",
                "ITAutomationDeleteTaskGroups",
                "ITAutomationGetTasks",
                "ITAutomationCreateTask",
                "ITAutomationUpdateTask",
                "ITAutomationDeleteTask",
                "ITAutomationSearchUserGroup",
                "ITAutomationQueryPolicies",
                "ITAutomationSearchScheduledTasks",
                "ITAutomationSearchTaskExecutions",
                "ITAutomationSearchTaskGroups",
                "ITAutomationSearchTasks",
                "ITAutomationStartTaskExecution",
                "ITAutomationRunLiveQuery",
                "ITAutomationCancelTaskExecution",
                "ITAutomationRerunTaskExecution",
            ],
            "incidents": ["QueryIncidents", "GetIncidents", "QueryBehaviors", "GetBehaviors", "CrowdScore"],
            "intel": [
                "QueryIntelActorIds",
                "QueryIntelActorEntities",
                "GetIntelActorEntities",
                "QueryIntelIndicatorIds",
                "QueryIntelIndicatorEntities",
                "GetIntelIndicatorEntities",
                "QueryIntelReportIds",
                "QueryIntelReportEntities",
                "GetIntelReportEntities",
                "GetIntelReportPDF",
                "QueryIntelRuleIds",
                "GetIntelRuleEntities",
                "GetIntelRuleFile",
                "GetLatestIntelRuleFile",
                "QueryMalware",
                "QueryMalwareEntities",
                "GetMalwareEntities",
                "GetMalwareMitreReport",
                "QueryMitreAttacks",
                "QueryMitreAttacksForMalware",
                "PostMitreAttacks",
                "QueryVulnerabilities",
                "GetVulnerabilities",
                "GetMitreReport",
            ],
            "spotlight": [
                "combinedQueryVulnerabilities",
                "queryVulnerabilities",
                "getVulnerabilities",
                "getRemediations",
                "getRemediationsV2",
            ],
            "cloud": [
                "ReadContainerCombined",
                "ReadContainerCount",
                "ReadCombinedVulnerabilities",
                "ReadCombinedVulnerabilitiesDetails",
                "ReadCombinedVulnerabilitiesInfo",
                "ReadVulnerabilityCount",
                "ReadVulnerabilityCountBySeverity",
                "ReadVulnerabilityCountByCPSRating",
                "ReadVulnerabilityCountByCVSSScore",
                "ReadVulnerabilityCountByActivelyExploited",
                "ReadVulnerabilitiesByImageCount",
                "ReadVulnerabilitiesPublicationDate",
            ],
            "discover": [
                "combined_applications",
                "combined_hosts",
                "query_accounts",
                "query_applications",
                "query_hosts",
                "query_iot_hosts",
                "query_iot_hostsV2",
                "query_logins",
                "get_accounts",
                "get_applications",
                "get_hosts",
                "get_iot_hosts",
                "get_logins",
            ],
            "exposure_management": [
                "query_external_assets_v2",
                "get_external_assets",
                "aggregate_external_assets",
                "post_external_assets_inventory_v1",
                "patch_external_assets",
                "delete_external_assets",
            ],
            "event_streams": [
                "listAvailableStreamsOAuth2",
                "refreshActiveStreamSession",
            ],
            "fdr": [
                "fdrschema_combined_event_get",
                "fdrschema_entities_event_get",
                "fdrschema_queries_event_get",
                "fdrschema_entities_field_get",
                "fdrschema_queries_field_get",
            ],
            "downloads": [
                "FetchFilesDownloadInfo",
                "FetchFilesDownloadInfoV2",
                "DownloadFile",
                "EnumerateFile",
            ],
            "delivery_settings": [
                "GetDeliverySettings",
                "PostDeliverySettings",
            ],
            "device_content": [
                "entities_states_v1",
                "queries_states_v1",
            ],
            "deployments": [
                "CombinedReleaseNotesV1",
                "CombinedReleasesV1Mixin0",
                "GetDeploymentsExternalV1",
                "GetEntityIDsByQueryPOST",
                "GetEntityIDsByQueryPOSTV2",
                "QueryReleaseNotesV1",
            ],
            "intelligence_feeds": [
                "DownloadFeedArchive",
                "ListFeedTypes",
                "QueryFeedArchives",
            ],
            "api_integrations": [
                "GetCombinedPluginConfigs",
                "ExecuteCommandProxy",
                "ExecuteCommand",
            ],
            "quick_scan": [
                "GetScansAggregates",
                "GetScans",
                "ScanSamples",
                "QuerySubmissionsMixin0",
            ],
            "threatgraph": [
                "combined_edges_get",
                "combined_ran_on_get",
                "combined_summary_get",
                "entities_vertices_get",
                "entities_vertices_getv2",
                "queries_edgetypes_get",
            ],
            "malquery": [
                "GetMalQueryQuotasV1",
                "PostMalQueryFuzzySearchV1",
                "GetMalQueryDownloadV1",
                "GetMalQueryMetadataV1",
                "GetMalQueryRequestV1",
                "GetMalQueryEntitiesSamplesFetchV1",
                "PostMalQueryEntitiesSamplesMultidownloadV1",
                "PostMalQueryExactSearchV1",
                "PostMalQueryHuntV1",
            ],
            "correlation_rules": [
                "aggregates_rule_versions_post_v1",
                "combined_rules_get_v1",
                "combined_rules_get_v2",
                "entities_latest_rules_get_v1",
                "entities_rule_versions_export_post_v1",
                "entities_rule_versions_import_post_v1",
                "entities_rule_versions_publish_patch_v1",
                "entities_rule_versions_delete_v1",
                "entities_rules_get_v1",
                "entities_rules_post_v1",
                "entities_rules_patch_v1",
                "entities_rules_delete_v1",
                "entities_rules_get_v2",
                "queries_rules_get_v1",
                "queries_rules_get_v2",
            ],
            "message_center": [
                "AggregateCases",
                "GetCaseActivityByIds",
                "CaseAddActivity",
                "CaseDownloadAttachment",
                "CaseAddAttachment",
                "CreateCaseV2",
                "GetCaseEntitiesByIDs",
                "QueryActivityByCaseID",
                "QueryCasesIdsByFilter",
            ],
            "mssp": [
                "getChildrenV2",
                "getChildren",
                "getCIDGroupMembersByV1",
                "addCIDGroupMembers",
                "deleteCIDGroupMembersV1",
                "getCIDGroupMembersBy",
                "deleteCIDGroupMembers",
                "getCIDGroupMembersByV2",
                "deleteCIDGroupMembersV2",
                "getCIDGroupByIdV1",
                "createCIDGroups",
                "deleteCIDGroups",
                "updateCIDGroups",
                "getCIDGroupById",
                "getCIDGroupByIdV2",
                "getRolesByID",
                "addRole",
                "deletedRoles",
                "getUserGroupMembersByIDV1",
                "addUserGroupMembers",
                "deleteUserGroupMembers",
                "getUserGroupMembersByID",
                "getUserGroupMembersByIDV2",
                "getUserGroupsByIDV1",
                "createUserGroups",
                "deleteUserGroups",
                "updateUserGroups",
                "getUserGroupsByID",
                "getUserGroupsByIDV2",
                "queryChildren",
                "queryCIDGroupMembers",
                "queryCIDGroups",
                "queryRoles",
                "queryUserGroupMembers",
                "queryUserGroups",
            ],
            "drift_indicators": [
                "GetDriftIndicatorsValuesByDate",
                "ReadDriftIndicatorsCount",
                "SearchAndReadDriftIndicatorEntities",
                "ReadDriftIndicatorEntities",
                "SearchDriftIndicators",
            ],
            "content_update_policies": [
                "queryCombinedContentUpdatePolicyMembers",
                "queryCombinedContentUpdatePolicies",
                "performContentUpdatePoliciesAction",
                "setContentUpdatePoliciesPrecedence",
                "getContentUpdatePolicies",
                "createContentUpdatePolicies",
                "updateContentUpdatePolicies",
                "deleteContentUpdatePolicies",
                "queryContentUpdatePolicyMembers",
                "queryPinnableContentVersions",
                "queryContentUpdatePolicies",
            ],
            "cao_hunting": [
                "AggregateHuntingGuides",
                "AggregateIntelligenceQueries",
                "GetArchiveExport",
                "GetHuntingGuides",
                "GetIntelligenceQueries",
                "SearchHuntingGuides",
                "SearchIntelligenceQueries",
            ],
            "idp": ["api_preempt_proxy_post_graphql"],
            "user_management": [
                "aggregateUsersV1",
                "queryUserV1",
                "retrieveUsersGETV1",
                "queriesRolesV1",
                "entitiesRolesGETV2",
                "entitiesRolesV1",
                "CombinedUserRolesV2",
                "createUserV1",
                "updateUserV1",
                "deleteUserV1",
                "userActionV1",
                "userRolesActionV1",
            ],
            "sensor_usage": ["GetSensorUsageWeekly"],
            "scheduled_reports": [
                "scheduled_reports_query", "scheduled_reports_get", "scheduled_reports_launch",
                "report_executions_query", "report_executions_get", "report_executions_download_get",
                "report_executions_retry",
            ],
            "sensor_download": [
                "GetCombinedSensorInstallersByQuery",
                "GetCombinedSensorInstallersByQueryV2",
                "DownloadSensorInstallerById",
                "DownloadSensorInstallerByIdV2",
                "GetSensorInstallersEntities",
                "GetSensorInstallersEntitiesV2",
                "GetSensorInstallersCCIDByQuery",
                "GetSensorInstallersByQuery",
                "GetSensorInstallersByQueryV2",
            ],
            "quarantine": [
                "ActionUpdateCount",
                "GetAggregateFiles",
                "GetQuarantineFiles",
                "QueryQuarantineFiles",
                "UpdateQfByQuery",
                "UpdateQuarantinedDetectsByIds",
            ],
            "installation_tokens": [
                "audit_events_read",
                "customer_settings_read",
                "tokens_read",
                "tokens_create",
                "tokens_delete",
                "tokens_update",
                "audit_events_query",
                "tokens_query",
                "customer_settings_update",
            ],
            "prevention_policies": [
                "queryCombinedPreventionPolicyMembers",
                "queryCombinedPreventionPolicies",
                "performPreventionPoliciesAction",
                "setPreventionPoliciesPrecedence",
                "getPreventionPolicies",
                "createPreventionPolicies",
                "updatePreventionPolicies",
                "deletePreventionPolicies",
                "queryPreventionPolicyMembers",
                "queryPreventionPolicies",
            ],
            "response_policies": [
                "queryCombinedRTResponsePolicyMembers",
                "queryCombinedRTResponsePolicies",
                "performRTResponsePoliciesAction",
                "setRTResponsePoliciesPrecedence",
                "getRTResponsePolicies",
                "createRTResponsePolicies",
                "updateRTResponsePolicies",
                "deleteRTResponsePolicies",
                "queryRTResponsePolicyMembers",
                "queryRTResponsePolicies",
            ],
            "sensor_update_policies": [
                "revealUninstallToken",
                "queryCombinedSensorUpdateBuilds",
                "queryCombinedSensorUpdateKernels",
                "queryCombinedSensorUpdatePolicyMembers",
                "queryCombinedSensorUpdatePolicies",
                "queryCombinedSensorUpdatePoliciesV2",
                "performSensorUpdatePoliciesAction",
                "setSensorUpdatePoliciesPrecedence",
                "getSensorUpdatePolicies",
                "createSensorUpdatePolicies",
                "updateSensorUpdatePolicies",
                "deleteSensorUpdatePolicies",
                "getSensorUpdatePoliciesV2",
                "createSensorUpdatePoliciesV2",
                "updateSensorUpdatePoliciesV2",
                "querySensorUpdateKernelsDistinct",
                "querySensorUpdatePolicyMembers",
                "querySensorUpdatePolicies",
            ],
            "device_control_policies": [
                "queryCombinedDeviceControlPolicyMembers",
                "queryCombinedDeviceControlPolicies",
                "getDefaultDeviceControlPolicies",
                "updateDefaultDeviceControlPolicies",
                "performDeviceControlPoliciesAction",
                "patchDeviceControlPoliciesClassesV1",
                "getDefaultDeviceControlSettings",
                "updateDefaultDeviceControlSettings",
                "setDeviceControlPoliciesPrecedence",
                "getDeviceControlPolicies",
                "createDeviceControlPolicies",
                "updateDeviceControlPolicies",
                "deleteDeviceControlPolicies",
                "getDeviceControlPoliciesV2",
                "postDeviceControlPoliciesV2",
                "patchDeviceControlPoliciesV2",
                "queryDeviceControlPolicyMembers",
                "queryDeviceControlPolicies",
            ],
            "firewall_policies": [
                "queryCombinedFirewallPolicyMembers",
                "queryCombinedFirewallPolicies",
                "performFirewallPoliciesAction",
                "setFirewallPoliciesPrecedence",
                "getFirewallPolicies",
                "createFirewallPolicies",
                "updateFirewallPolicies",
                "deleteFirewallPolicies",
                "queryFirewallPolicyMembers",
                "queryFirewallPolicies",
            ],
            "workflows": [
                "WorkflowActivitiesCombined",
                "WorkflowActivitiesContentCombined",
                "WorkflowDefinitionsCombined",
                "WorkflowExecutionsCombined",
                "WorkflowTriggersCombined",
                "WorkflowDefinitionsExport",
                "WorkflowExecutionResults",
                "WorkflowGetHumanInputV1",
                "WorkflowDefinitionsAction",
                "WorkflowDefinitionsImport",
                "WorkflowDefinitionsUpdate",
                "WorkflowExecute",
                "WorkflowExecuteInternal",
                "WorkflowMockExecute",
                "WorkflowExecutionsAction",
                "WorkflowUpdateHumanInputV1",
                "WorkflowSystemDefinitionsDeProvision",
                "WorkflowSystemDefinitionsPromote",
                "WorkflowSystemDefinitionsProvision",
            ],
            "ioa_exclusions": [
                "queryIOAExclusionsV1",
                "getIOAExclusionsV1",
                "createIOAExclusionsV1",
                "updateIOAExclusionsV1",
                "deleteIOAExclusionsV1",
            ],
            "ml_exclusions": [
                "getMLExclusionsV1",
                "createMLExclusionsV1",
                "deleteMLExclusionsV1",
                "updateMLExclusionsV1",
                "queryMLExclusionsV1",
            ],
            "sensor_visibility_exclusions": [
                "getSensorVisibilityExclusionsV1",
                "createSVExclusionsV1",
                "deleteSensorVisibilityExclusionsV1",
                "updateSensorVisibilityExclusionsV1",
                "querySensorVisibilityExclusionsV1",
            ],
            "certificate_based_exclusions": [
                "cb_exclusions_get_v1",
                "cb_exclusions_create_v1",
                "cb_exclusions_delete_v1",
                "cb_exclusions_update_v1",
                "certificates_get_v1",
                "cb_exclusions_query_v1",
            ],
            "firewall": [
                "aggregate_events",
                "aggregate_policy_rules",
                "aggregate_rule_groups",
                "aggregate_rules",
                "get_events",
                "get_firewall_fields",
                "get_network_locations",
                "get_network_locations_details",
                "get_platforms",
                "get_policy_containers",
                "query_events",
                "query_firewall_fields",
                "query_network_locations",
                "query_platforms",
                "query_policy_rules",
                "query_rule_groups",
                "query_rules",
                "get_rule_groups",
                "get_rules",
                "create_network_locations",
                "upsert_network_locations",
                "update_network_locations",
                "update_network_locations_metadata",
                "update_network_locations_precedence",
                "update_policy_container",
                "update_policy_container_v1",
                "create_rule_group",
                "create_rule_group_validation",
                "update_rule_group",
                "update_rule_group_validation",
                "delete_network_locations",
                "delete_rule_groups",
                "validate_filepath_pattern",
            ],
            "ngsiem": [
                "GetDashboardTemplate",
                "CreateDashboardFromTemplate",
                "UpdateDashboardFromTemplate",
                "DeleteDashboard",
                "UploadLookupV1",
                "GetLookupV1",
                "GetLookupFromPackageV1",
                "GetLookupFromPackageWithNamespaceV1",
                "GetLookupFile",
                "CreateLookupFile",
                "UpdateLookupFile",
                "DeleteLookupFile",
                "GetParserTemplate",
                "CreateParserFromTemplate",
                "GetParser",
                "CreateParser",
                "UpdateParser",
                "DeleteParser",
                "GetSavedQueryTemplate",
                "CreateSavedQuery",
                "UpdateSavedQueryFromTemplate",
                "DeleteSavedQuery",
                "ListDashboards",
                "ListLookupFiles",
                "ListParsers",
                "ListSavedQueries",
                "StartSearchV1",
                "GetSearchStatusV1",
                "StopSearchV1",
            ],
            "rtr": [
                "RTR_AggregateSessions",
                "BatchActiveResponderCmd",
                "BatchCmd",
                "BatchGetCmdStatus",
                "BatchGetCmd",
                "BatchInitSessions",
                "BatchRefreshSessions",
                "RTR_CheckActiveResponderCommandStatus",
                "RTR_ExecuteActiveResponderCommand",
                "RTR_GetExtractedFileContents",
                "RTR_ListFiles",
                "RTR_DeleteFile",
                "RTR_ListFilesV2",
                "RTR_DeleteFileV2",
                "RTR_ListQueuedSessions",
                "RTR_PulseSession",
                "RTR_ListAllSessions",
                "RTR_ListSessions",
                "RTR_InitSession",
                "RTR_ExecuteCommand",
                "RTR_CheckCommandStatus",
                "RTR_DeleteSession",
                "RTR_DeleteQueuedSession",
                "RTR_ListScripts",
                "RTR_GetScripts",
                "RTR_GetFalconScripts",
                "RTR_GetPutFileContents",
                "RTR_ListPut_Files",
                "RTR_GetPut_Files",
                "RTR_CreatePut_Files",
                "RTR_DeletePut_Files",
                "RTR_GetPut_FilesV2",
                "RTR_CreatePut_FilesV2",
                "RTR_CreateScripts",
                "RTR_UpdateScripts",
                "RTR_DeleteScripts",
                "RTR_GetScriptsV2",
                "RTR_CreateScriptsV2",
                "RTR_UpdateScriptsV2",
                "RTR_ListFalconScripts",
                "RTR_ExecuteAdminCommand",
                "RTR_CheckAdminCommandStatus",
                "BatchAdminCmd",
                "RTRAuditSessions",
            ],
            "serverless": ["GetCombinedVulnerabilitiesSARIF"],
            "zero_trust_assessment": [
                "getAssessmentV1",
                "getAuditV1",
                "getAssessmentsByScoreV1",
                "getCombinedAssessmentsQuery",
            ],
        }

        # Verify that all expected operations are mapped
        all_expected_operations = set()
        for operations in module_patterns.values():
            all_expected_operations.update(operations)

        mapped_operations = set(API_SCOPE_REQUIREMENTS.keys())

        # All expected operations should be mapped
        missing_operations = all_expected_operations - mapped_operations
        self.assertEqual(
            len(missing_operations), 0,
            f"Expected operations missing from scope mappings: {sorted(missing_operations)}"
        )

        # Should have reasonable coverage (at least 11 different modules)
        self.assertGreaterEqual(
            len(module_patterns), 11,
            "Should have scope mappings for at least 11 different functional modules"
        )


if __name__ == "__main__":
    unittest.main()
