import structlog
from pydantic import BaseModel, Field

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class RocketProvider(BaseModel):
    name: str
    slug: str


class RocketLaunchResult(BaseModel):
    id: int
    launch_description: str
    provider: RocketProvider


class RocketLaunch(BaseModel):
    result: list[RocketLaunchResult] = Field(..., min_length=1)
