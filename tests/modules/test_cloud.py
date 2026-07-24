"""Tests for the Cloud module."""

import unittest

from falcon_mcp.modules.cloud import CloudModule
from tests.modules.utils.test_modules import TestModules


class TestCloudModule(TestModules):
    """Test cases for the Cloud module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(CloudModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_kubernetes_containers",
            "falcon_count_kubernetes_containers",
            "falcon_search_images_vulnerabilities",
            "falcon_get_image_vulnerability_details",
            "falcon_get_image_vulnerability_info",
            "falcon_count_image_vulnerabilities",
            "falcon_count_image_vulnerabilities_by_severity",
            "falcon_count_image_vulnerabilities_by_cps_rating",
            "falcon_count_image_vulnerabilities_by_cvss_score",
            "falcon_count_image_vulnerabilities_by_actively_exploited",
            "falcon_get_top_vulnerabilities_by_image_count",
            "falcon_get_recent_vulnerabilities_by_publication_date",
            "falcon_search_cspm_assets",
            "falcon_search_iom_findings",
            "falcon_search_cspm_suppression_rules",
            "falcon_create_cspm_suppression_rule",
            "falcon_delete_cspm_suppression_rules",
            "falcon_search_cloud_risks",
            "falcon_search_cloud_groups",
            "falcon_get_cloud_groups",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_kubernetes_containers_fql_filter_guide",
            "falcon_images_vulnerabilities_fql_filter_guide",
            "falcon_search_cspm_assets_fql_guide",
            "falcon_search_iom_findings_fql_guide",
            "falcon_search_cloud_risks_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_kubernetes_containers(self):
        """Test searching for Kubernetes containers."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "meta": {"pagination": {"offset": 0, "limit": 1, "total": 2}},
                "resources": ["container_1", "container_2"],
            },
        }

        result = self.module.search_kubernetes_containers(filter="cloud_name:'AWS'", limit=1)

        self.mock_client.command.assert_called_once_with(
            "ReadContainerCombined",
            parameters={"filter": "cloud_name:'AWS'", "limit": 1},
        )
        self.assertEqual(result["results"], ["container_1", "container_2"])
        self.assertEqual(result["pagination"]["total"], 2)

    def test_count_kubernetes_containers(self):
        """Test counting Kubernetes containers."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"count": 500}]},
        }

        result = self.module.count_kubernetes_containers(filter="cloud_region:'us-1'")

        self.mock_client.command.assert_called_once_with(
            "ReadContainerCount",
            parameters={"filter": "cloud_region:'us-1'"},
        )
        self.assertEqual(result, 500)

    def test_search_images_vulnerabilities(self):
        """Test searching image vulnerabilities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cve_id": "CVE-2025-1111"}]},
        }

        result = self.module.search_images_vulnerabilities(filter="cvss_score:>5", limit=1)

        self.mock_client.command.assert_called_once_with(
            "ReadCombinedVulnerabilities",
            parameters={"filter": "cvss_score:>5", "limit": 1},
        )
        self.assertEqual(result["results"], [{"cve_id": "CVE-2025-1111"}])

    def test_get_image_vulnerability_details_requires_image_id(self):
        """Test details tool requires image_id."""
        result = self.module.get_image_vulnerability_details(image_id=None)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_image_vulnerability_details_success(self):
        """Test vulnerability detail retrieval by image ID."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cve_id": "CVE-2025-1111"}]},
        }

        result = self.module.get_image_vulnerability_details(
            image_id="image-uuid-1",
            filter="severity:'high'",
            limit=50,
            offset=0,
        )

        self.mock_client.command.assert_called_once_with(
            "ReadCombinedVulnerabilitiesDetails",
            parameters={
                "id": "image-uuid-1",
                "filter": "severity:'high'",
                "limit": 50,
                "offset": 0,
            },
        )
        self.assertEqual(result, [{"cve_id": "CVE-2025-1111"}])

    def test_get_image_vulnerability_info_requires_cve_id(self):
        """Test vulnerability info tool requires cve_id."""
        result = self.module.get_image_vulnerability_info(cve_id=None)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_image_vulnerability_info_success(self):
        """Test vulnerability info retrieval by CVE."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"package": "openssl"}]},
        }

        result = self.module.get_image_vulnerability_info(cve_id="CVE-2025-1111", limit=10)

        self.mock_client.command.assert_called_once_with(
            "ReadCombinedVulnerabilitiesInfo",
            parameters={"cve_id": "CVE-2025-1111", "limit": 10},
        )
        self.assertEqual(result, [{"package": "openssl"}])

    def test_count_image_vulnerabilities_by_severity(self):
        """Test severity aggregation operation wiring."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"severity": "critical", "count": 2}]},
        }

        result = self.module.count_image_vulnerabilities_by_severity(
            filter="repository:'app'",
            limit=5,
            offset=0,
        )

        self.mock_client.command.assert_called_once_with(
            "ReadVulnerabilityCountBySeverity",
            parameters={"filter": "repository:'app'", "limit": 5, "offset": 0},
        )
        self.assertEqual(result, [{"severity": "critical", "count": 2}])

    def test_count_image_vulnerabilities_by_cps_rating(self):
        """Test CPS rating aggregation operation wiring."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cps_rating": "A", "count": 4}]},
        }

        result = self.module.count_image_vulnerabilities_by_cps_rating(limit=10)

        self.mock_client.command.assert_called_once_with(
            "ReadVulnerabilityCountByCPSRating",
            parameters={"limit": 10},
        )
        self.assertEqual(result, [{"cps_rating": "A", "count": 4}])

    def test_count_image_vulnerabilities_by_cvss_score(self):
        """Test CVSS score aggregation operation wiring."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cvss_score": "9+", "count": 1}]},
        }

        result = self.module.count_image_vulnerabilities_by_cvss_score(limit=10)

        self.mock_client.command.assert_called_once_with(
            "ReadVulnerabilityCountByCVSSScore",
            parameters={"limit": 10},
        )
        self.assertEqual(result, [{"cvss_score": "9+", "count": 1}])

    def test_count_image_vulnerabilities_by_actively_exploited(self):
        """Test actively exploited aggregation operation wiring."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"actively_exploited": True, "count": 3}]},
        }

        result = self.module.count_image_vulnerabilities_by_actively_exploited(limit=10)

        self.mock_client.command.assert_called_once_with(
            "ReadVulnerabilityCountByActivelyExploited",
            parameters={"limit": 10},
        )
        self.assertEqual(result, [{"actively_exploited": True, "count": 3}])

    def test_count_image_vulnerabilities(self):
        """Test aggregate vulnerability count operation wiring."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"count": 42}]},
        }

        result = self.module.count_image_vulnerabilities(filter="severity:'high'")

        self.mock_client.command.assert_called_once_with(
            "ReadVulnerabilityCount",
            parameters={"filter": "severity:'high'", "limit": 100},
        )
        self.assertEqual(result, [{"count": 42}])

    def test_get_top_vulnerabilities_by_image_count(self):
        """Test top vulnerabilities by image count operation wiring."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cve_id": "CVE-2025-1111", "images_impacted": 7}]},
        }

        result = self.module.get_top_vulnerabilities_by_image_count(limit=5)

        self.mock_client.command.assert_called_once_with(
            "ReadVulnerabilitiesByImageCount",
            parameters={"limit": 5},
        )
        self.assertEqual(result[0]["cve_id"], "CVE-2025-1111")

    def test_get_recent_vulnerabilities_by_publication_date(self):
        """Test recent vulnerabilities by publication date operation wiring."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"cve_id": "CVE-2025-2222"}]},
        }

        result = self.module.get_recent_vulnerabilities_by_publication_date(limit=5)

        self.mock_client.command.assert_called_once_with(
            "ReadVulnerabilitiesPublicationDate",
            parameters={"limit": 5},
        )
        self.assertEqual(result[0]["cve_id"], "CVE-2025-2222")

    def test_cloud_operation_error_response(self):
        """Test API errors are returned in standardized format."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }

        result = self.module.search_kubernetes_containers(filter="bad filter")

        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("details", result[0])

    def test_search_cloud_risks_success(self):
        """Test search_cloud_risks returns entities on success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "risk-1", "severity": "critical", "status": "open"},
                    {"id": "risk-2", "severity": "high", "status": "open"},
                ]
            },
        }
        result = self.module.search_cloud_risks(
            filter="severity:'critical'", limit=10, offset=None, sort=None
        )
        self.assertEqual(self.mock_client.command.call_args[0][0], "combined_cloud_risks")
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "risk-1")

    def test_search_cloud_risks_empty(self):
        """Test search_cloud_risks returns empty list when no results."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        result = self.module.search_cloud_risks(filter=None, limit=100, offset=None, sort=None)
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["results"]), 0)

    def test_search_cloud_risks_api_error(self):
        """Test search_cloud_risks returns error dict on API failure."""
        self.mock_client.command.return_value = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        result = self.module.search_cloud_risks(filter="invalid!", limit=10, offset=None, sort=None)
        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])

    def test_search_cloud_risks_passes_all_params(self):
        """Test search_cloud_risks passes filter, sort, limit, offset to API."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.search_cloud_risks(
            filter="cloud_provider:'aws'",
            limit=50,
            offset=100,
            sort="severity|desc",
        )
        call_params = self.mock_client.command.call_args[1]["parameters"]
        self.assertEqual(call_params["filter"], "cloud_provider:'aws'")
        self.assertEqual(call_params["limit"], 50)
        self.assertEqual(call_params["offset"], 100)
        self.assertEqual(call_params["sort"], "severity|desc")

    def test_search_cloud_groups_success(self):
        """Test search_cloud_groups returns entities on success."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "grp-1", "name": "prod-group", "environment": "production"},
                ]
            },
        }
        result = self.module.search_cloud_groups(filter=None, limit=100, offset=None, sort=None)
        self.mock_client.command.assert_called_once_with(
            "ListCloudGroupsExternal",
            parameters={"limit": 100},
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"][0]["id"], "grp-1")

    def test_search_cloud_groups_with_filter(self):
        """Test search_cloud_groups passes filter param."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.search_cloud_groups(
            filter="environment:'production'", limit=10, offset=None, sort=None
        )
        call_params = self.mock_client.command.call_args[1]["parameters"]
        self.assertEqual(call_params["filter"], "environment:'production'")

    def test_search_cloud_groups_api_error(self):
        """Test search_cloud_groups returns error dict on API failure."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "access denied"}]},
        }
        result = self.module.search_cloud_groups(filter=None, limit=100, offset=None, sort=None)
        self.assertIsInstance(result, (dict, list))
        if isinstance(result, list):
            self.assertIn("error", result[0])
        else:
            self.assertIn("error", result)

    def test_get_cloud_groups_success(self):
        """Test get_cloud_groups fetches entities by ID."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "grp-1", "name": "prod-group"},
                ]
            },
        }
        result = self.module.get_cloud_groups(ids=["grp-1"])
        self.mock_client.command.assert_called_once_with(
            "ListCloudGroupsByIDExternal",
            parameters={"ids": ["grp-1"]},
        )
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], "grp-1")

    def test_get_cloud_groups_multiple_ids(self):
        """Test get_cloud_groups accepts multiple IDs."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.module.get_cloud_groups(ids=["grp-1", "grp-2"])
        call_params = self.mock_client.command.call_args[1]["parameters"]
        self.assertEqual(call_params["ids"], ["grp-1", "grp-2"])


if __name__ == "__main__":
    unittest.main()
