from scrapy import cmdline

# cmdline.execute('scrapy crawl detail -s JOBDIR=job/detail'.split())     # 该命令可以暂停与继续爬虫
cmdline.execute('scrapy crawl detail'.split())  #该命令只能直接开始和中断爬虫