# -*- coding: UTF-8 -*-
import random

from foursquare import Foursquare
from gevent.pool import Pool

from fsqaway.log import get_logger
from fsqaway.config import (
    FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET,
    CATEGORIES_LIST_CACHE_TIMEOUT,
    GEVENT_POOL_SIZE,
)
from fsqaway.models import Category
from fsqaway.cache import Cache


SEARCH_INTENT = 'browse'
SEARCH_RADIUS = 1500
COORDS_CENTER = (55.7517, 37.6178)
COORDS_RADIUS = 0.25


class FoursquareAPI(object):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.fsq = Foursquare(
            client_id=FOURSQUARE_CLIENT_ID,
            client_secret=FOURSQUARE_CLIENT_SECRET
        )
        self.cache = Cache()

    def batch_search(self, search_term, iterations, filter):
        """ @deprecated """
        pool = Pool(GEVENT_POOL_SIZE)
        result = pool.map(
            lambda x: self.search(
                search_term,
                self.categories_filter
            ).get('venues', []),
            range(iterations)
        )
        # Flatten mapped list and remove duplicates via temp dict
        return {
            x['id']: x for x in
            [item for sublist in result for item in sublist]
        }.values()

    def search(self, search_term, filter=None):
        coords = ','.join((str(x) for x in self.get_random_coords()))
        self.logger.debug('API call \'%s\' coords=%s' % (search_term, coords))
        params = {
            'intent': SEARCH_INTENT,
            'll': coords,
            'radius': SEARCH_RADIUS,
            'query': search_term.encode('UTF-8'),
            'limit': 50
        }
        if filter:
            params['categoryId'] = filter
        return self.fsq.venues.search(params=params)

    @property
    def categories_filter(self):
        KEY = '.'.join((__name__, self.__class__.__name__, 'categories_filter'))
        if self.cache.exists(KEY):
            return self.cache.get(KEY)

        result = ','.join(
            (x['id'] for x in Category.filter(self.get_categories()))
        )
        self.cache.put(KEY, result, CATEGORIES_LIST_CACHE_TIMEOUT)
        return result

    def get_categories(self):
        self.logger.debug('API call \'Categories\'')
        return Category.cleanup(self.fsq.venues.categories()['categories'])

    def get_random_coords(self, center=COORDS_CENTER, radius=COORDS_RADIUS):
        while True:
            point = (
                random.uniform(-radius, radius),
                random.uniform(-radius, radius),
            )
            if point[0] ** 2 + point[1] ** 2 <= radius ** 2:
                return (
                    center[0] + point[0],
                    center[1] + point[1]
                )
