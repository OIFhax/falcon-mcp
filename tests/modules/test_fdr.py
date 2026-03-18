"""Tests for the FDR module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.fdr import FDRModule
from tests.modules.utils.test_modules import TestModules


class TestFDRModule(TestModules):
    """Test cases for the FDR module."""

    def setUp(self):
        self.setup_module(FDRModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_get_fdr_combined_schema",
            "falcon_query_fdr_event_schema_ids",
            "falcon_get_fdr_event_schema_details",
            "falcon_search_fdr_event_schemas",
            "falcon_query_fdr_field_schema_ids",
            "falcon_get_fdr_field_schema_details",
            "falcon_search_fdr_field_schemas",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_fdr_event_schema_fql_guide",
            "falcon_fdr_field_schema_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_get_fdr_combined_schema", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_search_fdr_field_schemas", READ_ONLY_ANNOTATIONS)

    def test_get_fdr_combined_schema_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"events": [], "fields": []}]},
        }

        result = self.module.get_fdr_combined_schema()

        self.mock_client.command.assert_called_once_with("fdrschema_combined_event_get")
        self.assertEqual(result[0]["events"], [])

    def test_query_fdr_event_schema_ids_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["2391", "2042"]},
        }

        result = self.module.query_fdr_event_schema_ids(
            filter="name:'EmailFileWritten'",
            limit=2,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "fdrschema_queries_event_get",
            parameters={
                "filter": "name:'EmailFileWritten'",
                "limit": 2,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(result, ["2391", "2042"])

    def test_get_fdr_event_schema_details_validation_and_success(self):
        result = self.module.get_fdr_event_schema_details(ids=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "2391", "name": "EmailFileWritten"}]},
        }

        result = self.module.get_fdr_event_schema_details(ids=["2391"])

        self.mock_client.command.assert_called_once_with(
            "fdrschema_entities_event_get",
            parameters={"ids": ["2391"]},
        )
        self.assertEqual(result[0]["name"], "EmailFileWritten")

    def test_search_fdr_event_schemas_success(self):
        query_response = {"status_code": 200, "body": {"resources": ["2391"]}}
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "2391", "name": "EmailFileWritten"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_fdr_event_schemas(
            filter="name:'EmailFileWritten'",
            limit=1,
            offset=0,
            sort="name.asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "fdrschema_queries_event_get")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "fdrschema_entities_event_get")
        self.assertEqual(result[0]["id"], "2391")

    def test_query_fdr_field_schema_ids_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["2042"]},
        }

        result = self.module.query_fdr_field_schema_ids(
            filter="name:'AzureFirewallRuleType'",
            limit=1,
            offset=0,
            sort="name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "fdrschema_queries_field_get",
            parameters={
                "filter": "name:'AzureFirewallRuleType'",
                "limit": 1,
                "offset": 0,
                "sort": "name.asc",
            },
        )
        self.assertEqual(result, ["2042"])

    def test_get_fdr_field_schema_details_validation_and_success(self):
        result = self.module.get_fdr_field_schema_details(ids=None)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

        self.mock_client.command.reset_mock()
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "2042", "name": "AzureFirewallRuleType"}]},
        }

        result = self.module.get_fdr_field_schema_details(ids=["2042"])

        self.mock_client.command.assert_called_once_with(
            "fdrschema_entities_field_get",
            parameters={"ids": ["2042"]},
        )
        self.assertEqual(result[0]["name"], "AzureFirewallRuleType")

    def test_search_fdr_field_schemas_success(self):
        query_response = {"status_code": 200, "body": {"resources": ["2042"]}}
        details_response = {
            "status_code": 200,
            "body": {"resources": [{"id": "2042", "name": "AzureFirewallRuleType"}]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_fdr_field_schemas(
            filter="name:'AzureFirewallRuleType'",
            limit=1,
            offset=0,
            sort="name.asc",
        )

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(self.mock_client.command.call_args_list[0][0][0], "fdrschema_queries_field_get")
        self.assertEqual(self.mock_client.command.call_args_list[1][0][0], "fdrschema_entities_field_get")
        self.assertEqual(result[0]["id"], "2042")


if __name__ == "__main__":
    unittest.main()
