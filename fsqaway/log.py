# -*- coding: UTF-8 -*-
import os
import logging
import logging.handlers

from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler

from config import SENTRY_DSN, USE_SENTRY


LOG_FORMAT = '[%(asctime)-6s][%(levelname)s][%(name)s][%(lineno)d] %(message)s'
DATE_FORMAT = '%d.%m.%Y %H:%M:%S'

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))


def add_sentry(logger, level=logging.ERROR):
    sentry_handler = SentryHandler(SENTRY_DSN)
    sentry_handler.setLevel(level)
    logger.addHandler(sentry_handler)
    return logger


def get_logger(name, level=logging.DEBUG, sentry_level=logging.WARNING):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(console_handler)
    if sentry_level and USE_SENTRY:
        add_sentry(logger, sentry_level)
    return logger
