# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import random
import time
from scrapy.http.headers import Headers
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
if settings['BROWSER'] == 'Chrome':
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options
elif settings['BROWSER'] == 'Edge':
    from msedge.selenium_tools import Edge, EdgeOptions

# HEADER中间件
class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        type='SCDB'
        if settings['SEARCH_TYPE'] == 'article':type = 'SCDB'
        elif settings['SEARCH_TYPE'] == 'journal':type='CJFQ'
        headers = {
            'User-Agent': random.choice(settings['USER_AGENT']),
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
            'sec-ch-ua-mobile': '?0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Origin': 'https://kns.cnki.net',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': f'https://kns.cnki.net/kns/brief/result.aspx?dbprefix={type}&crossDbcodes=CJFQ%2CCDFD%2CCMFD%2CCPFD%2CIPFD%2CCCND%2CCISD%2CSNAD%2CBDZK%2CCCJD%2CCJRF%2CCJFN',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        }
        request.meta['headers'] = headers
        request.headers = Headers(headers)

# Cookie中间件
class AddCookieMiddleware(object):
    def process_request(self, request, spider):
        if request.meta['useSelenium']:
            if settings['BROWSER'] == 'Chrome':
                chrome_options = Options()
                # chrome_options.add_argument('--headless')
                self.browser = Chrome(options=chrome_options,executable_path="selenium_driver/chromedriver")
            elif settings['BROWSER'] == 'Edge':
                options = EdgeOptions()
                options.use_chromium = True
                options.add_argument('headless')
                self.browser = Edge(options=options, executable_path='selenium_driver/msedgedriver.exe')
            self.browser.get(settings['BASIC_URL'])  # 访问链接
            if settings['SEARCH_TYPE'] == 'article':
                #输入检索词，回车检索
                option = Select(self.browser.find_element_by_id('txt_1_sel'))
                option.select_by_index(settings['SEARCH_INDEX'])
                input = self.browser.find_element_by_id('txt_1_value1')
                input.clear()  # 检索前清空输入框
                input.send_keys(request.meta['word'])  # 输入检索词
                time.sleep(1)
                input.send_keys(Keys.ENTER)
            elif settings['SEARCH_TYPE'] == 'journal':
                input = self.browser.find_element_by_id('magazine_value1')
                input.clear()  # 检索前清空输入框
                # 选择精确检索
                select_jingque = Select(self.browser.find_element(by=By.ID, value='magazine_special1'))
                time.sleep(1)
                select_jingque.select_by_index(1)
                input.send_keys(request.meta['word'])  # 输入检索词
                time.sleep(1)
                input.send_keys(Keys.ESCAPE)
                # self.browser.find_element_by_id('mediaBox4').click()  # 选中cssci复选框
                input.send_keys(Keys.ENTER)  # 回车检索
                time.sleep(5)
            iframe = self.browser.find_element_by_id('iframeResult')
            self.browser.switch_to.frame(iframe)
            time.sleep(2)
            line50 = self.browser.find_element(by=By.XPATH, value='//*[@id="id_grid_display_num"]/a[3]')
            line50.send_keys(Keys.ENTER)  # 显示50条的结果
            time.sleep(5)
            cookies = self.browser.get_cookies()
            self.browser.close()
            scrapy_cookies = {}
            # 填充cookies
            for cookie in cookies:
                scrapy_cookies[cookie['name']] = cookie['value']
            request.cookies = scrapy_cookies
            json.dump(scrapy_cookies, open(f"cookies/cookies_{request.meta['word']}.json",'w'))