from RaspberryPiActions import get_raspi_gpu_temperature, get_raspi_up_time
from TwitterAPIClient import APIClient
from GoogleCustomSearchEngine import CustomSearchEngine
from Blackbox import Blackbox

blackbox = Blackbox("BotAction")
blackbox_logger = blackbox.logger


def create_tweet_morning_message():
    blackbox_logger.info("Initialized method create_tweet_morning_message")
    morning_message = "Sun's up, circuits activated. Ready to orbit through another day on this cosmic journey.\n" \
                      "#spaceexploration #interstellar #experience"
    PimetheusClient = APIClient()
    PimetheusClient.create_tweet(morning_message)


def create_tweet_raspi_status_message():
    blackbox_logger.info("Initialized method create_tweet_raspi_status_message")
    temperature = get_raspi_gpu_temperature()
    up_time = get_raspi_up_time()
    status_message = f"My CPU is keeping its cool at {temperature}°, operating within optimal parameters. " \
                     f"No signs of overheating in this electronic nebula. All systems are cruising smoothly since {up_time} through the cosmos.\n" \
                     f"#raspberrypi #cpu #temp"
    PimetheusClient = APIClient()
    PimetheusClient.create_tweet(status_message)


def create_tweet_information_message(message_term):
    blackbox_logger.info("Initialized method create_tweet_information_message")
    PimetheusEngine = CustomSearchEngine()
    message_output = PimetheusEngine.execute_custom_search_message_creation(message_term)

    PimetheusClient = APIClient()
    PimetheusClient.create_tweet(message_output)


def create_tweet_joke_message(message_joke):
    blackbox_logger.info("Initialized method create_tweet_joke_message")
    PimetheusClient = APIClient()
    PimetheusClient.create_tweet(message_joke)


def create_tweet_quote_message(message_quot):
    blackbox_logger.info("Initialized method create_tweet_quote_message")
    PimetheusClient = APIClient()
    PimetheusClient.create_tweet(message_quot)
