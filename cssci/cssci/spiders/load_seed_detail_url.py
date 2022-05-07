# coding:utf-8
import random
from urllib.parse import unquote, quote
from cssci.utils.redis_pool import get_redis
from cssci.utils.get_search_word import get_source_id

if __name__ == '__main__':
    my_redis = get_redis()

    base_url = 'http://cssci.nju.edu.cn/control/controllers.php?control=search&action=source_id&id='
    snos = get_source_id()
    for sno in snos:
        url = base_url + sno
        url = url + '&rand=' + str(random.random())
        print(url)
        my_redis.lpush('detail:start_urls',url)