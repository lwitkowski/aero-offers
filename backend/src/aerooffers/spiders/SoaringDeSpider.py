# noqa: N999
import datetime
import re
from collections.abc import Generator
from typing import Any, override

import scrapy
from scrapy.http import Response
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.python.failure import Failure

from aerooffers.my_logging import logging
from aerooffers.offer import AircraftCategory, OfferPageItem

GLIDER_OFFERS_URL = "https://soaring.de/osclass/index.php?page=search&sCategory=118"
ENGINE_OFFERS_URL = "https://soaring.de/osclass/index.php?page=search&sCategory=119"
BROKEN_OFFER_URL = "https://soaring.de/osclass/index.php?page=item&id="


def _parse_int_or_none(param: str) -> int:
    return int(param) if param is not None else None


class SoaringDeSpider(scrapy.Spider):
    name = "segelflug_de_kleinanzeigen"
    _logger = logging.getLogger(name)

    start_urls = [
        GLIDER_OFFERS_URL,
        GLIDER_OFFERS_URL + "&iPage=2",
        GLIDER_OFFERS_URL + "&iPage=3",
        ENGINE_OFFERS_URL,
    ]

    AD_SELECTOR = ".listing-thumb"

    def _extract_first_number(self, text: str) -> int | None:
        match = re.search(r"\d+", text)
        if (
            match is not None
        ):  # avoid having text like: "2345 (aber eigentlich nur 45 stunden)"
            return _parse_int_or_none(match.group(0))
        return None

    @override
    def parse(
        self, response: Response, **kwargs: Any
    ) -> Generator[scrapy.Request, None]:
        self._logger.debug("Scraping %s", response.url)
        for detail_url in response.css("div.listing-attr a::attr(href)").extract():
            if detail_url == BROKEN_OFFER_URL:
                self._logger.debug("Url seems to be broken, skipping: %s", detail_url)
                continue

            assert response.request is not None
            if response.request.url == ENGINE_OFFERS_URL:
                aircraft_category = AircraftCategory.airplane
            else:
                aircraft_category = AircraftCategory.glider

            self._logger.debug("Adding detail page for scraping %s", detail_url)
            yield scrapy.Request(
                detail_url,
                callback=self._parse_detail_page,
                errback=self._errback,
                meta={"aircraft_category": aircraft_category},
            )

    def _errback(self, failure: Failure) -> Any:
        if failure.check(HttpError):
            response = failure.value.response  # type: ignore
            self._logger.error(
                "Crawler HttpError status=%s url=%s", response.status, response.url
            )
        else:
            self._logger.error("Crawler generic exception: %s", repr(failure))

    def _parse_detail_page(self, response: Response) -> Generator[OfferPageItem, None]:
        self._logger.debug("Parsing offer page %s", response.url)
        try:
            date_str = response.css("#item-content .item-header li::text").extract()[3]
            date_str = date_str.replace("Veröffentlichungsdatum:", "").strip()

            offer = OfferPageItem(
                url=response.url,
                category=response.meta["aircraft_category"],
                title=response.css("#item-content .title strong::text").extract_first()
                or "",
                published_at=datetime.datetime.strptime(date_str, "%d/%m/%Y").date(),
                page_content="".join(response.css("div#description").extract()).strip(),
            )
            offer.raw_price = response.css(
                "#item-content .item-header li::text"
            ).extract()[1]

            raw_location = response.css(
                "#item-content #item_location li::text"
            ).extract_first()
            if raw_location is not None:
                offer.location = raw_location.strip()

            for aircraft_details in response.css(
                "#item-content .meta_list .meta"
            ).extract():
                if "Gesamtstunden" in aircraft_details:
                    offer.hours = self._extract_first_number(aircraft_details)
                if "Gesamtstarts" in aircraft_details:
                    offer.starts = self._extract_first_number(aircraft_details)

            yield offer

        except Exception:
            self._logger.error("Could not parse detail page %s because %s")
