
# import re
# import requests
# from bs4 import BeautifulSoup
# from lxml import etree
# def get_innerHTML(html):
#     return html[html.find(">")+1:html.rfind('</')]
# headers = {
#     'Connection': 'keep-alive',
#     'Accept': '*/*',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.55',
#     'X-Requested-With': 'XMLHttpRequest',
#     'Referer': 'http://114.212.7.155/Qw/Paper/748668',
#     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
#     # 'Cookie': 'zlzx_uid=92c5d5d3cf2641d783f76ae8bc39d0ca',
# }

# params = {
#     'pn': '1',
#     'ps': '50',
#     'id': '748668',
# }
# session = requests.session()
# response1 = session.get('http://114.212.7.155/Qw/Paper/748668',headers=headers)

# response2 = session.get('http://114.212.7.155/Qw/ArtText', headers=headers, params=params, verify=False)
# html_object1 = BeautifulSoup(response1.text,'lxml')
# html_object2 = BeautifulSoup(response2.text,'lxml')
# artibody1 = html_object1.find(class_='artibody')
# artibody2 = html_object2.find(class_='artibody')
# print(artibody2)
# html_object = BeautifulSoup(response1.text.replace(str(artibody1),str(artibody2)),'lxml')
# printArea = str(html_object.find(name='div',id='printArea'))
# printArea = printArea[printArea.find(">")+1:printArea.rfind('</')]
# head = "<div id=\"wraper\">" + printArea + "</div>";
# wname = html_object.find(id="artibodyTitle").text
# data = {
#     'word':head,
#     'wordName':wname
# }
# response = requests.post('http://114.212.7.155/Qw/DownWord', headers=headers,data=data, verify=False)
# with open('test.doc','wb') as wf:wf.write(response1.content)