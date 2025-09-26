import unittest
import datetime

from offer import OfferPageItem, AircraftCategory
from util import fake_response_from_file
from spiders import FlugzeugMarktDeSpider


class FlugzeugMarktDeSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = FlugzeugMarktDeSpider.FlugzeugMarktDeSpider()

    def test_collect_urls_of_all_offer_on_listing_page(self):
        # given
        listing_page_http_response = fake_response_from_file(
            "spiders/samples/flugzeugmarkt_de_listing.html"
        )

        # when
        listing_page_parse_result = self.spider.parse(listing_page_http_response)

        # then
        detail_pages = [i for i in listing_page_parse_result]
        self.assertEqual(len(detail_pages), 20)
        self.assertEqual(
            detail_pages[0].url,
            "https://www.flugzeugmarkt.de/ultraleichtflugzeug-kaufen/comco-ikarus/c42b-competition-gebraucht-kaufen/3331.html",
        )

    def test_parse_detail_page(self):
        item: OfferPageItem = next(
            self.spider.parse_detail_page(
                fake_response_from_file("spiders/samples/flugzeugmarkt_de_offer.html")
            )
        )
        self.assertIsNotNone(item.title)
        self.assertEqual(
            item.published_at,
            datetime.datetime.strptime("08.10.2019", "%d.%m.%Y").date(),
        )
        self.assertEqual("250.000 $", item.raw_price)
        self.assertEqual(1492, item.hours)
        self.assertTrue("IFR Approved" in item.page_content)
        self.assertEqual(AircraftCategory.airplane, item.category)
