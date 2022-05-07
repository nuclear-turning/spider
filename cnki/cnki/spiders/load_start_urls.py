# coding:utf-8
from urllib.parse import unquote, quote
from cnki.utils.redis_pool import get_redis
from cnki.utils.opmysql import import_data,get_data
from scrapy.utils.project import get_project_settings
import os
settings = get_project_settings()

if __name__ == '__main__':
    search_type = settings['SEARCH_TYPE']
    txt_path = ''
    base_url = ''
    if search_type == 'article':
        base_url = f'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=0&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&sKuaKuID=0&isinEn=1&'
        txt_path = os.path.join(os.path.abspath('..'),'input_data','articles.txt')
    elif search_type == 'journal':
        base_url = 'https://kns.cnki.net/kns/brief/brief.aspx?curpage=%d&RecordsPerPage=50&QueryID=0&ID=&turnpage=1&tpagemode=L&dbPrefix=CJFQ&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&sKuaKuID=0&isinEn=1&'
        txt_path = os.path.join(os.path.abspath('..'),'input_data','journals.txt')
    import_data(txt_path)
    my_redis = get_redis()
    # 检查是否url存在
    urls = my_redis.lrange('cnki:start_urls', 0, -1)
    url_list = []
    for url in urls:
        url = url.decode()
        url_list.append(url)
    for row in get_data():
        word = row[1].strip()
        cur_page = row[3]
        start_url = base_url%(cur_page+1)+':::'+word
        print(start_url)
        if start_url not in url_list:
            my_redis.lpush("cnki:start_urls", start_url)
        # break   # 测试用


