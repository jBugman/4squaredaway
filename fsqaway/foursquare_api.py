# -*- coding: UTF-8 -*-
import random
import math

from foursquare import Foursquare

from fsqaway.log import get_logger
from fsqaway.config import (
    FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET,
    CATEGORIES_LIST_CACHE_TIMEOUT,
)
from fsqaway.models import Category
from fsqaway.cache import Cache
from fsqaway.shapes import Point, Rect


SEARCH_INTENT = 'browse'
SEARCH_RADIUS = 1500
MOSCOW_CENTER = Point(55.7517, 37.6178)
MOSCOW_RADIUS = 0.25


class FoursquareAPI(object):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.fsq = Foursquare(
            client_id=FOURSQUARE_CLIENT_ID,
            client_secret=FOURSQUARE_CLIENT_SECRET
        )
        self.cache = Cache()

    def search(self, search_term, categories):
        bounds = Rect.rect_with_center_and_halfsize(
            MOSCOW_CENTER,
            MOSCOW_RADIUS
        )
        self.logger.debug(u'API::search \'{}\' with bounds {}'.format(
            search_term, bounds
        ))
        return self.fsq.venues.search(params={
            'intent': SEARCH_INTENT,
            'sw': bounds.sw,
            'ne': bounds.ne,
            'query': search_term.encode('UTF-8'),
            'limit': 50,
            'categoryId': categories,
        })

    def get_categories_filter(self):
        KEY = '.'.join((__name__, self.__class__.__name__, 'categories_filter'))
        if self.cache.exists(KEY):
            return self.cache.get(KEY)

        self.logger.debug('API::Categories')
        categories = Category.list_from_json(self.fsq.venues.categories())
        result = ','.join((x['id'] for x in categories))
        self.cache.put(KEY, result, CATEGORIES_LIST_CACHE_TIMEOUT)
        return result
