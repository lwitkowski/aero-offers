import unittest
import datetime

from offer import OfferPageItem, AircraftCategory
from tests.util import fake_response_from_file
from spiders import FlugzeugMarktDeSpider


class FlugzeugMarktDeSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = FlugzeugMarktDeSpider.FlugzeugMarktDeSpider()

    def test_parse_detail_page(self):
        item: OfferPageItem = next(self.spider.parse_detail_page(
            fake_response_from_file('samples/flugzeugmarkt_de_offer.html')))
        self.assertIsNotNone(item.title)
        self.assertEqual(item.published_at, datetime.datetime.strptime("08.10.2019", "%d.%m.%Y").date())
        self.assertEqual("250.000 $", item.raw_price)
        self.assertEqual(1492, item.hours)
        self.assertTrue("IFR Approved" in item.page_content)
        self.assertEqual(AircraftCategory.airplane, item.category)
