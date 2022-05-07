#coding:utf-8
from urllib.parse import unquote, quote
import redis
import random
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


def get_redis():
    redis_args = dict(
        host=settings['REDIS_HOST'],
        port=settings['REDIS_PORT'],
        username=settings["REDIS_PARAMS"]["username"],
        password=settings["REDIS_PARAMS"]["password"],
        db=settings["REDIS_PARAMS"]["db"],
    )
    pool = redis.ConnectionPool(**redis_args)
    return redis.Redis(connection_pool=pool)