# noqa: N999
import datetime
import re
from collections.abc import Generator
from typing import Any, override

import scrapy
from scrapy.http import Response
from twisted.python.failure import Failure

from aerooffers.my_logging import logging
from aerooffers.offer import AircraftCategory, OfferPageItem

BASE_URL = "https://www.flugzeugmarkt.de/"


class FlugzeugMarktDeSpider(scrapy.Spider):
    name = "flugzeugmarkt_de"
    _logger = logging.getLogger(name)

    # Rate limiting to avoid 429 throttling responses
    custom_settings = {
        "DOWNLOAD_DELAY": 2.0,  # Minimum delay between requests in seconds
        "RANDOMIZE_DOWNLOAD_DELAY": 0.5,  # Randomization factor: delay varies between 50% and 150% of DOWNLOAD_DELAY
    }

    start_urls = [
        "https://www.flugzeugmarkt.de/segelflugzeuge",
        "https://www.flugzeugmarkt.de/motorsegler",
        "https://www.flugzeugmarkt.de/motorflugzeuge",
        "https://www.flugzeugmarkt.de/ultraleichtflugzeuge",
        "https://www.flugzeugmarkt.de/helikopter",
    ]

    aircraft_type_mapping = {
        "Motorsegler": AircraftCategory.tmg,
        "Segelflugzeug": AircraftCategory.glider,
        "Motorflugzeug": AircraftCategory.airplane,
        "Ultraleichtflugzeug": AircraftCategory.ultralight,
        "Helikopter": AircraftCategory.helicopter,
    }

    @override
    def parse(
        self, response: Response, **kwargs: Any
    ) -> Generator[scrapy.Request, None]:
        self._logger.debug("Scraping %s", response.url)
        seen: set[str] = set()
        detail_urls = response.css("div.aircraft-listing a.slide::attr(href)").extract()
        if not detail_urls:
            # fallback for older markup
            detail_urls = response.css("div.content-inner a::attr(href)").extract()

        for detail_url in detail_urls:
            if not detail_url or not detail_url.startswith("./"):
                continue
            if detail_url in seen:
                continue
            seen.add(detail_url)

            full_url_to_crawl = BASE_URL + detail_url[2:]
            self._logger.debug("Adding detail page for scraping %s", full_url_to_crawl)
            yield scrapy.Request(
                full_url_to_crawl,
                callback=self._parse_detail_page,
                errback=self._errback,
            )

    def _errback(self, failure: Failure) -> Any:
        self._logger.error(repr(failure))

    def _extract_detail_value(self, name: str, response: Response) -> str:
        # Newer markup uses "day"/"schedule" blocks:
        # <div class="day">Standort</div> ... <span class="schedule">Verviers</span>
        raw = response.xpath(
            f"//div[@class='day' and normalize-space()='{name}']/../../span[contains(@class,'schedule')]//text()"
        ).get()
        if raw:
            return raw.strip()

        # Fallback to older table markup
        raw = response.xpath(
            f"//tr/td[contains(.,'{name}')]/../td[@class='value']//text()"
        ).get()
        return (raw or "").strip()

    def _extract_number_from_cell(self, name: str, response: Response) -> int:
        raw = self._extract_detail_value(name, response)
        if not raw:
            return 0

        number = "".join(re.findall(r"\d+", raw))
        if len(number) > 0:
            return int(number)
        return 0

    def _parse_detail_page(self, response: Response) -> Generator[OfferPageItem, None]:
        self._logger.debug("Parsing offer page %s", response.url)
        try:
            aircraft_type_german = self._extract_detail_value("Flugzeugtyp", response)
            if (
                aircraft_type_german
                and aircraft_type_german in self.aircraft_type_mapping
            ):
                category = (
                    self.aircraft_type_mapping[aircraft_type_german]
                    or AircraftCategory.unknown
                )
            else:
                category = AircraftCategory.unknown
                self._logger.info(
                    f"Couldn't determine aircraft type for offer with url: {response.url}"
                )

            date = response.css(
                "meta[property='article:published_time']::attr(content)"
            ).get()
            if date:
                # example: 2025-12-02T07:08:09+01:00
                published_at = datetime.date.fromisoformat(date[:10])
            else:
                date_ddmmyyyy = (
                    response.css("ul.aircraft_info i.fa-clock-o")
                    .xpath("parent::span/text()")
                    .get()
                    or ""
                ).strip()
                published_at = datetime.datetime.strptime(
                    date_ddmmyyyy, "%d.%m.%Y"
                ).date()

            title = response.css("h1.title::text").get()
            if not title:
                title = response.css(
                    "#content #page-heading .container .row h1::text"
                ).get()

            page_content_parts = response.css(
                "div.aircraft_description p.first-para ::text"
            ).getall()
            if page_content_parts:
                page_content = " ".join(
                    p.strip() for p in page_content_parts if p.strip()
                )
            else:
                page_content = (
                    response.xpath(
                        "//div/h3[contains(.,'Artikelbeschreibung')]/../p//text()"
                    ).get()
                    or ""
                ).strip()

            offer = OfferPageItem(
                url=response.url,
                category=category,
                title=(title or "").strip(),
                published_at=published_at,
                page_content=page_content,
            )

            offer.raw_price = (
                response.css("div.price_content div.price span::text").get()
                or response.css("div.buy-it-now div.price::text").get()
            )
            offer.location = self._extract_detail_value("Standort", response) or None
            offer.hours = int(self._extract_number_from_cell("Gesamtzeit", response))
            offer.starts = int(self._extract_number_from_cell("Landungen", response))

            yield offer

        except Exception as e:
            self._logger.error(
                f"Could not parse details of url: {response.url}, error: {e}"
            )
