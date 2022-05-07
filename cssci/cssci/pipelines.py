# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from cssci.items import Cssci,db


class CssciPipeline(object):
    def process_item(self, item, spider):
        with db: #python3在使用数据库实例
            if spider.name == 'list':
                if Cssci.table_exists() == False:
                    Cssci.create_table()
                try:
                    cssci = Cssci.get(Cssci.sno == item['sno'])
                except Cssci.DoesNotExist:
                    Cssci.insert(**dict(item)).execute()

            elif spider.name == 'detail':
                if Cssci.table_exists() == False:
                    Cssci.create_table()
                info_dict = {}
                for k, v in item.items():
                    if k != 'sno' and v != u'':
                        info_dict[k] = v
                if Cssci.update(**info_dict).where(Cssci.sno== item['sno']).execute() == 0:
                    Cssci.insert(**dict(item)).execute()

        return item