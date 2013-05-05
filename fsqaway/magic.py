# -*- coding: UTF-8 -*-
from operator import attrgetter
from itertools import chain

from gevent.pool import Pool

from fsqaway.config import GEVENT_POOL_SIZE
from fsqaway.log import get_logger
from fsqaway.dao.models import Venue
from fsqaway.dao.database import db


THRESHOLD = 5
SEARCH_CATEGORY_LIMIT = 15
REVIEWS_THRESHOLD = 1

logger = get_logger(__name__)


class Magic(object):
    def __init__(self, foursquare_api):
        self.api = foursquare_api

    def get_venues_magically(self):
        categories = self.api.get_categories_filter()
        pool = Pool(GEVENT_POOL_SIZE)
        result = pool.map(
            lambda x: self.api.search(
                search_term=x,
                categories=categories,
                per_category_limit=SEARCH_CATEGORY_LIMIT
            ).get('venues', []),
            self.keywords
        )
        # Flatten mapped list and remove duplicates via temp dict
        raw_venues = {
            x['id']: x for x in chain.from_iterable(result)
        }.values()

        venues = []
        for raw_venue in raw_venues:
            query = {'id': raw_venue['id']}
            venue = db.Venue.find_one(query)

            if venue is None:
                venue = db.Venue()
                venue = venue.from_json(raw_venue)
                venue.save()

            venue = self.add_relevance(venue)

            if venue.reviewed <= REVIEWS_THRESHOLD:
                venues.append(venue)
            else:
                logger.info('Filtered ' + venue.id)
        logger.info('Remaining: {}'.format(len(venues)))

        venues.sort(key=attrgetter('checkins'), reverse=True)
        venues.sort(key=attrgetter('relevance'), reverse=True)
        return venues

    def add_relevance(self, venue):
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
