from datetime import date

from assertpy import assert_that
from azure.cosmos import CosmosClient
from util import sample_offer

from aerooffers import offers_db
from aerooffers.offer import AircraftCategory, Offer


def test_should_store_and_fetch_offer(cosmos_db: CosmosClient) -> None:
    # given
    offers_db.store_offer(sample_offer(price="29500", currency="EUR"))

    # when
    all_offers = offers_db.get_offers()

    # then
    assert_that(all_offers).is_length(1)
    glider_offer = all_offers[0]
    assert_that(glider_offer.title).is_equal_to("Glider A")
    assert_that(glider_offer.price.amount).is_equal_to("29500")
    assert_that(glider_offer.price.currency).is_equal_to("EUR")


def test_should_filter_offers_by_aircraft_type(cosmos_db: CosmosClient) -> None:
    # given
    offers_db.store_offer(sample_offer())

    # when
    gliders_only = offers_db.get_offers(category=AircraftCategory.glider)
    airplanes_only = offers_db.get_offers(category=AircraftCategory.airplane)

    # then
    assert_that(gliders_only).is_length(1)
    assert_that(airplanes_only).is_empty()


def test_should_filter_offers_by_manufacturer_and_model(
    cosmos_db: CosmosClient,
) -> None:
    # given
    stored_offer_id = offers_db.store_offer(sample_offer())
    offers_db.classify_offer(
        offer_id=stored_offer_id,
        classifier_name="Manual",
        category=AircraftCategory.glider,
        manufacturer="Schempp-Hirth",
        model="Mini-Nimbus",
    )

    # when
    mini_nimbuses = offers_db.get_offers(
        manufacturer="Schempp-Hirth", model="Mini-Nimbus"
    )
    asg29s = offers_db.get_offers(manufacturer="Alexander Schleicher", model="ASG 29 E")

    # then
    assert_that(mini_nimbuses).is_length(1)
    assert_that(asg29s).is_empty()


def test_should_not_reset_category_if_none(cosmos_db: CosmosClient) -> None:
    # given
    stored_offer_id = offers_db.store_offer(sample_offer())
    offers_db.classify_offer(
        offer_id=stored_offer_id,
        classifier_name="Manual",
        category=AircraftCategory.glider,
        manufacturer="Schempp-Hirth",
        model="Mini-Nimbus",
    )

    # when
    offers_db.classify_offer(
        offer_id=stored_offer_id,
        classifier_name="Manual",
        category=None,
        manufacturer=None,
        model=None,
    )

    # then
    offer_from_db: Offer = offers_db.get_offers()[0]
    assert_that(offer_from_db.category).is_equal_to("glider")


def test_should_order_offers_by_published_date_desc(cosmos_db: CosmosClient) -> None:
    # given
    offers_db.store_offer(sample_offer(published_at=date(2024, 1, 2)))
    offers_db.store_offer(sample_offer(published_at=date(2024, 2, 1)))
    offers_db.store_offer(sample_offer(published_at=date(2023, 3, 15)))
    offers_db.store_offer(sample_offer(published_at=date(2024, 1, 31)))

    # when
    orders = offers_db.get_offers()

    # then
    assert_that(orders[0].published_at).is_equal_to("2024-02-01")
    assert_that(orders[1].published_at).is_equal_to("2024-01-31")
    assert_that(orders[2].published_at).is_equal_to("2024-01-02")
    assert_that(orders[3].published_at).is_equal_to("2023-03-15")


def test_should_check_url_exists(cosmos_db: CosmosClient) -> None:
    # given offer exists in db
    offers_db.store_offer(sample_offer(url="https://offers.com/1"))

    # when
    url_exists = offers_db.offer_url_exists("https://offers.com/1")

    # then
    assert_that(url_exists).is_true()
    assert_that(offers_db.offer_url_exists("https://offers.com/2")).is_false()
