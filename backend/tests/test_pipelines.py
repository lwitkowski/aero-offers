# -*- coding: UTF-8 -*-

import unittest

from scrapy.exceptions import DropItem
from ddt import ddt, data

import pipelines
import offers_db
from offer import OfferPageItem, AircraftCategory
from util import sample_offer


class DuplicateDetectionTest(unittest.TestCase):

    def setUp(self):
        offers_db.truncate_all_tables()
        self.detection = pipelines.DuplicateDetection()

    def test_new_offer_is_not_duplicate(self):
        # given offer in DB with different url
        offers_db.store_offer(sample_offer(url="https://offers.com/2"))

        # when & then
        try:
            self.detection.process_item(sample_offer(url="https://offers.com/1"), None)
        except DropItem:
            self.fail("DuplicateDetection unexpectedly dropped new item!")

    def test_existing_offer_is_duplicate(self):
        # given offer in DB with same url
        offers_db.store_offer(sample_offer())

        # when & then
        self.assertRaises(DropItem, self.detection.process_item, sample_offer(), None)

@ddt
class PriceParserTest(unittest.TestCase):
    def setUp(self):
        self.detection = pipelines.PriceParser()

    @data(
        (sample_offer(raw_price="2,01 Euro €"), "2.01"),
        (sample_offer(raw_price="1.234,00 Euro €"), "1234.00"),
        (sample_offer(raw_price="123.456,00 Euro €"), "123456.00"),
    )
    def test_parse_valid_prices(self, test_input):
        offer_with_valid_price: OfferPageItem = test_input[0]
        expected_price: str = test_input[1]

        try:
            self.detection.process_item(offer_with_valid_price, None)
        except DropItem:
            self.fail("PriceParser unexpectedly dropped offer with valid price!")

        self.assertEqual(expected_price, offer_with_valid_price.price)
        self.assertEqual("EUR", offer_with_valid_price.currency)

    @data(
        sample_offer(raw_price=""),
        sample_offer(raw_price="Ask for price")
    )
    def test_should_drop_if_price_is_missing(self, offer_with_invalid_price: OfferPageItem):
        self.assertRaises(DropItem, self.detection.process_item, offer_with_invalid_price, None)

    @data(
        sample_offer(raw_price="0 Euro €"),
        sample_offer(raw_price="0,89  Euro €"),  # smaller than 1
        sample_offer(raw_price="500.001,00 Euro €"),  # huge amount
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
        offer = sample_offer()
        offer.title = offer_title
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        self.assertRaises(DropItem, offer_filter.process_item, offer, None)

    @data(
        "Arcus M Charter in Bitterwasser ab dem 11.01.20",
        "Ventus cM Charter",
        "DuoDiscus-Turbo in Top Zustand zu verchartern mit Vorsaisonpreis !",
        "ASG29E with 15m and 18m wingtips for rent",
    )
    def test_charter_offers_are_dropped(self, offer_title):
        offer = sample_offer()
        offer.title = offer_title
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        self.assertRaises(DropItem, offer_filter.process_item, offer, None)

    @data(
        "DG101 G - Competition ready",
        "Biete tolles Flugzeug"
    )
    def test_regular_offers_are_not_dropped(self, offer_title):
        offer = sample_offer()
        offer.title = offer_title
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        offer_filter.process_item(offer, None)

@ddt
class StoragePipelineTest(unittest.TestCase):

    def setUp(self):
        offers_db.truncate_all_tables()
        self.storage = pipelines.StoragePipeline()

    def test_should_store_offer(self):
        # given
        sample_raw_offer = sample_offer(
            price="123456.00",
            currency="EUR",
            location="Moon",
            hours=1000,
            starts=300
        )

        # when
        self.storage.process_item(sample_raw_offer, None)

        # then
        all_gliders_in_db = offers_db.get_offers(category=AircraftCategory.glider)
        assert len(all_gliders_in_db) == 1
        assert all_gliders_in_db[0].title == "Glider A"
        assert all_gliders_in_db[0].category == 'glider'
        assert all_gliders_in_db[0].url == "https://offers.com/1"


if __name__ == '__main__':
    unittest.main()