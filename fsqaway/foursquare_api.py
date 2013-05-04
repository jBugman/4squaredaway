# -*- coding: UTF-8 -*-
import random
import math

from foursquare import Foursquare
import requests

from fsqaway.log import get_logger
from fsqaway.config import (
    FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET,
    CATEGORIES_LIST_CACHE_TIMEOUT,
)
from fsqaway.models import Category
from fsqaway.cache import Cache
from fsqaway.shapes import Point, Rect
from fsqaway.dao.models.user import User


LOGIN_REDIRECT_URI = 'http://4squaredaway.ru/login'
SEARCH_INTENT = 'browse'
SEARCH_RADIUS = 1500
MOSCOW_CENTER = Point(55.7517, 37.6178)
MOSCOW_RADIUS = 0.25


class FoursquareAPI(object):
    def __init__(self):
        self.logger = get_logger(__name__)
        self.fsq = Foursquare(
            client_id=FOURSQUARE_CLIENT_ID,
            client_secret=FOURSQUARE_CLIENT_SECRET,
            redirect_uri=LOGIN_REDIRECT_URI
        )
        self.cache = Cache()

    # TODO: разобраться, в чем дело
    # def auth(self, access_code):
    #     access_token = self.fsq.oauth.get_token(access_code)
    #     self.fsq.set_access_token(access_token)

    def auth(self, access_code):
        resp = requests.get(
            'https://foursquare.com/oauth2/access_token',
            params={
                'client_id': FOURSQUARE_CLIENT_ID,
                'client_secret': FOURSQUARE_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': LOGIN_REDIRECT_URI,
                'code': access_code,
            }
        ).json()
        self.logger.debug(resp)
        access_token = resp['access_token']
        self.fsq.set_access_token(access_token)

    @property
    def auth_url(self):
        return self.fsq.oauth.auth_url()

    def get_current_user(self):
        json_response = self.fsq.users()
        return User(json_user=json_response['user'])

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
