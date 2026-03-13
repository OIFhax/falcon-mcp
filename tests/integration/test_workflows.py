"""Integration tests for the Workflows module."""

from typing import Any

import pytest

from falcon_mcp.modules.workflows import WorkflowsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestWorkflowsIntegration(BaseIntegrationTest):
    """Integration tests for Workflows module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Workflows module with a real client."""
        self.module = WorkflowsModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        """Extract status code from standardized error responses."""
        if isinstance(result, dict):
            details = result.get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
            nested_results = result.get("results")
            if isinstance(nested_results, list) and nested_results:
                first = nested_results[0]
                if isinstance(first, dict):
                    nested_details = first.get("details", {})
                    if isinstance(nested_details, dict):
                        return nested_details.get("status_code")

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")

        return None

    def _skip_if_scope_or_service_missing(self, result: Any, context: str) -> None:
        """Skip when Workflow scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Workflows integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Workflows service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_definition_id(record: dict[str, Any]) -> str | None:
        """Extract workflow definition ID from a record."""
        for key in ["id", "definition_id"]:
            value = record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    @staticmethod
    def _extract_execution_id(record: dict[str, Any]) -> str | None:
        """Extract workflow execution ID from a record."""
        for key in ["id", "execution_id"]:
            value = record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    @staticmethod
    def _normalize_search_result(result: Any) -> Any:
        """Normalize search responses that may include FQL helper wrapping."""
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    def test_search_workflow_definitions_operation_name(self):
        """Validate workflow definitions search operation name."""
        result = self.call_method(
            self.module.search_workflow_definitions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_workflow_definitions")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_workflow_definitions")
        self.assert_valid_list_response(normalized, min_length=0, context="search_workflow_definitions")

    def test_search_workflow_executions_operation_name(self):
        """Validate workflow executions search operation name."""
        result = self.call_method(
            self.module.search_workflow_executions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_workflow_executions")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_workflow_executions")
        self.assert_valid_list_response(normalized, min_length=0, context="search_workflow_executions")

    def test_search_workflow_activities_operation_name(self):
        """Validate workflow activities search operation name."""
        result = self.call_method(
            self.module.search_workflow_activities,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_workflow_activities")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_workflow_activities")
        self.assert_valid_list_response(normalized, min_length=0, context="search_workflow_activities")

    def test_search_workflow_triggers_operation_name(self):
        """Validate workflow triggers search operation name."""
        result = self.call_method(
            self.module.search_workflow_triggers,
            filter=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_workflow_triggers")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_workflow_triggers")
        self.assert_valid_list_response(normalized, min_length=0, context="search_workflow_triggers")

    def test_export_workflow_definition_with_existing_id(self):
        """Validate export operation using a definition ID discovered via search."""
        search_result = self.call_method(
            self.module.search_workflow_definitions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "export_workflow_definition setup",
        )
        search_result = self._normalize_search_result(search_result)

        self.assert_no_error(search_result, context="export_workflow_definition setup")
        if not search_result:
            self.skip_with_warning(
                "No workflow definitions available to validate export operation",
                context="test_export_workflow_definition_with_existing_id",
            )

        definition_id = self._extract_definition_id(search_result[0])
        if not definition_id:
            self.skip_with_warning(
                "Could not extract workflow definition ID from search results",
                context="test_export_workflow_definition_with_existing_id",
            )

        result = self.call_method(
            self.module.export_workflow_definition,
            id=definition_id,
            sanitize=True,
        )
        self._skip_if_scope_or_service_missing(result, "export_workflow_definition")

        if isinstance(result, str):
            assert result.strip(), "Expected non-empty workflow export YAML content"
            return

        self.assert_no_error(result, context="export_workflow_definition")
        self.assert_valid_list_response(result, min_length=0, context="export_workflow_definition")

    def test_get_workflow_execution_results_with_existing_id(self):
        """Validate execution-results retrieval using discovered execution ID."""
        search_result = self.call_method(
            self.module.search_workflow_executions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "get_workflow_execution_results setup",
        )
        search_result = self._normalize_search_result(search_result)

        self.assert_no_error(search_result, context="get_workflow_execution_results setup")
        if not search_result:
            self.skip_with_warning(
                "No workflow executions available to validate result retrieval",
                context="test_get_workflow_execution_results_with_existing_id",
            )

        execution_id = self._extract_execution_id(search_result[0])
        if not execution_id:
            self.skip_with_warning(
                "Could not extract workflow execution ID from search results",
                context="test_get_workflow_execution_results_with_existing_id",
            )

        result = self.call_method(
            self.module.get_workflow_execution_results,
            ids=[execution_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_workflow_execution_results")

        self.assert_no_error(result, context="get_workflow_execution_results")
        self.assert_valid_list_response(result, min_length=0, context="get_workflow_execution_results")

    def test_import_workflow_definition_validate_only_operation_name(self):
        """Validate import operation name using validate-only mode."""
        result = self.call_method(
            self.module.import_workflow_definition,
            confirm_execution=True,
            data_file_content=(
                "name: falcon-mcp-workflows-validate-only\n"
                "description: Integration test validate-only import\n"
            ),
            name=None,
            validate_only=True,
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Workflow:write scope for import operation",
                context="import_workflow_definition",
            )
        if status_code == 404:
            self.skip_with_warning(
                "Workflows import endpoint unavailable for this tenant/region",
                context="import_workflow_definition",
            )
        if status_code in (400, 422):
            return

        self.assert_no_error(result, context="import_workflow_definition")
        self.assert_valid_list_response(result, min_length=0, context="import_workflow_definition")

    def test_update_workflow_execution_state_invalid_id_expected_error(self):
        """Validate execution-state action operation using an invalid ID selector."""
        result = self.call_method(
            self.module.update_workflow_execution_state,
            confirm_execution=True,
            action_name="cancel",
            ids=["00000000-0000-0000-0000-000000000000"],
            action_parameters=None,
            body=None,
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Workflow:write scope for execution-state action",
                context="update_workflow_execution_state",
            )
        if status_code == 404:
            return
        if status_code in (400, 422):
            return

        self.assert_no_error(result, context="update_workflow_execution_state")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="update_workflow_execution_state",
        )
