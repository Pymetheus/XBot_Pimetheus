import time
from collections.abc import Callable
from typing import TypeVar, cast

import structlog
from atproto import Client
from atproto_client.exceptions import InvokeTimeoutError as AtprotoInvokeTimeoutError
from atproto_client.exceptions import NetworkError as AtprotoNetworkError
from httpx import NetworkError

from pimetheus.utils.config import Settings

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)
T = TypeVar("T")


class BlueskyAPIClient:
    """
    BlueSky API client with authentication and retry logic.

    Attributes:
        settings (Settings): Application configuration.
        MAX_RETRIES (int): Max retry attempts.
        client (Client): Authenticated API client.
        did (str): User decentralized identifier.
    """

    settings = Settings.load()
    MAX_RETRIES = 3

    def __init__(self) -> None:
        self.client = self.initialize_client()
        self.did = self.get_did()

    def execute_with_retry(self, function: Callable[[], T], *, action: str) -> T:
        """
        Execute callable with retry logic.

        Parameters:
            function (Callable[[], T]): Operation to execute.
            action (str): Action description.

        Returns:
            T: Result of operation.

        Raises:
            NetworkError: If all retries fail.
            InvokeTimeoutError: If timeout persists.
        """

        last_exception: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            logger.info("Executing API call", action=action, attempt=attempt + 1)
            try:
                return function()
            except (AtprotoInvokeTimeoutError, AtprotoNetworkError) as e:
                logger.warning("API call failed", action=action)
                last_exception = e

                if attempt < self.MAX_RETRIES - 1:
                    sleep_time = 2**attempt
                    time.sleep(sleep_time)

        logger.error("Retry attempts failed", action=action)
        raise NetworkError(f"Error while {action}") from last_exception

    def initialize_client(self) -> Client:
        """
        Initialize and authenticate API client.

        Returns:
            Client: Authenticated client.

        Raises:
            NetworkError: If authentication fails.
        """

        client = Client()
        user = self.settings.bluesky_consumer_key.get_secret_value()
        key = self.settings.bluesky_consumer_key_secret.get_secret_value()
        profile = self.execute_with_retry(lambda: client.login(user, key), action="authenticating client")
        logger.info("Initialized Bluesky API Client", user=profile.display_name)
        return client

    def get_did(self) -> str:
        """
        Retrieve user DID.

        Returns:
            str: User DID.

        Raises:
            NetworkError: If request fails.
        """

        response = self.execute_with_retry(
            lambda: self.client.resolve_handle(self.settings.bluesky_consumer_key.get_secret_value()),
            action="retrieving did",
        )
        logger.info("Retrieved DID", did=response.did)
        did = cast(str, response.did)
        return did
