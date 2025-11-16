# noqa: N999

import unittest
from datetime import date

from util import fake_response_from_file

from aerooffers.offer import AircraftCategory, OfferPageItem
from aerooffers.spiders import SoaringDeSpider


class SoaringDeSpiderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.spider = SoaringDeSpider.SoaringDeSpider()

    def test_collect_urls_of_all_offer_on_listing_page(self) -> None:
        # given
        listing_page_http_response = fake_response_from_file(
            "spiders/samples/soaring_de_listing.html"
        )

        # when
        listing_page_parse_result = self.spider.parse(listing_page_http_response)

        # then
        detail_pages = [i for i in listing_page_parse_result]
        self.assertEqual(len(detail_pages), 107)

        self.assertEqual(
            detail_pages[0].url,
            "https://soaring.de/osclass/index.php?page=item&id=86069",
        )
        self.assertEqual(
            detail_pages[0].meta["aircraft_category"], AircraftCategory.glider
        )

        # no broken links collected
        self.assertNotIn(
            "https://soaring.de/osclass/index.php?page=item&id=",
            [page.url for page in detail_pages],
        )

    def test_parse_detail_page(self) -> None:
        item: OfferPageItem = next(
            self.spider._parse_detail_page(
                fake_response_from_file("spiders/samples/segelflug_de_offer.html")
            )
        )
        self.assertIsNotNone(item)
        self.assertEqual(date(2023, 11, 11), item.published_at)
        self.assertIsNotNone(item.title)
        self.assertEqual("25.000,00 Euro €                  ", item.raw_price)
        self.assertIsNotNone(item.url)
        self.assertIsNotNone(item.location)
        self.assertEqual(2522, item.hours)
        self.assertEqual(662, item.starts)
        self.assertIsNotNone(item.page_content)

    def test_parse_detail_page_with_html_tags(self) -> None:
        item: OfferPageItem = next(
            self.spider._parse_detail_page(
                fake_response_from_file(
                    "spiders/samples/segelflug_de_offer_different_details.html"
                )
            )
        )
        self.assertIsNotNone(item.page_content)
        self.assertTrue(
            "Because of organisational changes at BBAero" in item.page_content
        )

    def test_parse_detail_page_for_tmg(self) -> None:
        item: OfferPageItem = next(
            self.spider._parse_detail_page(
                fake_response_from_file("spiders/samples/segelflug_de_offer_tmg.html")
            )
        )
        self.assertEqual("Dimona H36", item.title)
        self.assertEqual(2880, item.hours)
        self.assertEqual(5672, item.starts)
        self.assertEqual(
            "22.000,00 Euro €\n                            ", item.raw_price
        )

    def test_parse_detail_page_for_ls3(self) -> None:
        item: OfferPageItem = next(
            self.spider._parse_detail_page(
                fake_response_from_file("spiders/samples/segelflug_de_offer_ls3.html")
            )
        )
        self.assertTrue("LS 3" in item.title)
