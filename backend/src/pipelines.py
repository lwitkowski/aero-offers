from price_parser import Price
from scrapy.exceptions import DropItem

import offers_db
from fx import to_price_in_euro
from my_logging import logging
from offer import OfferPageItem


class FilterSearchAndCharterOffers:
    logger = logging.getLogger("FilterSearchAndCharterOffers")

    search_offer_terms = ["suche", "gesucht", "looking for", "searching"]
    charter_offer_terms = ["charter", "for rent"]

    def process_item(self, item: OfferPageItem, _):
        self.logger.info("Checking if offer page is sell offer: " + item.url)
        for search_offer_term in self.search_offer_terms:
            if search_offer_term in item.title.lower():
                self.logger.info(
                    "Dropping search offer, title='%s' url=%s", item.title, item.url
                )
                raise DropItem("Dropping Search offer")
        for charter_term in self.charter_offer_terms:
            if charter_term in item.title.lower():
                self.logger.info(
                    "Dropping charter offer, title='%s' url=%s", item.title, item.url
                )
                raise DropItem("Dropping Charter Offer")
        return item


class DuplicateDetection:
    logger = logging.getLogger("DuplicateDetection")

    def process_item(self, item: OfferPageItem, _):
        self.logger.info("Checking if offer is already stored in DB: " + item.url)
        if offers_db.offer_url_exists(item.url):
            self.logger.debug(f"Offer already exists in DB, url={item.url}")
            raise DropItem(f"Offer already exists in DB, url={item.url}")
        return item


class PriceParser:
    logger = logging.getLogger("PriceParser")

    def process_item(self, item: OfferPageItem, _):
        self.logger.info("Parsing price: " + item.url)
        try:
            price = Price.fromstring(item.raw_price)
            if price is None or price.amount is None:
                msg = f"Offer has no valid price, raw_price='{item.raw_price.strip()}' url={item.url}"
                self.logger.info(msg)
                raise DropItem(msg)

            if price.amount <= 1:
                msg = f"Offer has unreasonable price smaller than 1, price={price.amount_text}, url={item.url}"
                self.logger.info(msg)
                raise DropItem(msg)

            if price.amount > 500_000:
                msg = f"Offer has unreasonable price higher than 500_000, price={price.amount_text}, url={item.url} "
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


class StoragePipeline:
    logger = logging.getLogger("StoragePipeline")

    def process_item(self, item: OfferPageItem, spider=None):
        self.logger.debug(
            "Storing offer title='%s', url=%s, currency=%s",
            item.title,
            item.url,
            item.currency,
        )

        if spider is not None:
            spider.crawler.stats.inc_value("items_stored")

        offers_db.store_offer(
            offer=item, spider=spider.name if spider is not None else "unknown"
        )
        return item
