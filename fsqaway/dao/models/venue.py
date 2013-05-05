# -*- coding: UTF-8 -*-
from mongokit import Document

from fsqaway.config import MONGODB_DATABASE


class Venue(Document):  # pragma: no cover
    __database__ = MONGODB_DATABASE
    __collection__ = 'venues'
    use_dot_notation = True
    skip_validation = True

    structure = {
        'id': basestring,
        'name': basestring,
        'url': basestring,
        'checkins': int,
        'users': int,
        'tips': int,
        'likes': int,
        'photos': int,
        'specials': int,
        'city': basestring,
        'address': basestring,
        'icon': (basestring, basestring),
        'categories': [basestring],

        'reviewed': int,
    }
    default_values = {
        'likes': 0,
        'photos': 0,
        'specials': 0,

        'reviewed': 0,
    }
    indexes = [
        {'fields': 'id'},
    ]

    def from_json(self, venue):
        self.id = venue['id']
        self.name = venue['name']
        self.url = venue['canonicalUrl']
        self.checkins = venue['stats']['checkinsCount']
        self.users = venue['stats']['usersCount']
        self.tips = venue['stats']['tipCount']
        self.specials = venue['specials']['count']
        self.city = venue['location'].get('city', '')
        self.address = venue['location'].get('address', '')

        _, icon, categories = self._get_categories(venue)
        self.icon = (icon['prefix'], icon['suffix'])
        self.categories = categories
        return self

    def _get_categories(self, venue):
        primary = None
        icon = None
        categories = []
        for cat in venue['categories']:
            if 'primary' in cat and cat['primary']:
                primary = cat['name']
                icon = cat['icon']
            else:
                categories.append(cat['name'])
        return primary, icon, [primary] + categories
