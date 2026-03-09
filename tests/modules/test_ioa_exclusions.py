"""
Tests for the IOA Exclusions module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.ioa_exclusions import IOAExclusionsModule
from tests.modules.utils.test_modules import TestModules


class TestIOAExclusionsModule(TestModules):
    """Test cases for the IOA Exclusions module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IOAExclusionsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_ioa_exclusions",
            "falcon_add_ioa_exclusion",
            "falcon_update_ioa_exclusion",
            "falcon_remove_ioa_exclusions",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_ioa_exclusions_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered with expected annotations."""
        self.module.register_tools(self.mock_server)

        self.assert_tool_annotations("falcon_search_ioa_exclusions", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations(
            "falcon_add_ioa_exclusion",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=False,
                openWorldHint=True,
            ),
        )
        self.assert_tool_annotations(
            "falcon_remove_ioa_exclusions",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=True,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_search_ioa_exclusions_success(self):
        """Test searching IOA exclusions and fetching full details."""
        query_response = {
            "status_code": 200,
            "body": {"resources": ["ioa-id-1", "ioa-id-2"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "ioa-id-1", "name": "IOA Exclusion 1"},
                    {"id": "ioa-id-2", "name": "IOA Exclusion 2"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_ioa_exclusions(
            filter="name:'Test*'",
            ifn_regex=None,
            cl_regex=None,
            limit=25,
            offset=0,
            sort="last_modified.desc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        second_call = self.mock_client.command.call_args_list[1]

        self.assertEqual(first_call[0][0], "queryIOAExclusionsV1")
        self.assertEqual(first_call[1]["parameters"]["filter"], "name:'Test*'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 25)
        self.assertEqual(first_call[1]["parameters"]["offset"], 0)
        self.assertEqual(first_call[1]["parameters"]["sort"], "last_modified.desc")

        self.assertEqual(second_call[0][0], "getIOAExclusionsV1")
        self.assertEqual(second_call[1]["parameters"]["ids"], ["ioa-id-1", "ioa-id-2"])
        self.assertEqual(len(result), 2)

    def test_search_ioa_exclusions_empty_results_with_filter(self):
        """Test empty search results with filter return FQL guide context."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.search_ioa_exclusions(
            filter="name:'DoesNotExist*'",
            ifn_regex=None,
            cl_regex=None,
            limit=10,
            offset=None,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("fql_guide", result)

    def test_add_ioa_exclusion_success(self):
        """Test creating an IOA exclusion with convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"id": "ioa-id-1", "name": "New IOA Exclusion"}]},
        }

        result = self.module.add_ioa_exclusion(
            name="New IOA Exclusion",
            pattern_id="pattern-id-1",
            pattern_name=None,
            ifn_regex=".*powershell.exe",
            cl_regex=".*-enc.*",
            groups=["group-id-1"],
            description="Test exclusion",
            comment="Create test exclusion",
            detection_json=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "createIOAExclusionsV1",
            body={
                "name": "New IOA Exclusion",
                "pattern_id": "pattern-id-1",
                "ifn_regex": ".*powershell.exe",
                "cl_regex": ".*-enc.*",
                "groups": ["group-id-1"],
                "description": "Test exclusion",
                "comment": "Create test exclusion",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ioa-id-1")

    def test_add_ioa_exclusion_validation_error(self):
        """Test create validation when no body or fields are provided."""
        result = self.module.add_ioa_exclusion(
            name=None,
            pattern_id=None,
            pattern_name=None,
            ifn_regex=None,
            cl_regex=None,
            groups=None,
            description=None,
            comment=None,
            detection_json=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_ioa_exclusion_success(self):
        """Test updating an IOA exclusion with convenience fields."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "ioa-id-1", "name": "Updated Name"}]},
        }

        result = self.module.update_ioa_exclusion(
            id="ioa-id-1",
            name="Updated Name",
            pattern_id=None,
            pattern_name=None,
            ifn_regex=None,
            cl_regex=None,
            groups=None,
            description="Updated description",
            comment="Update test exclusion",
            detection_json=None,
            body=None,
        )

        self.mock_client.command.assert_called_once_with(
            "updateIOAExclusionsV1",
            body={
                "id": "ioa-id-1",
                "name": "Updated Name",
                "description": "Updated description",
                "comment": "Update test exclusion",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ioa-id-1")

    def test_update_ioa_exclusion_validation_missing_id(self):
        """Test update validation when ID is missing."""
        result = self.module.update_ioa_exclusion(
            id=None,
            name="Updated Name",
            pattern_id=None,
            pattern_name=None,
            ifn_regex=None,
            cl_regex=None,
            groups=None,
            description=None,
            comment=None,
            detection_json=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_update_ioa_exclusion_validation_no_fields(self):
        """Test update validation when only ID is provided."""
        result = self.module.update_ioa_exclusion(
            id="ioa-id-1",
            name=None,
            pattern_id=None,
            pattern_name=None,
            ifn_regex=None,
            cl_regex=None,
            groups=None,
            description=None,
            comment=None,
            detection_json=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_remove_ioa_exclusions_success(self):
        """Test deleting IOA exclusions."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "ioa-id-1"}]},
        }

        result = self.module.remove_ioa_exclusions(
            ids=["ioa-id-1"],
            comment="Cleanup test exclusion",
        )

        self.mock_client.command.assert_called_once_with(
            "deleteIOAExclusionsV1",
            parameters={
                "ids": ["ioa-id-1"],
                "comment": "Cleanup test exclusion",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "ioa-id-1")

    def test_remove_ioa_exclusions_validation(self):
        """Test delete validation when IDs are missing."""
        result = self.module.remove_ioa_exclusions(ids=None, comment=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_add_ioa_exclusion_permission_error(self):
        """Test add_ioa_exclusion with 403 permission error returns error response."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Access denied"}]},
        }

        result = self.module.add_ioa_exclusion(
            name="New IOA Exclusion",
            pattern_id="pattern-id-1",
            pattern_name=None,
            ifn_regex=".*powershell.exe",
            cl_regex=None,
            groups=None,
            description=None,
            comment=None,
            detection_json=None,
            body=None,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
