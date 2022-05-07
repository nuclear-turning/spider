import requests
import random
from cssci.utils.redis_pool import get_redis

def set_session_id(redis_server):
    url = "http://cssci.nju.edu.cn/control/controllers.php"
    response = requests.post(url=url, data={
        'control': 'user_control',
        'action': 'check_user_online',
        'rand': str(random.random())
    })
    if 'wrong_school!' not in response.text:
        session_id = response.cookies['PHPSESSID']
        redis_server.set(name='session_id', value=session_id, ex=60*15)

if __name__ == '__main__':
    redis_server = get_redis()
    set_session_id(redis_server)