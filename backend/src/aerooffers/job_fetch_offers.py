import os
import pprint
from collections.abc import Mapping
from datetime import datetime

from scrapy.crawler import Crawler, CrawlerProcess, Spider
from scrapy.utils.project import get_project_settings

from aerooffers.mailer import send_mail
from aerooffers.my_logging import logging
from aerooffers.spiders import FlugzeugMarktDeSpider, SoaringDeSpider

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

        logger.info(f"Item pipelines settings: {str(pipelines)}")
        process = CrawlerProcess(settings)

        def create_crawler(spider_cls: type[Spider]) -> tuple[str, Crawler]:
            crawler: Crawler = process.create_crawler(crawler_or_spidercls=spider_cls)
            process.crawl(crawler)
            return spider_cls.__name__, crawler

        spiders: list[tuple[str, Crawler]] = [
            create_crawler(SoaringDeSpider.SoaringDeSpider),
            create_crawler(FlugzeugMarktDeSpider.FlugzeugMarktDeSpider),
        ]

        process.start()  # the script will block here until all crawling jobs are finished

        stats_per_spider: dict[str, Mapping[str, float]] = {}

        for spider_name, crawler in spiders:
            logger.debug("Fetching stats for spider: %s", spider_name)
            assert crawler.stats is not None
            stats_per_spider[spider_name] = crawler.stats.get_stats()

        msg = f"Crawling offers completed at {str(datetime.now())} \n\n {pprint.pformat(stats_per_spider)} \n"

        logger.info(msg)
        send_mail(msg)
    except Exception as e:
        msg = f"Error connecting to the database: {repr(e)}"
        logger.error(msg)
        send_mail(msg)
