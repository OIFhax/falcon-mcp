"""
Tests for the Hosts module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.hosts import HostsModule
from tests.modules.utils.test_modules import TestModules


class TestHostsModule(TestModules):
    """Test cases for the Hosts module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(HostsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_hosts",
            "falcon_get_host_details",
            "falcon_search_host_groups",
            "falcon_search_host_group_members",
            "falcon_add_host_group",
            "falcon_update_host_group",
            "falcon_remove_host_groups",
            "falcon_perform_host_group_action",
            "falcon_search_migrations",
            "falcon_search_host_migrations",
            "falcon_create_migration",
            "falcon_get_migration_destinations",
            "falcon_perform_migration_action",
            "falcon_perform_host_migration_action",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_hosts_fql_guide",
            "falcon_search_host_groups_fql_guide",
            "falcon_search_migrations_fql_guide",
            "falcon_search_host_migrations_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_hosts", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_host_groups", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_migrations", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_add_host_group",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_remove_host_groups",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_perform_host_migration_action",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )

    def test_search_hosts_success(self):
        """Test searching hosts returns full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["device-1", "device-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "device-1", "hostname": "host-1"},
                    {"device_id": "device-2", "hostname": "host-2"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_hosts(
            filter="platform_name:'Windows'",
            limit=25,
            offset=10,
            sort="hostname.asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "QueryDevicesByFilter")
        self.assertEqual(
            self.mock_client.command.call_args_list[0][1]["parameters"]["filter"],
            "platform_name:'Windows'",
        )
        self.assertEqual(
            self.mock_client.command.call_args_list[1][0][0],
            "PostDeviceDetailsV2",
        )
        self.assertEqual(len(result), 2)

    def test_get_host_details_empty_ids(self):
        """Test get_host_details with empty IDs returns empty list."""
        result = self.module.get_host_details([])
        self.assertEqual(result, [])
        self.mock_client.command.assert_not_called()

    def test_search_host_groups_success(self):
        """Test searching host groups and resolving full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["group-1", "group-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "group-1", "name": "Servers"},
                    {"id": "group-2", "name": "Workstations"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_host_groups(
            filter="group_type:'static'",
            limit=50,
            offset=0,
            sort="name.asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "queryHostGroups")
        self.assertEqual(
            self.mock_client.command.call_args_list[1][0][0],
            "getHostGroups",
        )
        self.assertEqual(
            self.mock_client.command.call_args_list[1][1]["parameters"]["ids"],
            ["group-1", "group-2"],
        )
        self.assertEqual(len(result), 2)

    def test_search_host_groups_empty_results_with_filter(self):
        """Test host group search empty results with filter return FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_host_groups(
            filter="name:'DoesNotExist*'",
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_search_host_group_members_success(self):
        """Test searching host group members."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "device-1", "hostname": "host-1"},
                    {"device_id": "device-2", "hostname": "host-2"},
                ]
            },
        }

        result = self.module.search_host_group_members(
            group_id="group-1",
            filter="hostname:'HOST*'",
            limit=10,
            offset=0,
            sort="hostname.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "queryCombinedGroupMembers",
            parameters={
                "id": "group-1",
                "filter": "hostname:'HOST*'",
                "limit": 10,
                "offset": 0,
                "sort": "hostname.asc",
            },
        )
        self.assertEqual(len(result), 2)

    def test_add_host_group_success(self):
        """Test creating a host group with convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "group-1", "name": "Servers"}]},
        }

        result = self.module.add_host_group(
            name="Servers",
            group_type="static",
            description="Production servers",
            assignment_rule=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "createHostGroups",
            body={
                "resources": [
                    {
                        "name": "Servers",
                        "group_type": "static",
                        "description": "Production servers",
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "group-1")

    def test_add_host_group_validation_error(self):
        """Test add_host_group validation when name and body are missing."""
        result = self.module.add_host_group(
            name=None,
            group_type="static",
            description=None,
            assignment_rule=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_host_group_success(self):
        """Test updating a host group with convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "group-1", "name": "Servers Updated"}]},
        }

        result = self.module.update_host_group(
            id="group-1",
            name="Servers Updated",
            group_type=None,
            description="Updated description",
            assignment_rule=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "updateHostGroups",
            body={
                "resources": [
                    {
                        "id": "group-1",
                        "name": "Servers Updated",
                        "description": "Updated description",
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)

    def test_update_host_group_validation_errors(self):
        """Test update_host_group validation errors."""
        missing_id_result = self.module.update_host_group(
            id=None,
            name="Servers Updated",
            group_type=None,
            description=None,
            assignment_rule=None,
            body=None,
        )
        self.assertIn("error", missing_id_result[0])

        no_fields_result = self.module.update_host_group(
            id="group-1",
            name=None,
            group_type=None,
            description=None,
            assignment_rule=None,
            body=None,
        )
        self.assertIn("error", no_fields_result[0])

    def test_remove_host_groups_success(self):
        """Test deleting host groups by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "group-1"}]},
        }

        result = self.module.remove_host_groups(ids=["group-1"])

        self.mock_client.command.assert_called_once_with(
            "deleteHostGroups",
            parameters={"ids": ["group-1"]},
        )
        self.assertEqual(len(result), 1)

    def test_perform_host_group_action_success(self):
        """Test performing host group action with filter-based target selection."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "group-1"}]},
        }

        result = self.module.perform_host_group_action(
            action_name="add-hosts",
            group_ids=["group-1"],
            filter="platform_name:'Windows'",
            action_parameters=None,
            disable_hostname_check=True,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "performGroupAction",
            parameters={"action_name": "add-hosts", "disable_hostname_check": True},
            body={
                "ids": ["group-1"],
                "action_parameters": [
                    {"name": "filter", "value": "platform_name:'Windows'"}
                ],
            },
        )
        self.assertEqual(len(result), 1)

    def test_perform_host_group_action_validation(self):
        """Test perform_host_group_action validation requirements."""
        missing_action_result = self.module.perform_host_group_action(
            action_name=None,
            group_ids=["group-1"],
            filter="platform_name:'Windows'",
            action_parameters=None,
            disable_hostname_check=None,
            body=None,
        )
        self.assertIn("error", missing_action_result[0])

        missing_selector_result = self.module.perform_host_group_action(
            action_name="add-hosts",
            group_ids=["group-1"],
            filter=None,
            action_parameters=None,
            disable_hostname_check=None,
            body=None,
        )
        self.assertIn("error", missing_selector_result[0])

    def test_search_migrations_success(self):
        """Test searching migrations and resolving full migration details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["migration-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"migration_id": "migration-1", "name": "Tenant Migration"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_migrations(
            filter="status:'pending'",
            limit=10,
            offset=0,
            sort="created_time.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "GetMigrationIDsV1")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "GetMigrationsV1")
        self.assertEqual(
            self.mock_client.command.call_args_list[1][1]["parameters"]["ids"],
            ["migration-1"],
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["migration_id"], "migration-1")

    def test_search_host_migrations_success(self):
        """Test searching host migrations and resolving full host migration details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["host-migration-1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"host_migration_id": "host-migration-1", "hostname": "host-1"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_host_migrations(
            migration_id="migration-1",
            filter="status:'pending'",
            limit=10,
            offset=0,
            sort="hostname|asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "GetHostMigrationIDsV1")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "GetHostMigrationsV1")
        self.assertEqual(
            self.mock_client.command.call_args_list[1][1]["body"]["ids"],
            ["host-migration-1"],
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["host_migration_id"], "host-migration-1")

    def test_create_migration_success(self):
        """Test creating a migration with convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "migration-1", "name": "Tenant Migration"}]},
        }

        result = self.module.create_migration(
            target_cid="ABCDEF0123456789ABCDEF0123456789",
            name="Tenant Migration",
            device_ids=["device-1", "device-2"],
            filter=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "CreateMigrationV1",
            body={
                "target_cid": "ABCDEF0123456789ABCDEF0123456789",
                "name": "Tenant Migration",
                "device_ids": ["device-1", "device-2"],
            },
        )
        self.assertEqual(len(result), 1)

    def test_create_migration_validation(self):
        """Test create_migration validation requirements."""
        missing_target_result = self.module.create_migration(
            target_cid=None,
            name="Tenant Migration",
            device_ids=["device-1"],
            filter=None,
            body=None,
        )
        self.assertIn("error", missing_target_result[0])

        missing_selector_result = self.module.create_migration(
            target_cid="ABCDEF0123456789ABCDEF0123456789",
            name="Tenant Migration",
            device_ids=None,
            filter=None,
            body=None,
        )
        self.assertIn("error", missing_selector_result[0])

    def test_get_migration_destinations_success(self):
        """Test getting migration destinations by device IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"target_cid": "ABCDEF0123456789ABCDEF0123456789"}]},
        }

        result = self.module.get_migration_destinations(
            device_ids=["device-1"],
            filter=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "GetMigrationDestinationsV1",
            body={"device_ids": ["device-1"]},
        )
        self.assertEqual(len(result), 1)

    def test_get_migration_destinations_validation(self):
        """Test get_migration_destinations validation requirements."""
        result = self.module.get_migration_destinations(
            device_ids=None,
            filter=None,
            body=None,
        )
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_perform_migration_action_success(self):
        """Test performing a migration action."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "migration-1"}]},
        }

        result = self.module.perform_migration_action(
            action_name="start_migration",
            ids=["migration-1"],
            filter=None,
            action_parameters=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "MigrationsActionsV1",
            parameters={"action_name": "start_migration"},
            body={"ids": ["migration-1"]},
        )
        self.assertEqual(len(result), 1)

    def test_perform_host_migration_action_success(self):
        """Test performing a host migration action."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "host-migration-1"}]},
        }

        result = self.module.perform_host_migration_action(
            migration_id="migration-1",
            action_name="remove_hosts",
            ids=["host-migration-1"],
            filter=None,
            action_parameters=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "HostMigrationsActionsV1",
            parameters={"id": "migration-1", "action_name": "remove_hosts"},
            body={"ids": ["host-migration-1"]},
        )
        self.assertEqual(len(result), 1)

    def test_perform_host_migration_action_validation(self):
        """Test perform_host_migration_action validation requirements."""
        missing_migration_result = self.module.perform_host_migration_action(
            migration_id=None,
            action_name="remove_hosts",
            ids=["host-migration-1"],
            filter=None,
            action_parameters=None,
            body=None,
        )
        self.assertIn("error", missing_migration_result[0])

        missing_selector_result = self.module.perform_host_migration_action(
            migration_id="migration-1",
            action_name="remove_hosts",
            ids=None,
            filter=None,
            action_parameters=None,
            body=None,
        )
        self.assertIn("error", missing_selector_result[0])

    def test_create_migration_permission_error(self):
        """Test create_migration with 403 returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.create_migration(
            target_cid="ABCDEF0123456789ABCDEF0123456789",
            name="Tenant Migration",
            device_ids=["device-1"],
            filter=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
