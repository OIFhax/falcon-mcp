"""
Tests for the Falcon API client.
"""

import platform
import sys
import unittest
from unittest.mock import MagicMock, patch

from requests.exceptions import Timeout as RequestsTimeout

from falcon_mcp.client import FalconClient


class TestFalconClient(unittest.TestCase):
    """Test cases for the Falcon API client."""

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_client_initialization(self, mock_apiharness, mock_environ_get):
        """Test client initialization with base URL."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        # Create client with base URL
        _client = FalconClient(base_url="https://api.test.crowdstrike.com", debug=True)

        # Verify APIHarnessV2 was initialized correctly with config values
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["client_id"], "test-client-id")
        self.assertEqual(call_args["client_secret"], "test-client-secret")
        self.assertEqual(call_args["base_url"], "https://api.test.crowdstrike.com")
        self.assertTrue(call_args["debug"])

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_client_initialization_with_env_vars(
        self, mock_apiharness, mock_environ_get
    ):
        """Test client initialization with environment variables."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "env-client-id",
            "FALCON_CLIENT_SECRET": "env-client-secret",
            "FALCON_BASE_URL": "https://api.env.crowdstrike.com",
        }.get(key, default)

        # Create client with environment variables
        _client = FalconClient()

        # Verify APIHarnessV2 was initialized correctly
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["client_id"], "env-client-id")
        self.assertEqual(call_args["client_secret"], "env-client-secret")
        self.assertEqual(call_args["base_url"], "https://api.env.crowdstrike.com")
        self.assertFalse(call_args["debug"])

    @patch("falcon_mcp.client.os.environ.get")
    def test_client_initialization_missing_credentials(self, mock_environ_get):
        """Test client initialization with missing credentials."""
        # Setup mock environment variables (missing credentials)
        mock_environ_get.return_value = None

        # Verify ValueError is raised when credentials are missing
        with self.assertRaises(ValueError):
            FalconClient()

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_client_initialization_with_direct_credentials(
        self, mock_apiharness, mock_environ_get
    ):
        """Test client initialization with directly passed credentials."""
        # No environment variables set
        mock_environ_get.return_value = None
        mock_apiharness.return_value = MagicMock()

        # Create client with direct credentials
        _client = FalconClient(
            client_id="direct-client-id",
            client_secret="direct-client-secret",
        )

        # Verify APIHarnessV2 was initialized with direct credentials
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["client_id"], "direct-client-id")
        self.assertEqual(call_args["client_secret"], "direct-client-secret")

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_client_direct_credentials_override_env_vars(
        self, mock_apiharness, mock_environ_get
    ):
        """Test that direct credentials take precedence over environment variables."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "env-client-id",
            "FALCON_CLIENT_SECRET": "env-client-secret",
        }.get(key, default)
        mock_apiharness.return_value = MagicMock()

        # Create client with direct credentials (should override env vars)
        _client = FalconClient(
            client_id="direct-client-id",
            client_secret="direct-client-secret",
        )

        # Verify APIHarnessV2 was initialized with direct credentials, not env vars
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["client_id"], "direct-client-id")
        self.assertEqual(call_args["client_secret"], "direct-client-secret")

    @patch("falcon_mcp.client.os.environ.get")
    def test_client_initialization_error_message(self, mock_environ_get):
        """Test that error message mentions both credential approaches."""
        # No environment variables set
        mock_environ_get.return_value = None

        # Verify error message mentions both approaches
        with self.assertRaises(ValueError) as context:
            FalconClient()

        error_message = str(context.exception)
        self.assertIn("client_id", error_message)
        self.assertIn("client_secret", error_message)
        self.assertIn("FALCON_CLIENT_ID", error_message)
        self.assertIn("FALCON_CLIENT_SECRET", error_message)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_authenticate(self, mock_apiharness, mock_environ_get):
        """Test authenticate method."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.login.return_value = True
        mock_apiharness.return_value = mock_instance

        # Create client and authenticate
        client = FalconClient()
        result = client.authenticate()

        # Verify login was called and result is correct
        mock_instance.login.assert_called_once()
        self.assertTrue(result)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_is_authenticated(self, mock_apiharness, mock_environ_get):
        """Test is_authenticated method."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.token_valid = True
        mock_apiharness.return_value = mock_instance

        # Create client and check authentication status
        client = FalconClient()
        result = client.is_authenticated()

        # Verify result is correct
        self.assertTrue(result)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_get_headers(self, mock_apiharness, mock_environ_get):
        """Test get_headers method."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.auth_headers = {"Authorization": "Bearer test-token"}
        mock_apiharness.return_value = mock_instance

        # Create client and get headers
        client = FalconClient()
        headers = client.get_headers()

        # Verify headers are correct
        self.assertEqual(headers, {"Authorization": "Bearer test-token"})

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_command(self, mock_apiharness, mock_environ_get):
        """Test command method."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        # Setup mock
        mock_instance = MagicMock()
        mock_instance.command.return_value = {
            "status_code": 200,
            "body": {"resources": [{"id": "test"}]},
        }
        mock_apiharness.return_value = mock_instance

        # Create client and execute command
        client = FalconClient()
        response = client.command("TestOperation", parameters={"filter": "test"})

        # Verify command was called with correct arguments
        mock_instance.command.assert_called_once_with(
            "TestOperation", parameters={"filter": "test"}
        )

        # Verify response is correct
        self.assertEqual(response["status_code"], 200)
        self.assertEqual(response["body"]["resources"][0]["id"], "test")

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_command_records_tool_io_history(self, mock_apiharness, mock_environ_get):
        """Test command history preserves tool context and raw I/O."""
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        mock_instance = MagicMock()
        mock_instance.command.return_value = {
            "status_code": 200,
            "headers": {"x-cs-traceid": "trace-123"},
            "body": {"resources": [{"id": "test"}]},
        }
        mock_apiharness.return_value = mock_instance

        client = FalconClient(base_url="https://api.us-2.crowdstrike.com")
        with client.tool_context("falcon_test_tool", {"device_id": "aid-123"}):
            client.command("TestOperation", parameters={"filter": "test"})

        history = client.get_tool_io_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["tool_name"], "falcon_test_tool")
        self.assertEqual(history[0]["tool_parameters"]["device_id"], "aid-123")
        self.assertEqual(history[0]["falcon_operation"], "TestOperation")
        self.assertEqual(history[0]["trace_ids"], ["trace-123"])
        self.assertEqual(history[0]["target_device_ids"], ["aid-123"])
        self.assertIsNone(history[0]["error_object"])

    @patch("falcon_mcp.client.sleep")
    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_command_retries_retryable_transient_5xx(
        self, mock_apiharness, mock_environ_get, mock_sleep
    ):
        """Test retry/backoff for transient RTR initialization failures."""
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        mock_instance = MagicMock()
        mock_instance.command.side_effect = [
            {
                "status_code": 503,
                "body": {"errors": [{"message": "Service unavailable"}]},
            },
            {
                "status_code": 201,
                "body": {"resources": [{"session_id": "session-1"}]},
            },
        ]
        mock_apiharness.return_value = mock_instance

        client = FalconClient()
        response = client.command("RTR_InitSession", body={"device_id": "aid-123"})

        self.assertEqual(mock_instance.command.call_count, 2)
        mock_sleep.assert_called_once()
        self.assertEqual(response["status_code"], 201)
        self.assertEqual(len(client.get_tool_io_history()), 2)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_retryable_operations_use_dedicated_rtr_timeout_client(
        self, mock_apiharness, mock_environ_get
    ):
        """Test RTR retryable operations use the shorter dedicated Falcon timeout client."""
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        primary_client = MagicMock()
        rtr_client = MagicMock()
        rtr_client.command.return_value = {
            "status_code": 201,
            "body": {"resources": [{"session_id": "session-1"}]},
        }
        mock_apiharness.side_effect = [primary_client, rtr_client]

        client = FalconClient()
        response = client.command("RTR_InitSession", body={"device_id": "aid-123"})

        self.assertEqual(mock_apiharness.call_count, 2)
        self.assertIs(client._rtr_client, rtr_client)
        self.assertEqual(mock_apiharness.call_args_list[0].kwargs["timeout"], None)
        self.assertEqual(mock_apiharness.call_args_list[1].kwargs["timeout"], 15.0)
        rtr_client.command.assert_called_once_with("RTR_InitSession", body={"device_id": "aid-123"})
        primary_client.command.assert_not_called()
        self.assertEqual(response["status_code"], 201)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_command_converts_timeout_exception_to_gateway_timeout(
        self, mock_apiharness, mock_environ_get
    ):
        """Test Falcon request timeouts return a structured 504 response instead of raising."""
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        mock_instance = MagicMock()
        mock_instance.command.side_effect = RequestsTimeout("request timed out")
        mock_apiharness.return_value = mock_instance

        client = FalconClient()
        response = client.command("QueryDevicesByFilter", parameters={"filter": "hostname:'test'"})

        self.assertEqual(response["status_code"], 504)
        self.assertTrue(response["meta"]["timed_out"])
        self.assertEqual(response["meta"]["operation"], "QueryDevicesByFilter")
        self.assertEqual(response["meta"]["configured_timeout_seconds"], None)
        self.assertIn("timed out", response["body"]["errors"][0]["message"])
        history = client.get_tool_io_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["status_code"], 504)
        self.assertEqual(history[0]["error_object"]["status_code"], 504)

    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_generate_support_bundle_extracts_summary(self, mock_apiharness, mock_environ_get):
        """Test support bundle generation extracts region, traces, operations, and device IDs."""
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        mock_instance = MagicMock()
        mock_instance.command.return_value = {
            "status_code": 500,
            "headers": {"x-cs-traceid": "trace-500"},
            "body": {"errors": [{"message": "Server error"}]},
        }
        mock_apiharness.return_value = mock_instance

        client = FalconClient(base_url="https://api.us-2.crowdstrike.com")
        with client.tool_context("falcon_init_rtr_session", {"device_id": "aid-123"}):
            client.command("TestOperation", body={"device_id": "aid-123"})

        bundle = client.generate_support_bundle()

        self.assertEqual(bundle["region"], "us-2")
        self.assertEqual(bundle["trace_ids"], ["trace-500"])
        self.assertEqual(bundle["target_device_ids"], ["aid-123"])
        self.assertIn(
            {
                "tool_name": "falcon_init_rtr_session",
                "falcon_operation": "TestOperation",
            },
            bundle["tool_functions"],
        )
        self.assertEqual(len(bundle["entries"]), 1)

    @patch("falcon_mcp.client.version")
    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_get_user_agent_best_case_scenario(
        self, mock_apiharness, mock_environ_get, mock_version
    ):
        """Test get_user_agent method in the best case scenario with all packages installed."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        # Setup mock version calls for best case scenario
        def version_side_effect(package_name):
            if package_name == "falcon-mcp":
                return "1.2.3"
            if package_name == "crowdstrike-falconpy":
                return "1.3.4"
            raise ValueError(f"Unexpected package: {package_name}")

        mock_version.side_effect = version_side_effect
        mock_apiharness.return_value = MagicMock()

        # Create client and get user agent
        client = FalconClient()
        user_agent = client.get_user_agent()

        # Verify user agent format and content
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        platform_info = f"{platform.system()}/{platform.release()}"
        expected = f"falcon-mcp/1.2.3 (falconpy/1.3.4; Python/{python_version}; {platform_info})"

        self.assertEqual(user_agent, expected)

        # Verify user agent is properly used in APIHarnessV2 initialization
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["user_agent"], expected)

        # Verify format components
        self.assertTrue(user_agent.startswith("falcon-mcp/1.2.3"))
        self.assertIn(f"Python/{python_version}", user_agent)
        self.assertIn(platform_info, user_agent)
        self.assertIn("falconpy/1.3.4", user_agent)

    @patch("falcon_mcp.client.version")
    @patch("falcon_mcp.client.os.environ.get")
    @patch("falcon_mcp.client.APIHarnessV2")
    def test_get_user_agent_with_user_agent_comment(
        self, mock_apiharness, mock_environ_get, mock_version
    ):
        """Test get_user_agent method with a user agent comment."""
        # Setup mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            "FALCON_CLIENT_ID": "test-client-id",
            "FALCON_CLIENT_SECRET": "test-client-secret",
        }.get(key, default)

        # Setup mock version calls
        def version_side_effect(package_name):
            if package_name == "falcon-mcp":
                return "1.2.3"
            if package_name == "crowdstrike-falconpy":
                return "1.3.4"
            raise ValueError(f"Unexpected package: {package_name}")

        mock_version.side_effect = version_side_effect
        mock_apiharness.return_value = MagicMock()

        # Create client with user agent comment
        client = FalconClient(user_agent_comment="CustomApp/1.0")
        user_agent = client.get_user_agent()

        # Verify user agent format and content (RFC-compliant format)
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        platform_info = f"{platform.system()}/{platform.release()}"
        expected = f"falcon-mcp/1.2.3 (CustomApp/1.0; falconpy/1.3.4; Python/{python_version}; {platform_info})"

        self.assertEqual(user_agent, expected)

        # Verify user agent is properly used in APIHarnessV2 initialization
        mock_apiharness.assert_called_once()
        call_args = mock_apiharness.call_args[1]
        self.assertEqual(call_args["user_agent"], expected)


if __name__ == "__main__":
    unittest.main()
