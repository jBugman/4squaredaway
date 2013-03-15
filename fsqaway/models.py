# -*- coding: UTF-8 -*-
import json


class Venue(object):
    def __init__(self, venue):
        self.name = venue['name']
        self.categories = [x['name'] for x in venue['categories']]
        self.checkins = venue['stats']['checkinsCount']
        self.users = venue['stats']['usersCount']
        self.tips = venue['stats']['tipCount']
        self.likes = venue['likes']['count']
        self.specials = venue['specials']['count']
        self.city = venue['location'].get('city', '')
        self.address = venue['location'].get('address', '')
        self.id = venue['id']

    @property
    def relevancy(self):
        if self.users:
            return self.checkins / self.users
        else:
            return 9999

    def __iter__(self):
        yield self.name
        yield ';'.join(self.categories)
        yield self.checkins
        yield self.users
        yield self.tips
        yield self.likes
        yield self.specials
        yield self.city
        yield self.address
        yield self.id

        yield self.relevancy


class Category(object):
    def __init__(self, category):
        self.name = category['name']
        self.id = category['id']
        self.categories = [Category(x) for x in category.get('categories', [])]

    # def __repr__(self):
    #     return json.dumps({
    #         'name': self.name,
    #         'id': self.id,
    #         'categories': len(self.categories)#[(x) for x in self.categories]
    #     })

    # def _cleanup(self, category):
    #     category.pop('pluralName', None)
    #     category.pop('shortName', None)
    #     icon = category.pop('icon', None)
    #     if icon:
    #         category['icon'] = icon['prefix'] + 'bg_32' + icon['suffix']
    #     if 'categories' in category:
    #         for c in category['categories']:
    #             self._cleanup(c)
    #         if not category['categories']:
    #             category.pop('categories', None)
    #     return category
