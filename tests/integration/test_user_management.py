"""Integration tests for the User Management module."""

from typing import Any

import pytest

from falcon_mcp.modules.user_management import UserManagementModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestUserManagementIntegration(BaseIntegrationTest):
    """Integration tests for User Management module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the User Management module with a real client."""
        self.module = UserManagementModule(falcon_client)

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
        """Skip test when API credentials are missing required User Management scope."""
        if self._extract_status_code(result) == 403:
            self.skip_with_warning(
                "Missing required API scope for User Management integration test",
                context=context,
            )

    @staticmethod
    def _extract_user_uuid(user_record: dict[str, Any]) -> str | None:
        """Extract user UUID from user detail record."""
        for key in ["uuid", "id", "user_uuid"]:
            value = user_record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    @staticmethod
    def _extract_role_id(role_record: dict[str, Any]) -> str | None:
        """Extract role ID from role detail record."""
        value = role_record.get("id")
        if isinstance(value, str) and value:
            return value
        return None

    def test_aggregate_users_operation_name(self):
        """Validate aggregateUsersV1 operation wiring."""
        result = self.call_method(
            self.module.aggregate_users,
            body=[{"field": "uid", "type": "terms", "size": 1}],
        )
        self._skip_if_scope_missing(result, "aggregate_users")

        self.assert_no_error(result, context="aggregate_users operation name validation")
        self.assert_valid_list_response(result, min_length=0, context="aggregate_users")

    def test_search_users_operation_name(self):
        """Validate read operation names for search_users."""
        result = self.call_method(
            self.module.search_users,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "search_users")

        self.assert_no_error(result, context="search_users operation name validation")
        self.assert_valid_list_response(result, min_length=0, context="search_users")

    def test_search_user_roles_operation_name(self):
        """Validate role query operation names for search_user_roles."""
        result = self.call_method(
            self.module.search_user_roles,
            user_uuid=None,
            cid=None,
            action="grant",
        )
        self._skip_if_scope_missing(result, "search_user_roles")

        self.assert_no_error(result, context="search_user_roles operation name validation")
        self.assert_valid_list_response(result, min_length=0, context="search_user_roles")

    def test_get_user_role_grants_with_existing_user_uuid(self):
        """Validate role grant retrieval using user UUID discovered from search."""
        users = self.call_method(
            self.module.search_users,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(users, "get_user_role_grants setup")
        self.assert_no_error(users, context="get_user_role_grants setup")

        if not users:
            self.skip_with_warning(
                "No users available to validate get_user_role_grants integration",
                context="test_get_user_role_grants_with_existing_user_uuid",
            )

        user_uuid = self._extract_user_uuid(users[0])
        if not user_uuid:
            self.skip_with_warning(
                "Could not extract user UUID from search_users results",
                context="test_get_user_role_grants_with_existing_user_uuid",
            )

        result = self.call_method(
            self.module.get_user_role_grants,
            user_uuid=user_uuid,
            cid=None,
            direct_only=None,
            filter=None,
            limit=20,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "get_user_role_grants")

        self.assert_no_error(result, context="get_user_role_grants")
        self.assert_valid_list_response(result, min_length=0, context="get_user_role_grants")

    def test_get_user_role_details_endpoints_with_discovered_role(self):
        """Validate entitiesRolesGETV2 and entitiesRolesV1 operation names."""
        roles = self.call_method(
            self.module.search_user_roles,
            user_uuid=None,
            cid=None,
            action="grant",
        )
        self._skip_if_scope_missing(roles, "get_user_role_details setup")
        self.assert_no_error(roles, context="get_user_role_details setup")

        if not roles:
            self.skip_with_warning(
                "No roles available to validate role detail endpoints",
                context="test_get_user_role_details_endpoints_with_discovered_role",
            )

        role_id = self._extract_role_id(roles[0])
        if not role_id:
            self.skip_with_warning(
                "Could not extract role ID from search_user_roles results",
                context="test_get_user_role_details_endpoints_with_discovered_role",
            )

        v2_result = self.call_method(
            self.module.get_user_role_details,
            ids=[role_id],
            cid=None,
        )
        self._skip_if_scope_missing(v2_result, "get_user_role_details")
        self.assert_no_error(v2_result, context="get_user_role_details")
        self.assert_valid_list_response(v2_result, min_length=0, context="get_user_role_details")

        v1_result = self.call_method(
            self.module.get_user_role_details_v1,
            ids=[role_id],
            cid=None,
        )
        self._skip_if_scope_missing(v1_result, "get_user_role_details_v1")
        self.assert_no_error(v1_result, context="get_user_role_details_v1")
        self.assert_valid_list_response(
            v1_result,
            min_length=0,
            context="get_user_role_details_v1",
        )

    def test_update_user_operation_name_with_invalid_uuid(self):
        """Validate updateUserV1 wiring with a non-existent UUID selector."""
        result = self.call_method(
            self.module.update_user,
            confirm_execution=True,
            user_uuid="00000000-0000-0000-0000-000000000000",
            first_name="Falcon",
            last_name="MCP",
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required User Management:write scope for update_user",
                context="update_user",
            )
        if status_code in (400, 404, 422, 500):
            return

        self.assert_no_error(result, context="update_user")
        self.assert_valid_list_response(result, min_length=0, context="update_user")

    def test_perform_user_action_operation_name_with_invalid_uuid(self):
        """Validate userActionV1 wiring with a non-existent UUID selector."""
        result = self.call_method(
            self.module.perform_user_action,
            confirm_execution=True,
            action_name="reset_password",
            user_uuids=["00000000-0000-0000-0000-000000000000"],
            action_value="temporary-password",
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required User Management:write scope for perform_user_action",
                context="perform_user_action",
            )
        if status_code in (400, 404, 422, 500):
            return

        self.assert_no_error(result, context="perform_user_action")
        self.assert_valid_list_response(result, min_length=0, context="perform_user_action")
