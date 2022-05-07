# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.utils.project import get_project_settings
from peewee import *
from playhouse.pool import PooledMySQLDatabase
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
class Cnki(Model):
    search_word = TextField()  # 搜索词
    title_id = IntegerField()  # 每篇文章对应的序号
    title = TextField()  # 题名
    author = CharField()  # 作者
    organization = CharField(null=True)  # 单位
    keyword = TextField(null=True)  # 关键词
    abstract = TextField()  # 摘要
    fund = CharField(null=True)  # 基金
    doi = CharField(null=True)  # doi
    cls = CharField(null=True)  # 分类号
    album = TextField(null=True)  # 專輯，一級類目
    subject = TextField(null=True) # 專題，二級類目
    datetime = CharField(null=True)  # 日期
    journal = CharField(null=True)  # 刊名
    cite_num = IntegerField(null=True)  # 被引次数
    down_num = IntegerField(null=True)  # 下载次数
    cur_page = IntegerField()  # 当前页
    result_num = IntegerField()  # 结果总条数
    pages = IntegerField()  # 总页数

    class Meta:
        database = db
class CnkiItem(scrapy.Item):
    search_word = scrapy.Field()
    title_id = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    organization = scrapy.Field()
    keyword = scrapy.Field()
    abstract = scrapy.Field()
    fund = scrapy.Field()
    doi = scrapy.Field()
    cls = scrapy.Field()
    album = scrapy.Field()
    subject = scrapy.Field()
    datetime = scrapy.Field()
    journal = scrapy.Field()
    cite_num = scrapy.Field()
    down_num = scrapy.Field()
    cur_page = scrapy.Field()
    result_num = scrapy.Field()
    pages = scrapy.Field()