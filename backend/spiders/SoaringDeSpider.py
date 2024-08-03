import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
import datetime
import re
from my_logging import *

GLIDER_OFFERS_URL = "https://soaring.de/osclass/index.php?page=search&sCategory=118"
ENGINE_OFFERS_URL = "https://soaring.de/osclass/index.php?page=search&sCategory=119"
BROKEN_OFFER_URL = "https://soaring.de/osclass/index.php?page=item&id="

# former SegelflugDeSpider
class SoaringDeSpider(scrapy.Spider):
    name = "segelflug_de_kleinanzeigen" # fixme, possibly needs db rows update
    logger = logging.getLogger(name)

    start_urls = [
        GLIDER_OFFERS_URL,
        ENGINE_OFFERS_URL
    ]

    AD_SELECTOR = ".listing-thumb"

    def _extract_first_number(self, text):
        match = re.search(r'\d+', text)
        if match is not None:  # avoid having text like: "2345 (aber eigentlich nur 45 stunden)"
            return match.group(0)
        return None

    def parse(self, response):
        for detail_url in response.css('div.listing-attr a::attr(href)').extract():
            if(detail_url == BROKEN_OFFER_URL):
                continue

            if response.request.url == ENGINE_OFFERS_URL:
                aircraft_type = "airplane"
            else:
                aircraft_type = "glider"

            self.logger.debug("Scraping offer detail url %s", detail_url)
            yield scrapy.Request(detail_url,
                                 callback=self.parse_detail_page,
                                 errback=self.errback,
                                 meta={"aircraft_type": aircraft_type})

    def errback(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("Crawler HttpError status=%s url=%s", response.status, response.url)
        else:
            self.logger.error("Crawler generic exception: %s", repr(failure))

    def parse_detail_page(self, response):
        price_str = response.css('#item-content .item-header li::text').extract()[1]
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

        yield {  # TODO introduce data class
            'title': response.css('#item-content .title strong::text').extract_first(),
            'raw_price': price_str,
            'offer_url': response.url,
            'location': location,
            'date': date_obj,
            'hours': hours,
            'starts': starts,
            'detail_text': detail_text,
            'aircraft_type': response.meta['aircraft_type'],
        }
