import scrapy
import datetime
import re
from price_parser import Price
from my_logging import *

GLIDER_OFFERS_URL = "https://soaring.de/osclass/index.php?page=search&sCategory=118"
ENGINE_OFFERS_URL = "https://soaring.de/osclass/index.php?page=search&sCategory=119"


class SegelflugDeSpider(scrapy.Spider):
    name = "segelflug_de_kleinanzeigen"
    logger = logging.getLogger(name)

    start_urls = [GLIDER_OFFERS_URL, ENGINE_OFFERS_URL]

    AD_SELECTOR = ".listing-thumb"

    def _extract_first_number(self, text):
        match = re.search(r'\d+', text)
        if match is not None:  # avoid having text like: "2345 (aber eigentlich nur 45 stunden)"
            return match.group(0)
        return None

    def parse(self, response):
        for detail_url in response.css('div.listing-attr a::attr(href)').extract():
            if response.request.url == ENGINE_OFFERS_URL:
                aircraft_type = "airplane"
            else:
                aircraft_type = "glider"
            self.logger.debug("yielding url %s", detail_url)
            yield scrapy.Request(detail_url,
                                 callback=self.parse_detail_page,
                                 errback=self.errback,
                                 meta={"aircraft_type": aircraft_type})

    def errback(self, failure):
        self.logger.error("%s", repr(failure))

    def parse_detail_page(self, response):
        price_str = response.css('#item-content .item-header li::text').extract()[1]
        parsed_price = Price.fromstring(price_str)
        date_str = response.css('#item-content .item-header li::text').extract()[3]
        date_str = date_str.replace('Veröffentlichungsdatum:', '').strip()
        date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
        location = response.css('#item-content #item_location li::text').extract_first()
        if location is not None:
            location = location.strip()
        hours = None
        starts = None
        detail_text = "".join(response.css('div#description').extract()).strip()
        for aircraft_details in response.css('#item-content .meta_list .meta').extract():
            if 'Gesamtstunden' in aircraft_details:
                hours = self._extract_first_number(aircraft_details)
            if 'Gesamtstarts' in aircraft_details:
                starts = self._extract_first_number(aircraft_details)

        yield {
            'title': response.css('#item-content .title strong::text').extract_first(),
            'price': parsed_price,
            'offer_url': response.url,
            'location': location,
            'date': date_obj,
            'hours': hours,
            'starts': starts,
            'detail_text': detail_text,
            'aircraft_type': response.meta['aircraft_type'],
        }
