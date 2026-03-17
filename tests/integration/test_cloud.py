"""Integration tests for the Cloud module."""

from typing import Any

import pytest

from falcon_mcp.modules.cloud import CloudModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestCloudIntegration(BaseIntegrationTest):
    """Integration tests for Cloud module with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        """Set up the cloud module with a real client."""
        self.module = CloudModule(falcon_client)

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
        """Skip when container/cloud scope or service is unavailable."""
        status_code = self._extract_status_code(result)
        if status_code == 403:
            self.skip_with_warning(
                "Missing required API scope for Cloud integration test",
                context=context,
            )
        if status_code == 404:
            self.skip_with_warning(
                "Cloud/Container service unavailable for this tenant/region",
                context=context,
            )

    def test_search_kubernetes_containers_operation_name(self):
        """Validate ReadContainerCombined operation wiring."""
        result = self.call_method(self.module.search_kubernetes_containers, limit=3)
        self._skip_if_scope_or_service_missing(result, "search_kubernetes_containers")

        self.assert_no_error(result, context="search_kubernetes_containers")
        self.assert_valid_list_response(result, min_length=0, context="search_kubernetes_containers")

    def test_count_kubernetes_containers_operation_name(self):
        """Validate ReadContainerCount operation wiring."""
        result = self.call_method(
            self.module.count_kubernetes_containers,
            filter="running_status:true",
        )
        self._skip_if_scope_or_service_missing(result, "count_kubernetes_containers")

        self.assert_no_error(result, context="count_kubernetes_containers")
        self.assert_valid_list_response(result, min_length=0, context="count_kubernetes_containers")

    def test_search_images_vulnerabilities_operation_name(self):
        """Validate ReadCombinedVulnerabilities operation wiring."""
        result = self.call_method(self.module.search_images_vulnerabilities, limit=3)
        self._skip_if_scope_or_service_missing(result, "search_images_vulnerabilities")

        self.assert_no_error(result, context="search_images_vulnerabilities")
        self.assert_valid_list_response(result, min_length=0, context="search_images_vulnerabilities")

    def test_vulnerability_count_operations(self):
        """Validate vulnerability aggregation operation names."""
        operations = [
            ("count_image_vulnerabilities", self.module.count_image_vulnerabilities),
            ("count_by_severity", self.module.count_image_vulnerabilities_by_severity),
            ("count_by_cps", self.module.count_image_vulnerabilities_by_cps_rating),
            ("count_by_cvss", self.module.count_image_vulnerabilities_by_cvss_score),
            (
                "count_by_actively_exploited",
                self.module.count_image_vulnerabilities_by_actively_exploited,
            ),
        ]

        for context, method in operations:
            result = self.call_method(method, limit=5)
            self._skip_if_scope_or_service_missing(result, context)
            self.assert_no_error(result, context=context)
            self.assert_valid_list_response(result, min_length=0, context=context)

    def test_top_and_recent_vulnerability_views(self):
        """Validate ReadVulnerabilitiesByImageCount and ReadVulnerabilitiesPublicationDate wiring."""
        top_result = self.call_method(self.module.get_top_vulnerabilities_by_image_count, limit=3)
        self._skip_if_scope_or_service_missing(top_result, "get_top_vulnerabilities_by_image_count")
        self.assert_no_error(top_result, context="get_top_vulnerabilities_by_image_count")
        self.assert_valid_list_response(
            top_result,
            min_length=0,
            context="get_top_vulnerabilities_by_image_count",
        )

        recent_result = self.call_method(
            self.module.get_recent_vulnerabilities_by_publication_date,
            limit=3,
        )
        self._skip_if_scope_or_service_missing(
            recent_result,
            "get_recent_vulnerabilities_by_publication_date",
        )
        self.assert_no_error(recent_result, context="get_recent_vulnerabilities_by_publication_date")
        self.assert_valid_list_response(
            recent_result,
            min_length=0,
            context="get_recent_vulnerabilities_by_publication_date",
        )

    def test_vulnerability_details_and_info_when_data_available(self):
        """Validate detail/info operations when required IDs are discoverable."""
        search_result = self.call_method(self.module.search_images_vulnerabilities, limit=5)
        self._skip_if_scope_or_service_missing(search_result, "vulnerability details setup")
        self.assert_no_error(search_result, context="vulnerability details setup")

        if not search_result:
            self.skip_with_warning(
                "No vulnerability records available to validate details/info operations",
                context="test_vulnerability_details_and_info_when_data_available",
            )

        first_item = search_result[0]
        image_id = first_item.get("image_id")
        cve_id = first_item.get("cve_id")

        if image_id:
            details_result = self.call_method(
                self.module.get_image_vulnerability_details,
                image_id=image_id,
                limit=5,
            )
            self._skip_if_scope_or_service_missing(details_result, "get_image_vulnerability_details")
            self.assert_no_error(details_result, context="get_image_vulnerability_details")
            self.assert_valid_list_response(
                details_result,
                min_length=0,
                context="get_image_vulnerability_details",
            )

        if cve_id:
            info_result = self.call_method(
                self.module.get_image_vulnerability_info,
                cve_id=cve_id,
                limit=5,
            )
            self._skip_if_scope_or_service_missing(info_result, "get_image_vulnerability_info")
            self.assert_no_error(info_result, context="get_image_vulnerability_info")
            self.assert_valid_list_response(
                info_result,
                min_length=0,
                context="get_image_vulnerability_info",
            )
