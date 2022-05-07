from urllib.parse import quote

import requests
import json
import yaml
import Levenshtein
import time

from KSVS_Moudle.utils.importToDb import getIdFromUser, KSUserData, getNameFromUser, updataUser
settings = yaml.safe_load(open('settings.yaml', encoding='utf8'))

class KsVSpider:
    def __init__(self):
        self.cookies = settings['cookies']
        self.headers = settings['headers']
        self.id_query = settings['id_query']
        self.detail_query = settings['detail_query']
        self.video_query = settings['video_query']
        self.pcursor = ''

    def getUserId(self,keyword):

        self.headers['Referer'] = "https://www.kuaishou.com/search/author?searchKey=" + quote(keyword)
        data = {
            "operationName": "visionSearchPhoto",
            "variables": {
                "keyword": keyword,
                "pcursor": "",
                "page": "search"
            },
            "query":self.id_query
        }
        response = requests.post('https://www.kuaishou.com/graphql', headers=self.headers, cookies=self.cookies,
                                 data=json.dumps(data))
        result = response.json()

        if result:
            if result['data']['visionSearchPhoto'] and result['data']['visionSearchPhoto']['feeds']:
                author_list = result['data']['visionSearchPhoto']['feeds']
                if_get = False
                for item in author_list:
                    userid = item['author']['id']
                    username = item['author']['name']
                    # 精确匹配目标用户
                    if Levenshtein.jaro_winkler(username,keyword) > 0.7: #计算字符串相似度
                        if Levenshtein.distance(username,keyword) < 3: #计算编辑距离，双重保障
                            updataUser(KSUserData.userId,userid,KSUserData.userName,keyword)
                            updataUser(KSUserData.matchedName,username, KSUserData.userName, keyword)
                            updataUser(KSUserData.doesIdGet, 1, KSUserData.userName, keyword)
                            print('\t',"抓取到"+username+"的id为："+userid)
                            if_get = True
                            # user_idAname.append('\t'.join([userid,username,keyword])) #以防万一，把关键词也添加进去方便检验
                            break
                if not if_get:
                    print('\t', keyword, "抓取失败")

            else:
                print('\t',keyword, "抓取失败")
        else:
            print('\t',keyword,"抓取失败")
            # user_idAname.append('\t'.join(['', '', keyword]))
        # return user_idAname
    def getUserDetail(self,userId,userName):
        data = {
            "operationName": "visionProfile",
            "variables": {
                "userId": userId,
            },
            "query": self.detail_query
        }
        self.headers['Referer'] = 'https://www.kuaishou.com/profile/'+userId
        response = requests.post('https://www.kuaishou.com/graphql', headers=self.headers, cookies=self.cookies,
                                 data=json.dumps(data))
        result = response.json()
        if result:
            if result["data"]["visionProfile"] and result["data"]["visionProfile"]["userProfile"]:
                if result["data"]["visionProfile"]["userProfile"]["ownerCount"]:
                    fan = result["data"]["visionProfile"]["userProfile"]["ownerCount"]["fan"]
                    follow = result["data"]["visionProfile"]["userProfile"]["ownerCount"]["follow"]
                    photo_public = result["data"]["visionProfile"]["userProfile"]["ownerCount"]["photo_public"]
                    updataUser(KSUserData.fan,fan,KSUserData.userId,userId)
                    updataUser(KSUserData.follow, follow,KSUserData.userId,userId)
                    updataUser(KSUserData.photoPublic,photo_public,KSUserData.userId,userId)
                    updataUser(KSUserData.doesDetailGet, 1, KSUserData.userId, userId)
                if result["data"]["visionProfile"]["userProfile"]["profile"]:
                    gender = result["data"]["visionProfile"]["userProfile"]["profile"]["gender"]
                    updataUser(KSUserData.gender, gender, KSUserData.userId, userId)
                    updataUser(KSUserData.doesDetailGet, 1, KSUserData.userId, userId)
                print('\t',userName,"抓取成功")
            else:
                print('\t',userName,"抓取失败")
        else:
            print('\t',userName,"抓取失败")




def runGetUserId():
    ksvs = KsVSpider()
    userData = getNameFromUser(KSUserData.doesIdGet,0)#从数据库中读取信息
    for row in userData:
        print("正在抓取(userId)：", row.userName,end='')
        username = row.userName.strip()
        ksvs.getUserId(username)
        time.sleep(5)

def runGetUserDetail():
    ksvs = KsVSpider()
    userData = getIdFromUser(KSUserData.doesDetailGet, 0)  # 从数据库中读取信息
    for row in userData:
        userId = row.userId.strip()
        print("正在抓取(user_detail)：", row.userName, end='')
        ksvs.getUserDetail(userId,row.userName)
        time.sleep(5)
