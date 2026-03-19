"""Integration tests for the Quick Scan module."""

from typing import Any

import pytest

from falcon_mcp.modules.quick_scan import QuickScanModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestQuickScanIntegration(BaseIntegrationTest):
    """Integration tests for Quick Scan with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = QuickScanModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_query_quick_scan_ids_operation_name(self):
        result = self.call_method(
            self.module.query_quick_scan_ids,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self.assert_no_error(result, context="query_quick_scan_ids")
        self.assert_valid_list_response(result, min_length=0, context="query_quick_scan_ids")

    def test_search_quick_scans_operation_name(self):
        result = self.call_method(
            self.module.search_quick_scans,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self.assert_no_error(result, context="search_quick_scans")
        self.assert_valid_list_response(result, min_length=0, context="search_quick_scans")

    def test_scan_quick_samples_invalid_hash(self):
        result = self.call_method(
            self.module.scan_quick_samples,
            confirm_execution=True,
            samples=["0" * 64],
        )

        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required quick-scan:write scope for write validation",
                context="scan_quick_samples",
            )
        if status_code in (400, 404, 409, 422):
            return

        self.assert_no_error(result, context="scan_quick_samples_invalid_hash")
