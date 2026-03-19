"""Integration tests for the Deployments module."""

import pytest

from falcon_mcp.modules.deployments import DeploymentsModule
from tests.integration.utils.base_integration_test import BaseIntegrationTest


@pytest.mark.integration
class TestDeploymentsIntegration(BaseIntegrationTest):
    """Integration tests for Deployments with real API calls."""

    @pytest.fixture(autouse=True)
    def setup_module(self, falcon_client):
        self.module = DeploymentsModule(falcon_client)

    @staticmethod
    def _extract_release_note_id(result):
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                for key in ("id", "release_note_id"):
                    value = first.get(key)
                    if isinstance(value, str) and value:
                        return value
        return None

    def test_search_deployment_releases_operation_name(self):
        result = self.call_method(
            self.module.search_deployment_releases,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self.assert_no_error(result, context="search_deployment_releases")
        self.assert_valid_list_response(result, min_length=0, context="search_deployment_releases")

    def test_search_release_notes_and_get_v2(self):
        search_result = self.call_method(
            self.module.search_release_notes,
            filter=None,
            limit=1,
            offset=0,
            sort=None,
        )

        self.assert_no_error(search_result, context="search_release_notes")
        self.assert_valid_list_response(search_result, min_length=0, context="search_release_notes")

        release_note_id = self._extract_release_note_id(search_result)
        if not release_note_id:
            self.skip_with_warning(
                "No release notes available to validate detail retrieval",
                context="test_search_release_notes_and_get_v2",
            )

        result = self.call_method(self.module.get_release_notes_v2, ids=[release_note_id])
        self.assert_no_error(result, context="get_release_notes_v2")
        self.assert_valid_list_response(result, min_length=0, context="get_release_notes_v2")
