"""Integration tests for the IT Automation module."""

from typing import Any

import pytest

from falcon_mcp.modules.it_automation import ITAutomationModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestITAutomationIntegration(BaseIntegrationTest):
    """Integration tests for IT Automation module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the IT Automation module with a real client."""
        self.module = ITAutomationModule(falcon_client)

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

    def _skip_if_scope_missing(self, result: Any, context: str) -> None:
        """Skip test when API credentials are missing required IT Automation scope."""
        if self._extract_status_code(result) == 403:
            self.skip_with_warning(
                "Missing required API scope for IT Automation integration test",
                context=context,
            )

    @staticmethod
    def _extract_execution_id(execution_record: dict[str, Any]) -> str | None:
        """Extract execution ID from execution detail records."""
        for key in ["id", "task_execution_id"]:
            value = execution_record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    def test_search_task_executions_operation_name(self):
        """Validate read operation name for task execution search."""
        result = self.call_method(
            self.module.search_it_automation_task_executions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "search_task_executions")

        self.assert_no_error(
            result,
            context="search_it_automation_task_executions operation name validation",
        )
        self.assert_valid_list_response(result, min_length=0, context="search_task_executions")

    def test_get_task_execution_with_existing_id(self):
        """Validate get operation names using an execution ID from search."""
        search_result = self.call_method(
            self.module.search_it_automation_task_executions,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(search_result, "get_task_execution setup")
        self.assert_no_error(search_result, context="get_task_execution setup")

        if not search_result:
            self.skip_with_warning(
                "No IT Automation task executions available to validate get operations",
                context="test_get_task_execution_with_existing_id",
            )

        execution_id = self._extract_execution_id(search_result[0])
        if not execution_id:
            self.skip_with_warning(
                "Could not extract execution ID from IT Automation search results",
                context="test_get_task_execution_with_existing_id",
            )

        detail_result = self.call_method(
            self.module.get_it_automation_task_executions,
            ids=[execution_id],
        )
        self._skip_if_scope_missing(detail_result, "get_task_executions")
        self.assert_no_error(detail_result, context="get_task_executions")
        self.assert_valid_list_response(detail_result, min_length=0, context="get_task_executions")

        host_status_result = self.call_method(
            self.module.get_it_automation_task_execution_host_status,
            ids=[execution_id],
            filter=None,
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(host_status_result, "get_task_execution_host_status")
        self.assert_no_error(host_status_result, context="get_task_execution_host_status")
        self.assert_valid_list_response(
            host_status_result,
            min_length=0,
            context="get_task_execution_host_status",
        )
