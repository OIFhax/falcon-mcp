"""Integration tests for the Sensor Download module."""

from typing import Any

import pytest

from falcon_mcp.modules.sensor_download import SensorDownloadModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestSensorDownloadIntegration(BaseIntegrationTest):
    """Integration tests for Sensor Download module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Sensor Download module with a real client."""
        self.module = SensorDownloadModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        """Extract status code from standardized error responses."""
        if isinstance(result, dict):
            details = result.get("details", {})
            if isinstance(details, dict):
                return details.get("status_code")
            nested_results = result.get("results")
            if isinstance(nested_results, list) and nested_results:
                first = nested_results[0]
                if isinstance(first, dict):
                    nested_details = first.get("details", {})
                    if isinstance(nested_details, dict):
                        return nested_details.get("status_code")

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")

        return None

    def _skip_if_scope_missing(self, result: Any, context: str) -> None:
        """Skip when Sensor Download scope is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Sensor Download integration test",
                context=context,
            )

    @staticmethod
    def _extract_sha(value: Any) -> str | None:
        """Extract installer SHA256 from a response item."""
        if isinstance(value, str) and value:
            return value
        if isinstance(value, dict):
            for key in ["sha256", "id"]:
                candidate = value.get(key)
                if isinstance(candidate, str) and candidate:
                    return candidate
        return None

    def test_get_sensor_installer_ccid_operation_name(self):
        """Validate CCID query operation name."""
        result = self.call_method(self.module.get_sensor_installer_ccid)
        self._skip_if_scope_missing(result, "get_sensor_installer_ccid")

        self.assert_no_error(result, context="get_sensor_installer_ccid")
        self.assert_valid_list_response(result, min_length=0, context="get_sensor_installer_ccid")

    def test_search_sensor_installer_ids_v2_operation_name(self):
        """Validate installer ID query operation name (v2)."""
        result = self.call_method(
            self.module.search_sensor_installer_ids_v2,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "search_sensor_installer_ids_v2")

        self.assert_no_error(result, context="search_sensor_installer_ids_v2")
        self.assert_valid_list_response(result, min_length=0, context="search_sensor_installer_ids_v2")

    def test_search_sensor_installers_combined_v2_operation_name(self):
        """Validate combined installer search operation name (v2)."""
        result = self.call_method(
            self.module.search_sensor_installers_combined_v2,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "search_sensor_installers_combined_v2")

        self.assert_no_error(result, context="search_sensor_installers_combined_v2")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_sensor_installers_combined_v2",
        )

    def test_get_sensor_installer_details_v2_round_trip(self):
        """Validate detail retrieval from discovered installer SHA256."""
        search_result = self.call_method(
            self.module.search_sensor_installer_ids_v2,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(search_result, "get_sensor_installer_details_v2 setup")
        self.assert_no_error(search_result, context="get_sensor_installer_details_v2 setup")

        if not search_result:
            self.skip_with_warning(
                "No sensor installer IDs available to validate detail retrieval",
                context="test_get_sensor_installer_details_v2_round_trip",
            )

        installer_sha = self._extract_sha(search_result[0])
        if not installer_sha:
            self.skip_with_warning(
                "Could not extract installer SHA256 from search results",
                context="test_get_sensor_installer_details_v2_round_trip",
            )

        result = self.call_method(
            self.module.get_sensor_installer_details_v2,
            ids=[installer_sha],
        )
        self._skip_if_scope_missing(result, "get_sensor_installer_details_v2")

        self.assert_no_error(result, context="get_sensor_installer_details_v2")
        self.assert_valid_list_response(result, min_length=1, context="get_sensor_installer_details_v2")

    def test_search_sensor_installer_ids_v1_operation_name(self):
        """Validate installer ID query operation name (v1)."""
        result = self.call_method(
            self.module.search_sensor_installer_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_missing(result, "search_sensor_installer_ids")

        self.assert_no_error(result, context="search_sensor_installer_ids")
        self.assert_valid_list_response(result, min_length=0, context="search_sensor_installer_ids")

    def test_download_sensor_installer_v2_invalid_id_expected_error(self):
        """Validate download endpoint invocation with an invalid SHA256 ID."""
        result = self.call_method(
            self.module.download_sensor_installer_v2,
            id="0" * 64,
            include_binary_base64=False,
            max_inline_bytes=5_000_000,
        )

        self._skip_if_scope_missing(result, "download_sensor_installer_v2")

        if isinstance(result, list) and result and isinstance(result[0], dict):
            status_code = result[0].get("details", {}).get("status_code")
            assert status_code in (400, 404), (
                "Expected invalid installer ID to return 400/404, got "
                f"{status_code} with response {result}"
            )
            return

        if isinstance(result, dict):
            # If the API unexpectedly resolves this installer, the wrapper should
            # still return structured metadata.
            assert "operation" in result
            assert "id" in result
            return

        assert False, f"Unexpected download response shape: {result}"
