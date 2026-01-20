import pytest
from assertpy import assert_that
from azure.cosmos import CosmosClient
from flask.testing import FlaskClient
from util import sample_offer

from aerooffers import offers_db
from aerooffers.api.flask_app import app
from aerooffers.offer import AircraftCategory


@pytest.fixture
def api_client(cosmos_db: CosmosClient) -> FlaskClient:
    return app.test_client()


def test_get_aircraft_models(api_client: FlaskClient) -> None:
    # when
    response = api_client.get("/api/models")

    # then
    assert_that(response.status_code).is_equal_to(200)
    assert response.json is not None
    assert_that(response.json["PZL Bielsko"]["models"]["glider"][0]).is_equal_to(
        "SZD-9 Bocian"
    )


def test_get_offers_for_all_categories(api_client: FlaskClient) -> None:
    # given
    offers_db.store_offer(sample_offer(price="29500", currency="EUR"))

    # when
    response = api_client.get("/api/offers")

    # then
    assert_that(response.status_code).is_equal_to(200)
    assert response.json is not None
    assert_that(response.json).is_length(1)
    offer = response.json[0]
    assert_that(offer["category"]).is_equal_to("glider")
    assert_that(offer["title"]).is_equal_to("Glider A")
    assert_that(offer["published_at"]).is_equal_to("2024-07-27")
    assert_that(offer["url"]).is_equal_to("https://offers.com/1")
    assert_that(offer["price"]["amount"]).is_equal_to("29500")
    assert_that(offer["price"]["currency"]).is_equal_to("EUR")


def test_get_offers_for_given_category(api_client: FlaskClient) -> None:
    # given
    offers_db.store_offer(sample_offer())

    # when & then
    assert_that(api_client.get("/api/offers?category=glider").json).is_length(1)
    assert_that(api_client.get("/api/offers?category=tmg").json).is_length(0)
    assert_that(api_client.get("/api/offers?category=what").json).is_length(0)


def test_get_offers_for_given_manufacturer_and_model(api_client: FlaskClient) -> None:
    # given
    offer_id = offers_db.store_offer(sample_offer(price="29500", currency="EUR"))
    offers_db.classify_offer(
        offer_id, "Manual", AircraftCategory.glider, "PZL Bielsko", "SZD-9 Bocian"
    )

    # when
    response = api_client.get("/api/offers/PZL Bielsko/SZD-9 Bocian")

    # then
    assert response.json is not None
    assert_that(response.status_code).is_equal_to(200)
    assert_that(response.json["manufacturer_website"]).is_equal_to(
        "https://en.wikipedia.org/wiki/Szybowcowy_Zak%C5%82ad_Do%C5%9Bwiadczalny"
    )
    assert_that(response.json["offers"]).is_length(1)
    offer = response.json["offers"][0]
    assert_that(offer["category"]).is_equal_to("glider")
    assert_that(offer["title"]).is_equal_to("Glider A")
    assert_that(offer["manufacturer"]).is_equal_to("PZL Bielsko")
    assert_that(offer["model"]).is_equal_to("SZD-9 Bocian")
    assert_that(offer["published_at"]).is_equal_to("2024-07-27")


def test_get_offers_even_when_manufacturer_website_is_not_defined(
    api_client: FlaskClient,
) -> None:
    # when
    response = api_client.get("/api/offers/Grob/Astir")

    # then
    assert_that(response.status_code).is_equal_to(200)
    assert response.json is not None
    assert_that(response.json["manufacturer_website"]).is_none()


def test_get_offers_404_for_unknown_manufacturer_or_model(
    api_client: FlaskClient,
) -> None:
    # given
    offers_db.store_offer(sample_offer())

    # when & then
    assert_that(
        api_client.get("/api/offers/Boeing/DoesNotMatter").status_code
    ).is_equal_to(404)
