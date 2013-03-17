# -*- coding: UTF-8 -*-
from operator import attrgetter

from gevent.pool import Pool

from fsqaway.log import get_logger
from fsqaway.foursquare_api import FoursquareAPI
from fsqaway.models import Venue
from fsqaway.config import GEVENT_POOL_SIZE


THRESHOLD = 5


class Magic(object):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.api = FoursquareAPI()

    def get_venues_magically(self):
        pool = Pool(GEVENT_POOL_SIZE)
        result = pool.map(
            lambda x: self.api.search(
                x,
                self.api.categories_filter
            ).get('venues', []),
            self.keywords
        )
        # Flatten mapped list and remove duplicates via temp dict
        raw_venues = {
            x['id']: x for x in
            [item for sublist in result for item in sublist]
        }.values()
        venues = [self.with_relevance(Venue(x)) for x in raw_venues]
        venues.sort(key=attrgetter('checkins'))
        venues.sort(key=attrgetter('relevance'))
        return venues

    def with_relevance(self, venue):
        r = 0
        if venue.checkins > 10:
            r += 1
        if venue.checkins > 50:
            r += 1
        if venue.checkins > 75:
            r += 2
        if venue.checkins > 100:
            r += 2
        if venue.checkins > 200:
            r += 4
        if venue.checkins > 500:
            r += 10

        if venue.users > 5:
            r += 1
        if venue.users > 10:
            r += 2
        if venue.users > 20:
            r += 3

        if venue.tips > 0:
            r += 1
        if venue.tips > 1:
            r += 1
        if venue.tips > 5:
            r += 5

        if venue.likes > 0:
            r += 3
        if venue.specials > 0:
            r += 5
        venue.relevance = r
        return venue

    @property
    def keywords(self):
        return (
            u'дом',
            u'house',
            u'sweet',
            u'берло',
            u'хат',
            u'квартир',
            u'хаус',
            u'апартамент',
        )
