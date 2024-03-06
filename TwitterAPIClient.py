import tweepy
import configparser
from RaspberryPiActions import renew_raspi_dhclient
from Blackbox import Blackbox

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

blackbox = Blackbox("APIClient")
blackbox_logger = blackbox.logger


class APIClient(object):

    def __init__(self):
        blackbox_logger.info("Initialized API Client")
        self.BEARER_TOKEN = ""
        self.API_KEY = ""
        self.API_KEY_SECRET = ""
        self.ACCESS_TOKEN = ""
        self.ACCESS_TOKEN_SECRET = ""
        self.CLIENT_ID = ""
        self.CLIENT_SECRET = ""

        self.import_config()
        self.client = self.initialize_client()
        self.api = self.initialize_api()
        # self.timeout_retry()
        # print(self.client.get_me())
        self.get_client_status()

    def import_config(self):
        try:
            blackbox_logger.info("Initialized method import_config")
            config = configparser.ConfigParser(interpolation=None)
            config.read("config.ini")
            self.BEARER_TOKEN = config["twitter"]["bearer_token"]
            self.API_KEY = config["twitter"]["api_key"]
            self.API_KEY_SECRET = config["twitter"]["api_key_secret"]
            self.ACCESS_TOKEN = config["twitter"]["access_token"]
            self.ACCESS_TOKEN_SECRET = config["twitter"]["access_token_secret"]
            self.CLIENT_ID = config["twitter"]["client_id"]
            self.CLIENT_SECRET = config["twitter"]["client_secret"]

        except KeyError:
            blackbox_logger.exception("method import_config")

    def initialize_client(self):
        blackbox_logger.info("Initialized method initialize_client")
        client = tweepy.Client(self.BEARER_TOKEN, self.API_KEY, self.API_KEY_SECRET,
                               self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
        blackbox_logger.info(f"GET client: {client}")
        return client

    def initialize_api(self):
        blackbox_logger.info("Initialized method initialize_api")
        auth = tweepy.OAuth1UserHandler(self.API_KEY, self.API_KEY_SECRET, self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        blackbox_logger.info(f"GET api: {api}")
        return api

    def get_client_status(self):
        try:
            blackbox_logger.info("Initialized method get_client_status")
            cient_status = self.client.get_me()
            blackbox_logger.info(f"GET status: {cient_status}")
        except:
            blackbox_logger.warning("TimeoutError method create_tweet")
            renew_raspi_dhclient()

    def create_tweet(self, message, timeout_retry=0):
        try:
            blackbox_logger.info("Initialized method create_tweet")
            blackbox_logger.info(f"GET create_tweet message len {len(message)}")
            if type(message) is str:
                if len(message) <= 280:
                    print("Tweet created")
                    print(message)
                    blackbox_logger.info(f"GET message: {message}")
                    self.client.create_tweet(text=message)
                else:
                    excuse_msg = "Houston, we have a problem! This celestial explorer is currently navigating through a cloud of confusion."
                    print(excuse_msg)
                    blackbox_logger.warning(f"GET message: {excuse_msg}")
                    self.client.create_tweet(text=excuse_msg)
            else:
                excuse_msg = "I'm experiencing a bit of cosmic confusion here. It seems the data is floating in a nebula of uncertainty."
                print(excuse_msg)
                blackbox_logger.warning(f"GET message: {excuse_msg}")
                self.client.create_tweet(text=excuse_msg)
        except TimeoutError:
            blackbox_logger.exception("method create_tweet")
            blackbox_logger.warning("TimeoutError method create_tweet")
            renew_raspi_dhclient()
            timeout_retry += 1
            if timeout_retry == 1:
                blackbox_logger.warning("Retry method create_tweet")
                self.create_tweet(message=message, timeout_retry=1)
        except:
            blackbox_logger.exception("method create_tweet")
            renew_raspi_dhclient()
            timeout_retry += 1
            if timeout_retry == 1:
                blackbox_logger.warning("Retry method create_tweet")
                self.create_tweet(message=message, timeout_retry=1)

    def timeout_retry(self):
        try:
            blackbox_logger.info("Initialized method timeout_retry")
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            self.client.session.mount('http://', adapter)
            self.client.session.mount('https://', adapter)
            # self.client.create_tweet(text=message)
        except:
            blackbox_logger.exception("method timeout_retry")
