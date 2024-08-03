import scrapy
import datetime
import re
from my_logging import *

BASE_URL = "https://www.flugzeugmarkt.de/"
AIRCRAFT_OFFERS_URL = "https://www.flugzeugmarkt.de/flugzeug-kaufen"


class FlugzeugMarktDeSpider(scrapy.Spider):
    name = "flugzeugmarkt_de"
    logger = logging.getLogger(name)
    start_urls = [
        AIRCRAFT_OFFERS_URL
    ]

    aircraft_type_mapping = {
        "Motorsegler": "tmg",
        "Segelflugzeug": "glider",
        "Motorflugzeug": "airplane",
        "Ultraleichtflugzeug": "ultralight",
        "Helikopter": "helicopter"
    }

    def parse(self, response):
        self.logger.debug("parsing result page")
        aircraft_type = "airplane"
        for detail_url in response.css('div.content-inner a::attr(href)').extract():
            full_url_to_crawl = BASE_URL + detail_url[2:]
            self.logger.debug("yielding request %s", full_url_to_crawl)
            yield scrapy.Request(full_url_to_crawl,
                                 callback=self.parse_detail_page,
                                 errback=self.errback,
                                 meta={"aircraft_type": aircraft_type})

    def errback(self, failure):
        self.logger.error(repr(failure))

    def _extract_number_from_cell(self, name, response):
        number = response.xpath(
            "//tr/td[contains(.,'{0}')]/../td[@class='value']/text()".format(name)).extract_first().strip()
        number = "".join(re.findall(r'\d+', number))
        if len(number) > 0:
            return int(number)
        return 0

    def parse_detail_page(self, response):
        date = response.xpath("//tr/td[contains(.,'Eingestellt')]/../td[@class='value']/text()").extract_first()
        price_str = response.css('div.buy-it-now div.price::text').extract_first()
        location = response.xpath("//tr/td[contains(.,'Standort')]/../td[@class='value']/text()").extract_first()
        hours = self._extract_number_from_cell("Gesamtzeit", response)
        starts = self._extract_number_from_cell("Landungen", response)
        detail_text = response.xpath("//div/h3[contains(.,'Artikelbeschreibung')]/../p/text()").extract_first()
        title = response.css('#content #page-heading .container .row h1::text').extract_first()
        aircraft_type_german = response.xpath(
            "//tr/td[contains(.,'Flugzeugtyp')]/../td[@class='value']/text()").extract_first()
        if aircraft_type_german and aircraft_type_german in self.aircraft_type_mapping:
            aircraft_type = self.aircraft_type_mapping[aircraft_type_german]
        else:
            aircraft_type = None
            self.logger.info(
                "Couldn't determine aircraft type for offer: {0} with url: {1}".format(title, response.url))
        self.logger.debug("yielding title %s", title)
        yield {  # TODO introduce data class
            'title': title,
            'date': datetime.datetime.strptime(date, "%d.%m.%Y").date(),
            'raw_price': price_str,
            'offer_url': response.url,
            'location': location,
            'aircraft_type': aircraft_type,
            'hours': hours,
            'starts': starts,
            'detail_text': detail_text,
        }
