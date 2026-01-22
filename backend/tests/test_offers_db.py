from datetime import date
from unittest.mock import patch

from assertpy import assert_that
from azure.cosmos import CosmosClient
from util import sample_offer

from aerooffers import db, offers_db
from aerooffers.offer import AircraftCategory, Offer


def test_should_store_and_fetch_offer(cosmos_db: CosmosClient) -> None:
    # given
    offers_db.store_offer(sample_offer(price="29500", currency="EUR"), spider="test")

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
    offers_db.store_offer(sample_offer(), spider="test")

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
    stored_offer_id = offers_db.store_offer(sample_offer(), spider="test")
    offers_db.classify_offer(
        offer_id=stored_offer_id,
        classifier_name="Manual",
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
    stored_offer_id = offers_db.store_offer(sample_offer(), spider="test")
    offers_db.classify_offer(
        offer_id=stored_offer_id,
        classifier_name="Manual",
        manufacturer="Schempp-Hirth",
        model="Mini-Nimbus",
    )

    # when
    offers_db.classify_offer(
        offer_id=stored_offer_id,
        classifier_name="Manual",
        manufacturer=None,
        model=None,
    )

    # then
    offer_from_db: Offer = offers_db.get_offers()[0]
    assert_that(offer_from_db.category).is_equal_to("glider")


def test_should_order_offers_by_published_date_desc(cosmos_db: CosmosClient) -> None:
    # given
    offers_db.store_offer(
        sample_offer(url="https://offers.com/1", published_at=date(2024, 1, 2)),
        spider="test",
    )
    offers_db.store_offer(
        sample_offer(url="https://offers.com/2", published_at=date(2024, 2, 1)),
        spider="test",
    )
    offers_db.store_offer(
        sample_offer(url="https://offers.com/3", published_at=date(2023, 3, 15)),
        spider="test",
    )
    offers_db.store_offer(
        sample_offer(url="https://offers.com/4", published_at=date(2024, 1, 31)),
        spider="test",
    )

    # when
    orders = offers_db.get_offers()

    # then
    assert_that(orders[0].published_at).is_equal_to("2024-02-01")
    assert_that(orders[1].published_at).is_equal_to("2024-01-31")
    assert_that(orders[2].published_at).is_equal_to("2024-01-02")
    assert_that(orders[3].published_at).is_equal_to("2023-03-15")


def test_should_check_url_exists(cosmos_db: CosmosClient) -> None:
    # given offer exists in db
    offers_db.store_offer(sample_offer(url="https://offers.com/1"), spider="test")

    # when
    url_exists = offers_db.offer_url_exists("https://offers.com/1")

    # then
    assert_that(url_exists).is_true()
    assert_that(offers_db.offer_url_exists("https://offers.com/2")).is_false()


def test_should_not_store_page_content_in_offers_container(
    cosmos_db: CosmosClient,
) -> None:
    # given
    test_page_content = "<html><body>Test page content</body></html>"
    offer = sample_offer(page_content=test_page_content)

    # when
    offer_id = offers_db.store_offer(offer, spider="test")

    # then - page_content should NOT be in offers container
    offer_doc = db.offers_container().read_item(item=offer_id, partition_key=offer_id)
    assert_that(offer_doc).does_not_contain_key("page_content")


def test_should_store_page_content_in_separate_container(
    cosmos_db: CosmosClient,
) -> None:
    # given
    test_page_content = (
        "<html><body>Test page content for separate container</body></html>"
    )
    offer = sample_offer(page_content=test_page_content)

    # when
    with patch("aerooffers.offers_db.store_page_content") as mock_store:
        offer_id = offers_db.store_offer(offer, spider="test")

    # then
    mock_store.assert_called_once_with(offer_id, test_page_content, offer.url)


def test_should_store_offer_with_page_content_in_both_containers(
    cosmos_db: CosmosClient,
) -> None:
    # given
    test_page_content = "<html><body>Complete test content</body></html>"
    offer = sample_offer(
        url="https://test.com/offer",
        title="Test Offer",
        page_content=test_page_content,
    )

    # when
    with patch("aerooffers.offers_db.store_page_content") as mock_store:
        offer_id = offers_db.store_offer(offer, spider="test")

    # then - offer should be in offers container without page_content
    offer_doc = db.offers_container().read_item(item=offer_id, partition_key=offer_id)
    assert_that(offer_doc["id"]).is_equal_to(offer_id)
    assert_that(offer_doc["title"]).is_equal_to("Test Offer")
    assert_that(offer_doc["url"]).is_equal_to("https://test.com/offer")
    assert_that(offer_doc).does_not_contain_key("page_content")

    # and - page_content should be stored via blob storage
    mock_store.assert_called_once_with(offer_id, test_page_content, offer.url)
