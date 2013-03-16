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


SEARCH_INTENT = 'browse'
SEARCH_RADIUS = 1500
COORDS_CENTER = (55.7517, 37.6178)
COORDS_RADIUS = 0.25


class FoursquareAPI(object):
    def __init__(self, cache):
        self.logger = get_logger(__name__)
        self.fsq = Foursquare(
            client_id=FOURSQUARE_CLIENT_ID,
            client_secret=FOURSQUARE_CLIENT_SECRET
        )
        self.cache = cache

    def batch_search(self, search_term, iterations, filter):
        pool = Pool(GEVENT_POOL_SIZE)
        categories_filter = ','.join(
            (x['id'] for x in Category.filter(
                Category.cleanup(self.get_categories())
            ))
        )
        result = pool.map(
            lambda x: self.search(
                search_term,
                categories_filter
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

    def get_categories(self):
        @self.cache.cached(timeout=CATEGORIES_LIST_CACHE_TIMEOUT)
        def _cached():
            self.logger.debug('API call \'Categories\'')
            return self.fsq.venues.categories()['categories']
        return _cached()

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
