import scrapy
import datetime
from my_logging import *

BASE_URL = "https://www.planecheck.com/"
AIRCRAFT_OFFERS_URL = BASE_URL + "aspseld.asp"
OFFER_PREFIX = "aspdet.asp?nr="


class PlaneCheckComSpider(scrapy.Spider):
    name = "planecheck_com"
    logger = logging.getLogger(name)
    start_urls = [AIRCRAFT_OFFERS_URL]

    def parse(self, response):
        aircraft_type = "airplane"
        # check for all a tags starting with <a href="aspdet.asp?nr=39145">
        for detail_url in response.css('a::attr(href)').extract():
            if OFFER_PREFIX not in detail_url:
                self.logger.debug("Skipping URL which is no offer: " + detail_url)
                continue
            full_url_to_crawl = BASE_URL + detail_url
            self.logger.debug("yielding request %s", full_url_to_crawl)
            yield scrapy.Request(full_url_to_crawl,
                                 callback=self.parse_detail_page,
                                 errback=self.errback,
                                 meta={"aircraft_type": aircraft_type})

    def parse_detail_page(self, response):
        title = response.css('font.bigtitle6 b::text').extract_first().replace(u'\xa0', u' ')
        date = response.xpath("//td[contains(.,'Last updated')]/../td[2]/text()").extract()[1].strip()
        # check for VAT (commercial offers)
        full_price_str = response.xpath("//td[contains(.,'Price')]/../td[2][contains(.,',')]").extract_first()
        if "excl" in full_price_str and "VAT" in full_price_str:
            logging.info("VAT is excluded, looking for the price with VAT included (url={0})".format(response.url))
            price_str = response.xpath("//td[contains(.,'incl VAT ]')]/../td[2][contains(.,',')]/text()").extract_first()
            logging.info("price with VAT should be: {0}".format(price_str))
        else:
            price_str = response.xpath("//td[contains(.,'Price')]/../td[2][contains(.,',')]/b/text()").extract_first()
        location = response.xpath("//td/b[contains(.,'Country')]/../../td[2]/text()").extract_first()
        yield {  # TODO introduce data class
            'offer_url': response.url,
            'title': title,
            'aircraft_type': 'airplane',
            'date': datetime.datetime.strptime(date, "%d-%m-%Y").date(),  # last updated value
            'raw_price': price_str,
            'detail_text': response.text,
            'location': location,  # TODO currently only the country is extracted,
            'hours': -1,
            'starts': -1
        }

    def errback(self, failure):
        self.logger.error("%s", repr(failure))
