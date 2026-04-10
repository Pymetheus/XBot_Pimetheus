import structlog
from atproto import client_utils
from atproto_client.models.app.bsky.feed.post import CreateRecordResponse

from pimetheus.integrations.publish.bluesky.client import BlueskyAPIClient

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class BlueskyCreator:
    """
    Build and publish posts to Bluesky.

    Attributes:
        blueskyapi (BlueskyAPIClient): API client.
        client (Client): Underlying Bluesky client.
        text_builder (TextBuilder): Post builder.
    """

    def __init__(self, blueskyapi: BlueskyAPIClient) -> None:
        self.blueskyapi = blueskyapi
        self.client = blueskyapi.client
        self.text_builder = client_utils.TextBuilder()

    def resolve_message(self, message: str) -> None:
        """
        Parse message and add hashtags to builder.

        Parameters:
            message (str): Input message.

        Returns:
            None

        Raises:
            None
        """

        hash_index = message.find("#")

        if hash_index != -1:
            pre_message = message[:hash_index]

            if len(pre_message) > 0:
                self.text_builder.text(pre_message)

            mid_message = message[hash_index + 1 :]
            suf_message = mid_message.split(sep=" ", maxsplit=1)

            tag = suf_message[0]
            tag_text = f"#{tag} "
            self.text_builder.tag(tag_text, tag)

            if len(suf_message) > 1:
                rest_message = suf_message[1]
                self.resolve_message(rest_message)

        else:
            message = message + " "
            self.text_builder.text(message)

    def build_text(
        self, message: str, hypertext: str | None = None, hyperlink: str | None = None, tags: list[str] | None = None
    ) -> None:
        """
        Build structured post text.

        Parameters:
            message (str): Post content.
            hypertext (str | None): Link display text.
            hyperlink (str | None): URL.
            tags (list[str] | None): Hashtags.

        Returns:
            None

        Raises:
            None
        """

        self.text_builder = client_utils.TextBuilder()
        self.resolve_message(message)

        if hyperlink:
            hyperlink = str(hyperlink)

            if hypertext:
                hypertext = hypertext + " "
            else:
                hypertext = hyperlink + " "
            self.text_builder.link(hypertext, hyperlink)

        if tags:
            self.text_builder.text("\n\n")
            for tag in tags:
                tag_text = f"#{tag} "
                self.text_builder.tag(tag_text, tag)
        logger.info("Build post message", message=message, hypertext=hypertext, hyperlink=hyperlink, tags=tags)

    def post_tweet(
        self, message: str, hypertext: str | None = None, hyperlink: str | None = None, tags: list[str] | None = None
    ) -> CreateRecordResponse | bool:
        """
        Post text message.

        Parameters:
            message (str): Post content.
            hypertext (str | None): Link text.
            hyperlink (str | None): URL.
            tags (list[str] | None): Hashtags.

        Returns:
            CreateRecordResponse | bool: API response or offline flag.

        Raises:
            Exception: If posting fails.
        """

        if self.blueskyapi.settings.pimetheus.offline:
            logger.info("Posted TEST", text=message, post_id="TEST")
            return self.blueskyapi.settings.pimetheus.offline

        self.build_text(message, hypertext, hyperlink, tags)

        response = self.blueskyapi.execute_with_retry(
            lambda: self.client.send_post(self.text_builder), action="posting tweet"
        )
        logger.info("Posted tweet", text=message, uri=response.uri, cid=response.cid)
        return response

    def post_tweet_image(
        self,
        image: bytes,
        image_desc: str,
        message: str,
        hypertext: str | None = None,
        hyperlink: str | None = None,
        tags: list[str] | None = None,
    ) -> CreateRecordResponse | bool:
        """
        Post image with message.

        Parameters:
            image (bytes): Image content.
            image_desc (str): Alt text.
            message (str): Post content.
            hypertext (str | None): Link text.
            hyperlink (str | None): URL.
            tags (list[str] | None): Hashtags.

        Returns:
            CreateRecordResponse | bool: API response or offline flag.

        Raises:
            Exception: If posting fails.
        """

        if self.blueskyapi.settings.pimetheus.offline:
            logger.info("Posted TEST image", text=message, post_id="TEST")
            return self.blueskyapi.settings.pimetheus.offline

        self.build_text(message, hypertext, hyperlink, tags)

        response = self.blueskyapi.execute_with_retry(
            lambda: self.client.send_image(image=image, image_alt=image_desc, text=self.text_builder),
            action="posting image tweet",
        )
        logger.info("Posted image tweet", text=message, uri=response.uri, cid=response.cid)
        return response

    def post_tweet_video(
        self,
        video: bytes,
        video_desc: str,
        message: str,
        hypertext: str | None = None,
        hyperlink: str | None = None,
        tags: list[str] | None = None,
    ) -> CreateRecordResponse | bool:
        """
        Post video with message.

        Parameters:
            video (bytes): Video content.
            video_desc (str): Alt text.
            message (str): Post content.
            hypertext (str | None): Link text.
            hyperlink (str | None): URL.
            tags (list[str] | None): Hashtags.

        Returns:
            CreateRecordResponse | bool: API response or offline flag.

        Raises:
            Exception: If posting fails.
        """

        if self.blueskyapi.settings.pimetheus.offline:
            logger.info("Posted TEST video", text=message, post_id="TEST")
            return self.blueskyapi.settings.pimetheus.offline

        self.build_text(message, hypertext, hyperlink, tags)

        response = self.blueskyapi.execute_with_retry(
            lambda: self.client.send_video(video=video, video_alt=video_desc, text=self.text_builder),
            action="posting video tweet",
        )
        logger.info("Posted video tweet", text=message, uri=response.uri, cid=response.cid)
        return response
