"""Tests for the Downloads module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.downloads import DownloadsModule
from tests.modules.utils.test_modules import TestModules


class TestDownloadsModule(TestModules):
    """Test cases for the Downloads module."""

    def setUp(self):
        self.setup_module(DownloadsModule)

    def test_register_tools(self):
        expected_tools = [
            "falcon_enumerate_download_files",
            "falcon_fetch_download_file_info",
            "falcon_fetch_download_file_info_v2",
            "falcon_get_download_file_url",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        expected_resources = [
            "falcon_downloads_fql_guide",
            "falcon_downloads_usage_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_enumerate_download_files", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_download_file_url", READ_ONLY_ANNOTATIONS)

    def test_enumerate_download_files_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"file_name": "FalconSensor.exe", "file_version": "1.0.0"}]},
        }

        result = self.module.enumerate_download_files(category="sensor", platform="windows")

        self.mock_client.command.assert_called_once_with(
            "EnumerateFile",
            parameters={"platform": "windows", "category": "sensor"},
        )
        self.assertEqual(result[0]["file_name"], "FalconSensor.exe")

    def test_fetch_download_file_info_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"file_name": "FalconSensor.exe", "download_url": "https://example"}]},
        }

        result = self.module.fetch_download_file_info(
            filter="category:'sensor'+os:'Windows'",
            sort="file_version.desc",
        )

        self.mock_client.command.assert_called_once_with(
            "FetchFilesDownloadInfo",
            parameters={
                "filter": "category:'sensor'+os:'Windows'",
                "sort": "file_version.desc",
            },
        )
        self.assertEqual(result[0]["download_url"], "https://example")

    def test_fetch_download_file_info_v2_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"file_name": "CloudTool", "download_url": "https://example/v2"}]},
        }

        result = self.module.fetch_download_file_info_v2(
            filter="category:'tool'",
            limit=2,
            offset=0,
            sort="file_name.asc",
        )

        self.mock_client.command.assert_called_once_with(
            "FetchFilesDownloadInfoV2",
            parameters={
                "filter": "category:'tool'",
                "limit": 2,
                "offset": 0,
                "sort": "file_name.asc",
            },
        )
        self.assertEqual(result[0]["file_name"], "CloudTool")

    def test_get_download_file_url_validation(self):
        result = self.module.get_download_file_url(file_name=None, file_version="1.0.0")
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_download_file_url_success(self):
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": {"download_url": "https://example/direct"}},
        }

        result = self.module.get_download_file_url(
            file_name="FalconSensor.exe",
            file_version="1.0.0",
        )

        self.mock_client.command.assert_called_once_with(
            "DownloadFile",
            parameters={"file_name": "FalconSensor.exe", "file_version": "1.0.0"},
        )
        self.assertEqual(result["download_url"], "https://example/direct")


if __name__ == "__main__":
    unittest.main()
