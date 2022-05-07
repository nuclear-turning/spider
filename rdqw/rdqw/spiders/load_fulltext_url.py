import os.path

from rdqw.utils.redis_pool import get_redis

if __name__ == '__main__':
    my_redis = get_redis()

    base_url = 'http://114.212.7.155'
    with open(os.path.join('..','data','detail_urls.txt'),encoding='utf8') as f:urls = f.read().splitlines()
    for url in urls:
        url = base_url+url.strip()
        print(url)
        my_redis.lpush('fulltext:start_urls',url)