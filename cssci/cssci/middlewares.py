# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random

from cssci.utils.cookie import set_session_id
from .settings import USER_AGENTS
from time import sleep
# import requests
# useful for handling different item types with a single interface
from cssci.utils.redis_pool import get_redis


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        user_agent = random.choice(USER_AGENTS)
        if user_agent:
            request.headers.setdefault("User-Agent", user_agent)
            request.headers.setdefault("content-type", "application/x-www-form-urlencoded")
            request.headers.setdefault("accept", "application/json, text/javascript, */*; q=0.01")
            request.headers.setdefault("cache-control", "no-cache")
            redis_server = get_redis()
            while True:
                session_id = redis_server.get('session_id')
                print(session_id)
                if session_id:
                    cookies = {
                        'PHPSESSID': session_id,
                    }
                    request.cookies = cookies
                    break
                else:
                    set_session_id(redis_server)
                    sleep(10 * 0.5)
            print('end')
            # url = "http://cssci.nju.edu.cn/control/controllers.php"
            # response = requests.post(url=url, input_data={
            #     'control': 'user_control',
            #     'action': 'check_user_online',
            #     'rand': str(random.random())
            # })
            # request.cookies = response.cookies.get_dict()