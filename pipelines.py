import datetime

from scrapy.exceptions import DropItem

import db
from my_logging import *
from spiders import SegelflugDeSpider, FlugzeugMarktDeSpider, PlaneCheckComSpider
from exchange_rates import get_currency_code

logger = logging.getLogger('pipeline')


class DuplicateDetection(object):

    def process_item(self, item, spider):
        logger.debug("Detecting duplicates for item %s", str(item))
        if spider.name in [SegelflugDeSpider.SegelflugDeSpider.name,
                           FlugzeugMarktDeSpider.FlugzeugMarktDeSpider.name,
                           PlaneCheckComSpider.PlaneCheckComSpider.name]:
            has_offer = db.has_offer_url(item["offer_url"])
            if has_offer:
                logger.debug("Offer URL matches, Offer is already stored. dropping item")
                raise DropItem("Offer already stored")
            elif item['price'].amount is None:
                raise DropItem("Offer has no price")
        else:
            logger.warning("Can't handle this spider for duplicate detection: %s", spider.name)
        return item


class FilterUnreasonablePrices(object):

    def process_item(self, item, _):
        logger.debug("Filtering Prices of 1 and below")
        if item["price"] and item["price"].amount <= 1:
            raise DropItem("Offer has price of 1 (or below)")
        return item


class FilterSearchAndCharterOffers(object):
    search_offer_terms = ["suche", "gesucht", "looking for", "searching"]
    charter_offer_terms = ["charter", "for rent"]

    def process_item(self, item, _):
        logger.debug("Filtering Searches for Aircraft Offers")
        for search_offer_term in self.search_offer_terms:
            if search_offer_term in item["title"].lower():
                logger.info("dropping search offer: " + str(item["title"]))
                raise DropItem("Dropping Search offer")
        for charter_term in self.charter_offer_terms:
            if charter_term in item["title"].lower():
                logger.info("dropping charter offer: " + str(item["title"]))
                raise DropItem("Dropping Charter Offer")
        return item


class StoragePipeline(object):

    def process_item(self, item, spider):
        spider.crawler.stats.inc_value('items_stored')
        logger.debug("Storing offer %s", str(item))
        logging.debug("Fetching currency code")
        currency_code = get_currency_code(item["price"])
        logging.debug("currency code is {0}".format(currency_code))
        db.store_offer(db.AircraftOffer(
            title=item["title"],
            creation_datetime=datetime.datetime.now(),
            date=item["date"],
            price=item["price"].amount,
            currency=item["price"].currency,
            currency_code=currency_code,
            location=item["location"],
            offer_url=item["offer_url"],
            spider=spider.name,
            hours=item["hours"],
            starts=item["starts"],
            detail_text=item["detail_text"],
            aircraft_type=item["aircraft_type"],
        ))
        return item
