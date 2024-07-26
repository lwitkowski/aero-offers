import unittest
import datetime
from tests.util import fake_response_from_file
from spiders import FlugzeugMarktDeSpider


class FlugzeugMarktDeSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = FlugzeugMarktDeSpider.FlugzeugMarktDeSpider()

    def test_parse_detail_page(self):
        item = next(self.spider.parse_detail_page(
            fake_response_from_file('samples/flugzeugmarkt_de_offer.html')))
        self.assertIsNotNone(item["title"])
        self.assertEqual(item["date"], datetime.datetime.strptime("08.10.2019", "%d.%m.%Y").date())
        self.assertIsNotNone(item["price"])
        self.assertEqual(1492, item["hours"])
        self.assertTrue("IFR Approved" in item["detail_text"])
        self.assertEqual("airplane", item["aircraft_type"])
