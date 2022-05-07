import os
import time

import scrapy
from scrapy_redis.spiders import RedisSpider
import requests
import re
from rdqw.utils.redis_pool import get_redis
class FulltextSpider(RedisSpider):
    name = 'fulltext'
    redis_key = 'fulltext:start_urls'
    redis_error_key = 'fulltext:error_urls'
    redis_df_key = 'fulltext:dupefilter'
    redis_server = get_redis()

    def make_requests_from_url(self, url):
        return scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        try:
            html = response.body.decode()
            start = re.search(r'<div id="printArea">',html).end()
            end = re.search(r'<h3 class="t_artiInfo">相关文章：</h3>',html).start()
            printArea = html[start:end]
            head = "<div id=\"wraper\">" + printArea.lstrip('&#13;')
            head = re.sub('src="/jpg','src="http://img.ipub.exuezhe.com/jpg',head)
            wname = response.xpath('//*[@id="artibodyTitle"]/text()').get()
            head = head.replace('&#13;','')
            data = {
                'word':head,
                'wordName':wname,
            }
            headers = {
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'Origin': 'http://114.212.7.155',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.55',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Referer': response.url,
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                # 'Cookie': 'zlzx_uid=2371cb9f4bd24fcbbfe1e3c3cf668a62',
            }
            response = requests.post('http://114.212.7.155/Qw/DownWord',data=data,headers=headers,verify=False)
            with open(os.path.join(os.path.abspath('.'),'data','docs',wname+'.doc'),'wb') as df:df.write(response.content)
            time.sleep(5)
        except Exception as e:

            self.redis_server.lpush(self.redis_error_key, response.url)
            raise e

        # yield scrapy.FormRequest('http://114.212.7.155/Qw/DownWord',formdata=data)