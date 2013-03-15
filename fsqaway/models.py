# -*- coding: UTF-8 -*-


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
