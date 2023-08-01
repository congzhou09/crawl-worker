import os
import logging
import logging.config
import logging.handlers

from common.util.tool import load_json
from logging.handlers import TimedRotatingFileHandler
from logging import INFO


# class InfoFileHandler(TimedRotatingFileHandler):
#     def emit(self, record):
#         if not record.levelno > INFO:
#             return
#         super().emit(record)


# dict_config = {
#     "version": 1,
#     "fileName": "log",
#     "formatters": {
#         "base": {"format": "%(asctime)s - %(name)s - %(levelname)s: %(message)s"}
#     },
#     "handlers": {
#         "file-warn-error": {
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "logs/warn-error.log",
#             "when": "midnight",
#             "backupCount": 7,
#             "formatter": "base",
#             "level": "WARN",
#         },
#         "file-info": {
#             "class": "logging.handlers.TimedRotatingFileHandler",
#             "filename": "logs/info.log",
#             "when": "midnight",
#             "backupCount": 7,
#             "formatter": "base",
#             "level": "INFO",
#         },
#         "std-debug": {
#             "class": "logging.StreamHandler",
#             "formatter": "base",
#             "level": "DEBUG",
#         },
#     },
#     "root": {
#         "level": "DEBUG",
#         "handlers": ["std-debug", "file-warn-error", "file-info"],
#         "propagate": 0,
#     },
# }


def get_logger(config_file, app_name):
    dict_config = load_json(config_file)
    logging.config.dictConfig(dict_config)
    logger = logging.getLogger(app_name)
    return logger
