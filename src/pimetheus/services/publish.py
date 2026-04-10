from typing import Any

import structlog
import tweepy
from atproto_client.models.app.bsky.feed.post import CreateRecordResponse
from httpx import NetworkError

from pimetheus.infrastructure.storage.files import FileStorage
from pimetheus.infrastructure.storage.paths import ProjectPaths
from pimetheus.integrations.publish.bluesky.client import BlueskyAPIClient
from pimetheus.integrations.publish.bluesky.creator import BlueskyCreator
from pimetheus.integrations.publish.bluesky.schemas import BlueSkyMediaTweet, BlueSkyVideoTweet, BluSkyTweet
from pimetheus.integrations.publish.twitter.client import TwitterAPIClient
from pimetheus.integrations.publish.twitter.schemas import TwitterTweet
from pimetheus.utils.config import Settings

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class Messenger:
    """
    Publish messages to Twitter/X and Bluesky.

    Attributes:
        settings (Settings): Global configuration.
        message_dict (dict[str, Any]): Message payload.
        twitter_client (TwitterAPIClient): X platform client.
        bluesky_client (BlueskyAPIClient): Bluesky client.
        bluesky_creator (BlueskyCreator): Bluesky posting handler.
        twitter (bool): Enable X posting.
        bluesky (bool): Enable Bluesky posting.
    """

    settings = Settings.load()

    def __init__(self, message_dict: dict[str, Any]) -> None:
        """
        Initialize the Messenger with message data and platform clients.

        Args:
            message_dict (dict[str, Any]): Dictionary containing keys such as:
                - "message" (str): The post text.
                - "hyperlink" (str, optional): URL to attach to the post.
                - "tags" (list[str], optional): List of hashtags.
                - "image"/"video" (bytes, optional): Media content for BlueSky posts.
        """

        logger.info("Starting Messenger")
        self.message_dict = message_dict

        self.twitter_client = TwitterAPIClient()
        self.bluesky_client = BlueskyAPIClient()
        self.bluesky_creator = BlueskyCreator(self.bluesky_client)

        self.twitter = self.settings.pimetheus.twitter
        self.bluesky = self.settings.pimetheus.bluesky

    def create_twitter_message(self) -> str:
        """
        Build formatted X post text.

        Returns:
            str: Formatted tweet text.
        """

        message = self.message_dict.get("message")
        hyperlink = self.message_dict.get("hyperlink")
        tags = self.message_dict.get("tags")

        twitter_message = f"{message}\n"
        if hyperlink:
            twitter_message += f"{hyperlink}\n"
        if tags:
            tag_string = ""
            for tag in tags:
                tag_string += f"#{tag} "
            twitter_message += tag_string

        return twitter_message

    def create_posts(self) -> None:
        """
        Publish text posts to enabled platforms.

        Returns:
            None

        Raises:
            NetworkError: If publishing fails.
        """

        logger.info("Creating posts")
        try:
            if self.twitter:
                twitter_message = self.create_twitter_message()
                post = TwitterTweet(message=twitter_message).message
                twitter_response = self.twitter_client.post_tweet(post)

                if isinstance(twitter_response, tweepy.Response):
                    logger.info("Created X post")

            if self.bluesky:
                bluesky_msg = BluSkyTweet.model_validate(self.message_dict)
                bluesky_response = self.bluesky_creator.post_tweet(
                    message=bluesky_msg.message,
                    hypertext=bluesky_msg.hypertext,
                    hyperlink=bluesky_msg.hyperlink,
                    tags=bluesky_msg.tags,
                )

                if isinstance(bluesky_response, CreateRecordResponse):
                    logger.info("Created Bluesky post")

        except NetworkError:
            logger.error("Failed to create post")
            raise

    def create_image_posts(self, file_name: str) -> None:
        """
        Publish image posts to enabled platforms.

        Parameters:
            file_name (str): Image filename.

        Returns:
            None

        Raises:
            NetworkError: If publishing fails.
        """

        logger.info("Creating media posts")
        try:
            if self.twitter:
                twitter_message = self.create_twitter_message()
                post = TwitterTweet(message=twitter_message).message

                file_path = ProjectPaths.PROCESSED / file_name
                twitter_api = self.twitter_client.api
                media = twitter_api.media_upload(filename=file_path)
                twitter_response = self.twitter_client.post_tweet_media(post, media)

                if isinstance(twitter_response, tweepy.Response):
                    logger.info("Created X post")

            if self.bluesky:
                image = FileStorage(ProjectPaths.PROCESSED, file_name)
                self.message_dict["image"] = image.read_image_bytes()

                bluesky_msg = BlueSkyMediaTweet.model_validate(self.message_dict)
                bluesky_response = self.bluesky_creator.post_tweet_image(
                    image=bluesky_msg.image,
                    image_desc=bluesky_msg.media_desc,
                    message=bluesky_msg.message,
                    hypertext=bluesky_msg.hypertext,
                    hyperlink=bluesky_msg.hyperlink,
                    tags=bluesky_msg.tags,
                )

                if isinstance(bluesky_response, CreateRecordResponse):
                    logger.info("Created Bluesky post")

        except NetworkError:
            logger.error("Failed to create post")
            raise

    def create_video_posts(self, file_name: str) -> None:
        """
        Publish video posts to enabled platforms.

        Parameters:
            file_name (str): Video filename.

        Returns:
            None

        Raises:
            NetworkError: If publishing fails.
        """

        logger.info("Creating media posts")
        try:
            if self.twitter:
                twitter_message = self.create_twitter_message()
                post = TwitterTweet(message=twitter_message).message

                file_path = ProjectPaths.RAW / file_name
                twitter_api = self.twitter_client.api
                media = twitter_api.media_upload(filename=file_path)
                twitter_response = self.twitter_client.post_tweet_media(post, media)

                if isinstance(twitter_response, tweepy.Response):
                    logger.info("Created X post")

            if self.bluesky:
                video = FileStorage(ProjectPaths.RAW, file_name)
                self.message_dict["video"] = video.read_image_bytes()

                bluesky_msg = BlueSkyVideoTweet.model_validate(self.message_dict)
                bluesky_response = self.bluesky_creator.post_tweet_video(
                    video=bluesky_msg.video,
                    video_desc=bluesky_msg.media_desc,
                    message=bluesky_msg.message,
                    hypertext=bluesky_msg.hypertext,
                    hyperlink=bluesky_msg.hyperlink,
                    tags=bluesky_msg.tags,
                )

                if isinstance(bluesky_response, CreateRecordResponse):
                    logger.info("Created Bluesky post")

        except NetworkError:
            logger.error("Failed to create post")
            raise
