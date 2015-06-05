# -*- coding: UTF-8 -*-
HTTP_PORT = 8087

DEBUG = False
ASSETS_DEBUG = False

SECRET_KEY = '4sqawsecretkey'

CACHE_TYPE = 'redis'
CACHE_DATABASE = 1

MONGODB_DATABASE = 'fsqaway'

SENTRY_DSN = ''
USE_SENTRY = False

FOURSQUARE_CLIENT_ID = '<my_id>'
FOURSQUARE_CLIENT_SECRET = '<my_secret>'

CATEGORIES_LIST_CACHE_TIMEOUT = 8 * 3600

GEVENT_POOL_SIZE = 10

ALLOWED_USERS = (
    '23245433',  # Sergey Parshukov
    '17699551',  # Tyoma Kazakov
)

try:
    from local_config import *
except ImportError:
    pass
