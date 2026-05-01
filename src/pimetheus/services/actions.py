import random
import time
from urllib.parse import urlparse

import structlog
from atproto.exceptions import AtProtocolError
from httpx import NetworkError
from pydantic import ValidationError

from pimetheus.infrastructure.http.exceptions import HTTPClientError
from pimetheus.infrastructure.image.exceptions import ImageProcessingError
from pimetheus.infrastructure.image.processor import ImageProcessor
from pimetheus.infrastructure.raspberrypi.system import GroundControl
from pimetheus.infrastructure.storage.files import FileStorage
from pimetheus.infrastructure.storage.paths import ProjectPaths
from pimetheus.integrations.apis.google.client import GoogleSearchClient, GoogleSearchExtractor
from pimetheus.integrations.apis.nasa.client import NasaAPIClient, NasaApodExtractor, NasaEpicExtractor
from pimetheus.integrations.apis.rocketlaunch.client import RocketLaunchAPIClient, RocketLaunchExtractor
from pimetheus.services.engage import BlueskyEngager
from pimetheus.services.publish import Messenger
from pimetheus.utils.config import Settings

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class Bot:
    """
    High-level orchestration service for content creation and engagement.

    This class coordinates fetching data from external APIs, processing content,
    and publishing posts via the Messenger service. It also manages automated
    engagement workflows on Bluesky.
    """

    settings = Settings.load()
    MAX_IMAGE_SIZE_KB = 976
    MIN_SLEEP_TIME = 3300
    MAX_SLEEP_TIME = 3650

    def __init__(self) -> None:
        """
        Initialize the bot by ensuring all required project directories exist.
        """

        ProjectPaths.create_project_directories()

    def bot_sleep(self) -> int:
        """
        Sleep for a random interval to simulate human-like behavior.

        Returns:
            int: Sleep duration in seconds.
        """

        sleep_time = random.randint(self.MIN_SLEEP_TIME, self.MAX_SLEEP_TIME)
        logger.info("Sleeping", sleep_time=sleep_time)
        time.sleep(sleep_time)
        return sleep_time

    def create_launch_message(self) -> None:
        """
        Publish a static launch-themed message to social platforms.

        Raises:
            NetworkError: If publishing fails.
        """

        try:
            logger.info("Creating Launch Message")
            message = (
                "☀️ Sun's up, circuits activated. Preparing for another journey through the cosmos.\n\n"
                "What mysteries await today?"
            )
            tags = ["SpaceExploration", "Astronomy", "NewHorizons"]

            post_dict = {
                "message": message,
                "tags": tags,
            }
            messenger = Messenger(post_dict)
            messenger.create_posts()

        except NetworkError as e:
            logger.error("Failed to publish post", exc_info=e)
        finally:
            self.bot_sleep()

    def create_raspi_status_message(self) -> None:
        """
        Publish Raspberry Pi system status (temperature and uptime).

        Raises:
            NetworkError: If publishing fails.
        """

        logger.info("Creating Raspi Status Message")
        try:
            raspi = GroundControl()
            temperature = raspi.get_gpu_temperature()
            uptime = raspi.get_uptime()

            message = (
                f"📡 My CPU is keeping its cool at {temperature}°, operating within optimal parameters.\n\n"
                f"No signs of overheating in this electronic nebula. All systems are cruising smoothly since {uptime} through the cosmos."
            )
            tags = ["RaspberryPi", "Tech", "Monitoring"]

            post_dict = {
                "message": message,
                "tags": tags,
            }

            messenger = Messenger(post_dict)
            messenger.create_posts()

        except NetworkError as e:
            logger.error("Failed to publish post", exc_info=e)
        finally:
            self.bot_sleep()

    def create_google_search_message(self) -> None:
        """
        Publish a post generated from Google Custom Search results.

        Raises:
            HTTPClientError: If API request fails.
            ValidationError: If response validation fails.
            ValueError: If response parsing fails.
            NetworkError: If publishing fails.
        """

        logger.info("Creating Google Search Message")
        fetcher: GoogleSearchClient | None = None
        try:
            file_name = "googlesearch_queries.json"
            file = FileStorage(ProjectPaths.PROCESSED, file_name)
            data = file.read_json()
            query = random.choice(data["space_terms"])

            fetcher = GoogleSearchClient(search_query=query)
            validated_result = fetcher.get_validated_results()

            extractor = GoogleSearchExtractor(validated_result)
            post_dict = extractor.extract_google_search_data()

            messenger = Messenger(post_dict)
            messenger.create_posts()

        except HTTPClientError as e:
            logger.error(f"Failed to create google search message: {HTTPClientError.__name__}", exc_info=e)
        except ValidationError as e:
            logger.error("Failed to validate result", exc_info=e)
        except ValueError as e:
            logger.error("Failed to fetch json", exc_info=e)
        except NetworkError as e:
            logger.error("Failed to publish post", exc_info=e)
        finally:
            if fetcher is not None:
                fetcher.http_client.close()
            self.bot_sleep()

    def create_nasa_apod_message(self) -> None:
        """
        Fetch and publish NASA APOD content as image or video post.

        Raises:
            HTTPClientError: If API request fails.
            ValidationError: If response validation fails.
            ValueError: If parsing fails.
            NetworkError: If publishing fails.
        """

        logger.info("Creating NASA APOD Message")
        fetcher: NasaAPIClient | None = None
        try:
            fetcher = NasaAPIClient()
            validated_result = fetcher.get_validated_apod_results()

            extractor = NasaApodExtractor(validated_result)
            post_dict = extractor.extract_apod_data()
            image_url = str(post_dict.get("image_url"))

            response = fetcher.get_image_response(image_url)

            suffix = urlparse(image_url).path.split(".")[-1]
            file_name = f"apod.{suffix}"
            FileStorage(ProjectPaths.RAW, file_name).write_http_response(response)

            image_formats = ["jpg", "jpeg", "png"]
            if suffix in image_formats:
                processor = ImageProcessor(file_name)
                processor.compress_to_target(self.MAX_IMAGE_SIZE_KB)

                messenger = Messenger(post_dict)
                messenger.create_image_posts(file_name)
            elif suffix == "mp4":
                messenger = Messenger(post_dict)
                messenger.create_video_posts(file_name)

        except HTTPClientError as e:
            logger.error(f"Failed to create apod message: {HTTPClientError.__name__}", exc_info=e)
        except ValidationError as e:
            logger.error("Failed to validate result", exc_info=e)
        except ValueError as e:
            logger.error("Failed to fetch json", exc_info=e)
        except NetworkError as e:
            logger.error("Failed to publish post", exc_info=e)
        except ImageProcessingError as e:
            logger.error("Failed to process image", exc_info=e)
        finally:
            if fetcher is not None:
                fetcher.http_client.close()
            self.bot_sleep()

    def create_nasa_epic_message(self) -> None:
        """
        Fetch and publish NASA EPIC Earth imagery as an image post.

        Raises:
            HTTPClientError: If API request fails.
            ValidationError: If response validation fails.
            ValueError: If parsing fails.
            NetworkError: If publishing fails.
        """

        logger.info("Creating NASA EPIC Message")
        fetcher: NasaAPIClient | None = None
        try:
            fetcher = NasaAPIClient()
            validated_result = fetcher.get_validated_epic_results()

            extractor = NasaEpicExtractor(validated_result)
            post_dict = extractor.extract_epic_data()

            image_id = str(post_dict.get("image_id"))
            image_url = fetcher.build_epic_image_url(image_id)
            response = fetcher.get_image_response(image_url)

            file_name = "epic.jpg"
            FileStorage(ProjectPaths.RAW, file_name).write_http_response(response)

            processor = ImageProcessor(file_name)
            processor.compress_to_target(self.MAX_IMAGE_SIZE_KB)

            messenger = Messenger(post_dict)
            messenger.create_image_posts(file_name)

        except HTTPClientError as e:
            logger.error(f"Failed to create epic message: {HTTPClientError.__name__}", exc_info=e)
        except ValidationError as e:
            logger.error("Failed to validate result", exc_info=e)
        except ValueError as e:
            logger.error("Failed to fetch json", exc_info=e)
        except NetworkError as e:
            logger.error("Failed to publish post", exc_info=e)
        finally:
            if fetcher is not None:
                fetcher.http_client.close()
            self.bot_sleep()

    def create_rocket_launch_message(self) -> None:
        """
        Fetch and publish rocket launch announcement.

        Persists published launch IDs to avoid duplicates.

        Raises:
            HTTPClientError: If API request fails.
            ValidationError: If response validation fails.
            ValueError: If parsing fails.
            NetworkError: If publishing fails.
        """

        logger.info("Creating Rocket Launch Message")
        fetcher: RocketLaunchAPIClient | None = None
        try:
            fetcher = RocketLaunchAPIClient()
            validated_result = fetcher.get_validated_results()

            storage = FileStorage(ProjectPaths.PROCESSED, "rocketlaunch_records.json")
            published_ids = storage.read_json().get("published_launch_ids", [])

            extractor = RocketLaunchExtractor(validated_result, published_ids)
            post_dict = extractor.extract_rocket_launch_data()

            launch_id = post_dict.get("launch_id")
            published_ids.append(launch_id)
            storage.write_json({"published_launch_ids": published_ids})

            messenger = Messenger(post_dict)
            messenger.create_posts()

        except HTTPClientError as e:
            logger.error(f"Failed to create rocket launch message: {HTTPClientError.__name__}", exc_info=e)
        except ValidationError as e:
            logger.error("Failed to validate result", exc_info=e)
        except ValueError as e:
            logger.error("Failed to fetch json", exc_info=e)
        except NetworkError as e:
            logger.error("Failed to publish post", exc_info=e)
        finally:
            if fetcher is not None:
                fetcher.http_client.close()
            self.bot_sleep()

    def engage_on_bluesky(self) -> None:
        """
        Run automated engagement workflow on Bluesky.

        Performs liking, reposting, and following actions with randomized delays.

        Raises:
            AtProtocolError: If Bluesky API call fails.
            NetworkError: If network interaction fails.
        """

        logger.info("Starting Bluesky engagement")
        try:
            if self.settings.pimetheus.bluesky:
                engager = BlueskyEngager()

                engager.like_self_mentioned()
                engager.sleep_for_random_time()

                engager.like_random_author_posts_x_times(
                    actor=engager.get_random_esa_handle(), times=engager.get_random_likes_amount()
                )
                engager.sleep_for_random_time()

                engager.repost_latest_esa()
                engager.sleep_for_random_time()

                engager.like_random_author_posts_x_times(
                    actor=engager.get_random_space_handle(), times=engager.get_random_likes_amount()
                )
                engager.sleep_for_random_time()

                response = engager.like_random_authors_follower_posts_x_times(
                    actor=engager.get_random_esa_handle(), times=engager.get_random_likes_amount()
                )
                engager.save_likes_to_json(response)
                engager.sleep_for_random_time()

                hashtag = engager.get_random_space_hashtag()
                response = engager.follow_random_query_posts_author(
                    query=f"#{hashtag}", tag=[hashtag], since=engager.get_since_date()
                )
                engager.save_follows_to_json(response)
                engager.sleep_for_random_time()

                response = engager.like_random_authors_follows_posts_x_times(
                    actor=engager.get_random_esa_handle(), times=engager.get_random_likes_amount()
                )
                engager.save_likes_to_json(response)
                engager.sleep_for_random_time()

                hashtag = engager.get_random_space_hashtag()
                response = engager.follow_random_query_posts_author(
                    query=f"#{hashtag}", tag=[hashtag], since=engager.get_since_date()
                )
                engager.save_follows_to_json(response)
                engager.sleep_for_random_time()

                hashtag = engager.get_random_space_hashtag()
                response = engager.like_random_query_posts_x_times(
                    query=f"#{hashtag}",
                    tag=[hashtag],
                    since=engager.get_since_date(),
                    times=engager.get_random_likes_amount(),
                )
                engager.save_likes_to_json(response)
            else:
                logger.info("Simulated Bluesky Engagement")

            logger.info("Finished Bluesky engagement")

        except AtProtocolError as e:
            logger.error("Bluesky API error", exc_info=e)
        except NetworkError as e:
            logger.error("Failed to engage", exc_info=e)
        finally:
            self.bot_sleep()

    def unengage_on_bluesky(self) -> None:
        """
        Revert previously stored Bluesky engagement actions.

        Raises:
            AtProtocolError: If Bluesky API call fails.
            NetworkError: If network interaction fails.
        """

        logger.info("Starting Bluesky unengagement")
        try:
            if self.settings.pimetheus.bluesky:
                engager = BlueskyEngager()
                engager.unengage_likes_and_follows()
            else:
                logger.info("Simulated Bluesky unengagement")

            logger.info("Finished Bluesky unengagement")
        except AtProtocolError as e:
            logger.error("Bluesky API error", exc_info=e)
        except NetworkError as e:
            logger.error("Failed to engage", exc_info=e)
