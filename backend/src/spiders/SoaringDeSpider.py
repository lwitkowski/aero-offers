from typing import Any

import scrapy
from scrapy.http import Response
from scrapy.spidermiddlewares.httperror import HttpError
import datetime
import re
from my_logging import *
from offer import OfferPageItem, AircraftCategory

GLIDER_OFFERS_URL = "https://soaring.de/osclass/index.php?page=search&sCategory=118"
ENGINE_OFFERS_URL = "https://soaring.de/osclass/index.php?page=search&sCategory=119"
BROKEN_OFFER_URL = "https://soaring.de/osclass/index.php?page=item&id="


def parseIntOrNone(param):
    return int(param) if param is not None else None


class SoaringDeSpider(scrapy.Spider):
    name = "segelflug_de_kleinanzeigen"
    logger = logging.getLogger(name)

    start_urls = [
        GLIDER_OFFERS_URL,
        #GLIDER_OFFERS_URL + "&iPage=2",
        #GLIDER_OFFERS_URL + "&iPage=3",
        #GLIDER_OFFERS_URL + "&iPage=4",
        #GLIDER_OFFERS_URL + "&iPage=5",
        #GLIDER_OFFERS_URL + "&iPage=6",
        ENGINE_OFFERS_URL
    ]

    AD_SELECTOR = ".listing-thumb"

    def _extract_first_number(self, text):
        match = re.search(r'\d+', text)
        if match is not None:  # avoid having text like: "2345 (aber eigentlich nur 45 stunden)"
            return match.group(0)
        return None

    def parse(self, response: Response, **kwargs):
        for detail_url in response.css('div.listing-attr a::attr(href)').extract():
            if detail_url == BROKEN_OFFER_URL:
                continue

            if response.request.url == ENGINE_OFFERS_URL:
                aircraft_category = AircraftCategory.airplane
            else:
                aircraft_category = AircraftCategory.glider

            self.logger.debug("Scraping offer detail url %s", detail_url)
            yield scrapy.Request(detail_url,
                                 callback=self.parse_detail_page,
                                 errback=self.errback,
                                 meta={"aircraft_category": aircraft_category})

    def errback(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("Crawler HttpError status=%s url=%s", response.status, response.url)
        else:
            self.logger.error("Crawler generic exception: %s", repr(failure))

    def parse_detail_page(self, response):
        try:
            date_str = response.css('#item-content .item-header li::text').extract()[3]
            date_str = date_str.replace('Veröffentlichungsdatum:', '').strip()

            offer = OfferPageItem(
                url=response.url,
                category=response.meta['aircraft_category'],
                title=response.css('#item-content .title strong::text').extract_first(),
                published_at=datetime.datetime.strptime(date_str, "%d/%m/%Y").date(),
                page_content="".join(response.css('div#description').extract()).strip()
            )
            offer.raw_price = response.css('#item-content .item-header li::text').extract()[1]

            raw_location = response.css('#item-content #item_location li::text').extract_first()
            if raw_location is not None:
                offer.location = raw_location.strip()

            for aircraft_details in response.css('#item-content .meta_list .meta').extract():
                if 'Gesamtstunden' in aircraft_details:
                    offer.hours = parseIntOrNone(self._extract_first_number(aircraft_details))
                if 'Gesamtstarts' in aircraft_details:
                    offer.starts = parseIntOrNone(self._extract_first_number(aircraft_details))

            yield offer

        except Exception as e:
            self.logger.error(e)
