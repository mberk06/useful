# This code wraps API calls, specifically for the Databricks API. It extends to other APIs thare are authenticated via a token in the header.

import os
from urllib.parse import urlparse
import requests
from requests.exceptions import HTTPError
from tenacity import retry, stop_after_attempt, wait_exponential, before_log, after_log

import logging

from pydantic import SecretStr
from typing import Type

# Response codes that generally indicate transient network failures and merit client retries,
# based on guidance from cloud service providers
# (https://docs.microsoft.com/en-us/azure/architecture/best-practices/retry-service-specific#general-rest-and-retry-guidelines)
_TRANSIENT_FAILURE_RESPONSE_CODES = frozenset(
    [
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    ]
)
_MAX_RETRY_COUNT = 3
_ALLOWED_HTTP_COMMANDS = {"GET", "POST", "PUT", "DELETE"}

# Create a logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Client:
    def __init__(self, host: str, token: SecretStr):
        self.host = host.rstrip("/") + "/"
        self._token = token

    @property
    def token(self):
        return self._token.get_secret_value()

    def _is_retryable_exception(retry_state):
        exception = retry_state.outcome.exception()
        return (
            isinstance(exception, HTTPError)
            and exception.response.status_code in _TRANSIENT_FAILURE_RESPONSE_CODES
        )

    @staticmethod
    def _url_is_valid(url: str) -> bool:
        result = urlparse(url)
        return all([result.netloc, result.scheme, result.path])

    @retry(
        stop=stop_after_attempt(_MAX_RETRY_COUNT),
        wait=wait_exponential(multiplier=2, min=1, max=15),
        retry=_is_retryable_exception,
    )
    def _execute(self, endpoint: str, http_command: str, json: dict = {}) -> dict:
        """
        This method makes a request to the host URL joined with the provided endpoint and returns the JSON response.
        If the provided URL is invalid, it raises a ValueError.
        :param endpoint: The API endpoint to execute the HTTP command against.
        :param http_command: The HTTP command (e.g., "GET", "POST", "PUT", "DELETE") to execute.
        :param json: Optional dictionary containing JSON data to send with the HTTP request. Default is an empty dictionary.
        :return: The JSON response from the server as a dictionary.
        """
        if http_command.upper() not in _ALLOWED_HTTP_COMMANDS:
            logger.error(f"{http_command} is not a valid HTTP command.")
            raise ValueError(f"{http_command} is not a valid HTTP command.")
            
        auth = {"Authorization": f"Bearer {self.token}"}
        url = os.path.join(self.host, endpoint.lstrip("/"))
        print(url)
        if self._url_is_valid(url):
            with requests.Session() as session:
                logger.info(f"Making a {http_command} request to {url}")

                response = session.request(http_command, url, headers=auth, json=json)
                response.raise_for_status()
                return response.json() or {}
        else:
            error_str = f"{url} is not a valid URL format."
            logger.error(error_str)
            raise ValueError(error_str)
