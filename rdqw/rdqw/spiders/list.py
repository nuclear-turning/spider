# import requests
# from bs4 import BeautifulSoup
# from lxml import etree
# import time
# cookies = {
#     'zlzx_uid': '09abe3107ca640b18b5b8c2bfe422728',
# }

# headers = {
#     'Connection': 'keep-alive',
#     'Accept': 'text/html, */*; q=0.01',
#     'X-Requested-With': 'XMLHttpRequest',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.55',
#     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#     'Origin': 'http://114.212.7.155',
#     'Referer': 'http://114.212.7.155/qw',
#     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
#     # 'Cookie': 'zlzx_uid=09abe3107ca640b18b5b8c2bfe422728',
# }

# for page in range(67,68):#33112
#     data = {
#         'data': '{"DbCode":1,"TreeCode":"01,02,03,04,05,06,07,08,09","StartYear":"1995","EndYear":"2021","Order":"","IsAbs":0,"PageIndex":%d,"PageSize":10000,"ListSearchCondition":[]}'%page,
#     }
#     response = requests.post('http://114.212.7.155/Qw/Search', headers=headers,cookies=cookies,data=data, verify=False)
#     selector = etree.HTML(response.text)
#     links = selector.xpath('//*[@class="li_title"]/a/@href')
#     with open('detail_urls.txt','a+',encoding='utf8') as f:
#         f.write('\n'.join(links)+'\n')
#     time.sleep(2)

#     # for link in links:
#         # print('http://114.212.7.155'+link)