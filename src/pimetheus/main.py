import sys
import time
from io import TextIOWrapper
from typing import cast

import structlog

from pimetheus.infrastructure.storage.paths import ProjectPaths
from pimetheus.services.actions import Bot
from pimetheus.utils.config import Settings
from pimetheus.utils.logger import setup_logging

stdout = cast(TextIOWrapper, sys.stdout)
stdout.reconfigure(encoding="utf-8")

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)
setup_logging(write_to_disk=True, log_dir=ProjectPaths().LOGS)
settings = Settings.load()


def pimetheus() -> None:
    """
    Execute a full bot cycle consisting of content creation and engagement.

    Summary:
        Runs a fixed sequence of 12 content-generation steps, each followed
        by a Bluesky engagement routine.

    Behavior:
        - Publishes different types of posts (static, NASA, Google, etc.)
        - Triggers engagement after each post
        - Tracks total runtime for observability

    Returns:
        None
    """

    logger.info("Bot started", app=settings.app_name)
    start_time = time.time()
    bot = Bot()

    logger.info("Step 1/12: Launch Message", runtime=(time.time() - start_time))
    bot.create_launch_message()
    bot.engage_on_bluesky()

    logger.info("Step 2/12: Raspi Message", runtime=(time.time() - start_time))
    bot.create_raspi_status_message()
    bot.engage_on_bluesky()

    logger.info("Step 3/12: Epic Message", runtime=(time.time() - start_time))
    bot.create_nasa_epic_message()
    bot.engage_on_bluesky()

    logger.info("Step 4/12: Google Message", runtime=(time.time() - start_time))
    bot.create_google_search_message()
    bot.engage_on_bluesky()

    logger.info("Step 5/12: Apod Message", runtime=(time.time() - start_time))
    bot.create_nasa_apod_message()
    bot.engage_on_bluesky()

    logger.info("Step 6/12: Raspi Message", runtime=(time.time() - start_time))
    bot.create_raspi_status_message()
    bot.engage_on_bluesky()

    logger.info("Step 7/12: Epic Message", runtime=(time.time() - start_time))
    bot.create_nasa_epic_message()
    bot.engage_on_bluesky()

    logger.info("Step 8/12: Google Message", runtime=(time.time() - start_time))
    bot.create_google_search_message()
    bot.engage_on_bluesky()

    logger.info("Step 9/12: Rocket Launch Message", runtime=(time.time() - start_time))
    bot.create_rocket_launch_message()
    bot.engage_on_bluesky()

    logger.info("Step 10/12: Raspi Message", runtime=(time.time() - start_time))
    bot.create_raspi_status_message()
    bot.engage_on_bluesky()

    logger.info("Step 11/12: Epic Message", runtime=(time.time() - start_time))
    bot.create_nasa_epic_message()
    bot.engage_on_bluesky()

    logger.info("Step 12/12: Google Message", runtime=(time.time() - start_time))
    bot.create_google_search_message()
    bot.engage_on_bluesky()

    logger.info("Bot ended", app=settings.app_name, runtime=(time.time() - start_time))


def main() -> None:
    """
    Entry point for the Pimetheus bot application.

    Summary:
        Runs the bot continuously in an infinite loop, executing full
        content and engagement cycles.

    Behavior:
        - Executes repeated bot cycles via `pimetheus()`
        - Tracks number of completed rounds
        - Performs unengagement (unlike/unfollow) every 3 rounds

    Raises:
        Exception: Logs and suppresses any unhandled runtime errors to avoid crash.
    """

    logger.info("Application started", app=settings.app_name)
    try:
        rounds = 0
        while True:
            logger.info("Pimetheus running", rounds=rounds)
            pimetheus()
            rounds += 1

            if rounds % 3 == 0:
                bot = Bot()
                logger.info("Unengage step: Unengage", rounds=rounds)
                bot.unengage_on_bluesky()

    except Exception as e:
        logger.exception("Unhandled exception", e=e)

    logger.info("Application ended", app=settings.app_name)


if __name__ == "__main__":
    main()
