import json
import os

import requests
import scrapy
import time
from scrapy_redis.spiders import RedisSpider
from bs4 import BeautifulSoup
from cnki.items import CnkiItem
from cnki.utils.opmysql import update_data
from cnki.utils.redis_pool import get_redis
from cnki.utils.get_file_name import get_file_name
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
class Cnki4FilesSpider(RedisSpider):
    name = 'cnki4files'
    allowed_domains = ['kns.cnki.net','t.cnki.net','*.cnki.net']
    redis_key = "cnki:start_urls"
    redis_error_key = 'cnki:error_urls'
    redis_server = get_redis()
    def make_requests_from_url(self, url):
        url, word = url.split(':::')
        print(url)
        meta = {'useSelenium': True, 'word': word}
        return scrapy.Request(
            url, meta=meta,callback=self.parse,dont_filter=True
        )
    def parse(self, response,**kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        result_num = soup.find(attrs={'class':'pagerTitleCell'}).text
        result_num = int(result_num[result_num.find('找到')+2:result_num.find('条结果')].strip().replace(',',''))
        if result_num != 0:
            # pages = soup.find(attrs={'class': 'countPageMark'}).text.strip()
            # cur_page, pages = pages.split('/')
            # cur_page = int(cur_page)
            # pages = int(pages)
            # 定位到内容表区域
            cur_page = 1
            pages = 1
            tr_table = soup.find(name='table', attrs={'class': 'GridTableContent'})
            try:
                # 去除第一个tr标签（表头）
                tr_table.tr.extract()
                crawl_success = True  # 记录每页是否抓取成功
                # 遍历每一行
                for index, tr_info in enumerate(tr_table.find_all(name='tr')):
                    tr_text = ''
                    detail_url = ''
                    # 遍历每一列
                    for idx, td_info in enumerate(tr_info.find_all(name='td')):
                        # 因为一列中的信息非常杂乱，此处进行二次拼接
                        td_text = ''
                        for string in td_info.stripped_strings:
                            if ' ' in string:
                                string = string.split(' ')[0]
                            td_text += string
                        tr_text += td_text + ' '
                        # 寻找详情链接
                        dt_url = td_info.find('a', attrs={'class': 'fz14'})
                        # 排除不是所需要的列
                        if dt_url:
                            detail_url = "https://kns.cnki.net"+dt_url.attrs['href']
                    # 将每一篇文献的信息分组
                    single_refence_list = tr_text.split(' ')
                    single_refence_list += [cur_page,result_num,pages]
                    yield scrapy.Request(detail_url,callback=self.parse_detail,meta={'useSelenium':False,'info':single_refence_list,'word':response.meta['word']},dont_filter=True)
            except Exception as e:
                crawl_success = False
            next_page_url = f'https://kns.cnki.net/kns/brief/brief.aspx?curpage={cur_page + 1}&RecordsPerPage=50&QueryID=0&ID=&turnpage=1&tpagemode=L&dbPrefix=CJFQ&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx&isinEn=1&'
            if cur_page < pages:
                # yield scrapy.Request(next_page_url, callback=self.parse,
                #                      meta={'useSelenium': True, 'word': response.meta['word']},dont_filter=True)
                next_url = next_page_url + ':::' + response.meta['word']
                self.redis_server.lpush('cnki:start_urls',next_url)
                print(next_url)
            if crawl_success:
                update_data(response.meta['word'], 1, cur_page, pages)  # 标记数据库
        else:
            update_data(response.meta['word'],0,0,0)
    def parse_detail(self,response):
        detail = response.meta['info']
        soup = BeautifulSoup(response.text, 'lxml')
        item = CnkiItem()
        try:
            # 获取作者单位信息
            self.orgn = ''
            try:
                orgn_list = soup.find_all(name='a', class_='author')
                for o in orgn_list:
                    self.orgn += o.string +';'
            except Exception:
                self.orgn = ''
            # 获取摘要
            if soup.find(name='span', id='ChDivSummary'):
                abstract_list = soup.find(name='span', id='ChDivSummary').strings
            else:
                abstract_list = ''
            self.abstract = ''
            for a in abstract_list:
                self.abstract += a
            # 获取关键词
            self.keywords = ''
            try:
                keywords_list = soup.find(name='p', class_='keywords').find_all('a')
                for k_l in keywords_list:
                    # 去除关键词中的空格，换行
                    self.keywords += k_l.text.strip()
            except Exception:
                self.keywords = ''
            self.doi = ''
            self.cls= ''
            self.album = ''
            self.subject = ''
            try:
                other_info = soup.find_all(name='li',class_='top-space')
                for li in other_info:
                    if 'DOI' in li.span.text:
                        self.doi = li.p.text.strip()
                    if '专辑' in li.span.text:
                        self.album = li.p.text.strip()
                    if '专题' in li.span.text:
                        self.subject = li.p.text.strip()
                    if '分类号' in li.span.text:
                        self.cls = li.p.text.strip()
            except Exception:
                pass
            # 获取基金
            self.fund = ''
            try:
                fund_list = soup.find(name='p', class_='funds').find_all('a')
                for f_l in fund_list:
                    # 去除基金中的空格，换行
                    self.fund += f_l.text.strip()
            except Exception:
                self.fund = ''

            # 下载文件
            if soup.find(name='a', id="pdfDown"):
                down_url = soup.find(name='a', id="pdfDown").get('href')
                file_type = 'pdf'
            else:
                down_url = soup.find(name='a',id='cajDown').get('href')
                file_type = 'caj'
            if settings['DOES_DOWN']:
                file_res = requests.get(down_url,headers=response.meta['headers'],cookies=json.load(open(os.path.join(os.path.abspath('.'),'cookies',f'cookies_{response.meta["word"]}.json'))),timeout=180)
                # file_name = get_file_name(file_res.headers)
                time.sleep(1)
                # if file_name:
                file_name = detail[1] + '_' + detail[2][:detail[2].find(';')] + '.' + file_type
                if not os.path.exists(os.path.join(settings['DOWNLOADER_DIR'], file_name)):
                    with open(os.path.join(settings['DOWNLOADER_DIR'], file_name), 'wb') as f:
                        f.write(file_res.content)
            item['search_word'] = response.meta['word']
            item['title_id'] = detail[0]
            item['title'] = detail[1]
            item['author'] = detail[2]

            item['journal'] = detail[3]
            item['datetime'] = detail[4]
            item['cite_num'] = detail[5]
            item['down_num'] = detail[6]
            item['organization'] = self.orgn
            item['keyword'] = self.keywords
            item['abstract'] = self.abstract
            item['fund'] = self.fund
            item['doi'] = self.doi
            item['cls'] = self.cls
            item['album'] = self.album
            item['subject'] = self.subject
            item['cur_page'] = detail[10]
            item['result_num'] = detail[11]
            item['pages'] = detail[12]

            print(f'{detail[3]},共{detail[12]}页，目前第{detail[10]}页,第{detail[0]}条数据。')
            yield item
        except Exception as e:
            print(e)

