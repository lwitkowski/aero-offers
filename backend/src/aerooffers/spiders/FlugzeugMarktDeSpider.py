# noqa: N999
import datetime
import re
from collections.abc import Generator
from typing import Any

import scrapy
from scrapy.http import Response
from twisted.python.failure import Failure

from aerooffers.my_logging import logging
from aerooffers.offer import AircraftCategory, OfferPageItem

BASE_URL = "https://www.flugzeugmarkt.de/"
AIRCRAFT_OFFERS_URL = "https://www.flugzeugmarkt.de/flugzeug-kaufen"


class FlugzeugMarktDeSpider(scrapy.Spider):
    name = "flugzeugmarkt_de"
    _logger = logging.getLogger(name)
    start_urls = [AIRCRAFT_OFFERS_URL]

    aircraft_type_mapping = {
        "Motorsegler": AircraftCategory.tmg,
        "Segelflugzeug": AircraftCategory.glider,
        "Motorflugzeug": AircraftCategory.airplane,
        "Ultraleichtflugzeug": AircraftCategory.ultralight,
        "Helikopter": AircraftCategory.helicopter,
    }

    def parse(self, response: Response) -> Generator[scrapy.Request, None]:
        self._logger.debug("Scraping %s", response.url)
        for detail_url in response.css("div.content-inner a::attr(href)").extract():
            full_url_to_crawl = BASE_URL + detail_url[2:]
            self._logger.debug("Adding detail page for scraping %s", full_url_to_crawl)
            yield scrapy.Request(
                full_url_to_crawl,
                callback=self._parse_detail_page,
                errback=self._errback,
            )

    def _errback(self, failure: Failure) -> Any:
        self._logger.error(repr(failure))

    def _extract_number_from_cell(self, name: str, response: Response) -> int:
        raw = response.xpath(
            f"//tr/td[contains(.,'{name}')]/../td[@class='value']/text()"
        ).extract_first()
        if raw is None:
            return 0

        number = "".join(re.findall(r"\d+", raw.strip()))
        if len(number) > 0:
            return int(number)
        return 0

    def _parse_detail_page(self, response: Response) -> Generator[OfferPageItem, None]:
        self._logger.debug("Parsing offer page %s", response.url)
        try:
            aircraft_type_german = response.xpath(
                "//tr/td[contains(.,'Flugzeugtyp')]/../td[@class='value']/text()"
            ).extract_first()
            if (
                aircraft_type_german
                and aircraft_type_german in self.aircraft_type_mapping
            ):
                category = self.aircraft_type_mapping[aircraft_type_german]
            else:
                category = AircraftCategory.unknown
                self._logger.info(
                    f"Couldn't determine aircraft type for offer with url: {response.url}"
                )

            date = (
                response.xpath(
                    "//tr/td[contains(.,'Eingestellt')]/../td[@class='value']/text()"
                ).extract_first()
                or ""
            )

            offer = OfferPageItem(
                url=response.url,
                category=category,
                title=response.css(
                    "#content #page-heading .container .row h1::text"
                ).extract_first()
                or "",
                published_at=datetime.datetime.strptime(date, "%d.%m.%Y").date(),
                page_content=response.xpath(
                    "//div/h3[contains(.,'Artikelbeschreibung')]/../p/text()"
                ).extract_first()
                or "",
            )

            offer.raw_price = response.css(
                "div.buy-it-now div.price::text"
            ).extract_first()
            offer.location = response.xpath(
                "//tr/td[contains(.,'Standort')]/../td[@class='value']/text()"
            ).extract_first()
            offer.hours = int(self._extract_number_from_cell("Gesamtzeit", response))
            offer.starts = int(self._extract_number_from_cell("Landungen", response))

            yield offer

        except Exception as e:
            self._logger.error(
                f"Could not parse details of url: {response.url}, error: {e}"
            )
