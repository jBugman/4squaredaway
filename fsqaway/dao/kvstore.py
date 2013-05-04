# -*- coding: UTF-8 -*-
import redis

from simplekv.memory.redisstore import RedisStore

from fsqaway.config import CACHE_DATABASE


def get_redis():
    return redis.StrictRedis(db=CACHE_DATABASE)


def get_kvstore():
    return RedisStore(get_redis())
