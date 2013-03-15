# -*- coding: UTF-8 -*-
from foursquare import Foursquare

from fsqaway.log import get_logger
from fsqaway.config import (
    FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET,
    SEARCH_CACHE_TIMEOUT, CATEGORIES_LIST_CACHE_TIMEOUT
)


NEAR = 'Москва'


class FoursquareAPI(object):
    def __init__(self, cache):
        self.logger = get_logger(__name__)
        self.fsq = Foursquare(
            client_id=FOURSQUARE_CLIENT_ID,
            client_secret=FOURSQUARE_CLIENT_SECRET
        )
        self.cache = cache

    def search_with_intent(self, search_term, intent='match', near=NEAR):
        @self.cache.memoize(timeout=SEARCH_CACHE_TIMEOUT)
        def _cached(search_term, intent, near):
            self.logger.debug('API call \'%s\' intent=%s' % (search_term, intent))
            return self.fsq.venues.search(params={
                'intent': intent,
                'near': NEAR,
                'query': search_term.encode('UTF-8'),
                'limit': 50
            })
        return _cached(search_term, intent, near)

    def get_categories(self):
        @self.cache.cached(timeout=CATEGORIES_LIST_CACHE_TIMEOUT)
        def _cached():
            self.logger.debug('API call \'Categories\'')
            return self.fsq.venues.categories()['categories']
        return _cached()
