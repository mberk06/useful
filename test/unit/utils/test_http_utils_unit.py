import pytest
from unittest.mock import MagicMock

from pydantic import SecretStr
from requests import HTTPError, Response

from useful import Client
from utils.http_utils import (
    url_is_valid,
    is_retryable_exception,
    TRANSIENT_FAILURE_RESPONSE_CODES,
)

HOST = "https://blueberries.are.cool.gov"
TOKEN_STR = "SHHHHHH"
ENDPOINT = "/api/2.1/salmon-avocado-roll"


@pytest.fixture
def client():
    return Client(HOST, SecretStr(TOKEN_STR))


def test_url_is_valid_https(client):
    assert url_is_valid("https://validurl.com/path")


def test_url_is_valid_http(client):
    assert url_is_valid("http://validurl.com/path")


def test_url_is_invalid_scheme(client):
    assert not url_is_valid("http:/invalidurl.com")


def test_url_is_invalid_netloc(client):
    assert not url_is_valid("https:///missingnetloc.com")


def test_url_is_invalid_empty(client):
    assert not url_is_valid("")  # empty string


def test_is_retryable_exception_is_retryable(client):
    mock_retry_state = MagicMock()
    mock_retry_state.outcome.exception.return_value = HTTPError("An error occurred")
    mock_retry_state.outcome.exception.return_value.response = Response()
    mock_retry_state.outcome.exception.return_value.response.status_code = 500

    assert is_retryable_exception(
        mock_retry_state, retry_codes=TRANSIENT_FAILURE_RESPONSE_CODES
    )


def test_is_retryable_exception_non_retryable_status_code(client):
    mock_retry_state = MagicMock()
    mock_retry_state.outcome.exception.return_value = HTTPError("An error occurred")
    mock_retry_state.outcome.exception.return_value.response = Response()
    mock_retry_state.outcome.exception.return_value.response.status_code = 400

    assert not is_retryable_exception(
        mock_retry_state, retry_codes=TRANSIENT_FAILURE_RESPONSE_CODES
    )
