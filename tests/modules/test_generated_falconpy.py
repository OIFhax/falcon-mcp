"""Tests for generated FalconPy all-operation modules."""

import ast
import base64
import unittest
from importlib.resources import files
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from falcon_mcp import registry
from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.falconpy_operations import WRITE_ANNOTATIONS
from falcon_mcp.modules.generated_falconpy import (
    AlertsModule,
    FalconxSandboxModule,
    GENERATED_SERVICE_COLLECTIONS,
    SampleUploadsModule,
)
from falcon_mcp.modules.falconpy_raw_gaps import (
    RawHostsModule,
    RawOauth2Module,
    RawSensorUpdatePoliciesModule,
)
from tests.modules.utils.test_modules import TestModules


class TestGeneratedFalconPyModules(TestModules):
    """Test cases for generated FalconPy modules."""

    def setUp(self):
        self.setup_module(AlertsModule)

    def test_expected_generated_service_collections_present(self):
        self.assertIn("alerts", GENERATED_SERVICE_COLLECTIONS)
        self.assertIn("sample_uploads", GENERATED_SERVICE_COLLECTIONS)
        self.assertIn("kubernetes_protection", GENERATED_SERVICE_COLLECTIONS)

    def test_all_falconpy_endpoint_operations_have_tool_specs(self):
        endpoint_operations = set()
        endpoint_dir = files("falconpy._endpoint")
        for endpoint_file in endpoint_dir.iterdir():
            name = endpoint_file.name
            if not name.startswith("_") or not name.endswith(".py") or name == "__init__.py":
                continue
            endpoint_tree = ast.parse(endpoint_file.read_text(encoding="utf-8"))
            for node in endpoint_tree.body:
                if not isinstance(node, ast.Assign):
                    continue
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.endswith("_endpoints"):
                        endpoints = ast.literal_eval(node.value)
                        endpoint_operations.update(str(endpoint[0]) for endpoint in endpoints)

        covered_operations = {
            spec["operation"]
            for module_class in registry.get_available_modules().values()
            for spec in getattr(module_class, "TOOL_SPECS", []) or []
            if isinstance(spec, dict) and "operation" in spec
        }
        modules_dir = Path(__file__).parents[2] / "falcon_mcp" / "modules"
        for module_file in modules_dir.glob("*.py"):
            source = module_file.read_text(encoding="utf-8")
            for operation in endpoint_operations:
                if repr(operation) in source or f'"{operation}"' in source:
                    covered_operations.add(operation)

        self.assertEqual(endpoint_operations - covered_operations, set())

    def test_raw_gap_modules_cover_straggler_operations(self):
        oauth_operations = {spec["operation"] for spec in RawOauth2Module.TOOL_SPECS}
        sensor_update_operations = {
            spec["operation"] for spec in RawSensorUpdatePoliciesModule.TOOL_SPECS
        }

        self.assertEqual(oauth_operations, {"oauth2AccessToken", "oauth2RevokeToken"})
        self.assertEqual(sensor_update_operations, {"incrementUninstallToken"})

    def test_register_tools(self):
        expected_tools = [f"falcon_{spec['tool_name']}" for spec in AlertsModule.TOOL_SPECS]
        self.assert_tools_registered(expected_tools)
        self.assertIn("falcon_alerts_get_queries_alerts_v2", expected_tools)

    def test_register_resources(self):
        self.assert_resources_registered(["falcon_alerts_operations_guide"])

    def test_generated_body_schema_has_array_items(self):
        server = FastMCP("schema-test")
        self.module.register_tools(server)
        tool = server._tool_manager._tools["falcon_alerts_post_entities_alerts_v2"]
        body_options = tool.parameters["properties"]["body"]["anyOf"]
        array_schema = next(option for option in body_options if option.get("type") == "array")

        self.assertIn("items", array_schema)

    def test_generated_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_alerts_get_queries_alerts_v2",
            READ_ONLY_ANNOTATIONS,
        )
        self.assert_tool_annotations(
            "falcon_alerts_patch_entities_alerts_v3",
            WRITE_ANNOTATIONS,
        )

    def test_params_operation_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["alert-id"]},
        }

        result = self.module.alerts_get_queries_alerts_v2(
            parameters={"filter": "status:'new'", "limit": 1}
        )

        self.mock_client.command.assert_called_once_with(
            "GetQueriesAlertsV2",
            parameters={"filter": "status:'new'", "limit": 1},
        )
        self.assertEqual(result, ["alert-id"])

    def test_body_required_operation_validation(self):
        result = self.module.alerts_post_entities_alerts_v2(parameters={"include_hidden": True})

        self.assertIn("error", result[0])
        self.assertEqual(self.mock_client.command.call_count, 0)

    def test_params_body_operation_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "alert-id"}]},
        }

        result = self.module.alerts_post_entities_alerts_v2(
            parameters={"include_hidden": True},
            body={"composite_ids": ["alert-id"]},
        )

        self.mock_client.command.assert_called_once_with(
            "PostEntitiesAlertsV2",
            parameters={"include_hidden": True},
            body={"composite_ids": ["alert-id"]},
        )
        self.assertEqual(result[0]["id"], "alert-id")

    def test_multipart_operation_builds_files_payload(self):
        sample_module = SampleUploadsModule(self.mock_client)
        self.mock_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"sha256": "abc"}]},
        }

        result = sample_module.sample_uploads_upload_sample_v3(
            parameters={"comment": "test"},
            file_name="sample.bin",
            file_data_base64=base64.b64encode(b"hello").decode("ascii"),
        )

        self.mock_client.command.assert_called_once()
        operation, = self.mock_client.command.call_args.args
        call_kwargs = self.mock_client.command.call_args.kwargs
        self.assertEqual(operation, "UploadSampleV3")
        self.assertEqual(call_kwargs["parameters"]["comment"], "test")
        self.assertEqual(call_kwargs["files"][0][0], "file")
        self.assertEqual(call_kwargs["files"][0][1][0], "sample.bin")
        self.assertEqual(call_kwargs["files"][0][1][1], b"hello")
        self.assertEqual(result[0]["sha256"], "abc")

    def test_binary_response_can_be_returned_as_base64(self):
        sandbox_module = FalconxSandboxModule(self.mock_client)
        self.mock_client.command.return_value = b"artifact"

        result = sandbox_module.falconx_sandbox_get_artifacts(
            parameters={"id": "artifact-id"},
            include_binary_base64=True,
            max_inline_bytes=100,
        )

        self.assertEqual(result[0]["operation"], "GetArtifacts")
        self.assertEqual(result[0]["binary_base64"], base64.b64encode(b"artifact").decode("ascii"))

    def test_raw_gap_operation_success(self):
        hosts_module = RawHostsModule(self.mock_client)
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "host-id"}]},
        }

        result = hosts_module.raw_hosts_update_device_tags(
            body={"action": "add", "ids": ["host-id"], "tags": ["FalconGroupingTags/test"]}
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateDeviceTags",
            body={"action": "add", "ids": ["host-id"], "tags": ["FalconGroupingTags/test"]},
        )
        self.assertEqual(result[0]["id"], "host-id")


if __name__ == "__main__":
    unittest.main()
