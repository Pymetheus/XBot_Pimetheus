import random
from typing import Any

import httpx
import structlog
from pydantic import ValidationError

from pimetheus.infrastructure.http.client import HttpClient
from pimetheus.infrastructure.http.exceptions import HTTPClientError
from pimetheus.integrations.apis.nasa.schemas import NasaApod, NasaEpicCollection
from pimetheus.utils.config import Settings
from pimetheus.utils.date_utils import get_date
from pimetheus.validation.validators import SchemaValidator

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class NasaAPIClient:
    """
    Client for NASA API interactions.

    Attributes:
        http_client (HttpClient): HTTP client instance.
        api_key (str): NASA API key.
        base_url (str): Base API URL.
        apod_url (str): APOD endpoint.
        epic_url (str): EPIC base URL.
        epic_timedelta (int): Days offset for EPIC.
    """

    settings = Settings.load()

    def __init__(self) -> None:
        """
        Initialize the API client.
        """

        logger.info("Initializing NASA API Client")
        self.http_client = HttpClient()
        self.api_key = self.settings.nasa_api_key.get_secret_value()
        self.base_url = "https://api.nasa.gov"
        self.apod_url = f"{self.base_url}/planetary/apod"
        self.epic_url = "https://epic.gsfc.nasa.gov"
        self.epic_timedelta = 7

    def build_apod_params(self) -> dict[str, Any]:
        """
        Build APOD request parameters.

        Returns:
            dict[str, Any]: Query parameters.
        """

        parameters = {
            "api_key": self.api_key,
            "date": get_date(timedelta_days=0),
        }
        logger.info("Setting APOD parameters", date=parameters["date"])
        return parameters

    def build_epic_metadata_url(self) -> str:
        """
        Build EPIC metadata URL.

        Returns:
            str: Metadata URL.
        """

        date = str(get_date(timedelta_days=self.epic_timedelta))
        metadata_url = self.epic_url + "/api/natural/date/" + date
        logger.info("Setting EPIC metadata URL", date=date, url=metadata_url)
        return metadata_url

    def build_epic_image_url(self, image_id: str) -> str:
        """
        Build EPIC image URL.

        Parameters:
            image_id (str): Image identifier.

        Returns:
            str: Image URL.
        """

        date = get_date(timedelta_days=self.epic_timedelta)
        url = self.epic_url + f"/archive/natural/{date:%Y/%m/%d}/png/{image_id}.png"
        logger.info("Setting EPIC image URL", image_id=image_id, url=url)
        return url

    def get_validated_apod_results(self) -> NasaApod:
        """
        Fetch and validate APOD data.

        Returns:
            NasaApod: Validated APOD model.

        Raises:
            HTTPClientError: If request fails.
            ValidationError: If validation fails.
            ValueError: If JSON decoding fails.
        """

        try:
            params = self.build_apod_params()
            payload = self.http_client.fetch_json(url=self.apod_url, params=params)
            model = SchemaValidator(schema=NasaApod, payload=payload).validate_payload()
            return model

        except HTTPClientError:
            logger.error("Failed to fetch APOD response", url=self.apod_url)
            raise
        except ValidationError:
            logger.error("Failed to validate APOD response", url=self.apod_url)
            raise
        except ValueError:
            logger.error("Failed to decode APOD JSON response", url=self.apod_url)
            raise

    def get_validated_epic_results(self) -> NasaEpicCollection:
        """
        Fetch and validate EPIC data.

        Returns:
            NasaEpicCollection: Validated EPIC model.

        Raises:
            HTTPClientError: If request fails.
            ValidationError: If validation fails.
            ValueError: If JSON decoding fails.
        """

        url = self.build_epic_metadata_url()
        try:
            payload = self.http_client.fetch_json(url=url)
            model = SchemaValidator(schema=NasaEpicCollection, payload=payload).validate_payload()
            return model

        except HTTPClientError:
            logger.error("Failed to fetch EPIC response", url=url)
            raise
        except ValidationError:
            logger.error("Failed to validate EPIC response", url=url)
            raise
        except ValueError:
            logger.error("Failed to decode APOD EPIC response", url=url)
            raise

    def get_image_response(self, image_url: str) -> httpx.Response:
        """
        Fetch image response.

        Parameters:
            image_url (str): Image URL.

        Returns:
            httpx.Response: HTTP response.

        Raises:
            HTTPClientError: If request fails.
        """

        try:
            response = self.http_client.get_response(url=image_url)
            logger.info("Getting image response", url=image_url)
            return response
        except HTTPClientError:
            logger.exception("Failed to fetch image", url=image_url)
            raise


class NasaApodExtractor:
    """
    Extract APOD data.

    Attributes:
        search_results (NasaApod): APOD model.
    """

    def __init__(self, search_results: NasaApod) -> None:
        """
        Initialize the extractor.
        """
        self.search_results = search_results

    def extract_apod_data(self) -> dict[str, Any]:
        """
        Extract APOD fields.

        Returns:
            dict[str, Any]: Extracted data.

        Raises:
            AttributeError: If fields are missing.
        """

        title = self.search_results.title
        image_url = self.search_results.url
        copyright_info = self.search_results.copyright_info

        message = f"🔭 Astronomy Picture of the Day:\n{title}."
        tags = ["NASA", "Astronomy", "Astrophotography"]

        if copyright_info:
            copyright_info = copyright_info.replace("\n", " ")
            copyright_string = f"\nCopyright: {copyright_info}"
            message += copyright_string

        apod_dict = {
            "image_url": image_url,
            "media_desc": "Astronomy Picture of the Day",
            "message": message,
            "tags": tags,
        }
        logger.info("Extracted APOD data", apod_dict=apod_dict)
        return apod_dict


class NasaEpicExtractor:
    """
    Extract EPIC data.

    Attributes:
        search_results (NasaEpicCollection): EPIC model.
    """

    def __init__(self, search_results: NasaEpicCollection) -> None:
        """
        Initialize the extractor.
        """

        self.search_results = search_results

    def extract_epic_data(self) -> dict[str, Any]:
        """
        Extract EPIC item.

        Returns:
            dict[str, Any]: Extracted data.

        Raises:
            ValueError: If collection is empty.
        """

        item = random.randrange(len(self.search_results.root))
        selection = self.search_results.root[item]

        title = selection.caption
        image_id = selection.image
        date = selection.date

        message = f"🛰️ Impression from the Earth Polychromatic Imaging Camera:\n\n{title} on the {date.date()}."
        tags = ["NASA", "EPIC", "PlanetEarth", "EarthFromSpace"]

        epic_dict = {
            "item": item,
            "title": title,
            "image_id": image_id,
            "date": date,
            "media_desc": "Impression from the Earth Polychromatic Imaging Camera",
            "message": message,
            "tags": tags,
        }
        logger.info("Extracted EPIC data", epic_dict=epic_dict)
        return epic_dict
