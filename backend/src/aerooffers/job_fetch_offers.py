import os

from scrapy.crawler import Crawler, CrawlerProcess, Spider
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from aerooffers.my_logging import logging, remove_scrapy_handlers
from aerooffers.spiders import FlugzeugMarktDeSpider

logger = logging.getLogger("offers_crawler")

if __name__ == "__main__":
    from aerooffers.utils import load_env

    load_env()

    # Configure Scrapy logging to not install its own root handler
    # This prevents duplicate logs since we use custom logging.conf
    configure_logging(install_root_handler=False)

    settings_file_path = "settings"
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", settings_file_path)

    settings = get_project_settings()
    pipelines = settings.getlist("ITEM_PIPELINES")
    if len(pipelines) == 0:
        raise Exception(
            "Pipelines missing/not loaded properly, most likely scrapy.cfg/settings.py was not loaded properly"
        )

    logger.debug(f"Item pipelines settings: {str(pipelines)}")

    process = CrawlerProcess(settings)

    def create_crawler(spider_cls: type[Spider]) -> tuple[str, Crawler]:
        crawler: Crawler = process.create_crawler(crawler_or_spidercls=spider_cls)
        process.crawl(crawler)
        return spider_cls.__name__, crawler

    spiders: list[tuple[str, Crawler]] = [
        # create_crawler(SegelflugDeSpider.SegelflugDeSpider),
        create_crawler(FlugzeugMarktDeSpider.FlugzeugMarktDeSpider),
    ]

    # Remove Scrapy's handlers to prevent duplicate log messages
    # This must be done after creating crawlers but before starting the process
    remove_scrapy_handlers()

    process.start()  # the script will block here until all crawling jobs are finished

    logger.info("Crawling offers completed")
