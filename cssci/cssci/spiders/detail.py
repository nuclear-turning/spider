#coding:utf-8
import logging
import random

import execjs
import scrapy
from scrapy_redis.spiders import RedisCrawlSpider
from cssci.utils.request import request_fingerprint
from cssci.utils.redis_pool import get_redis
from cssci.items import CssciItem
from cssci.utils.subject_code import subject_code

class DetailSpider(RedisCrawlSpider):
    name = "detail"
    redis_key = 'detail:start_urls'
    redis_error_key = 'detail:error_urls'
    redis_df_key = 'detail:dupefilter'
    handle_httpstatus_list = [
        404,
        503,
        504,
    ]
    source_type = {
        '1': u"论文",
        '2': u"综述",
        '3': u"评论",
        '4': u"传记资料",
        '5': u"报告",
        '9': u"其他",
    }

    allowed_domains = ["cssci.nju.edu.cn"]
    def make_requests_from_url(self, url):
        yield scrapy.Request(url=url, callback=self.parse)
    redis_server = get_redis()
    log = logging.getLogger("detail")
    cited_base_url = 'http://cssci.nju.edu.cn/control/controllers.php?control=search&action=catation_id&id=%s&ywnd=1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021&pagenow=1'
    def parse(self, response):
        try:
            result = execjs.eval(response.body.decode())
            print(result)
            state = result['state']

            if response.status in self.handle_httpstatus_list:
                log_str = '%d url %s' %(response.status, response.url)
                self.log.error(log_str)
                self.redis_server.rpush(self.redis_error_key, response.url)
            else:
                if state == 'ok!':
                    for d in result['contents']:
                        item = {}
                        item['cid'] = d['id']       # 被引文献ID
                        cited_url = self.cited_base_url % d['id'] +'&rand=' + str(random.random())
                        item['sno'] = d['sno']        # 来源文献ID
                        item['title'] = d['lypm']    # 来源文献题目
                        item['title_en'] = d['blpm']    # 英文题目
                        authors = []
                        orgs = []
                        if result['author']:
                            for author_info in result['author']:
                                authors.append(author_info['zzmc'])
                                orgs.append(author_info['jgmc'] + '·' + author_info['bmmc'])
                        item['organization'] = '###'.join(orgs)
                        item['author'] = '###'.join(authors)           #作者

                        if d['wzlx'] in self.source_type:
                            item['type'] = self.source_type[d['wzlx']]  # 文献类型
                        else:
                            item['type'] = d['wzlx']

                        item['subject_code'] = '/'.join([d['xkfl1'],d['xkfl2']])  # 学科类别
                        item['subject_name'] = '/'.join([subject_code[d['xkfl1']],subject_code[d['xkfl2']]])
                        item['classification_code'] = '/'.join([d['xkdm1'],d['xkdm2']]) #中图分类号
                        item['fund'] = d['xmlb']    #基金
                        item['journal'] = d['qkmc'] #来源期刊
                        item['journal_code'] = d['qkdm'] #期刊代码
                        item['year'] = d['nian']   #年
                        item['vol_'] = d['juan']   #卷
                        item['stage'] = d['qi']    #期
                        item['page'] = d['ym']    #页码
                        item['key_word'] = d['byc'].replace('aaa', '') #关键词

                        refer = []
                        if result['catation']:
                            for data_catation in result['catation']:
                                # 期刊论文
                                if data_catation['ywlx'] == '1':
                                    tmp = data_catation['ywcc'].replace(data_catation['ywnd'] + '，', '')
                                    tmp = tmp.replace(data_catation['ywnd'] + '.', '')
                                    tmp = tmp.replace(data_catation['ywnd'] + '（', '（')
                                    tmp = tmp.replace(data_catation['ywnd'] + ',', '')
                                    show_content = '.'.join([
                                        data_catation['ywzz'],
                                        data_catation['ywpm'],
                                        data_catation['ywqk'],
                                    ])
                                    if len(data_catation['ywnd']) > 2:
                                        show_content += '.' + data_catation['ywnd']
                                    show_content += ',' + tmp
                                # 报纸
                                elif data_catation['ywlx'] == '3':
                                    show_content = '.'.join([
                                        data_catation['ywzz'],
                                        data_catation['ywpm'],
                                        data_catation['ywqk'],
                                    ])
                                    if len(data_catation['ywcc']) > 0:
                                        show_content += "." + data_catation['ywcc']
                                    else:
                                        show_content += "." + data_catation['ywnd']
                                #电子文献、网站
                                elif data_catation['ywlx'] == '11':
                                    show_content = '.'.join([
                                        data_catation['ywzz'],
                                        data_catation['ywpm'],
                                        data_catation['ywqk'],
                                    ])
                                    if len(data_catation['ywnd']) > 2:
                                        show_content += '.' + data_catation['ywnd']
                                #其他
                                elif data_catation['ywlx'] == '99':
                                    show_content = data_catation['ywpm']
                                #汇编
                                elif data_catation['ywlx'] == '7':
                                    show_content = ''
                                    if len(data_catation['ywzz'].strip()) > 0:
                                        show_content += data_catation['ywzz']
                                    if len(data_catation['ywpm'].strip()) > 0:
                                        show_content += "." + data_catation['ywpm']

                                    if len(data_catation['ywcc']) > 0:
                                        show_content += "." + data_catation['ywcc']
                                    else:
                                        if len(data_catation['ywqk'].strip()) > 0:
                                            show_content += ":" + data_catation['ywqk']
                                        if len(data_catation['ywcbd'].strip()) > 0:
                                            show_content += "." + data_catation['ywcbd']
                                        if len(data_catation['ywcbs'].strip()) > 0:
                                            show_content += ":" + data_catation['ywcbs']
                                        if len(data_catation['ywnd'].strip()) > 2:
                                            show_content += "," + data_catation['ywnd']
                                        if len(data_catation['ywym']) > 0:
                                            show_content += ":" + data_catation['ywym']
                                else:
                                    show_content = ''
                                    if len(data_catation['ywzz'].strip()) > 0:
                                        show_content += data_catation['ywzz']
                                    if len(data_catation['ywpm'].strip()) > 0:
                                        show_content += "." + data_catation['ywpm']
                                    if len(data_catation['ywcbd'].strip()) > 0:
                                        show_content += "." + data_catation['ywcbd']

                                    if len(data_catation['ywcbs'].strip()) > 0:
                                        show_content += ":" + data_catation['ywcbs']
                                    if len(data_catation['ywnd'].strip()) > 2:
                                        show_content += "," + data_catation['ywnd']
                                    if len(data_catation['ywym']) > 0:
                                        show_content += ":" + data_catation['ywym']
                                refer.append(show_content)

                        item['refer'] = '###'.join(refer)

                        yield scrapy.Request(cited_url,callback=self.parse_cite_info,meta={'item': item})

                    fp = request_fingerprint(response.request)
                    self.redis_server.sadd(self.redis_df_key, fp)

                elif state == 'wrong_year':
                    self.redis_server.lpush(self.redis_error_key, response.url)

        except Exception as err:
            self.log.error(str(err))
            self.log.error(response.url)
            self.log.error(response.body)
            self.redis_server.lpush(self.redis_error_key, response.url)


    def parse_cite_info(self,response):
        item = CssciItem()
        item.update(response.meta['item'])
        try:
            result = execjs.eval(response.body.decode())
            state = result['state']
            if response.status in self.handle_httpstatus_list:
                log_str = '%d url %s' % (response.status, response.url)
                logging.error(log_str)
            else:
                if state == 'ok!':
                    if result['totalnum'] != '':
                        item['cite_num'] = result['totalnum']

        except Exception as err:
            logging.error(str(err))
            logging.error(response.url)
        yield item









