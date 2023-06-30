import pytest
from unittest.mock import MagicMock, Mock, patch
from pydantic import SecretStr

import tenacity
from requests import Response
from requests.exceptions import HTTPError

from useful import Client
from utils.http_utils import is_retryable_exception

HOST = "https://blueberries.are.cool.gov"
TOKEN_STR = "hush!"
ENDPOINT = "/api/2.1/salmon-avocado-roll"


@pytest.fixture
def client():
    return Client(HOST, SecretStr(TOKEN_STR))


def test_string_token_raises():
    with pytest.raises(
        AssertionError, match="The token must be of type pydantic.SecretStr"
    ):
        Client(HOST, TOKEN_STR)


def test_retry_success(client):
    with patch("requests.Session") as mock_session:
        failed_response = Mock(spec=Response)
        failed_response.raise_for_status.side_effect = HTTPError("Error message")
        failed_response.status_code = 500

        success_payload = {"pan": "cakes"}
        successful_response = Mock(spec=Response)
        successful_response.raise_for_status.return_value = None
        successful_response.json.return_value = success_payload

        mock_session().__enter__().request.side_effect = [
            HTTPError(response=failed_response),
            successful_response,
        ]

        result = client._execute(http_command="GET", endpoint=ENDPOINT)
        assert result == success_payload

        assert mock_session().__enter__().request.call_count == 2


def test_retry_success(client):
    with patch("requests.Session") as mock_session:
        n_failures = 3
        failed_response = Mock(spec=Response)
        failed_response.raise_for_status.side_effect = HTTPError("Error message")
        failed_response.status_code = 500

        success_payload = {"pan": "cakes"}
        successful_response = Mock(spec=Response)
        successful_response.raise_for_status.return_value = None
        successful_response.json.return_value = success_payload

        mock_session().__enter__().request.side_effect = [
            HTTPError(response=failed_response)
        ] * n_failures + [
            success_payload
        ]  # success should never be reached

        with pytest.raises(tenacity.RetryError):
            client._execute(http_command="GET", endpoint=ENDPOINT)

        assert mock_session().__enter__().request.call_count == n_failures


"""
def test_retry_failure(client):
    with patch("requests.Session") as mock_session:
        n_failures = 1

        failed_response = Mock(spec=Response)
        failed_response.raise_for_status.side_effect = HTTPError("Error message")
        failed_response.status_code = 500

        failed_response1 = Mock(spec=Response)
        failed_response1.raise_for_status.side_effect = HTTPError("Error message")
        failed_response1.status_code = 500

        failed_response2 = Mock(spec=Response)
        failed_response2.raise_for_status.side_effect = HTTPError("Error message")
        failed_response2.status_code = 500
        # succes shuold never be reached
        successful_response = Mock(spec=Response)
        successful_response.raise_for_status.return_value = None
        successful_response.json.return_value = {"key": "value"}

        mock_session().__enter__().request.side_effect = [
            HTTPError(response=failed_response),
            HTTPError(response=failed_response1),
            HTTPError(response=failed_response2),
        ] * n_failures

        with pytest.raises(tenacity.RetryError):
            client._execute("hdsf", "GET")

        # assert mock_session.return_value.request.call_count == n_failures
"""
