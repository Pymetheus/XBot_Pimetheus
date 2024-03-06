import logging


class Blackbox(object):

    def __init__(self, logger_name):
        self.logger = None
        self.logger_name = logger_name
        self.initialize_blackbox_logger()

    def initialize_blackbox_logger(self):
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler('blackbox.log')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
