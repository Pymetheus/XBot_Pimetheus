import structlog
from pydantic import BaseModel, Field

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class SearchItem(BaseModel):
    """
    Single search result item returned by Google Custom Search.
    """

    title: str
    link: str
    snippet: str


class SearchInformation(BaseModel):
    """
    Metadata about the search request.
    """

    search_time: float = Field(..., alias="searchTime")
    total_results: int = Field(..., alias="totalResults")


class QueryInformation(BaseModel):
    """
    Represents a search query returned in the API response.
    """

    search_terms: str = Field(..., alias="searchTerms")


class Queries(BaseModel):
    """
    Query metadata containing the original search request.
    """

    request: list[QueryInformation] = Field(..., min_length=1)


class GoogleSearchItems(BaseModel):
    """
    Root response model for Google Custom Search API.
    """

    items: list[SearchItem] = Field(..., min_length=1)
    search_information: SearchInformation = Field(..., alias="searchInformation")
    queries: Queries
