# -*- coding: UTF-8 -*-
from mongokit import Connection

from fsqaway.dao.models import Venue


db = Connection()
db.register(Venue)
