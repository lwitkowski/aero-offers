import scrapy
import datetime
import re
from my_logging import *
from offer import OfferPageItem, AircraftCategory

BASE_URL = "https://www.flugzeugmarkt.de/"
AIRCRAFT_OFFERS_URL = "https://www.flugzeugmarkt.de/flugzeug-kaufen"


class FlugzeugMarktDeSpider(scrapy.Spider):
    name = "flugzeugmarkt_de"
    logger = logging.getLogger(name)
    start_urls = [
        AIRCRAFT_OFFERS_URL
    ]

    aircraft_type_mapping = {
        "Motorsegler": AircraftCategory.tmg,
        "Segelflugzeug": AircraftCategory.glider,
        "Motorflugzeug": AircraftCategory.airplane,
        "Ultraleichtflugzeug": AircraftCategory.ultralight,
        "Helikopter": AircraftCategory.helicopter
    }

    def parse(self, response, **kwargs):
        self.logger.debug("Scraping %s", response.url)
        for detail_url in response.css('div.content-inner a::attr(href)').extract():
            full_url_to_crawl = BASE_URL + detail_url[2:]
            self.logger.debug("Adding detail page for scraping %s", full_url_to_crawl)
            yield scrapy.Request(full_url_to_crawl,
                                 callback=self.parse_detail_page,
                                 errback=self.errback)

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
        self.logger.debug("Parsing offer page %s", response.url)
        try:
            aircraft_type_german = response.xpath(
                "//tr/td[contains(.,'Flugzeugtyp')]/../td[@class='value']/text()").extract_first()
            if aircraft_type_german and aircraft_type_german in self.aircraft_type_mapping:
                category = self.aircraft_type_mapping[aircraft_type_german]
            else:
                category = None
                self.logger.info(
                    "Couldn't determine aircraft type for offer with url: {0}".format(response.url))

            date = response.xpath("//tr/td[contains(.,'Eingestellt')]/../td[@class='value']/text()").extract_first()

            offer = OfferPageItem(
                url=response.url,
                category=category,
                title=response.css('#content #page-heading .container .row h1::text').extract_first(),
                published_at=datetime.datetime.strptime(date, "%d.%m.%Y").date(),
                page_content=response.xpath("//div/h3[contains(.,'Artikelbeschreibung')]/../p/text()").extract_first()
            )

            offer.raw_price = response.css('div.buy-it-now div.price::text').extract_first()
            offer.location = response.xpath("//tr/td[contains(.,'Standort')]/../td[@class='value']/text()").extract_first()
            offer.hours = int(self._extract_number_from_cell("Gesamtzeit", response))
            offer.starts = int(self._extract_number_from_cell("Landungen", response))

            yield offer

        except Exception as e:
            self.logger.error("Could not parse details of url: {0}, error: {1}".format(response.url, e))
