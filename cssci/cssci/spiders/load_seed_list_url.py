# coding:utf-8
import random
from urllib.parse import unquote, quote
from cssci.utils.redis_pool import get_redis
from cssci.utils.get_search_word import get_journal_name
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

if __name__ == '__main__':
    my_redis = get_redis()
    start_year = settings['START_YEAR']
    end_year = settings['END_YEAR']
    base_url = f'http://cssci.nju.edu.cn/control/controllers.php?control=search_base&action=search_lysy&title=&xkfl1=&wzlx=&qkname=&type=&jj=&start_year={start_year}&end_year={end_year}&nian=&juan=&qi=&xw1=&xw2=&pagesize=50&pagenow=1&order_type=nian&order_px=DESC&search_tag=0'
    journal_titles = get_journal_name()
    for journal_title in journal_titles:
        s = journal_title.encode('utf-8')
        print(journal_title)
        url = my_redis.get(s)

        if url:
            if url == "end":
                pass
            else:
                my_redis.lpush("list:start_urls", url)
        else:
            title = quote(quote(s) + quote('+++8+++AND|||'))
            url = base_url.replace('&title=', '&title=%s' % title)
            url = url + '&rand=' + str(random.random())
            my_redis.lpush("list:start_urls", url)