import unittest

from price_parser import Price
from scrapy.exceptions import DropItem
from ddt import ddt, data

import tests.test__testcontainers_setup
import pipelines
import db

@ddt
class DuplicateDetectionTest(unittest.TestCase):

    def setUp(self):
        db.truncate_offers()

        self.sample_offer = buildOfferWithUrl("https://offers.com/1")
        self.detection = pipelines.DuplicateDetection()

    def test_new_offer_is_not_duplicate(self):
        # given offer in DB with different url
        db.store_offer(buildOfferWithUrl("https://offers.com/2"))

        # when & then
        try:
            self.detection.process_item({"offer_url": "https://offers.com/1"}, None)
        except DropItem:
            self.fail("DuplicateDetection unexpectedly dropped new item!")

    def test_existing_offer_is_duplicate(self):
        # given offer in DB with same url
        db.store_offer(self.sample_offer)

        # when & then
        self.assertRaises(DropItem, self.detection.process_item, {"offer_url": "https://offers.com/1"}, None)

@ddt
class FilterUnreasonablePricesTest(unittest.TestCase):
    def setUp(self):
        self.sample_offer = buildOfferWithUrl("https://offers.com/1")
        self.detection = pipelines.FilterUnreasonablePrices()

    @data(
        {"raw_price": "2,01 Euro €", "offer_url": "https://offers.com/1"},
        {"raw_price": "1.234,00 Euro €", "offer_url": "https://offers.com/2"},
        {"raw_price": "123.456,00 Euro €", "offer_url": "https://offers.com/3"},
    )
    def test_should_allow_valid_prices(self, offer_with_valid_price):
        try:
            self.detection.process_item(offer_with_valid_price, None)
        except DropItem:
            self.fail("FilterUnreasonablePrices unexpectedly dropped offer with valid price!")

    @data(
        {"raw_price": None, "offer_url": "https://offers.com/1"},
         {"raw_price": "Ask for price", "offer_url": "https://offers.com/2"}
    )
    def test_should_drop_if_price_is_missing(self, offer_with_invalid_price):
        self.assertRaises(DropItem, self.detection.process_item, offer_with_invalid_price, None)

    @data(
        {"raw_price": "0 Euro €", "offer_url": "https://offers.com/1"},
        {"raw_price": "0,89  Euro €", "offer_url": "https://offers.com/2"},  # smaller than 1
        {"raw_price": "500.001,00 Euro €", "offer_url": "https://offers.com/3"},  # huge amount
    )
    def test_should_drop_if_price_is_unreasonable(self, offer_with_unreasonable_price):
        self.assertRaises(DropItem, self.detection.process_item, offer_with_unreasonable_price, None)

@ddt
class FilterSearchAndCharterOffersTest(unittest.TestCase):

    @data(
        "Suche Stemme S12",
        "Looking for Stemme S12",
        "Discus CS - SUCHE"
    )
    def test_search_offers_are_dropped(self, offer_title):
        offer = {"title": offer_title, "offer_url": "https://offers.com/1"}
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        self.assertRaises(DropItem, offer_filter.process_item, offer, None)

    @data(
        "Arcus M Charter in Bitterwasser ab dem 11.01.20",
        "Ventus cM Charter",
        "DuoDiscus-Turbo in Top Zustand zu verchartern mit Vorsaisonpreis !",
        "ASG29E with 15m and 18m wingtips for rent",
    )
    def test_charter_offers_are_dropped(self, offer_title):
        offer = {"title": offer_title, "offer_url": "https://offers.com/1"}
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        self.assertRaises(DropItem, offer_filter.process_item, offer, None)

    @data(
        "DG101 G - Competition ready",
        "Biete tolles Flugzeug"
    )
    def test_regular_offers_are_not_dropped(self, offer_title):
        offer = {"title": offer_title}
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        offer_filter.process_item(offer, None)


@ddt
class StoragePipelineTest(unittest.TestCase):

    def setUp(self):
        db.truncate_offers()
        self.storage = pipelines.StoragePipeline()

    def test_should_store_offer(self):
        # given
        sample_raw_offer = {
            "title": "Glider A",
            "price": Price.fromstring("123.456,00 Euro €"),
            "offer_url": "https://offers.com/1",
            "location": "Moon",
            "date": "2024-07-27",
            "hours": 1000,
            "starts": 300,
            "detail_text": "does not matter that much here",
            "aircraft_type": "glider",
         }
        # when
        self.storage.process_item(sample_raw_offer, None)

        # then
        all_gliders_in_db = db.get_offers_dict(aircraft_type="glider")
        self.assertEqual(len(all_gliders_in_db), 1)
        self.assertEqual(all_gliders_in_db[0]["title"], "Glider A")
        self.assertTrue(db.offer_url_exists("https://offers.com/1"))

def buildOfferWithUrl(url):
    return db.AircraftOffer(
        title="Glider A",
        creation_datetime="2024-07-30 18:45:42.571 +0200",
        date="2024-07-27",
        price=29500.00,
        currency="€",
        currency_code="EUR",
        offer_url=url,
        spider="segelflug_de_kleinanzeigen",
        detail_text="does not matter to much",
        aircraft_type="glider"
    )

if __name__ == '__main__':
    unittest.main()