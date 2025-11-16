import unittest

import pytest
from assertpy import assert_that
from azure.cosmos import CosmosClient
from ddt import data, ddt
from scrapy.exceptions import DropItem
from util import sample_offer

from aerooffers import offers_db, pipelines
from aerooffers.offer import AircraftCategory, OfferPageItem


def test_new_offer_is_not_duplicate(cosmos_db: CosmosClient) -> None:
    # given offer in DB with different url
    offers_db.store_offer(sample_offer(url="https://offers.com/2"))

    # when & then
    pipelines.DuplicateDetection().process_item(
        sample_offer(url="https://offers.com/1")
    )


def test_existing_offer_is_duplicate(cosmos_db: CosmosClient) -> None:
    # given offer in DB with same url
    offers_db.store_offer(sample_offer())

    # when
    with pytest.raises(DropItem) as e:
        pipelines.DuplicateDetection().process_item(sample_offer())

    # then
    assert_that(str(e.value)).is_equal_to(
        "Offer already exists in DB, url=https://offers.com/1"
    )


@ddt
class PriceParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.detection = pipelines.PriceParser()

    @data(
        (sample_offer(raw_price="2,01 Euro €"), "2.01"),
        (sample_offer(raw_price="1.234,00 Euro €"), "1234.00"),
        (sample_offer(raw_price="123.456,00 Euro €"), "123456.00"),
    )
    def test_parse_valid_prices(self, test_input: tuple[OfferPageItem, str]) -> None:
        offer_with_valid_price: OfferPageItem = test_input[0]
        expected_price: str = test_input[1]

        try:
            self.detection.process_item(offer_with_valid_price)
        except DropItem:
            self.fail("PriceParser unexpectedly dropped offer with valid price!")

        self.assertEqual(expected_price, offer_with_valid_price.price)
        self.assertEqual("EUR", offer_with_valid_price.currency)
        self.assertEqual(expected_price, offer_with_valid_price.price_in_euro)
        self.assertEqual(1.0, offer_with_valid_price.exchange_rate)

    @data(sample_offer(raw_price=""), sample_offer(raw_price="Ask for price"))
    def test_should_drop_if_price_is_missing(
        self, offer_with_invalid_price: OfferPageItem
    ) -> None:
        self.assertRaises(
            DropItem, self.detection.process_item, offer_with_invalid_price
        )

    @data(
        sample_offer(raw_price="0 Euro €"),
        sample_offer(raw_price="0,89  Euro €"),  # smaller than 1
        sample_offer(raw_price="500.001,00 Euro €"),  # huge amount
    )
    def test_should_drop_if_price_is_unreasonable(
        self, offer_with_unreasonable_price: OfferPageItem
    ) -> None:
        self.assertRaises(
            DropItem, self.detection.process_item, offer_with_unreasonable_price
        )


@ddt
class FilterSearchAndCharterOffersTest(unittest.TestCase):
    @data("Suche Stemme S12", "Looking for Stemme S12", "Discus CS - SUCHE")
    def test_search_offers_are_dropped(self, offer_title: str) -> None:
        offer = sample_offer()
        offer.title = offer_title
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        self.assertRaises(DropItem, offer_filter.process_item, offer)

    @data(
        "Arcus M Charter in Bitterwasser ab dem 11.01.20",
        "Ventus cM Charter",
        "DuoDiscus-Turbo in Top Zustand zu verchartern mit Vorsaisonpreis !",
        "ASG29E with 15m and 18m wingtips for rent",
    )
    def test_charter_offers_are_dropped(self, offer_title: str) -> None:
        offer = sample_offer()
        offer.title = offer_title
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        self.assertRaises(DropItem, offer_filter.process_item, offer)

    @data("DG101 G - Competition ready", "Biete tolles Flugzeug")
    def test_regular_offers_are_not_dropped(self, offer_title: str) -> None:
        offer = sample_offer()
        offer.title = offer_title
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        offer_filter.process_item(offer)


def test_should_store_offer(cosmos_db: CosmosClient) -> None:
    # given
    sample_raw_offer = sample_offer(
        price="123456.00", currency="EUR", location="Moon", hours=1000, starts=300
    )

    # when
    pipelines.StoragePipeline().process_item(sample_raw_offer)

    # then
    all_gliders_in_db = offers_db.get_offers(category=AircraftCategory.glider)
    assert_that(all_gliders_in_db).is_length(1)
    assert_that(all_gliders_in_db[0].title).is_equal_to("Glider A")
    assert_that(all_gliders_in_db[0].category).is_equal_to("glider")
    assert_that(all_gliders_in_db[0].url).is_equal_to("https://offers.com/1")
