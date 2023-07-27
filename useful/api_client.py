# This code wraps API calls, specifically for the Databricks API. It extends to other APIs thare are authenticated via a token in the header.

import os
import requests
import logging
from pydantic import SecretStr
from functools import partial

from tenacity import retry, stop_after_attempt, wait_exponential, before_log, after_log

from utils.http_utils import (
    is_retryable_exception,
    url_is_valid,
    TRANSIENT_FAILURE_RESPONSE_CODES,
)
from utils.logging import BaseFilter


_MAX_RETRY_COUNT = 3
_ALLOWED_HTTP_COMMANDS = {"GET", "POST", "PUT", "DELETE"}

# create logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addFilter(BaseFilter())


# main class
class Client:
    wait_func: callable = None

    def __init__(self, host: str, token: SecretStr):
        self.host = host.rstrip("/") + "/"

        assert isinstance(
            token, SecretStr
        ), "The token must be of type pydantic.SecretStr"
        self._token = token

    @property
    def token(self):
        return self._token.get_secret_value()

    @retry(
        stop=stop_after_attempt(_MAX_RETRY_COUNT),
        wait=wait_exponential(multiplier=3, min=1, max=10),
        retry=partial(
            is_retryable_exception, retry_codes=TRANSIENT_FAILURE_RESPONSE_CODES
        ),
        before=before_log(logger, logging.INFO),  # log before a retry
        after=after_log(logger, logging.INFO),  # log after a retry
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
        if url_is_valid(url):
            with requests.Session() as session:
                logger.info(f"Making a {http_command} request to {url}")

                response = session.request(http_command, url, headers=auth, json=json)
                response.raise_for_status()
                return response.json() or {}
        else:
            error_str = f"{url} is not a valid URL format."
            logger.error(error_str)
            raise ValueError(error_str)
