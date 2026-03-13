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
        self.assertEqual(get_required_scopes("GetQueriesAlertsV2"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("PostEntitiesAlertsV2"), ["Alerts:read"])
        self.assertEqual(get_required_scopes("QueryIncidents"), ["Incidents:read"])
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
            get_required_scopes("ITAutomationRunLiveQuery"),
            ["IT Automation:write"],
        )
        self.assertEqual(get_required_scopes("queryIOAExclusionsV1"), ["IOA Exclusions:read"])
        self.assertEqual(get_required_scopes("createIOAExclusionsV1"), ["IOA Exclusions:write"])
        self.assertEqual(
            get_required_scopes("query_external_assets_v2"),
            ["Exposure Management:read"],
        )
        self.assertEqual(
            get_required_scopes("delete_external_assets"),
            ["Exposure Management:write"],
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
            get_required_scopes("GetSensorInstallersByQueryV2"),
            ["Sensor Download:read"],
        )
        self.assertEqual(
            get_required_scopes("QueryQuarantineFiles"),
            ["Quarantined Files:read"],
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
            get_required_scopes("WorkflowDefinitionsCombined"),
            ["Workflow:read"],
        )
        self.assertEqual(
            get_required_scopes("WorkflowExecute"),
            ["Workflow:write"],
        )
        self.assertEqual(
            get_required_scopes("RTR_ExecuteAdminCommand"),
            ["Real Time Response Admin:write"],
        )
        self.assertEqual(
            get_required_scopes("RTRAuditSessions"),
            ["Real Time Response Audit:read"],
        )
        self.assertEqual(get_required_scopes("queryUserV1"), ["User Management:read"])
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
            ("GetQueriesAlertsV2", ["Alerts:read"]),
            ("QueryIncidents", ["Incidents:read"]),
            ("QueryIntelActorEntities", ["Actors (Falcon Intelligence):read"]),
            ("queryHostGroups", ["Host Groups:read"]),
            ("createHostGroups", ["Host Groups:write"]),
            ("GetMigrationIDsV1", ["Host Migration:read"]),
            ("CreateMigrationV1", ["Host Migration:write"]),
            ("ITAutomationGetTaskExecution", ["IT Automation:read"]),
            ("ITAutomationRunLiveQuery", ["IT Automation:write"]),
            ("queryIOAExclusionsV1", ["IOA Exclusions:read"]),
            ("createIOAExclusionsV1", ["IOA Exclusions:write"]),
            ("query_external_assets_v2", ["Exposure Management:read"]),
            ("delete_external_assets", ["Exposure Management:write"]),
            ("SearchHuntingGuides", ["CAO Hunting:read"]),
            ("GetArchiveExport", ["CAO Hunting:read"]),
            ("getAssessmentV1", ["Zero Trust Assessment:read"]),
            ("getCombinedAssessmentsQuery", ["Zero Trust Assessment:read"]),
            ("GetSensorInstallersByQueryV2", ["Sensor Download:read"]),
            ("QueryQuarantineFiles", ["Quarantined Files:read"]),
            ("tokens_query", ["Installation Tokens:read"]),
            ("queryCombinedPreventionPolicies", ["Prevention Policies:read"]),
            ("performPreventionPoliciesAction", ["Prevention Policies:write"]),
            ("queryCombinedRTResponsePolicies", ["Response Policies:read"]),
            ("performRTResponsePoliciesAction", ["Response Policies:write"]),
            ("queryCombinedSensorUpdatePolicies", ["Sensor Update Policies:read"]),
            ("performSensorUpdatePoliciesAction", ["Sensor Update Policies:write"]),
            ("queryCombinedDeviceControlPolicies", ["Device Control Policies:read"]),
            ("performDeviceControlPoliciesAction", ["Device Control Policies:write"]),
            ("WorkflowDefinitionsCombined", ["Workflow:read"]),
            ("WorkflowExecute", ["Workflow:write"]),
            ("RTR_ExecuteCommand", ["Real Time Response:read"]),
            ("RTR_ExecuteAdminCommand", ["Real Time Response Admin:write"]),
            ("RTRAuditSessions", ["Real Time Response Audit:read"]),
            ("queryUserV1", ["User Management:read"]),
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
            "Alerts", "Hosts", "Incidents", "Vulnerabilities",
            "Assets", "Sensor Usage", "Scheduled Reports",
            "Real Time Response", "Real Time Response Audit", "CAO Hunting",
            "Zero Trust Assessment", "Sensor Download",
        ]

        for resource in read_only_resources:
            if resource in scope_patterns:
                self.assertEqual(
                    scope_patterns[resource],
                    {"read"},
                    f"Resource '{resource}' should only use 'read' permission"
                )

        read_write_resources = [
            "Host Groups",
            "Host Migration",
            "IT Automation",
            "IOC Management",
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
                "ITAutomationGetTaskExecutionsByQuery",
                "ITAutomationGetTaskExecution",
                "ITAutomationGetTaskExecutionHostStatus",
                "ITAutomationStartExecutionResultsSearch",
                "ITAutomationGetExecutionResultsSearchStatus",
                "ITAutomationGetExecutionResults",
                "ITAutomationStartTaskExecution",
                "ITAutomationRunLiveQuery",
                "ITAutomationCancelTaskExecution",
                "ITAutomationRerunTaskExecution",
            ],
            "incidents": ["QueryIncidents", "GetIncidents", "QueryBehaviors", "GetBehaviors", "CrowdScore"],
            "intel": ["QueryIntelActorEntities", "QueryIntelIndicatorEntities", "QueryIntelReportEntities", "GetMitreReport"],
            "spotlight": ["combinedQueryVulnerabilities"],
            "cloud": ["ReadContainerCombined", "ReadContainerCount", "ReadCombinedVulnerabilities"],
            "discover": ["combined_applications", "combined_hosts"],
            "exposure_management": [
                "query_external_assets_v2",
                "get_external_assets",
                "aggregate_external_assets",
                "post_external_assets_inventory_v1",
                "patch_external_assets",
                "delete_external_assets",
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
                "queryUserV1",
                "retrieveUsersGETV1",
                "queriesRolesV1",
                "entitiesRolesGETV2",
                "CombinedUserRolesV2",
                "createUserV1",
                "deleteUserV1",
                "userRolesActionV1",
            ],
            "sensor_usage": ["GetSensorUsageWeekly"],
            "scheduled_reports": [
                "scheduled_reports_query", "scheduled_reports_get", "scheduled_reports_launch",
                "report_executions_query", "report_executions_get", "report_executions_download_get"
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
            "rtr": [
                "RTR_ListAllSessions",
                "RTR_ListSessions",
                "RTR_InitSession",
                "RTR_ExecuteCommand",
                "RTR_CheckCommandStatus",
                "RTR_DeleteSession",
                "RTR_DeleteQueuedSession",
                "RTR_ListScripts",
                "RTR_GetScripts",
                "RTR_ListPut_Files",
                "RTR_GetPut_Files",
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
