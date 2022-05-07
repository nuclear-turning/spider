from scrapy import cmdline

# cmdline.execute('scrapy crawl cnki4files -s JOBDIR=job/cnki4files'.split())    # 该命令可以暂停与继续爬虫
cmdline.execute('scrapy crawl cnki4files'.split())  #该命令只能直接开始和中断爬虫