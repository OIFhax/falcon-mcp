"""Integration tests for the Device Control Policies module."""

from typing import Any

import pytest

from falcon_mcp.modules.device_control_policies import DeviceControlPoliciesModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDeviceControlPoliciesIntegration(BaseIntegrationTest):
    """Integration tests for Device Control Policies module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Device Control Policies module with a real client."""
        self.module = DeviceControlPoliciesModule(falcon_client)

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
        """Skip when Device Control Policies scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Device Control Policies integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Device Control Policies service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_policy_id(record: dict[str, Any]) -> str | None:
        """Extract device control policy ID from a record."""
        value = record.get("id")
        if isinstance(value, str) and value:
            return value
        return None

    @staticmethod
    def _normalize_search_result(result: Any) -> Any:
        """Normalize search responses that may include FQL helper wrapping."""
        if isinstance(result, dict) and "results" in result:
            return result.get("results", [])
        return result

    def _assert_write_result_or_expected_error(self, result: Any, context: str) -> None:
        """Accept expected validation/not-found errors, otherwise require success."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required Device Control Policies:write scope",
                context=context,
            )
        if status_code in (400, 404, 422):
            return

        self.assert_no_error(result, context=context)
        self.assert_valid_list_response(result, min_length=0, context=context)

    def test_search_device_control_policies_operation_name(self):
        """Validate policy search operation name."""
        result = self.call_method(
            self.module.search_device_control_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_device_control_policies")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_device_control_policies")
        self.assert_valid_list_response(normalized, min_length=0, context="search_device_control_policies")

    def test_query_device_control_policy_ids_operation_name(self):
        """Validate policy ID query operation name."""
        result = self.call_method(
            self.module.query_device_control_policy_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_device_control_policy_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_device_control_policy_ids")
        self.assert_valid_list_response(normalized, min_length=0, context="query_device_control_policy_ids")

    def test_get_device_control_policy_details_with_existing_id(self):
        """Validate policy detail retrieval from discovered policy ID."""
        search_result = self.call_method(
            self.module.search_device_control_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(search_result, "get_device_control_policy_details setup")
        search_result = self._normalize_search_result(search_result)

        self.assert_no_error(search_result, context="get_device_control_policy_details setup")
        if not search_result:
            self.skip_with_warning(
                "No device control policies available to validate detail retrieval",
                context="test_get_device_control_policy_details_with_existing_id",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract device control policy ID from search results",
                context="test_get_device_control_policy_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_device_control_policy_details,
            ids=[policy_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_device_control_policy_details")

        self.assert_no_error(result, context="get_device_control_policy_details")
        self.assert_valid_list_response(result, min_length=0, context="get_device_control_policy_details")

    def test_search_device_control_policy_members_with_existing_policy(self):
        """Validate combined policy-member search using discovered policy ID."""
        search_result = self.call_method(
            self.module.search_device_control_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "search_device_control_policy_members setup",
        )
        search_result = self._normalize_search_result(search_result)
        self.assert_no_error(search_result, context="search_device_control_policy_members setup")

        if not search_result:
            self.skip_with_warning(
                "No device control policies available to validate member search",
                context="test_search_device_control_policy_members_with_existing_policy",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract device control policy ID from search results",
                context="test_search_device_control_policy_members_with_existing_policy",
            )

        result = self.call_method(
            self.module.search_device_control_policy_members,
            policy_id=policy_id,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_device_control_policy_members")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="search_device_control_policy_members")
        self.assert_valid_list_response(
            normalized,
            min_length=0,
            context="search_device_control_policy_members",
        )

    def test_query_device_control_policy_member_ids_with_existing_policy(self):
        """Validate member ID query using discovered policy ID."""
        search_result = self.call_method(
            self.module.search_device_control_policies,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(
            search_result,
            "query_device_control_policy_member_ids setup",
        )
        search_result = self._normalize_search_result(search_result)
        self.assert_no_error(search_result, context="query_device_control_policy_member_ids setup")

        if not search_result:
            self.skip_with_warning(
                "No device control policies available to validate member ID query",
                context="test_query_device_control_policy_member_ids_with_existing_policy",
            )

        policy_id = self._extract_policy_id(search_result[0])
        if not policy_id:
            self.skip_with_warning(
                "Could not extract device control policy ID from search results",
                context="test_query_device_control_policy_member_ids_with_existing_policy",
            )

        result = self.call_method(
            self.module.query_device_control_policy_member_ids,
            policy_id=policy_id,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "query_device_control_policy_member_ids")
        normalized = self._normalize_search_result(result)

        self.assert_no_error(normalized, context="query_device_control_policy_member_ids")
        self.assert_valid_list_response(
            normalized,
            min_length=0,
            context="query_device_control_policy_member_ids",
        )

    def test_get_default_device_control_operations(self):
        """Validate default policy/settings read operation wiring."""
        policies_result = self.call_method(self.module.get_default_device_control_policies)
        self._skip_if_scope_or_service_missing(policies_result, "get_default_device_control_policies")
        self.assert_no_error(policies_result, context="get_default_device_control_policies")
        self.assert_valid_list_response(
            policies_result,
            min_length=0,
            context="get_default_device_control_policies",
        )

        settings_result = self.call_method(self.module.get_default_device_control_settings)
        self._skip_if_scope_or_service_missing(settings_result, "get_default_device_control_settings")
        self.assert_no_error(settings_result, context="get_default_device_control_settings")
        self.assert_valid_list_response(
            settings_result,
            min_length=0,
            context="get_default_device_control_settings",
        )

    def test_write_operations_invalid_payload_expected_error_or_success(self):
        """Validate write operation wiring using invalid payloads/selectors."""
        invalid_policy_id = "0" * 32

        action_result = self.call_method(
            self.module.perform_device_control_policies_action,
            confirm_execution=True,
            action_name="disable",
            ids=[invalid_policy_id],
            group_id=None,
            action_parameters=None,
            body=None,
        )
        self._assert_write_result_or_expected_error(
            action_result,
            context="perform_device_control_policies_action",
        )

        precedence_result = self.call_method(
            self.module.set_device_control_policies_precedence,
            confirm_execution=True,
            body=None,
            ids=[invalid_policy_id],
            platform_name="Windows",
        )
        self._assert_write_result_or_expected_error(
            precedence_result,
            context="set_device_control_policies_precedence",
        )

        delete_result = self.call_method(
            self.module.delete_device_control_policies,
            confirm_execution=True,
            ids=[invalid_policy_id],
        )
        self._assert_write_result_or_expected_error(
            delete_result,
            context="delete_device_control_policies",
        )

        update_defaults_result = self.call_method(
            self.module.update_default_device_control_policies,
            confirm_execution=True,
            body={"invalid": True},
        )
        self._assert_write_result_or_expected_error(
            update_defaults_result,
            context="update_default_device_control_policies",
        )

        update_settings_result = self.call_method(
            self.module.update_default_device_control_settings,
            confirm_execution=True,
            body={"invalid": True},
        )
        self._assert_write_result_or_expected_error(
            update_settings_result,
            context="update_default_device_control_settings",
        )

        update_classes_result = self.call_method(
            self.module.update_device_control_policies_classes,
            confirm_execution=True,
            body={"invalid": True},
        )
        self._assert_write_result_or_expected_error(
            update_classes_result,
            context="update_device_control_policies_classes",
        )

        create_v1_result = self.call_method(
            self.module.create_device_control_policies,
            confirm_execution=True,
            body={"resources": [{}]},
            name=None,
            platform_name=None,
            description=None,
            settings=None,
        )
        self._assert_write_result_or_expected_error(
            create_v1_result,
            context="create_device_control_policies",
        )

        update_v1_result = self.call_method(
            self.module.update_device_control_policies,
            confirm_execution=True,
            body={"resources": [{"id": invalid_policy_id}]},
            id=None,
            name=None,
            description=None,
            settings=None,
        )
        self._assert_write_result_or_expected_error(
            update_v1_result,
            context="update_device_control_policies",
        )

        create_v2_result = self.call_method(
            self.module.create_device_control_policies_v2,
            confirm_execution=True,
            body={"resources": [{}]},
            name=None,
            platform_name=None,
            description=None,
            settings=None,
        )
        self._assert_write_result_or_expected_error(
            create_v2_result,
            context="create_device_control_policies_v2",
        )

        update_v2_result = self.call_method(
            self.module.update_device_control_policies_v2,
            confirm_execution=True,
            body={"resources": [{"id": invalid_policy_id}]},
            id=None,
            name=None,
            description=None,
            settings=None,
        )
        self._assert_write_result_or_expected_error(
            update_v2_result,
            context="update_device_control_policies_v2",
        )
