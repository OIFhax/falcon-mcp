"""Tests for the Deployments module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.deployments import DeploymentsModule
from tests.modules.utils.test_modules import TestModules


class TestDeploymentsModule(TestModules):
    """Test cases for the Deployments module."""

    def setUp(self):
        self.setup_module(DeploymentsModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_search_deployment_releases",
            "falcon_get_deployment_details",
            "falcon_search_release_notes",
            "falcon_query_release_note_ids",
            "falcon_get_release_notes_v1",
            "falcon_get_release_notes_v2",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        self.assert_resources_registered(["falcon_deployments_fql_guide"])

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_deployment_releases", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_release_notes_v2", READ_ONLY_ANNOTATIONS)

    def test_query_release_note_ids_empty_filter_returns_guide(self):
        self.mock_client.command.return_value = {"status_code": 200, "body": {"resources": []}}

        result = self.module.query_release_note_ids(
            filter="title:'not-real'",
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("fql_guide", result)

    def test_get_deployment_details_validation(self):
        result = self.module.get_deployment_details(ids=None)
        self.assertIn("error", result[0])

    def test_get_release_notes_v2_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "note-1"}]},
        }

        result = self.module.get_release_notes_v2(ids=["note-1"])

        self.mock_client.command.assert_called_once_with(
            "GetEntityIDsByQueryPOSTV2",
            body={"ids": ["note-1"]},
        )
        self.assertEqual(result[0]["id"], "note-1")


if __name__ == "__main__":
    unittest.main()
