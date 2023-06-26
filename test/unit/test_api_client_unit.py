import pytest
from unittest import mock
from unittest.mock import MagicMock
from requests.models import Response
from requests.exceptions import HTTPError
from pydantic import SecretStr

from useful import Client

HOST = "https://blueberries.are.cool.gov"
TOKEN_STR = "SHHHHHH"
ENDPOINT = "/api/2.1/salmon-avocado-roll"


@pytest.fixture
def client():
    return Client(HOST, SecretStr(TOKEN_STR))


def test_string_token_raises():
    with pytest.raises(
        AssertionError, match="The token must be of type pydantic.SecretStr"
    ):
        Client(HOST, TOKEN_STR)


def test_is_retryable_exception_is_retryable(client):
    mock_retry_state = MagicMock()
    mock_retry_state.outcome.exception.return_value = HTTPError("An error occurred")
    mock_retry_state.outcome.exception.return_value.response = Response()
    mock_retry_state.outcome.exception.return_value.response.status_code = 500

    assert client._is_retryable_exception(mock_retry_state)


def test_is_retryable_exception_non_retryable_status_code(client):
    mock_retry_state = MagicMock()
    mock_retry_state.outcome.exception.return_value = HTTPError("An error occurred")
    mock_retry_state.outcome.exception.return_value.response = Response()
    mock_retry_state.outcome.exception.return_value.response.status_code = 400

    assert not client._is_retryable_exception(mock_retry_state)


def test_url_is_valid(client):
    assert client._url_is_valid("https://validurl.com/path")
    assert client._url_is_valid("https://validurl.com/")
    assert not client._url_is_valid("http:/invalidurl.com")  # invalid scheme
    assert not client._url_is_valid("https:///missingnetloc.com")  # missing netloc
    assert not client._url_is_valid("")  # empty string


"""
def test_retry(client):
    with mock.patch("requests.Session") as mock_session:
        mock_request = mock.Mock()

        # First call will raise an HTTPError, second call will succeed
        successful_response = mock.Mock()
        successful_response.raise_for_status.return_value = (
            None  # So it doesn't raise an exception
        )
        successful_response.json.return_value = {"key": "value"}

        mock_request.side_effect = [
            HTTPError(response=mock.Mock(status_code=500)),
            successful_response,
        ]

        mock_session.return_value.request = mock_request

        # Call the _execute method and check the returned data
        result = client._execute("test_endpoint", "GET")
        assert result == {"key": "value"}

        # Assert that the request method was called twice (a retry happened)
        assert mock_request.call_count == 2

"""
