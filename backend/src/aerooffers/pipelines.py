from abc import ABC, abstractmethod
from typing import override

from price_parser import Price
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

from aerooffers.fx import to_price_in_euro
from aerooffers.my_logging import logging
from aerooffers.offer import OfferPageItem
from aerooffers.offers_db import offer_url_exists, store_offer


class OfferPipelineFilter(ABC):
    """It is very easy to break scrapy pipelines if process_item has invalid signature, this protocol helps keeping it exactly as scrapy wants it to be."""

    @abstractmethod
    def process_item(self, item: OfferPageItem) -> OfferPageItem:
        pass


class SkipSearchAndCharterOffers(OfferPipelineFilter):
    logger = logging.getLogger("FilterSearchAndCharterOffers")

    search_offer_terms = ["suche", "gesucht", "looking for", "searching"]
    charter_offer_terms = ["charter", "for rent"]

    def process_item(self, item: OfferPageItem) -> OfferPageItem:
        for search_offer_term in self.search_offer_terms:
            if search_offer_term in item.title.lower():
                self.logger.debug(
                    "Dropping search offer, title='%s' url=%s", item.title, item.url
                )
                raise DropItem("Dropping Search offer")
        for charter_term in self.charter_offer_terms:
            if charter_term in item.title.lower():
                self.logger.debug(
                    "Dropping charter offer, title='%s' url=%s", item.title, item.url
                )
                raise DropItem("Dropping Charter Offer")
        return item


class SkipDuplicates(OfferPipelineFilter):
    logger = logging.getLogger("DuplicateDetection")

    @override
    def process_item(self, item: OfferPageItem) -> OfferPageItem:
        if offer_url_exists(item.url):
            self.logger.debug(f"Existing offer, title='{item.title}', url={item.url}")
            raise DropItem(
                f"Offer already exists in DB, title='{item.title}' url={item.url}"
            )
        else:
            return item


class ParsePrice(OfferPipelineFilter):
    logger = logging.getLogger("PriceParser")

    @override
    def process_item(self, item: OfferPageItem) -> OfferPageItem:
        try:
            price = Price.fromstring(item.raw_price)
            if price is None or price.amount is None:
                msg = f"Offer has no valid price, raw_price='{item.raw_price}' url={item.url}"
                self.logger.info(msg)
                raise DropItem(msg)

            if price.amount <= 1:
                msg = f"Offer has unreasonable price smaller than 1, price={price.amount_text}, url={item.url}"
                self.logger.info(msg)
                raise DropItem(msg)

            if price.amount > 1_500_000:
                msg = f"Offer has unreasonable price higher than 1_500_000, price={price.amount_text}, url={item.url} "
                self.logger.info(msg)
                raise DropItem(msg)

            (original_price, original_currency, price_in_euro, exchange_rate) = (
                to_price_in_euro(price)
            )

            item.price = original_price
            item.currency = original_currency
            item.price_in_euro = price_in_euro
            item.exchange_rate = exchange_rate

            return item

        except Exception as e:
            msg = f"Could not parse price for item {item.url}, error: {e}"
            self.logger.error(msg)
            raise DropItem(msg) from e


class StoreOffer(OfferPipelineFilter):
    logger = logging.getLogger("StoragePipeline")

    def __init__(self, crawler: Crawler):
        self._crawler = crawler

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "StoreOffer":
        return cls(crawler)

    @override
    def process_item(self, item: OfferPageItem) -> OfferPageItem:
        self.logger.info("Storing offer title='%s', url=%s", item.title, item.url)

        spider = self._crawler.spider
        if spider is not None:
            spider_name = spider.name or "unknown"
            if self._crawler.stats:
                self._crawler.stats.inc_value("items_stored")
        else:
            spider_name = "unknown"

        store_offer(offer=item, spider=spider_name)
        return item
