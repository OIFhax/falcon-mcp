"""Tests for the Intel module."""

import unittest

from falcon_mcp.modules.base import READ_ONLY_ANNOTATIONS
from falcon_mcp.modules.intel import IntelModule
from tests.modules.utils.test_modules import TestModules


class TestIntelModule(TestModules):
    """Test cases for the Intel module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IntelModule)

    def test_register_tools(self):
        """Test registering all intel tools with the server."""
        expected_tools = [
            "falcon_search_actors",
            "falcon_query_actor_ids",
            "falcon_get_actor_details",
            "falcon_search_indicators",
            "falcon_query_indicator_ids",
            "falcon_get_indicator_details",
            "falcon_search_reports",
            "falcon_query_report_ids",
            "falcon_get_report_details",
            "falcon_download_report_pdf",
            "falcon_query_rule_ids",
            "falcon_get_rule_details",
            "falcon_download_rule_file",
            "falcon_download_latest_rule_file",
            "falcon_query_malware_ids",
            "falcon_search_malware",
            "falcon_get_malware_details",
            "falcon_get_malware_mitre_report",
            "falcon_query_mitre_attacks",
            "falcon_query_mitre_attacks_for_malware",
            "falcon_get_mitre_attack_details",
            "falcon_get_mitre_report",
            "falcon_query_vulnerability_ids",
            "falcon_get_vulnerability_details",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_actors_fql_guide",
            "falcon_search_indicators_fql_guide",
            "falcon_search_reports_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_tool_annotations(self):
        """Test tools are registered as read-only."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations("falcon_search_actors", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_get_mitre_report", READ_ONLY_ANNOTATIONS)
        self.assert_tool_annotations("falcon_download_rule_file", READ_ONLY_ANNOTATIONS)

    def test_search_actors_success(self):
        """Test search_actors uses QueryIntelActorEntities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "actor-1", "name": "Actor One"}]},
        }

        result = self.module.search_actors(
            filter="name:'Actor One'",
            limit=25,
            offset=0,
            sort="created_date|desc",
            q="actor",
            fields=["id", "name"],
        )

        self.mock_client.command.assert_called_once_with(
            "QueryIntelActorEntities",
            parameters={
                "filter": "name:'Actor One'",
                "limit": 25,
                "offset": 0,
                "sort": "created_date|desc",
                "q": "actor",
                "fields": ["id", "name"],
            },
        )
        self.assertEqual(result[0]["id"], "actor-1")

    def test_query_actor_ids_success(self):
        """Test query_actor_ids uses QueryIntelActorIds."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["111", "222"]},
        }

        result = self.module.query_actor_ids(filter="animal_classifier:'BEAR'", limit=2)

        self.mock_client.command.assert_called_once_with(
            "QueryIntelActorIds",
            parameters={"filter": "animal_classifier:'BEAR'", "limit": 2},
        )
        self.assertEqual(result, ["111", "222"])

    def test_get_actor_details_requires_ids(self):
        """Test get_actor_details validates required IDs."""
        result = self.module.get_actor_details(ids=None)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_actor_details_success(self):
        """Test get_actor_details uses GetIntelActorEntities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "111", "name": "Actor One"}]},
        }

        result = self.module.get_actor_details(ids=["111"], fields=["id", "name"])

        self.mock_client.command.assert_called_once_with(
            "GetIntelActorEntities",
            parameters={"ids": ["111"], "fields": ["id", "name"]},
        )
        self.assertEqual(result[0]["id"], "111")

    def test_search_indicators_success(self):
        """Test search_indicators uses QueryIntelIndicatorEntities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "ioc-1", "indicator": "evil.example"}]},
        }

        result = self.module.search_indicators(
            filter="type:'domain'",
            limit=10,
            include_deleted=True,
            include_relations=True,
        )

        self.mock_client.command.assert_called_once_with(
            "QueryIntelIndicatorEntities",
            parameters={
                "filter": "type:'domain'",
                "limit": 10,
                "include_deleted": True,
                "include_relations": True,
            },
        )
        self.assertEqual(result[0]["id"], "ioc-1")

    def test_query_indicator_ids_success(self):
        """Test query_indicator_ids uses QueryIntelIndicatorIds."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["ioc-1"]},
        }

        result = self.module.query_indicator_ids(
            filter="type:'hash_sha256'",
            limit=1,
            include_relations=True,
        )

        self.mock_client.command.assert_called_once_with(
            "QueryIntelIndicatorIds",
            parameters={
                "filter": "type:'hash_sha256'",
                "limit": 1,
                "include_deleted": False,
                "include_relations": True,
            },
        )
        self.assertEqual(result, ["ioc-1"])

    def test_get_indicator_details_uses_body(self):
        """Test get_indicator_details uses POST body for ids."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "ioc-1"}]},
        }

        result = self.module.get_indicator_details(ids=["ioc-1"])

        self.mock_client.command.assert_called_once_with(
            "GetIntelIndicatorEntities",
            body={"ids": ["ioc-1"]},
        )
        self.assertEqual(result[0]["id"], "ioc-1")

    def test_search_reports_success(self):
        """Test search_reports uses QueryIntelReportEntities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "report-1", "name": "Report"}]},
        }

        result = self.module.search_reports(filter="type:'CSIT'", limit=3)

        self.mock_client.command.assert_called_once_with(
            "QueryIntelReportEntities",
            parameters={"filter": "type:'CSIT'", "limit": 3},
        )
        self.assertEqual(result[0]["id"], "report-1")

    def test_query_report_ids_success(self):
        """Test query_report_ids uses QueryIntelReportIds."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["report-1"]},
        }

        result = self.module.query_report_ids(filter="name:'weekly'", limit=1)

        self.mock_client.command.assert_called_once_with(
            "QueryIntelReportIds",
            parameters={"filter": "name:'weekly'", "limit": 1},
        )
        self.assertEqual(result, ["report-1"])

    def test_get_report_details_success(self):
        """Test get_report_details uses GetIntelReportEntities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "report-1"}]},
        }

        result = self.module.get_report_details(ids=["report-1"], fields=["id", "name"])

        self.mock_client.command.assert_called_once_with(
            "GetIntelReportEntities",
            parameters={"ids": ["report-1"], "fields": ["id", "name"]},
        )
        self.assertEqual(result[0]["id"], "report-1")

    def test_download_report_pdf_binary_returns_metadata(self):
        """Test download_report_pdf returns metadata for PDF binary."""
        self.mock_client.command.return_value = b"%PDF-1.7 fake bytes"

        result = self.module.download_report_pdf(report_id="report-1")

        self.mock_client.command.assert_called_once_with(
            "GetIntelReportPDF",
            parameters={"id": "report-1"},
        )
        self.assertEqual(len(result), 1)
        self.assertIn("message", result[0])
        self.assertIn("size_bytes", result[0])

    def test_query_rule_ids_success(self):
        """Test query_rule_ids uses QueryIntelRuleIds."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [12345]},
        }

        result = self.module.query_rule_ids(
            rule_type="yara-master",
            limit=1,
            offset=0,
            q="ransomware",
        )

        self.mock_client.command.assert_called_once_with(
            "QueryIntelRuleIds",
            parameters={"type": "yara-master", "limit": 1, "offset": 0, "q": "ransomware"},
        )
        self.assertEqual(result, [12345])

    def test_get_rule_details_success(self):
        """Test get_rule_details uses GetIntelRuleEntities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "12345"}]},
        }

        result = self.module.get_rule_details(ids=["12345"])

        self.mock_client.command.assert_called_once_with(
            "GetIntelRuleEntities",
            parameters={"ids": ["12345"]},
        )
        self.assertEqual(result[0]["id"], "12345")

    def test_download_rule_file_binary_returns_metadata(self):
        """Test download_rule_file handles archive binary payload."""
        self.mock_client.command.return_value = b"PK\x03\x04fake-zip"

        result = self.module.download_rule_file(rule_id=12345, format="zip")

        self.mock_client.command.assert_called_once_with(
            "GetIntelRuleFile",
            parameters={"id": 12345, "format": "zip"},
        )
        self.assertEqual(len(result), 1)
        self.assertIn("Archive content is binary", result[0]["message"])

    def test_download_latest_rule_file_with_conditions(self):
        """Test download_latest_rule_file passes optional condition parameters."""
        self.mock_client.command.return_value = b"PK\x03\x04latest-zip"

        result = self.module.download_latest_rule_file(
            rule_type="cql-master",
            format="gzip",
            if_none_match="etag-value",
            if_modified_since="Wed, 21 Oct 2015 07:28:00 GMT",
        )

        self.mock_client.command.assert_called_once_with(
            "GetLatestIntelRuleFile",
            parameters={
                "type": "cql-master",
                "format": "gzip",
                "if_none_match": "etag-value",
                "if_modified_since": "Wed, 21 Oct 2015 07:28:00 GMT",
            },
        )
        self.assertEqual(len(result), 1)
        self.assertIn("size_bytes", result[0])

    def test_query_malware_ids_success(self):
        """Test query_malware_ids uses QueryMalware."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["emotet"]},
        }

        result = self.module.query_malware_ids(filter="name:'emotet'", limit=1)

        self.mock_client.command.assert_called_once_with(
            "QueryMalware",
            parameters={"filter": "name:'emotet'", "limit": 1},
        )
        self.assertEqual(result, ["emotet"])

    def test_search_malware_success(self):
        """Test search_malware uses QueryMalwareEntities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "emotet"}]},
        }

        result = self.module.search_malware(filter="family:'emotet'", limit=5, fields=["id"])

        self.mock_client.command.assert_called_once_with(
            "QueryMalwareEntities",
            parameters={"filter": "family:'emotet'", "limit": 5, "fields": ["id"]},
        )
        self.assertEqual(result[0]["id"], "emotet")

    def test_get_malware_details_requires_ids(self):
        """Test get_malware_details validates required IDs."""
        result = self.module.get_malware_details(ids=None)

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_malware_details_success(self):
        """Test get_malware_details returns entity records."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "emotet"}]},
        }

        result = self.module.get_malware_details(ids=["emotet"])

        self.mock_client.command.assert_called_once_with(
            "GetMalwareEntities",
            parameters={"ids": ["emotet"]},
        )
        self.assertEqual(result[0]["id"], "emotet")

    def test_get_malware_mitre_report_decodes_bytes(self):
        """Test malware MITRE report bytes are decoded to string."""
        self.mock_client.command.return_value = b'{"family":"emotet"}'

        result = self.module.get_malware_mitre_report(malware_id="emotet", format="JSON")

        self.mock_client.command.assert_called_once_with(
            "GetMalwareMitreReport",
            parameters={"id": "emotet", "format": "JSON"},
        )
        self.assertIsInstance(result, str)
        self.assertIn("emotet", result)

    def test_query_mitre_attacks_requires_id_or_ids(self):
        """Test query_mitre_attacks validates required actor input."""
        result = self.module.query_mitre_attacks(id=None, ids=None)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_query_mitre_attacks_success(self):
        """Test query_mitre_attacks uses QueryMitreAttacks."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["fancy-bear_TA0011_T1071"]},
        }

        result = self.module.query_mitre_attacks(ids=["fancy-bear"])

        self.mock_client.command.assert_called_once_with(
            "QueryMitreAttacks",
            parameters={"ids": ["fancy-bear"]},
        )
        self.assertEqual(result, ["fancy-bear_TA0011_T1071"])

    def test_query_mitre_attacks_for_malware_requires_ids(self):
        """Test query_mitre_attacks_for_malware validates required IDs."""
        result = self.module.query_mitre_attacks_for_malware(ids=None)
        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_get_mitre_attack_details_uses_body(self):
        """Test get_mitre_attack_details uses PostMitreAttacks body payload."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "fancy-bear_TA0011_T1071"}]},
        }

        result = self.module.get_mitre_attack_details(ids=["fancy-bear_TA0011_T1071"])

        self.mock_client.command.assert_called_once_with(
            "PostMitreAttacks",
            body={"ids": ["fancy-bear_TA0011_T1071"]},
        )
        self.assertEqual(result[0]["id"], "fancy-bear_TA0011_T1071")

    def test_get_mitre_report_by_actor_id(self):
        """Test get_mitre_report by numeric actor ID."""
        self.mock_client.command.return_value = b'{"actor":"123456"}'

        result = self.module.get_mitre_report(actor="123456", format="json")

        self.mock_client.command.assert_called_once_with(
            "GetMitreReport",
            parameters={"actor_id": "123456", "format": "json"},
        )
        self.assertIsInstance(result, str)
        self.assertIn("123456", result)

    def test_get_mitre_report_by_actor_name_resolves_id(self):
        """Test get_mitre_report resolves actor name before MITRE request."""
        self.mock_client.command.side_effect = [
            {
                "status_code": 200,
                "body": {"resources": [{"id": "7890", "name": "FAKE BEAR"}]},
            },
            b'{"actor":"7890"}',
        ]

        result = self.module.get_mitre_report(actor="FAKE BEAR", format="csv")

        self.assertEqual(self.mock_client.command.call_count, 2)
        self.assertEqual(
            self.mock_client.command.call_args_list[0],
            unittest.mock.call(
                "QueryIntelActorEntities",
                parameters={"filter": "name:'FAKE BEAR'", "limit": 1},
            ),
        )
        self.assertEqual(
            self.mock_client.command.call_args_list[1],
            unittest.mock.call(
                "GetMitreReport",
                parameters={"actor_id": "7890", "format": "csv"},
            ),
        )
        self.assertIsInstance(result, str)
        self.assertIn("7890", result)

    def test_get_mitre_report_actor_name_not_found(self):
        """Test get_mitre_report returns clear not-found error for actor name."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        result = self.module.get_mitre_report(actor="UNKNOWN ACTOR", format="json")

        self.mock_client.command.assert_called_once_with(
            "QueryIntelActorEntities",
            parameters={"filter": "name:'UNKNOWN ACTOR'", "limit": 1},
        )
        self.assertEqual(len(result), 1)
        self.assertIn("Actor not found", result[0]["error"])

    def test_query_vulnerability_ids_success(self):
        """Test query_vulnerability_ids uses QueryVulnerabilities."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": ["vuln-1"]},
        }

        result = self.module.query_vulnerability_ids(
            filter="severity:'high'",
            limit=2,
            sort="updated_timestamp|desc",
        )

        self.mock_client.command.assert_called_once_with(
            "QueryVulnerabilities",
            parameters={
                "filter": "severity:'high'",
                "limit": 2,
                "sort": "updated_timestamp|desc",
            },
        )
        self.assertEqual(result, ["vuln-1"])

    def test_get_vulnerability_details_uses_body(self):
        """Test get_vulnerability_details uses GetVulnerabilities body payload."""
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "vuln-1"}]},
        }

        result = self.module.get_vulnerability_details(ids=["vuln-1"])

        self.mock_client.command.assert_called_once_with(
            "GetVulnerabilities",
            body={"ids": ["vuln-1"]},
        )
        self.assertEqual(result[0]["id"], "vuln-1")

    def test_binary_text_decode_error_returns_error(self):
        """Test non-UTF8 binary response returns structured error."""
        self.mock_client.command.return_value = b"\xff\xfe\x00\x01"

        result = self.module.get_malware_mitre_report(malware_id="emotet", format="JSON")

        self.assertEqual(len(result), 1)
        self.assertIn("error", result[0])


if __name__ == "__main__":
    unittest.main()
