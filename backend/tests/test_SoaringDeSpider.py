import unittest

from spiders import SoaringDeSpider
from datetime import date
from tests.util import fake_response_from_file


class SoaringDeSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = SoaringDeSpider.SoaringDeSpider()

    def test_parse_detail_page(self):
        item = next(self.spider.parse_detail_page(
            fake_response_from_file('samples/segelflug_de_offer.html')))
        self.assertIsNotNone(item["date"])
        self.assertTrue(isinstance(item["date"], date))
        self.assertIsNotNone(item["title"])
        self.assertIsNotNone(item["price"])
        self.assertIsNotNone(item["offer_url"])
        self.assertIsNotNone(item["location"])
        self.assertEqual(item["hours"], str(2522))
        self.assertEqual(item["starts"], str(662))
        self.assertIsNotNone(item["detail_text"])

    def test_parse_detail_page_with_html_tags(self):
        item = next(self.spider.parse_detail_page(
            fake_response_from_file('samples/segelflug_de_offer_different_details.html')))
        self.assertIsNotNone(item["detail_text"])
        self.assertTrue("Because of organisational changes at BBAero" in item["detail_text"])

    def test_parse_detail_page_for_tmg(self):
        item = next(self.spider.parse_detail_page(
            fake_response_from_file('samples/segelflug_de_offer_tmg.html')))
        self.assertEqual("Dimona H36", item["title"])
        self.assertEqual("2880", item["hours"])
        self.assertEqual("5672", item["starts"])
        self.assertEqual("22.000,00", item["price"].amount_text)
        self.assertEqual("€", item["price"].currency)

    def test_parse_detail_page_for_ls3(self):
        item = next(self.spider.parse_detail_page(
            fake_response_from_file('samples/segelflug_de_offer_ls3.html')))
        self.assertTrue("LS 3" in item["title"])
