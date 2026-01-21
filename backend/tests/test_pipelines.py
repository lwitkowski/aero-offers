from unittest.mock import MagicMock

import pytest
from assertpy import assert_that
from azure.cosmos import CosmosClient
from scrapy.exceptions import DropItem
from util import sample_offer

from aerooffers import offers_db, pipelines
from aerooffers.offer import AircraftCategory


def test_new_offer_is_not_duplicate(cosmos_db: CosmosClient) -> None:
    # given offer in DB with different url
    offers_db.store_offer(sample_offer(url="https://offers.com/2"), spider="test")

    # when & then
    pipelines.SkipDuplicates().process_item(sample_offer(url="https://offers.com/1"))


def test_existing_offer_is_duplicate(cosmos_db: CosmosClient) -> None:
    # given offer in DB with same url
    offers_db.store_offer(sample_offer(), spider="test")

    # when
    with pytest.raises(DropItem) as e:
        pipelines.SkipDuplicates().process_item(sample_offer())

    # then
    assert_that(str(e.value)).is_equal_to(
        "Offer already exists in DB, title='Glider A' url=https://offers.com/1"
    )


@pytest.mark.parametrize(
    ("raw_valid_price", "expected_price"),
    [
        ("2,01 Euro €", "2.01"),
        ("1.234,00 Euro €", "1234.00"),
        ("123.456,00 Euro €", "123456.00"),
    ],
)
def test_parse_valid_prices(raw_valid_price: str, expected_price: str) -> None:
    # given
    offer_with_valid_price = sample_offer(raw_price=raw_valid_price)

    # when
    pipelines.ParsePrice().process_item(offer_with_valid_price)

    # then
    assert_that(offer_with_valid_price.price).is_equal_to(expected_price)
    assert_that(offer_with_valid_price.currency).is_equal_to("EUR")
    assert_that(offer_with_valid_price.price_in_euro).is_equal_to(expected_price)
    assert_that(offer_with_valid_price.exchange_rate).is_equal_to(1.0)


def test_should_drop_if_price_is_missing() -> None:
    offer_with_invalid_price = sample_offer(raw_price="Ask for price")
    with pytest.raises(DropItem):
        pipelines.ParsePrice().process_item(offer_with_invalid_price)


@pytest.mark.parametrize(
    ("unreasonable_price", "error_msg"),
    [
        ("0 Euro €", "Offer has unreasonable price smaller than 1"),
        ("0,89  Euro €", "Offer has unreasonable price smaller than 1"),
        ("1.500.001,00 Euro €", "Offer has unreasonable price higher than 1_500_000"),
    ],
)
def test_should_drop_if_price_is_unreasonable(
    unreasonable_price: str, error_msg: str
) -> None:
    offer_with_unreasonable_price = sample_offer(raw_price=unreasonable_price)

    with pytest.raises(DropItem) as e:
        pipelines.ParsePrice().process_item(offer_with_unreasonable_price)

    assert_that(str(e.value)).contains(error_msg)


@pytest.mark.parametrize(
    ("offer_title"),
    [
        "Suche Stemme S12",
        "suche Stemme S12",
        "searching for Stemme S12",
        "Looking for Stemme S12",
        "Discus CS - SUCHE",
        "Looking 18m for WGC2026",
    ],
)
def test_search_offers_are_dropped(offer_title: str) -> None:
    offer = sample_offer(title=offer_title)

    with pytest.raises(DropItem) as e:
        pipelines.SkipSearchAndCharterOffers().process_item(offer)

    assert_that(str(e.value)).is_equal_to("Dropping search/charter offer")


@pytest.mark.parametrize(
    ("offer_title"),
    [
        "Arcus M Charter in Bitterwasser ab dem 11.01.20",
        "Ventus cM Charter",
        "DuoDiscus-Turbo in Top Zustand zu verchartern mit Vorsaisonpreis !",
        "ASG29E with 15m and 18m wingtips for rent",
    ],
)
def test_charter_offers_are_dropped(offer_title: str) -> None:
    offer = sample_offer(title=offer_title)

    with pytest.raises(DropItem) as e:
        pipelines.SkipSearchAndCharterOffers().process_item(offer)

    assert_that(str(e.value)).is_equal_to("Dropping search/charter offer")


@pytest.mark.parametrize(
    ("offer_title"),
    ["DG101 G - Competition ready", "Biete tolles Flugzeug"],
)
def test_regular_offers_are_not_dropped(offer_title: str) -> None:
    offer = sample_offer(title=offer_title)

    filtered_item = pipelines.SkipSearchAndCharterOffers().process_item(offer)

    assert_that(filtered_item).is_equal_to(offer)


def test_should_store_offer(cosmos_db: CosmosClient) -> None:
    # given
    sample_raw_offer = sample_offer(
        price="123456.00", currency="EUR", location="Moon", hours=1000, starts=300
    )
    crawler = MagicMock()
    crawler.spider.name = "awesome_spider"

    # when
    pipelines.StoreOffer(crawler).process_item(sample_raw_offer)

    # then
    all_gliders_in_db = offers_db.get_offers(category=AircraftCategory.glider)
    assert_that(all_gliders_in_db).is_length(1)
    assert_that(all_gliders_in_db[0].spider).is_equal_to("awesome_spider")
    assert_that(all_gliders_in_db[0].title).is_equal_to("Glider A")
    assert_that(all_gliders_in_db[0].category).is_equal_to("glider")
    assert_that(all_gliders_in_db[0].url).is_equal_to("https://offers.com/1")
