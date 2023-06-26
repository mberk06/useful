# This code wraps API calls, specifically for the Databricks API. It extends to other APIs thare are authenticated via a token in the header.

import os
import requests
from requests.exceptions import HTTPError
import tenacity
from tenacity import retry, wait_exponential, stop_after_attempt
from urllib.parse import urlparse

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


class Client:
    def __init__(self, host: str, token: SecretStr):
        self.host = host.rstrip("/") + "/"
        self._token = token

    def __enter__(self):
        self.session = requests.Session()
        return self

    def __exit__(self):
        self.session.close()

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
        auth = {"Authorization": f"Bearer {self.token}"}
        url = os.path.join(self.host, endpoint.lstrip("/"))
        print(url)
        if self._url_is_valid(url):
            response = self.session.request(http_command, url, headers=auth, json=json)
            response.raise_for_status()
            return response.json()
        else:
            raise ValueError(f"{url} is not a valid format.")
