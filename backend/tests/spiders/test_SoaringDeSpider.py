import unittest

from offer import OfferPageItem
from spiders import SoaringDeSpider
from datetime import date
from util import fake_response_from_file


class SoaringDeSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = SoaringDeSpider.SoaringDeSpider()

    def test_parse_detail_page(self):
        item: OfferPageItem = next(self.spider.parse_detail_page(
            fake_response_from_file('spiders/samples/segelflug_de_offer.html')))
        self.assertIsNotNone(item)
        self.assertEqual(date(2023, 11, 11), item.published_at)
        self.assertIsNotNone(item.title)
        self.assertEqual("25.000,00 Euro €                  ", item.raw_price)
        self.assertIsNotNone(item.url)
        self.assertIsNotNone(item.location)
        self.assertEqual(2522, item.hours)
        self.assertEqual(662, item.starts)
        self.assertIsNotNone(item.page_content)

    def test_parse_detail_page_with_html_tags(self):
        item: OfferPageItem = next(self.spider.parse_detail_page(
            fake_response_from_file('spiders/samples/segelflug_de_offer_different_details.html')))
        self.assertIsNotNone(item.page_content)
        self.assertTrue("Because of organisational changes at BBAero" in item.page_content)

    def test_parse_detail_page_for_tmg(self):
        item: OfferPageItem = next(self.spider.parse_detail_page(
            fake_response_from_file('spiders/samples/segelflug_de_offer_tmg.html')))
        self.assertEqual("Dimona H36", item.title)
        self.assertEqual(2880, item.hours)
        self.assertEqual(5672, item.starts)
        self.assertEqual("22.000,00 Euro €\n                            ", item.raw_price)

    def test_parse_detail_page_for_ls3(self):
        item: OfferPageItem = next(self.spider.parse_detail_page(
            fake_response_from_file('spiders/samples/segelflug_de_offer_ls3.html')))
        self.assertTrue("LS 3" in item.title)
