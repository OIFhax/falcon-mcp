"""Integration tests for the Exposure Management module."""

from typing import Any

import pytest

from falcon_mcp.modules.exposure_management import ExposureManagementModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestExposureManagementIntegration(BaseIntegrationTest):
    """Integration tests for Exposure Management module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the Exposure Management module with a real client."""
        self.module = ExposureManagementModule(falcon_client)

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

    def _skip_if_scope_or_service_missing(self, result: Any, context: str) -> None:
        """Skip when Exposure Management scope/service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Exposure Management integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Exposure Management service unavailable for this tenant/region",
                context=context,
            )

    @staticmethod
    def _extract_asset_id(asset_record: dict[str, Any]) -> str | None:
        """Extract asset ID from an exposure asset record."""
        for key in ["id", "asset_id"]:
            value = asset_record.get(key)
            if isinstance(value, str) and value:
                return value
        return None

    def test_search_exposure_assets_operation_name(self):
        """Validate operation names for exposure asset search flow."""
        result = self.call_method(
            self.module.search_exposure_assets,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_exposure_assets")

        self.assert_no_error(result, context="search_exposure_assets")
        self.assert_valid_list_response(result, min_length=0, context="search_exposure_assets")

    def test_search_exposure_assets_with_filter(self):
        """Validate filtered exposure asset search call."""
        result = self.call_method(
            self.module.search_exposure_assets,
            filter="asset_type:'ip'",
            limit=5,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(result, "search_exposure_assets with filter")

        self.assert_no_error(result, context="search_exposure_assets with filter")
        self.assert_valid_list_response(
            result,
            min_length=0,
            context="search_exposure_assets with filter",
        )

    def test_get_exposure_asset_details_with_existing_id(self):
        """Validate detail retrieval using an ID from search results."""
        search_result = self.call_method(
            self.module.search_exposure_assets,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )
        self._skip_if_scope_or_service_missing(search_result, "get_exposure_asset_details setup")
        self.assert_no_error(search_result, context="get_exposure_asset_details setup")

        if not search_result:
            self.skip_with_warning(
                "No exposure assets available to validate get_exposure_asset_details",
                context="test_get_exposure_asset_details_with_existing_id",
            )

        asset_id = self._extract_asset_id(search_result[0])
        if not asset_id:
            self.skip_with_warning(
                "Could not extract asset ID from search_exposure_assets results",
                context="test_get_exposure_asset_details_with_existing_id",
            )

        result = self.call_method(
            self.module.get_exposure_asset_details,
            ids=[asset_id],
        )
        self._skip_if_scope_or_service_missing(result, "get_exposure_asset_details")

        self.assert_no_error(result, context="get_exposure_asset_details")
        self.assert_valid_list_response(result, min_length=0, context="get_exposure_asset_details")

