from datetime import datetime
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner

import pprint
from my_logging import *
from spiders import SoaringDeSpider, FlugzeugMarktDeSpider, PlaneCheckComSpider
from mailer import send_mail

logger = logging.getLogger("fetch_offers")

if __name__ == '__main__':
    try:
        settings = get_project_settings()
        runner = CrawlerRunner(settings)
        process = CrawlerProcess(settings)

        spiders = {
            SoaringDeSpider.SoaringDeSpider: None,
            FlugzeugMarktDeSpider.FlugzeugMarktDeSpider: None,
            #PlaneCheckComSpider.PlaneCheckComSpider: None
        }
        for spider_cls in spiders.keys():
            crawler = process.create_crawler(spider_cls)
            spiders[spider_cls] = crawler
            process.crawl(crawler)

        d = runner.join()
        d.addBoth(lambda _: reactor.stop())

        process.start() # the script will block here until all crawling jobs are finished

        stats_per_spider = {}

        for spider_cls, crawler in spiders.items():
            logger.debug("Fetching stats for spider: %s", spider_cls)
            stats_per_spider[spider_cls.name] = crawler.stats.get_stats()

        msg = "Crawling offers completed at {0} \n\n {1} \n".format(str(datetime.now()), pprint.pformat(stats_per_spider))

        logger.info(msg)
        send_mail(msg)
    except Exception as e:
        msg = "Error connecting to the database: {0}".format(repr(e))
        logger.error(msg)
        send_mail(msg)
