#coding:utf-8
from urllib.parse import unquote
import sys
import random
import logging
from time import sleep
import execjs #node.js
import scrapy
from scrapy_redis.spiders import RedisCrawlSpider
from cssci.utils.request import request_fingerprint
from cssci.utils.redis_pool import get_redis
from cssci.items import CssciItem
from cssci.utils.string_process import de_url_cat
import re


class ListSpider(RedisCrawlSpider):
    name = "list"
    redis_key = 'list:start_urls'
    redis_error_key = 'list:error_urls'
    redis_df_key = 'list:dupefilter'
    handle_httpstatus_list = [
        404,
        503,
        504,
    ]
    allowed_domains = ["cssci.nju.edu.cn"]
    def make_requests_from_url(self, url):
        yield scrapy.Request(url=url, callback=self.parse)
    detail_url = 'http://cssci.nju.edu.cn/control/controllers.php?control=search&action=source_id&id='
    redis_server = get_redis()


    def parse(self, response):
        try:
            result = execjs.eval(response.body.decode('utf8'))
            print(result)
            end_page = int(result['pagenum']) if result['pagenum'] else None
            current_page = int(result['pagenow']) if result['pagenow'] else None
            state = result['state']
            subject = self.parse_subject(response.url)

            if response.status in self.handle_httpstatus_list:
                log_str = '%d url %s' %(response.status, response.url)
                logging.error(log_str)
                self.redis_server.rpush(self.redis_error_key, response.url)
            else:
                if state == 'ok!':
                    for d in result['contents']:
                        id = d['sno']
                        item = CssciItem()
                        item['sno'] = id
                        item['journal'] = subject
                        self.redis_server.lpush('detail:start_urls', self.detail_url + id + '&rand=' + str(random.random()))
                        yield item

                    fp = request_fingerprint(response.request)
                    self.redis_server.sadd(self.redis_df_key, fp)
                elif state == 'wrong_year':
                    self.redis_server.lpush(self.redis_error_key, response.url)

            self.next_page(current_page, end_page, response.url, subject, '&pagenow=%d')

        except Exception as err:
            logging.error(str(err))
            logging.error(response.url)
            self.redis_server.lpush(self.redis_error_key, response.url)

    def next_page(self, current_page, end_page, url, subject, url_para):
        if current_page < end_page:
            next_page = current_page + 1
            url = url.replace(url_para % current_page, url_para % next_page)
            url = re.sub("(?<=&rand\=).*?$", str(random.random()), url)
            sleep(60 * 1)
            self.redis_server.lpush(self.redis_key, url)
            self.redis_server.set(subject, url)
        else:
            self.redis_server.set(subject, 'end')

    def parse_subject(self, url):
        query_string = de_url_cat(url)
        title = query_string['title']
        subject = unquote(unquote(title)).replace('+++8+++AND|||', '')
        return subject