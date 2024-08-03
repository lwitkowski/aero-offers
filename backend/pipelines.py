import datetime
from scrapy.exceptions import DropItem
from price_parser import Price

import db
from my_logging import *
from exchange_rates import get_currency_code

logger = logging.getLogger('pipeline')

class DuplicateDetection(object):

    def process_item(self, item, _):
        if db.offer_url_exists(item["offer_url"]):
            logger.debug("Offer already exists in DB, url={0}".format(item["offer_url"]))
            raise DropItem("Offer already exists in DB, url={0}".format(item["offer_url"]))
        return item


class PriceParser(object):

    def process_item(self, item, _):
        price = Price.fromstring(item['raw_price'])
        if price is None or price.amount is None:
            msg = "Offer has no valid price, raw_price='{0}' url={1}".format(item['raw_price'].strip(), item["offer_url"])
            logger.info(msg)
            raise DropItem(msg)

        if price.amount <= 1:
            msg = "Offer has unreasonable price smaller than 1, price={0}, url={1}".format(price.amount_text, item["offer_url"])
            logger.info(msg)
            raise DropItem(msg)

        if price.amount > 500_000:
            msg = "Offer has unreasonable price higher than 500_000, price={0}, url={1} ".format(price.amount_text, item["offer_url"])
            logger.info(msg)
            raise DropItem(msg)

        item['price'] = price
        return item


class FilterSearchAndCharterOffers(object):
    search_offer_terms = ["suche", "gesucht", "looking for", "searching"]
    charter_offer_terms = ["charter", "for rent"]

    def process_item(self, item, _):
        for search_offer_term in self.search_offer_terms:
            if search_offer_term in item["title"].lower():
                logger.info("Dropping search offer, title='%s' url=%s", item["title"], item["offer_url"])
                raise DropItem("Dropping Search offer")
        for charter_term in self.charter_offer_terms:
            if charter_term in item["title"].lower():
                logger.info("Dropping charter offer, title='%s' url=%s", item["title"], item["offer_url"])
                raise DropItem("Dropping Charter Offer")
        return item


class StoragePipeline(object):

    def process_item(self, item, spider=None):
        if spider is not None:
            spider.crawler.stats.inc_value('items_stored')

        currency_code = get_currency_code(item["price"])
        logger.debug("Storing offer title='%s', url=%s, currency_code=%s", item["title"], item["offer_url"], currency_code)

        db.store_offer(db.AircraftOffer(
            title=item["title"],
            creation_datetime=datetime.datetime.now(),
            date=item["date"],
            price=item["price"].amount,
            currency=item["price"].currency,
            currency_code=currency_code,
            location=item["location"],
            offer_url=item["offer_url"],
            spider=spider.name if spider is not None else "unknown",
            hours=item["hours"],
            starts=item["starts"],
            detail_text=item["detail_text"],
            aircraft_type=item["aircraft_type"],
        ))
        return item
