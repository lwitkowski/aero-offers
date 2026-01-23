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
from aerooffers.offers_db import offer_url_exists

ROOT_URL = "https://www.segelflug.de"


def _parse_int_or_none(param: str) -> int:
    return int(param) if param is not None else None


class SegelflugDeSpider(scrapy.Spider):
    name = "segelflug_de_2026"
    _logger = logging.getLogger(name)

    start_urls_with_category: dict[str, AircraftCategory] = {
        "https://www.segelflug.de/index.php/de/kleinanzeigen/filterseite-de/com-djclassifieds-cat-sailplanes,5": AircraftCategory.glider,
        "https://www.segelflug.de/index.php/de/kleinanzeigen/filterseite-de/com-djclassifieds-cat-motorplanes,11": AircraftCategory.tmg,
    }

    @property
    def start_urls(self) -> list[str]:  # type: ignore[override]
        """Generate start_urls from dictionary keys for Scrapy compatibility."""
        return list(self.start_urls_with_category.keys())

    def _extract_first_number(self, text: str) -> int | None:
        match = re.search(r"\d+", text)
        if (
            match is not None
        ):  # avoid having text like: "2345 (aber eigentlich nur 45 stunden)"
            return _parse_int_or_none(match.group(0))
        return None

    def _parse_date(self, date_text: str) -> datetime.date:
        """Parse date in format 'Published: 06 November 2025' or 'Veröffentlicht am: 06. November 2025'."""
        # Remove prefix if present
        date_text = (
            date_text.replace("Published:", "")
            .replace("Veröffentlicht am:", "")
            .strip()
        )

        # German and English month names mapping
        months = {
            "januar": 1,
            "februar": 2,
            "märz": 3,
            "april": 4,
            "mai": 5,
            "juni": 6,
            "juli": 7,
            "august": 8,
            "september": 9,
            "oktober": 10,
            "november": 11,
            "dezember": 12,
            "january": 1,
            "february": 2,
            "march": 3,
            "may": 5,
            "june": 6,
            "july": 7,
            "october": 10,
            "december": 12,
        }

        # Match pattern: DD. Month YYYY or DD Month YYYY
        match = re.search(r"(\d{1,2})\.?\s*(\w+)\s*(\d{4})", date_text, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower()
            year = int(match.group(3))
            month = months.get(month_name)
            if month:
                return datetime.date(year, month, day)

        raise ValueError(f"Could not parse date: {date_text}")

    @override
    def parse(
        self, response: Response, **kwargs: Any
    ) -> Generator[scrapy.Request, None]:
        assert response.request is not None

        self._logger.debug("Scraping %s", response.url)

        visited = set()
        category = self.start_urls_with_category.get(
            response.request.url, AircraftCategory.unknown
        )
        for detail_url in response.css("h3.el-title a::attr(href)").extract():
            if detail_url in visited or "task=addFavourite" in detail_url:
                continue

            visited.add(detail_url)

            full_url = ROOT_URL + detail_url

            # Check if already exists in DB (duplication detection)
            if offer_url_exists(full_url):
                self._logger.debug("Skipping existing offer: %s", full_url)
                continue

            self._logger.debug("Adding offer for scraping %s", full_url)
            yield scrapy.Request(
                full_url,
                callback=self._parse_detail_page,
                errback=self._errback,
                meta={"aircraft_category": category},
            )

    def _errback(self, failure: Failure) -> Any:
        if failure.check(HttpError):
            response = failure.value.response  # type: ignore
            self._logger.error(
                "Crawler HttpError status=%s url=%s", response.status, response.url
            )
        else:
            self._logger.error("Crawler generic exception: %s", repr(failure))

    def _extract_title(self, response: Response) -> str:
        """Extract title from the offer page."""
        title = response.css("h1.uk-h2::text, h1::text").extract_first()
        if title:
            return title.strip()
        raise ValueError("Could not find title on page")

    def _extract_price(self, response: Response) -> str:
        """Extract price from the offer page."""
        price_val = response.css(".price_val::text").extract_first()
        price_unit = response.css(".price_unit::text").extract_first()
        if price_val:
            if price_unit:
                return f"{price_val} {price_unit}".strip()
            return price_val.strip()
        raise ValueError("Could not find price on page")

    def _extract_published_at(self, response: Response) -> datetime.date:
        """Extract published date from the offer page."""
        date_text = response.xpath(
            '//text()[contains(., "Published:") or contains(., "Veröffentlicht am:")]'
        ).extract_first()
        if not date_text:
            raise ValueError("Could not find date on page")
        return self._parse_date(date_text)

    def _extract_hours(self, response: Response) -> int | None:
        """Extract hours from the offer page."""
        hours_text = response.xpath('//text()[contains(., "Stunden:")]').extract_first()
        if hours_text:
            hours_match = re.search(r"Stunden:\s*(\d+)", hours_text)
            if hours_match:
                return self._extract_first_number(hours_match.group(1))

        # Search in all text (Stunden: might be in separate elements)
        all_text = " ".join(response.css("::text").extract())
        hours_match = re.search(r"Stunden[:\s]*(\d+)", all_text, re.IGNORECASE)
        if hours_match:
            return self._extract_first_number(hours_match.group(1))

        return None

    def _extract_starts(self, response: Response) -> int | None:
        """Extract starts from the offer page."""
        starts_text = response.xpath('//text()[contains(., "Starts:")]').extract_first()
        if starts_text:
            starts_match = re.search(r"Starts:\s*(\d+)", starts_text)
            if starts_match:
                return self._extract_first_number(starts_match.group(1))

        # Search in all text (Starts: might be in separate elements)
        all_text = " ".join(response.css("::text").extract())
        starts_match = re.search(r"Starts[:\s]*(\d+)", all_text, re.IGNORECASE)
        if starts_match:
            return self._extract_first_number(starts_match.group(1))

        return None

    def _extract_page_content(self, response: Response) -> str:
        """Extract description content from the offer page."""
        return "".join(response.css("main, article").extract()).strip()

    def _extract_location(self, response: Response) -> str | None:
        """Extract location from the offer page."""
        location_container = response.css(".reg_path").xpath("./parent::*")
        if location_container:
            location_text = " ".join(
                location_container[0].css("::text").extract()
            ).strip()
            # Clean up extra spaces and translate
            location_text = re.sub(r"\s+", " ", location_text)
            location_text = location_text.replace("Europa", "Europe")
            location_text = location_text.replace("Schweiz", "Switzerland")
            # Remove spaces around commas
            location_text = re.sub(r"\s*,\s*", ", ", location_text)
            if location_text:
                return location_text
        return None

    def _parse_detail_page(self, response: Response) -> Generator[OfferPageItem, None]:
        self._logger.debug("Parsing offer page %s", response.url)
        try:
            offer = OfferPageItem(
                url=response.url,
                category=response.meta["aircraft_category"],
                title=self._extract_title(response),
                published_at=self._extract_published_at(response),
                page_content=self._extract_page_content(response),
            )
            offer.raw_price = self._extract_price(response)
            offer.location = self._extract_location(response)
            offer.hours = self._extract_hours(response)
            offer.starts = self._extract_starts(response)

            yield offer

        except Exception as e:
            self._logger.error(
                "Could not parse detail page %s because %s", response.url, e
            )
