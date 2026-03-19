"""Integration tests for the Downloads module."""

import pytest

from falcon_mcp.modules.downloads import DownloadsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDownloadsIntegration(BaseIntegrationTest):
    """Integration tests for Downloads module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Downloads module with a real client."""
        self.module = DownloadsModule(falcon_client)

    def test_enumerate_download_files_operation_name(self):
        """Validate EnumerateFile operation name."""
        result = self.call_method(
            self.module.enumerate_download_files,
            category="sensor",
            platform="windows",
        )

        self.assert_no_error(result, context="enumerate_download_files operation name")
        self.assert_valid_list_response(result, min_length=0, context="enumerate_download_files")

    def test_fetch_download_file_info_v2_operation_name(self):
        """Validate FetchFilesDownloadInfoV2 operation name."""
        result = self.call_method(
            self.module.fetch_download_file_info_v2,
            filter="category:'sensor'+os:'Windows'",
            limit=2,
            offset=0,
            sort="file_version.desc",
        )

        self.assert_no_error(result, context="fetch_download_file_info_v2 operation name")
        if isinstance(result, list):
            self.assert_valid_list_response(result, min_length=0, context="fetch_download_file_info_v2")

    def test_get_download_file_url_operation_name(self):
        """Validate DownloadFile operation name using a known not-found response."""
        result = self.call_method(
            self.module.get_download_file_url,
            file_name="FalconSensor_Windows.exe",
            file_version="0.0.0",
        )

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict) and "error" in first:
                details = first.get("details", {})
                if details.get("status_code") == 404:
                    body = details.get("body", {})
                    errors = body.get("errors", []) if isinstance(body, dict) else []
                    if errors and "unable to fetch the download url" in errors[0].get("message", "").lower():
                        return

        self.assert_no_error(result, context="get_download_file_url operation name")
