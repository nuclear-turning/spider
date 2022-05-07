# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from peewee import *
from playhouse.pool import PooledMySQLDatabase
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

db = PooledMySQLDatabase(
    settings['MYSQL_DB'],
    max_connections=settings['MYSQL_MAX_CONNECTIONS'],
    stale_timeout=settings['MYSQL_STALE_TIMEOUT'],
    user=settings['MYSQL_USER'],
    host=settings['MYSQL_HOST'],
    passwd=settings['MYSQL_PASSWORD'],
    charset=settings['MYSQL_CHARSET'],
)

class Cssci(Model):
    sno = CharField(max_length=255, primary_key=True)
    cid = CharField(max_length=255)
    title = TextField(null=True, default='')
    title_en = TextField(null=True, default='')
    author = TextField(null=True, default='')
    organization = TextField(null=True, default='')
    type = TextField(null=True, default='')
    subject_code = TextField(null=True, default='')
    subject_name = TextField(null=True, default='')
    classification_code = CharField(max_length=255, null=True, default='')
    fund = TextField(null=True, default='')
    journal = TextField(null=True, default='')
    journal_code = TextField(null=True, default='')
    year = TextField(null=True, default='')
    vol_ = TextField(null=True, default='')
    stage = TextField(null=True, default='')
    page = TextField(null=True, default='')
    key_word = TextField(null=True, default='')
    cite_num = TextField(null=True, default='')
    refer = TextField(null=True, default='')
    class Meta:
        database = db

class CssciItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    sno = scrapy.Field()
    cid = scrapy.Field()
    title = scrapy.Field()
    title_en = scrapy.Field()
    author = scrapy.Field()
    organization = scrapy.Field()
    type = scrapy.Field()
    subject_code = scrapy.Field()
    subject_name = scrapy.Field()
    classification_code = scrapy.Field()
    fund = scrapy.Field()
    journal = scrapy.Field()
    journal_code = scrapy.Field()
    year = scrapy.Field()
    vol_ = scrapy.Field()
    stage = scrapy.Field()
    page = scrapy.Field()
    key_word = scrapy.Field()
    cite_num = scrapy.Field()
    refer = scrapy.Field()