import structlog
from pydantic import BaseModel, Field, field_validator

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class TwitterTweet(BaseModel):
    """
    Model representing a Twitter post.

    Attributes:
        message (str): The post message (10–280 characters).
    """

    message: str = Field(default="Houston, we have a problem!", description="Twitter post message")

    @field_validator("message")
    @classmethod
    def fallback_to_default(cls, msg: str) -> str:
        if len(msg) < 10 or len(msg) > 280:
            fallback_post = cls.model_fields["message"].default
            logger.error("Failed to validate X post", text=msg, fallback_post=fallback_post)
            return str(fallback_post)

        logger.info("Validated X post", text=msg)
        return msg
