"""Integration tests for the ThreatGraph module."""

from typing import Any

import pytest

from falcon_mcp.modules.threatgraph import ThreatGraphModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestThreatGraphIntegration(BaseIntegrationTest):
    """Integration tests for ThreatGraph with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = ThreatGraphModule(falcon_client)

    @staticmethod
    def _extract_status_code(result: Any) -> int | None:
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                details = first.get("details", {})
                if isinstance(details, dict):
                    return details.get("status_code")
        return None

    def test_get_threatgraph_edge_types_operation_name(self):
        result = self.call_method(self.module.get_threatgraph_edge_types)
        self.assert_no_error(result, context="get_threatgraph_edge_types")
        self.assert_valid_list_response(result, min_length=0, context="get_threatgraph_edge_types")

    def test_get_threatgraph_ran_on_operation_name(self):
        result = self.call_method(
            self.module.get_threatgraph_ran_on,
            type="domain",
            value="example.invalid",
            limit=1,
            offset=0,
            nano=False,
        )

        status_code = self._extract_status_code(result)
        if status_code in (400, 404, 422):
            return

        self.assert_no_error(result, context="get_threatgraph_ran_on")
        self.assert_valid_list_response(result, min_length=0, context="get_threatgraph_ran_on")

    def test_get_threatgraph_summary_invalid_vertex(self):
        result = self.call_method(
            self.module.get_threatgraph_summary,
            ids=["00000000000000000000000000000000"],
            vertex_type="any-vertex",
            scope="customer",
            nano=False,
        )

        status_code = self._extract_status_code(result)
        if status_code in (400, 404, 422):
            return

        self.assert_no_error(result, context="get_threatgraph_summary_invalid_vertex")
