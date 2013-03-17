# -*- coding: UTF-8 -*-
import redis

from fsqaway.config import CACHE_DATABASE


class Cache(object):
    def __init__(self):
        self.r = redis.StrictRedis(db=CACHE_DATABASE)

    def exists(self, key):
        return self.r.exists(key)

    def get(self, key):
        return self.r.get(key)

    def put(self, key, value, expire=None):
        p = self.r.pipeline()
        p.set(key, value)
        if expire:
            p.expire(key, expire)
        p.execute()
