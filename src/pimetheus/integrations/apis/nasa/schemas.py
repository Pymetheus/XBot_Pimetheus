from datetime import date, datetime

import structlog
from pydantic import BaseModel, Field, HttpUrl, RootModel

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class NasaApod(BaseModel):
    """
    Astronomy Picture of the Day response.
    """

    date: date
    explanation: str
    title: str
    url: str
    hdurl: HttpUrl | None = None
    copyright_info: str | None = None


class NasaEpicCoordinates(BaseModel):
    """
    Geographic coordinates for the EPIC image centroid.
    """

    lat: float
    lon: float


class NasaEpicItem(BaseModel):
    """
    Single EPIC image metadata entry.
    """

    caption: str
    image: str
    date: datetime
    centroid_coordinates: NasaEpicCoordinates


class NasaEpicCollection(RootModel[list[NasaEpicItem]]):
    """
    Collection of EPIC image items.
    """

    root: list[NasaEpicItem] = Field(..., min_length=1)
