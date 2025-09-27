import os
import pprint
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from mailer import send_mail
from my_logging import logging
from spiders import FlugzeugMarktDeSpider, SoaringDeSpider

logger = logging.getLogger("offers_crawler")

if __name__ == "__main__":
    try:
        settings_file_path = "settings"
        os.environ.setdefault("SCRAPY_SETTINGS_MODULE", settings_file_path)

        settings = get_project_settings()
        pipelines = settings.getlist("ITEM_PIPELINES")
        if len(pipelines) == 0:
            raise Exception(
                "Pipelines missing/not loaded properly, most likely scrapy.cfg/settings.py was not loaded properly"
            )

        logger.info("Item pipelines settings: {0}".format(str(pipelines)))
        process = CrawlerProcess(settings)

        spiders = {
            SoaringDeSpider.SoaringDeSpider: None,
            FlugzeugMarktDeSpider.FlugzeugMarktDeSpider: None,
        }
        for spider_cls in spiders:
            crawler = process.create_crawler(spider_cls)
            spiders[spider_cls] = crawler
            process.crawl(crawler)

        process.start()  # the script will block here until all crawling jobs are finished

        stats_per_spider = {}

        for spider_cls, crawler in spiders.items():
            logger.debug("Fetching stats for spider: %s", spider_cls)
            stats_per_spider[spider_cls.name] = crawler.stats.get_stats()

        msg = "Crawling offers completed at {0} \n\n {1} \n".format(
            str(datetime.now()), pprint.pformat(stats_per_spider)
        )

        logger.info(msg)
        send_mail(msg)
    except Exception as e:
        msg = "Error connecting to the database: {0}".format(repr(e))
        logger.error(msg)
        send_mail(msg)
