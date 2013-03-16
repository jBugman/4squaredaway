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
    def relevance(self):
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

        yield self.relevance


class Category(object):
    def __init__(self, category):
        self.name = category['name']
        self.id = category['id']
        self.categories = [Category(x) for x in category.get('categories', [])]

    @classmethod
    def cleanup(cls, categories):
        for c in categories:
            c.pop('pluralName', None)
            c.pop('shortName', None)
            icon = c.pop('icon', None)
            if icon:
                c['icon'] = icon['prefix'] + 'bg_32' + icon['suffix']
            if 'categories' in c:
                cls.cleanup(c['categories'])
                if not c['categories']:
                    c.pop('categories', None)
        return categories

    @classmethod
    def filter(cls, categories):
        result = []
        for c in categories:
            if c['id'] != '4e67e38e036454776db1fb3a':
                # Is not 'Residence'
                c.pop('categories', None)
                result.append(c)
            else:
                for sub_c in c['categories']:
                    if sub_c['id'] != '4bf58dd8d48988d103941735':
                        # Is not 'Home (private)'
                        sub_c.pop('categories', None)
                        result.append(sub_c)
        return result
