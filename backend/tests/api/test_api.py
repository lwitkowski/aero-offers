# -*- coding: UTF-8 -*-

import pytest

from api.flask_app import app
import offers_db
from util import sample_offer


@pytest.fixture
def api_client():
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setUp():
    offers_db.truncate_all_tables()


def test_get_aircraft_models(api_client):
    # when
    response = api_client.get("/api/models")

    # then
    assert response.status_code == 200
    assert response.json["PZL Bielsko"]["models"]["glider"][0] == "SZD-9 Bocian"


def test_get_offers_for_all_categories(api_client):
    # given
    offers_db.store_offer(sample_offer(price="29500", currency="EUR"))

    # when
    response = api_client.get("/api/offers")

    # then
    assert response.status_code == 200
    assert len(response.json) == 1
    offer = response.json[0]
    assert offer["category"] == "glider"
    assert offer["title"] == "Glider A"
    assert offer["published_at"] == "2024-07-27"
    assert offer["url"] == "https://offers.com/1"
    assert offer["price"]["amount"] == "29500"
    assert offer["price"]["currency"] == "EUR"


def test_get_offers_for_given_category(api_client):
    # given
    offers_db.store_offer(sample_offer())

    # when & then
    assert len(api_client.get("/api/offers?category=glider").json) == 1
    assert len(api_client.get("/api/offers?category=tmg").json) == 0
    assert len(api_client.get("/api/offers?category=what").json) == 0


def test_get_offers_for_given_manufacturer_and_model(api_client):
    # given
    offer_id = offers_db.store_offer(sample_offer(price="29500", currency="EUR"))
    offers_db.classify_offer(offer_id, "glider", "PZL Bielsko", "SZD-9 Bocian")

    # when
    response = api_client.get("/api/offers/PZL Bielsko/SZD-9 Bocian")

    # then
    assert response.status_code == 200
    assert (
        response.json["manufacturer_website"]
        == "https://en.wikipedia.org/wiki/Szybowcowy_Zak%C5%82ad_Do%C5%9Bwiadczalny"
    )
    assert len(response.json["offers"]) == 1
    offer = response.json["offers"][0]
    assert offer["category"] == "glider"
    assert offer["title"] == "Glider A"
    assert offer["manufacturer"] == "PZL Bielsko"
    assert offer["model"] == "SZD-9 Bocian"
    assert offer["published_at"] == "2024-07-27"


def test_get_offers_even_when_manufacturer_website_is_not_defined(api_client):
    # when
    response = api_client.get("/api/offers/Grob/Astir")

    # then
    assert response.status_code == 200
    assert response.json["manufacturer_website"] is None


def test_get_offers_404_for_unknown_manufacturer_or_model(api_client):
    # given
    offers_db.store_offer(sample_offer())

    # when & then
    assert api_client.get("/api/offers/Boeing/DoesNotMatter").status_code == 404


if __name__ == "__main__":
    pytest.main()
