import configparser
import requests
from Blackbox import Blackbox

blackbox = Blackbox("CS_Engine")
blackbox_logger = blackbox.logger


class CustomSearchEngine(object):

    def __init__(self):
        blackbox_logger.info("Initialized CustomSearchEngine")
        self.API_KEY = ""
        self.SEARCH_ENGINE_ID = ""
        self.import_config()

    def import_config(self):
        try:
            blackbox_logger.info("Initialized method import_config")
            config = configparser.ConfigParser(interpolation=None)
            config.read(".config/config.ini")
            self.API_KEY = config["google"]["api_key"]
            self.SEARCH_ENGINE_ID = config["google"]["search_engine_id"]
        except KeyError:
            blackbox_logger.exception("method import_config")

    def set_custom_search_parameters(self, search_query):
        blackbox_logger.info("Initialized method set_custom_search_parameters")
        blackbox_logger.info(f"GET search query: {search_query}")
        parameter = {
            'q': search_query,
            'key': self.API_KEY,
            'cx': self.SEARCH_ENGINE_ID,
            'lr': 'lang_en',
            'siteSearch': 'https://en.wikipedia.org'
        }
        blackbox_logger.info(f"SET parameters to {parameter}")
        return parameter

    def get_custom_search_results(self, params):
        try:
            blackbox_logger.info("Initialized method get_custom_search_results")
            url = 'https://www.googleapis.com/customsearch/v1'
            response = requests.get(url, params=params)
            results = response.json()
            blackbox_logger.info(f"GET results: {str(results).encode('utf8').decode('ascii', 'ignore')}")
            return results
        except:
            blackbox_logger.exception(f"method get_custom_search_results")

    def get_custom_search_metadata_results(self, results):
        try:
            blackbox_logger.info("Initialized method get_custom_search_metadata_results")
            search_query = results['queries']['request'][0]['searchTerms']
            search_time = results['searchInformation']['searchTime']
            total_results = results['searchInformation']['totalResults']
            search_query_string = str(search_query).replace(" ", "")
            metadata_text = f"Used Search API to find #{search_query_string}.\n{total_results} results in {round(search_time, 2)} sec."

            blackbox_logger.info(f"GET metadata: {metadata_text}")
            return metadata_text
        except:
            blackbox_logger.exception(f"method get_custom_search_metadata_results")

    def get_custom_search_url_results(self, results):
        try:
            blackbox_logger.info("Initialized method get_custom_search_url_results")
            url_result = results['items'][0]['link']
            snippet_result = results['items'][0]['snippet']
            search_result_text = url_result + "\n" + snippet_result

            # Added encoding to avoid UnicodeEncodeError: 'charmap' codec can't encode character
            search_result_text = str(search_result_text).encode('utf8').decode('ascii', 'ignore')

            blackbox_logger.info(f"GET search result text: {search_result_text}")
            return search_result_text
        except:
            blackbox_logger.exception(f"method get_custom_search_url_results")

    def create_custom_search_result_message(self, metadata, url_snippet):
        try:
            blackbox_logger.info("Initialized method create_custom_search_result_message")
            result_message = metadata + "\n" + url_snippet
            blackbox_logger.info(f"GET search result message: {result_message}")
            blackbox_logger.info(f"GET search result message length: {len(result_message)}")
            blackbox_logger.info(f"GET search result message type: {type(result_message)}")
            return result_message

        except:
            blackbox_logger.exception(f"method create_custom_search_result_message")

    def execute_custom_search_message_creation(self, search_query):
        blackbox_logger.info("Initialized method execute_custom_search_message_creation")
        search_parameter = self.set_custom_search_parameters(search_query)
        result = self.get_custom_search_results(search_parameter)
        metadata_result = self.get_custom_search_metadata_results(result)
        url_result = self.get_custom_search_url_results(result)
        message = self.create_custom_search_result_message(metadata_result, url_result)
        blackbox_logger.info(f"GET search result message: {message}")
        return message
