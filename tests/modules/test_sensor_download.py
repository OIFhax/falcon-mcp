"""
Tests for the Sensor Download module.
"""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.sensor_download import SensorDownloadModule
from tests.modules.utils.test_modules import TestModules


class TestSensorDownloadModule(TestModules):
    """Test cases for the Sensor Download module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(SensorDownloadModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_sensor_installer_ids",
            "falcon_search_sensor_installer_ids_v2",
            "falcon_get_sensor_installer_details",
            "falcon_get_sensor_installer_details_v2",
            "falcon_search_sensor_installers_combined",
            "falcon_search_sensor_installers_combined_v2",
            "falcon_get_sensor_installer_ccid",
            "falcon_download_sensor_installer",
            "falcon_download_sensor_installer_v2",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_sensor_installers_fql_guide",
            "falcon_sensor_installer_download_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_sensor_installer_ids_success(self):
        """Test v1 installer ID query operation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["sha-1", "sha-2"]},
        }

        result = self.module.search_sensor_installer_ids(
            filter="platform:'windows'",
            limit=10,
            offset=0,
            sort="release_date.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "GetSensorInstallersByQuery",
            parameters={
                "filter": "platform:'windows'",
                "limit": 10,
                "offset": 0,
                "sort": "release_date.desc",
            },
        )
        self.assertEqual(result, ["sha-1", "sha-2"])

    def test_search_sensor_installer_ids_v2_error_returns_fql_guide(self):
        """Test v2 ID query errors return FQL helper response."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"code": 400, "message": "invalid filter"}]},
        }

        result = self.module.search_sensor_installer_ids_v2(
            filter="bad-filter",
            limit=10,
            offset=0,
            sort=None,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("fql_guide", result)
        self.assertEqual(result["filter_used"], "bad-filter")

    def test_get_sensor_installer_details_validation_error(self):
        """Test installer detail lookup requires IDs."""
        result = self.module.get_sensor_installer_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_sensor_installer_details_v2_success(self):
        """Test v2 installer detail retrieval."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "sha-1", "architectures": ["x86_64"]}]},
        }

        result = self.module.get_sensor_installer_details_v2(ids=["sha-1"])

        self.mock_client.command.assert_called_once_with(
            "GetSensorInstallersEntitiesV2",
            parameters={"ids": ["sha-1"]},
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sha256"], "sha-1")

    def test_search_sensor_installers_combined_success(self):
        """Test combined installer search v1."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "sha-1", "platform": "windows"}]},
        }

        result = self.module.search_sensor_installers_combined(
            filter="platform:'windows'",
            limit=1,
            offset=0,
            sort="release_date.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "GetCombinedSensorInstallersByQuery",
            parameters={
                "filter": "platform:'windows'",
                "limit": 1,
                "offset": 0,
                "sort": "release_date.desc",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["platform"], "windows")

    def test_search_sensor_installers_combined_v2_success(self):
        """Test combined installer search v2."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"sha256": "sha-1", "architectures": ["x86_64"]}]},
        }

        result = self.module.search_sensor_installers_combined_v2(
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self.mock_client.command.assert_called_once_with(
            "GetCombinedSensorInstallersByQueryV2",
            parameters={
                "limit": 1,
                "offset": 0,
            },
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["sha256"], "sha-1")

    def test_get_sensor_installer_ccid_success(self):
        """Test CCID query operation."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["ABCD1234-01"]},
        }

        result = self.module.get_sensor_installer_ccid()

        self.mock_client.command.assert_called_once_with("GetSensorInstallersCCIDByQuery")
        self.assertEqual(result, ["ABCD1234-01"])

    def test_download_sensor_installer_validation_error(self):
        """Test installer download requires ID."""
        result = self.module.download_sensor_installer(id=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_download_sensor_installer_metadata_only(self):
        """Test binary download returns metadata-only by default."""
        self.mock_client.command.return_value = b"installer-bytes"

        result = self.module.download_sensor_installer(
            id="sha-1",
            include_binary_base64=False,
            max_inline_bytes=5_000_000,
        )

        self.mock_client.command.assert_called_once_with(
            "DownloadSensorInstallerById",
            parameters={"id": "sha-1"},
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["operation"], "DownloadSensorInstallerById")
        self.assertEqual(result["id"], "sha-1")
        self.assertIn("size_bytes", result)
        self.assertIn("sha256", result)
        self.assertIn("hint", result)
        self.assertNotIn("binary_base64", result)

    def test_download_sensor_installer_inline_base64(self):
        """Test binary download inline base64 mode."""
        self.mock_client.command.return_value = b"abc"

        result = self.module.download_sensor_installer(
            id="sha-1",
            include_binary_base64=True,
            max_inline_bytes=100,
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["binary_base64"], "YWJj")
        self.assertNotIn("hint", result)

    def test_download_sensor_installer_inline_too_large(self):
        """Test inline base64 mode enforces max bytes."""
        self.mock_client.command.return_value = b"abcdef"

        result = self.module.download_sensor_installer(
            id="sha-1",
            include_binary_base64=True,
            max_inline_bytes=2,
        )

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.assertIn("max_inline_bytes", result[0].get("details", {}))

    def test_download_sensor_installer_v2_dict_error_response(self):
        """Test v2 download propagates API errors for dict responses."""
        self.mock_client.command.return_value = {
            "status_code": 404,
            "body": {"errors": [{"code": 404, "message": "not found"}]},
        }

        result = self.module.download_sensor_installer_v2(
            id="missing-sha",
            include_binary_base64=False,
            max_inline_bytes=5_000_000,
        )

        self.mock_client.command.assert_called_once_with(
            "DownloadSensorInstallerByIdV2",
            parameters={"id": "missing-sha"},
        )
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])

    def test_search_sensor_installer_ids_has_read_only_annotations(self):
        """Test that search_sensor_installer_ids is read-only annotated."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_search_sensor_installer_ids",
            READ_ONLY_ANNOTATIONS,
        )


if __name__ == "__main__":
    unittest.main()
