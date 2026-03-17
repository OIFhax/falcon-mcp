"""
Tests for the User Management module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.user_management import UserManagementModule
from tests.modules.utils.test_modules import TestModules


class TestUserManagementModule(TestModules):
    """Test cases for the User Management module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(UserManagementModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_aggregate_users",
            "falcon_search_users",
            "falcon_get_user_details",
            "falcon_search_user_roles",
            "falcon_get_user_role_details",
            "falcon_get_user_role_details_v1",
            "falcon_get_user_role_grants",
            "falcon_create_user",
            "falcon_update_user",
            "falcon_delete_user",
            "falcon_perform_user_action",
            "falcon_grant_user_roles",
            "falcon_revoke_user_roles",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_users_fql_guide",
            "falcon_user_role_grants_fql_guide",
            "falcon_user_management_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_aggregate_users_requires_body(self):
        """Test aggregate_users requires body."""
        result = self.module.aggregate_users(body=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_aggregate_users_success(self):
        """Test aggregate_users operation wiring."""
        aggregation_body = [{"field": "status", "type": "terms", "size": 10}]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"status": "active", "count": 3}]},
        }

        result = self.module.aggregate_users(body=aggregation_body)

        self.mock_client.command.assert_called_once_with("aggregateUsersV1", body=aggregation_body)
        self.assertEqual(result, [{"status": "active", "count": 3}])

    def test_search_users_success(self):
        """Test searching users and fetching full details."""
        search_response = {
            "status_code": 200,
            "body": {"resources": ["user-uuid-1", "user-uuid-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"uuid": "user-uuid-1", "uid": "one@example.com"},
                    {"uuid": "user-uuid-2", "uid": "two@example.com"},
                ]
            },
        }
        self.mock_client.command.side_effect = [search_response, details_response]

        result = self.module.search_users(
            filter="status:'active'",
            limit=10,
            offset=0,
            sort="uid|asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "queryUserV1")
        self.assertEqual(first_call[1]["parameters"]["filter"], "status:'active'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "uid|asc")

        self.assertEqual(second_call[0][0], "retrieveUsersGETV1")
        self.assertEqual(second_call[1]["body"]["ids"], ["user-uuid-1", "user-uuid-2"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["uuid"], "user-uuid-1")

    def test_search_users_empty_results_returns_fql_guide(self):
        """Test user search empty results include FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_users(filter="uid:'none@example.com'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)
        self.assertIn("No results matched", result["hint"])

    def test_search_users_error_returns_fql_guide(self):
        """Test user search errors include FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_users(filter="bad filter")

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])
        self.assertIn("fql_guide", result)

    def test_get_user_details_validation_error(self):
        """Test get_user_details requires ids."""
        result = self.module.get_user_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_user_details_success(self):
        """Test retrieving user details by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"uuid": "user-uuid-1", "uid": "one@example.com"}]},
        }

        result = self.module.get_user_details(ids=["user-uuid-1"])

        self.mock_client.command.assert_called_once_with(
            "retrieveUsersGETV1",
            body={"ids": ["user-uuid-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uuid"], "user-uuid-1")

    def test_search_user_roles_success(self):
        """Test searching roles and fetching full role details."""
        role_search_response = {
            "status_code": 200,
            "body": {"resources": ["role-id-1", "role-id-2"]},
        }
        role_details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "role-id-1", "name": "Falcon Administrator"},
                    {"id": "role-id-2", "name": "Falcon Analyst"},
                ]
            },
        }
        self.mock_client.command.side_effect = [role_search_response, role_details_response]

        result = self.module.search_user_roles(
            user_uuid="user-uuid-1",
            cid="1234567890abcdef",
            action="grant",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "queriesRolesV1")
        self.assertEqual(first_call[1]["parameters"]["user_uuid"], "user-uuid-1")
        self.assertEqual(first_call[1]["parameters"]["cid"], "1234567890abcdef")
        self.assertEqual(first_call[1]["parameters"]["action"], "grant")

        self.assertEqual(second_call[0][0], "entitiesRolesGETV2")
        self.assertEqual(second_call[1]["parameters"]["cid"], "1234567890abcdef")
        self.assertEqual(second_call[1]["body"]["ids"], ["role-id-1", "role-id-2"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "role-id-1")

    def test_get_user_role_details_requires_ids(self):
        """Test role detail retrieval requires ids."""
        result = self.module.get_user_role_details(ids=None, cid=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_user_role_details_success(self):
        """Test role detail retrieval using entitiesRolesGETV2."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "role-id-1", "name": "Falcon Administrator"}]},
        }

        result = self.module.get_user_role_details(
            ids=["role-id-1"],
            cid="1234567890abcdef",
        )

        self.mock_client.command.assert_called_once_with(
            "entitiesRolesGETV2",
            parameters={"cid": "1234567890abcdef"},
            body={"ids": ["role-id-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "role-id-1")

    def test_get_user_role_details_v1_success(self):
        """Test role detail retrieval using entitiesRolesV1."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "role-id-2", "name": "Falcon Analyst"}]},
        }

        result = self.module.get_user_role_details_v1(
            ids=["role-id-2"],
            cid="1234567890abcdef",
        )

        self.mock_client.command.assert_called_once_with(
            "entitiesRolesV1",
            parameters={"ids": ["role-id-2"], "cid": "1234567890abcdef"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "role-id-2")

    def test_get_user_role_grants_validation_error(self):
        """Test get_user_role_grants requires user_uuid."""
        result = self.module.get_user_role_grants(user_uuid=None)

        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.mock_client.command.assert_not_called()

    def test_get_user_role_grants_success(self):
        """Test retrieving role grants for a user."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"role_id": "role-id-1", "role_name": "Falcon Analyst"}]},
        }

        result = self.module.get_user_role_grants(
            user_uuid="user-uuid-1",
            cid="1234567890abcdef",
            direct_only=True,
            filter="role_name:'Falcon Analyst'",
            limit=25,
            offset=5,
            sort="role_name|asc",
        )

        self.mock_client.command.assert_called_once_with(
            "CombinedUserRolesV2",
            parameters={
                "user_uuid": "user-uuid-1",
                "cid": "1234567890abcdef",
                "direct_only": True,
                "filter": "role_name:'Falcon Analyst'",
                "limit": 25,
                "offset": 5,
                "sort": "role_name|asc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["role_id"], "role-id-1")

    def test_get_user_role_grants_error_with_filter_returns_guide(self):
        """Test role grant filter errors include FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.get_user_role_grants(
            user_uuid="user-uuid-1",
            filter="bad filter",
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("error", result["results"][0])

    def test_create_user_requires_confirmation(self):
        """Test create_user requires explicit confirmation."""
        result = self.module.create_user(
            confirm_execution=False,
            uid="new.user@example.com",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_user_requires_uid(self):
        """Test create_user requires uid."""
        result = self.module.create_user(
            confirm_execution=True,
            uid=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_create_user_success(self):
        """Test create_user passes query and body parameters correctly."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"uuid": "user-uuid-1", "uid": "new.user@example.com"}]},
        }

        result = self.module.create_user(
            confirm_execution=True,
            uid="new.user@example.com",
            first_name="New",
            last_name="User",
            password=None,
            cid="1234567890abcdef",
            validate_only=False,
        )

        self.mock_client.command.assert_called_once_with(
            "createUserV1",
            parameters={"validate_only": False},
            body={
                "uid": "new.user@example.com",
                "first_name": "New",
                "last_name": "User",
                "cid": "1234567890abcdef",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uuid"], "user-uuid-1")

    def test_update_user_requires_confirmation(self):
        """Test update_user requires explicit confirmation."""
        result = self.module.update_user(
            confirm_execution=False,
            user_uuid="user-uuid-1",
            first_name="Updated",
            last_name="User",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_user_requires_first_and_last_name(self):
        """Test update_user requires both first_name and last_name."""
        result = self.module.update_user(
            confirm_execution=True,
            user_uuid="user-uuid-1",
            first_name="Updated",
            last_name=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_user_success(self):
        """Test update_user request wiring and default submitted response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.update_user(
            confirm_execution=True,
            user_uuid="user-uuid-1",
            first_name="Updated",
            last_name="Name",
        )

        self.mock_client.command.assert_called_once_with(
            "updateUserV1",
            parameters={"user_uuid": "user-uuid-1"},
            body={"first_name": "Updated", "last_name": "Name"},
        )
        self.assertEqual(result[0]["status"], "submitted")

    def test_delete_user_requires_confirmation(self):
        """Test delete_user requires explicit confirmation."""
        result = self.module.delete_user(
            confirm_execution=False,
            user_uuid="user-uuid-1",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_delete_user_success(self):
        """Test delete_user request and default submitted response."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.delete_user(
            confirm_execution=True,
            user_uuid="user-uuid-1",
        )

        self.mock_client.command.assert_called_once_with(
            "deleteUserV1",
            parameters={"user_uuid": "user-uuid-1"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "submitted")

    def test_perform_user_action_requires_confirmation(self):
        """Test perform_user_action requires explicit confirmation."""
        result = self.module.perform_user_action(
            confirm_execution=False,
            action_name="reset_password",
            user_uuids=["user-uuid-1"],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_perform_user_action_invalid_action_name(self):
        """Test perform_user_action validates action_name."""
        result = self.module.perform_user_action(
            confirm_execution=True,
            action_name="invalid_action",
            user_uuids=["user-uuid-1"],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_perform_user_action_success(self):
        """Test perform_user_action sends expected payload."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.perform_user_action(
            confirm_execution=True,
            action_name="reset_password",
            user_uuids=["user-uuid-1", "user-uuid-2"],
            action_value="temporary-password",
        )

        self.mock_client.command.assert_called_once_with(
            "userActionV1",
            body={
                "ids": ["user-uuid-1", "user-uuid-2"],
                "action": {
                    "action_name": "reset_password",
                    "action_value": "temporary-password",
                },
            },
        )
        self.assertEqual(result[0]["status"], "submitted")

    def test_grant_user_roles_requires_confirmation(self):
        """Test grant_user_roles requires explicit confirmation."""
        result = self.module.grant_user_roles(
            confirm_execution=False,
            user_uuid="user-uuid-1",
            role_ids=["role-id-1"],
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_grant_user_roles_success(self):
        """Test grant_user_roles sends the expected request body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.grant_user_roles(
            confirm_execution=True,
            user_uuid="user-uuid-1",
            role_ids=["role-id-1", "role-id-2"],
            cid="1234567890abcdef",
        )

        self.mock_client.command.assert_called_once_with(
            "userRolesActionV1",
            body={
                "action": "grant",
                "uuid": "user-uuid-1",
                "role_ids": ["role-id-1", "role-id-2"],
                "cid": "1234567890abcdef",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["action"], "grant")
        self.assertEqual(result[0]["status"], "submitted")

    def test_revoke_user_roles_success(self):
        """Test revoke_user_roles sends the expected request body."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.revoke_user_roles(
            confirm_execution=True,
            user_uuid="user-uuid-1",
            role_ids=["role-id-1"],
            cid=None,
        )

        self.mock_client.command.assert_called_once_with(
            "userRolesActionV1",
            body={
                "action": "revoke",
                "uuid": "user-uuid-1",
                "role_ids": ["role-id-1"],
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["action"], "revoke")
        self.assertEqual(result[0]["status"], "submitted")

    def test_search_users_has_read_only_annotations(self):
        """Test that search_users is registered with read-only annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_users", READ_ONLY_ANNOTATIONS)

    def test_create_user_has_write_annotations(self):
        """Test that create_user is registered with write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_create_user",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_update_user_has_write_annotations(self):
        """Test that update_user is registered with write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_update_user",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_delete_user_has_destructive_annotations(self):
        """Test that delete_user is registered with destructive write annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_delete_user",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_perform_user_action_has_destructive_annotations(self):
        """Test that perform_user_action is registered as destructive."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_perform_user_action",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )


if __name__ == "__main__":
    unittest.main()
