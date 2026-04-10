from typing import Any

import structlog
import tweepy

from pimetheus.utils.config import Settings

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class TwitterAPIClient:
    """
    Client for interacting with X API.

    Attributes:
        settings (Settings): Configuration.
        client (tweepy.Client): API client.
        api (tweepy.API): OAuth1 API.
        offline (bool): Offline mode flag.
    """

    settings = Settings.load()

    def __init__(self) -> None:
        """
        Initialize the Twitter API client.
        Sets up both the Client and OAuth1 API.
        """

        logger.info("Initializing X API Client")
        self.client = self.initialize_client()
        self.api = self.initialize_api()
        self.offline = self.settings.pimetheus.offline

    def initialize_client(self) -> tweepy.Client:
        """
        Initialize Tweepy client.

        Returns:
            tweepy.Client: Authenticated client.
        """

        client = tweepy.Client(
            self.settings.x_bearer_token.get_secret_value(),
            self.settings.x_consumer_key.get_secret_value(),
            self.settings.x_consumer_key_secret.get_secret_value(),
            self.settings.x_access_token.get_secret_value(),
            self.settings.x_access_token_secret.get_secret_value(),
        )
        return client

    def initialize_api(self) -> tweepy.API:
        """
        Initialize OAuth1 API.

        Returns:
            tweepy.API: Authenticated API.
        """

        auth = tweepy.OAuth1UserHandler(
            self.settings.x_consumer_key.get_secret_value(),
            self.settings.x_consumer_key_secret.get_secret_value(),
            self.settings.x_access_token.get_secret_value(),
            self.settings.x_access_token_secret.get_secret_value(),
        )
        api = tweepy.API(auth)
        return api

    def get_client_status(self) -> int:
        """
        Check API connectivity.

        Returns:
            int: Status code.

        Raises:
            tweepy.TweepyException: If request fails.
        """

        logger.info("Getting client status")
        try:
            client_status = self.client.get_me()
            logger.info("Getting client status", status=client_status)
            return 200
        except tweepy.TwitterServerError as e:
            logger.error("Twitter Server Error", status=503, exc_info=e)
            return 503
        except Exception as e:
            logger.error("Unexpected error while getting client status", status=500, exc_info=e)
            return 500

    def post_tweet(self, message: str) -> tweepy.Response | bool:
        """
        Post text tweet.

        Parameters:
            message (str): Tweet content.

        Returns:
            tweepy.Response | bool: API response or offline flag.

        Raises:
            Exception: If request fails.
        """

        logger.info("Posting tweet")
        try:
            if self.offline:
                logger.info("Posted TEST", text=message, post_id="TEST")
                return self.offline
            else:
                response = self.client.create_tweet(text=message)
                logger.info("Posted tweet", text=message, post_id=response.data["id"])
                return response
        except TimeoutError:
            logger.warning("Timeout error when trying to post tweet", exc_info=TimeoutError)
            raise
        except Exception as e:
            logger.error("Error posting tweet", exc_info=e)
            raise

    def post_tweet_media(self, message: str, media: Any) -> tweepy.Response | bool:
        """
        Post tweet with media.

        Parameters:
            message (str): Tweet content.
            media (Any): Media object.

        Returns:
            tweepy.Response | bool: API response or offline flag.

        Raises:
            Exception: If request fails.
        """

        logger.info("Posting tweet with media")
        try:
            if self.offline:
                logger.info("Posted TEST media", text=message, post_id="TEST")
                return self.offline
            else:
                response = self.client.create_tweet(text=message, media_ids=[media.media_id])
                logger.info("Posted tweet with media", text=message, post_id=response.data["id"])
                return response
        except TimeoutError:
            logger.warning("Timeout error when trying to post tweet with media", exc_info=TimeoutError)
            raise
        except Exception as e:
            logger.error("Error posting tweet with media", exc_info=e)
            raise
