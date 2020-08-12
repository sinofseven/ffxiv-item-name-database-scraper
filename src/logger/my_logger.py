import json
import logging
import logging.config
import os


class MyLogger(object):
    def __init__(self, name: str):
        file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "logging.json"
        )
        logging.config.dictConfig(json.load(open(file_path)))
        self.logger = logging.getLogger(name)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, exc_info=True, extra={"additional_data": kwargs})

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, exc_info=True, extra={"additional_data": kwargs})

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(
            msg, *args, exc_info=True, extra={"additional_data": kwargs}
        )

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, exc_info=True, extra={"additional_data": kwargs})
