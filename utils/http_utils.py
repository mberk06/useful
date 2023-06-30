from requests import HTTPError
from urllib.parse import urlparse
from typing import Iterable

# Response codes that generally indicate transient network failures and merit client retries,
# based on guidance from cloud service providers
# (https://docs.microsoft.com/en-us/azure/architecture/best-practices/retry-service-specific#general-rest-and-retry-guidelines)
TRANSIENT_FAILURE_RESPONSE_CODES = frozenset(
    [
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    ]
)


# url parsing helpers
def is_retryable_exception(retry_state, retry_codes: Iterable[int]):
    exception = retry_state.outcome.exception()
    return (
        isinstance(exception, HTTPError)
        and exception.response.status_code in retry_codes
    )


def url_is_valid(url: str) -> bool:
    result = urlparse(url)
    return all([result.netloc, result.scheme, result.path])
