from typing import Any

import structlog
from pydantic import ValidationError

from pimetheus.infrastructure.http.client import HttpClient
from pimetheus.infrastructure.http.exceptions import HTTPClientError
from pimetheus.integrations.apis.google.schemas import GoogleSearchItems
from pimetheus.utils.config import Settings
from pimetheus.validation.validators import SchemaValidator

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class GoogleSearchClient:
    """
    Client for Google Custom Search API.

    Attributes:
        settings (Settings): Application configuration.
        search_query (str): Search query.
        http_client (HttpClient): HTTP client instance.
        api_key (SecretStr): API key.
        search_engine_id (SecretStr): Search engine ID.
        url (str): API endpoint.
        site_search (str): Domain filter.
    """

    settings = Settings.load()

    def __init__(self, search_query: str) -> None:
        """
        Initialize the API client.
        """

        logger.info("Initializing Custom Search API Client")
        self.search_query = search_query
        self.http_client = HttpClient()
        self.api_key = self.settings.google_api_key
        self.search_engine_id = self.settings.google_search_engine_id
        self.url = "https://www.googleapis.com/customsearch/v1"
        self.site_search = "https://en.wikipedia.org"

    def build_search_params(self) -> dict[str, Any]:
        """
        Build API query parameters.

        Returns:
            dict[str, Any]: Query parameters.
        """

        parameters = {
            "q": self.search_query,
            "key": self.api_key.get_secret_value(),
            "cx": self.search_engine_id.get_secret_value(),
            "lr": "lang_en",
            "siteSearch": self.site_search,
        }
        logger.info("Setting custom search parameters", query=self.search_query, siteSearch=self.site_search)

        return parameters

    def get_validated_results(self) -> GoogleSearchItems:
        """
        Fetch and validate search results.

        Returns:
            GoogleSearchItems: Validated response model.

        Raises:
            HTTPClientError: If request fails.
            ValidationError: If validation fails.
            ValueError: If JSON decoding fails.
        """

        try:
            payload = self.http_client.fetch_json(url=self.url, params=self.build_search_params())
            model = SchemaValidator(schema=GoogleSearchItems, payload=payload).validate_payload()
            return model

        except HTTPClientError:
            logger.error("Failed to fetch custom search response", url=self.url)
            raise
        except ValidationError:
            logger.error("Failed to validate custom search response", url=self.url)
            raise
        except ValueError:
            logger.error("Failed to decode custom search JSON response", url=self.url, query=self.search_query)
            raise


class GoogleSearchExtractor:
    """
    Extract structured data from search results.

    Attributes:
        search_results (GoogleSearchItems): Search results.
    """

    def __init__(self, search_results: GoogleSearchItems) -> None:
        """
        Initialize the extractor.

        Args:
            search_results (GoogleSearchItems): Validated search response.
        """

        self.search_results = search_results

    def extract_google_search_data(self) -> dict[str, Any]:
        """
        Build message payload from search results.

        Returns:
            dict[str, Any]: Message, hyperlink, and tags.

        Raises:
            IndexError: If expected fields are missing.
        """

        search_query = self.search_results.queries.request[0].search_terms
        search_query_string = search_query.replace(" ", "")

        hyperlink = self.search_results.items[0].link

        snippet = self.search_results.items[0].snippet
        snippet_result = str(snippet).encode("utf8").decode("ascii", "ignore").capitalize()

        message = f"{snippet_result}\n📖 Read more at:"

        post_dict = {"message": message, "hyperlink": hyperlink, "tags": [search_query_string, "Explore", "Space"]}

        logger.info("Extracted message", post_dict=post_dict)
        return post_dict
