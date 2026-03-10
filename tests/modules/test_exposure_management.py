"""
Tests for the Exposure Management module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.exposure_management import ExposureManagementModule
from tests.modules.utils.test_modules import TestModules


class TestExposureManagementModule(TestModules):
    """Test cases for the Exposure Management module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(ExposureManagementModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_exposure_assets",
            "falcon_get_exposure_asset_details",
            "falcon_aggregate_exposure_assets",
            "falcon_add_exposure_assets",
            "falcon_update_exposure_assets",
            "falcon_remove_exposure_assets",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_exposure_assets_fql_guide",
            "falcon_exposure_management_safety_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_exposure_assets_success(self):
        """Test searching exposure assets and fetching full details."""
        search_response = {
            "status_code": 200,
            "body": {"resources": ["asset-id-1", "asset-id-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "asset-id-1", "asset_type": "ip"},
                    {"id": "asset-id-2", "asset_type": "dns_domain"},
                ]
            },
        }
        self.mock_client.command.side_effect = [search_response, details_response]

        result = self.module.search_exposure_assets(
            filter="asset_type:'ip'",
            limit=10,
            offset=0,
            sort="last_seen.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "query_external_assets_v2")
        self.assertEqual(first_call[1]["parameters"]["filter"], "asset_type:'ip'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 10)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "last_seen.desc")

        self.assertEqual(second_call[0][0], "get_external_assets")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["asset-id-1", "asset-id-2"])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "asset-id-1")

    def test_search_exposure_assets_empty_results_returns_fql_guide(self):
        """Test empty search results include FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_exposure_assets(filter="asset_id:'none'")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)
        self.assertIn("No results matched", result["hint"])

    def test_get_exposure_asset_details_validation_error(self):
        """Test get_exposure_asset_details requires ids."""
        result = self.module.get_exposure_asset_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_exposure_asset_details_success(self):
        """Test retrieving exposure asset details by IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "asset-id-1"}]},
        }

        result = self.module.get_exposure_asset_details(ids=["asset-id-1"])

        self.mock_client.command.assert_called_once_with(
            "get_external_assets",
            parameters={"ids": ["asset-id-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "asset-id-1")

    def test_aggregate_exposure_assets_validation_error(self):
        """Test aggregate_exposure_assets requires body."""
        result = self.module.aggregate_exposure_assets(body=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_aggregate_exposure_assets_success(self):
        """Test aggregate query execution."""
        aggregate_body = [{"field": "asset_type", "name": "asset_type", "type": "terms"}]
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"field": "asset_type", "count": 20}]},
        }

        result = self.module.aggregate_exposure_assets(body=aggregate_body)

        self.mock_client.command.assert_called_once_with(
            "aggregate_external_assets",
            body=aggregate_body,
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["field"], "asset_type")

    def test_add_exposure_assets_requires_confirmation(self):
        """Test add_exposure_assets requires explicit confirmation."""
        result = self.module.add_exposure_assets(
            confirm_execution=False,
            data=None,
            subsidiary_id="sub-1",
            assets=[{"id": "asset-id-1", "value": "10.0.0.1"}],
            asset_id=None,
            value=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_add_exposure_assets_success_with_convenience_fields(self):
        """Test add_exposure_assets builds payload from convenience inputs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.add_exposure_assets(
            confirm_execution=True,
            data=None,
            subsidiary_id="sub-1",
            assets=None,
            asset_id="asset-id-1",
            value="10.0.0.1",
        )

        self.mock_client.command.assert_called_once_with(
            "post_external_assets_inventory_v1",
            body={
                "data": [
                    {
                        "subsidiary_id": "sub-1",
                        "assets": [{"id": "asset-id-1", "value": "10.0.0.1"}],
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "submitted")

    def test_update_exposure_assets_requires_confirmation(self):
        """Test update_exposure_assets requires explicit confirmation."""
        result = self.module.update_exposure_assets(
            confirm_execution=False,
            assets=None,
            id="asset-id-1",
            cid=None,
            criticality=None,
            criticality_description=None,
            action=None,
            assigned_to=None,
            description=None,
            status=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_exposure_assets_success_with_single_asset_patch(self):
        """Test update_exposure_assets builds patch payload from convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.update_exposure_assets(
            confirm_execution=True,
            assets=None,
            id="asset-id-1",
            cid=None,
            criticality="high",
            criticality_description="Production edge",
            action="investigate",
            assigned_to="analyst@example.com",
            description="Escalated",
            status="in_progress",
        )

        self.mock_client.command.assert_called_once_with(
            "patch_external_assets",
            body={
                "assets": [
                    {
                        "id": "asset-id-1",
                        "criticality": "high",
                        "criticality_description": "Production edge",
                        "triage": {
                            "action": "investigate",
                            "assigned_to": "analyst@example.com",
                            "description": "Escalated",
                            "status": "in_progress",
                        },
                    }
                ]
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "submitted")

    def test_remove_exposure_assets_requires_confirmation(self):
        """Test remove_exposure_assets requires explicit confirmation."""
        result = self.module.remove_exposure_assets(
            confirm_execution=False,
            ids=["asset-id-1"],
            description="cleanup",
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_remove_exposure_assets_success(self):
        """Test remove_exposure_assets sends expected query/body params."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.remove_exposure_assets(
            confirm_execution=True,
            ids=["asset-id-1", "asset-id-2"],
            description="cleanup test assets",
        )

        self.mock_client.command.assert_called_once_with(
            "delete_external_assets",
            parameters={"ids": ["asset-id-1", "asset-id-2"]},
            body={"description": "cleanup test assets"},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "submitted")

    def test_search_exposure_assets_has_read_only_annotations(self):
        """Test that search_exposure_assets is registered as read-only."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_exposure_assets", READ_ONLY_ANNOTATIONS)

    def test_remove_exposure_assets_has_destructive_annotations(self):
        """Test that remove_exposure_assets has destructive annotations."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_remove_exposure_assets",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )


if __name__ == "__main__":
    unittest.main()

