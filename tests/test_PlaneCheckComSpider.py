import unittest
import datetime

from spiders import PlaneCheckComSpider
from tests.util import fake_response_from_file


class PlaneCheckComSpiderTest(unittest.TestCase):

    def setUp(self):
        self.spider = PlaneCheckComSpider.PlaneCheckComSpider()

    def test_parse_generates_correct_requests(self):
        response = fake_response_from_file('samples/planecheck_com_start_url.html', encoding='iso-8859-1')
        generator = self.spider.parse(response)
        first_offer_request = next(generator) # should not raise StopError
        self.assertTrue("aspdet.asp?nr=48234" in first_offer_request.url)

    def test_parse_detail_page(self):
        item = next(self.spider.parse_detail_page(
            fake_response_from_file('samples/planecheck_com_offer_beech.html', encoding='iso-8859-1')))
        self.assertIsNotNone(item["title"])
        self.assertEqual("Beech 95 Travel Air D95A", item["title"])
        self.assertEqual(item["date"], datetime.datetime.strptime("31.12.2019", "%d.%m.%Y").date())
        self.assertIsNotNone(item["price"])
        self.assertEqual("92,500", item["price"].amount_text)
        self.assertEqual("€", item["price"].currency)
        self.assertTrue(len(item["detail_text"]) > 0)
        self.assertTrue("Switzerland" in item["location"])
        self.assertTrue(len(item["offer_url"]) > 0)

    def test_parse_detail_page_price_vat_included(self):
        item = next(self.spider.parse_detail_page(
            fake_response_from_file('samples/planecheck_com_offer_piper.html', encoding='iso-8859-1')))
        self.assertIsNotNone(item["title"])
        self.assertEqual("Piper PA-34-220T Seneca V", item["title"])
        self.assertEqual(item["price"].currency, "$")
        self.assertEqual(item["price"].amount_text, "743,750")
