# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline

from cnki.items import Cnki,db

class CnkiPipeline:
    def process_item(self, item, spider):

        with db:  # python3在使用数据库实例
            if Cnki.table_exists() == False:
                Cnki.create_table()
            try:
                Cnki.get(Cnki.title == item['title'] and Cnki.author == item['author'])
            except Cnki.DoesNotExist:
                item_dict = dict(item)
                Cnki.insert(item_dict).execute()
        return item


class CnkiFilesPipeline(FilesPipeline):
#
    # def file_path(self, request, response=None, info=None):
    #     item = request.meta['item']
    #     # 创建sort_name文件，在里面保存novel_name文件
    #     return
    def get_media_requests(self, item, info):
        for url in item['down_url']:
            yield scrapy.Request(url,meta={'item':item})
    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta['item']
        type = item['type']
        name = item['title']+'_'+item['author']
        filepath = name+'.'+type
        return filepath
    def item_completed(self, results, item, info):
        print(results)
        return item