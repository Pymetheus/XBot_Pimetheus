from typing import Any

import structlog
from pydantic import ValidationError

from pimetheus.infrastructure.http.client import HttpClient
from pimetheus.infrastructure.http.exceptions import HTTPClientError
from pimetheus.integrations.apis.rocketlaunch.schemas import RocketLaunch
from pimetheus.validation.validators import SchemaValidator

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class RocketLaunchAPIClient:
    """
    Client for RocketLaunch API.

    Attributes:
        http_client (HttpClient): HTTP client instance.
        base_url (str): API endpoint.
    """

    def __init__(self) -> None:
        """
        Initialize the RocketLaunch API client.
        Sets up the HTTP client and endpoint URL for fetching upcoming launches.
        """

        self.http_client = HttpClient()
        self.base_url = "https://fdo.rocketlaunch.live/json/launches/next/5"

    def get_validated_results(self) -> RocketLaunch:
        """
        Fetch and validate rocket launch data.

        Returns:
            RocketLaunch: Validated response model.

        Raises:
            HTTPClientError: If request fails.
            ValidationError: If validation fails.
            ValueError: If JSON decoding fails.
        """

        try:
            payload = self.http_client.fetch_json(url=self.base_url)
            model = SchemaValidator(schema=RocketLaunch, payload=payload).validate_payload()
            return model

        except HTTPClientError:
            logger.error("Failed to fetch RocketLaunch payload", url=self.base_url)
            raise
        except ValidationError:
            logger.error("Failed to validate RocketLaunch response", url=self.base_url)
            raise
        except ValueError:
            logger.error("Failed to decode RocketLaunch JSON response", url=self.base_url)
            raise


class RocketLaunchExtractor:
    """
    Extract rocket launch data.

    Attributes:
        search_results (RocketLaunch): Launch data.
        item_index (int): Selected launch index.
    """

    def __init__(self, search_results: RocketLaunch, published_ids: list[int]) -> None:
        """
        Initialize the extractor and determine the index of the next unpublished launch.
        """

        self.search_results = search_results
        self.item_index = self.set_item_index(published_ids)

    def set_item_index(self, published_ids: list[int]) -> int:
        """
        Select index of first unpublished launch.

        Parameters:
            published_ids (list[int]): Published launch IDs.

        Returns:
            int: Selected index.

        Raises:
            ValueError: If no launches are available.
        """

        rocket_launch_ids = [item.id for item in self.search_results.result]

        for index, launch_id in enumerate(rocket_launch_ids):
            if launch_id not in published_ids:
                item_index = index
                logger.info("Setting item index", item_index=item_index, launch_id=launch_id)
                return index

        default_index = 0
        logger.warning("Fallback to default item index", item_index=default_index)
        return default_index

    def extract_rocket_launch_data(self) -> dict[str, Any]:
        """
        Extract launch data from selected item.

        Returns:
            dict[str, Any]: Launch data.

        Raises:
            IndexError: If selected index is invalid.
            AttributeError: If expected fields are missing.
        """

        selection = self.search_results.result[self.item_index]
        launch_id = selection.id
        launch_description = selection.launch_description
        provider = selection.provider.name.replace(" ", "")

        message = f"🚀 Upcoming rocket launch:\n\n{launch_description}"
        tags = [provider, "RocketLaunch", "SpaceFlight"]

        rocket_launch_dict = {
            "launch_id": launch_id,
            "message": message,
            "tags": tags,
        }

        return rocket_launch_dict
