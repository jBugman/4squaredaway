# -*- coding: UTF-8 -*-


class User(object):
    def __init__(self, json_user):
        self.id = json_user['id']
        self.first_name = json_user['firstName']
        self.last_name = json_user['lastName']
        self.photo = json_user['photo']

    @property
    def name(self):
        return ' '.join((self.first_name, self.last_name))

    @property
    def userpic(self):
        return self.photo['prefix'] + '36x36' + self.photo['suffix']

    @property
    def url(self):
        return 'https://foursquare.com/user/' + self.id
