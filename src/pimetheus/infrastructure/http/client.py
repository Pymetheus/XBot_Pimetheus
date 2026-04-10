import logging
from typing import Any

import httpx
import structlog

from pimetheus.infrastructure.http.exceptions import HTTPClientError
from pimetheus.infrastructure.raspberrypi.system import GroundControl

logging.getLogger("httpx").propagate = False
logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class HttpClient:
    """
    Wrapper around httpx.Client with retry and JSON helpers.

    Attributes:
        MAX_RETRIES (int): Maximum retry attempts.
        timeout (httpx.Timeout): Request timeout configuration.
        client (httpx.Client): HTTP client instance.
        ground_control (GroundControl): Network controller.
    """

    MAX_RETRIES = 3

    def __init__(self) -> None:
        """
        Initialize the HttpClient.
        """

        self.timeout = httpx.Timeout(timeout=5.0, connect=2.0)
        self.client = httpx.Client(timeout=self.timeout)
        self.ground_control = GroundControl()

    def close(self) -> None:
        """
        Close the HTTP client.
        """
        self.client.close()
        logger.info("Closed HTTP client connection")

    def get_response(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """
        Perform GET request with retry logic.

        Parameters:
            url (str): Request URL.
            params (dict[str, Any] | None): Query parameters.

        Returns:
            httpx.Response: Successful response.

        Raises:
            HTTPClientError: If all retries fail or non-retryable error occurs.
        """

        last_exception: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            logger.info("Requesting url", attempt=attempt + 1, url=url)
            try:
                response = self.client.get(url=str(url), params=params)
                response.raise_for_status()
                logger.info("HTTP request successful", url=url, status_code=response.status_code)
                return response

            except httpx.TimeoutException as e:
                logger.warning("Timeout error", url=url)
                self.ground_control.renew_dhclient()
                last_exception = e

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if 500 <= status < 600:
                    logger.warning("HTTP server error", url=url, status_code=status)
                    last_exception = e
                else:
                    logger.exception("HTTP client error", url=url, status_code=status)
                    raise HTTPClientError(f"Client error {status}") from e

            except httpx.RequestError as e:
                logger.warning("Network error", url=url)
                self.ground_control.renew_dhclient()
                last_exception = e

        logger.error("Retry attempts failed", url=url, retries=self.MAX_RETRIES)
        raise HTTPClientError(f"Error while requesting url: {url}") from last_exception

    def fetch_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        """
        Fetch JSON response from GET request.

        Parameters:
            url (str): Request URL.
            params (dict[str, Any] | None): Query parameters.

        Returns:
            Any: Parsed JSON content.

        Raises:
            HTTPClientError: If request fails.
            ValueError: If response is not valid JSON.
        """

        try:
            response = self.get_response(url, params)
            result = response.json()
            logger.info("Fetched json", url=url)
            return result
        except HTTPClientError:
            logger.error("Failed to fetch response", url=url)
            raise
        except ValueError:
            logger.exception("Failed to fetch json", url=url)
            raise

    def __del__(self) -> None:
        """
        Ensure the HTTP client connection is closed on object destruction.
        """

        try:
            self.client.close()
        except Exception as e:
            logger.debug("Unable to close HTTP client", error=str(e))
            pass
