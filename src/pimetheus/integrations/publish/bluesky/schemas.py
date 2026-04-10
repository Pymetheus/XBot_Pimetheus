import structlog
from pydantic import BaseModel, Field, field_validator

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class BluSkyTweet(BaseModel):
    """
    Model representing a BlueSky post.

    Attributes:
        message (str): The post message (10–280 characters).
        hypertext (Optional[str]): Optional additional text or markup.
        hyperlink (Optional[HttpUrl]): Optional URL associated with the post.
        tags (Optional[list[str]]): Optional list of tags.
    """

    message: str = Field(default="Houston, we have a problem!", description="BluSky post message")
    hypertext: str | None = None
    hyperlink: str | None = None
    tags: list[str] | None = None

    @field_validator("message")
    @classmethod
    def fallback_to_default(cls, msg: str) -> str:
        if len(msg) < 10 or len(msg) > 280:
            fallback_post = cls.model_fields["message"].default
            logger.error("Failed to validate BlueSky post", text=msg, fallback_post=fallback_post)
            return str(fallback_post)

        logger.info("Validated BlueSky post", text=msg)
        return msg


class BlueSkyMediaTweet(BluSkyTweet):
    """
    Model representing a BlueSky post containing an image.

    Inherits all fields from BluSkyTweet and adds media-specific attributes.

    Attributes:
        image (bytes): The image content to attach to the post.
        media_desc (str): A short description of the image for context.
    """

    image: bytes
    media_desc: str


class BlueSkyVideoTweet(BluSkyTweet):
    """
    Model representing a BlueSky post containing a video.

    Inherits all fields from BluSkyTweet and adds media-specific attributes.

    Attributes:
        video (bytes): The video content to attach to the post.
        media_desc (str): A short description of the video for context.
    """

    video: bytes
    media_desc: str
