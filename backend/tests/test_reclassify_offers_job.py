from assertpy import assert_that
from azure.cosmos import CosmosClient
from util import sample_offer

from aerooffers import offers_db
from aerooffers.job_reclassify_offers import reclassify_all
from aerooffers.offer import AircraftCategory


def test_reclassify_only_unclassified_offers(cosmos_db: CosmosClient) -> None:
    # given
    classified_offer_id = offers_db.store_offer(
        sample_offer(url="https://offers.com/1")
    )
    offers_db.classify_offer(
        offer_id=classified_offer_id,
        category=AircraftCategory.glider,
        manufacturer="PZL Bielsko",
        model="Bocian",
    )
    second_classified_offer_id = offers_db.store_offer(
        sample_offer(url="https://offers.com/2")
    )
    offers_db.classify_offer(
        offer_id=second_classified_offer_id,
        category=AircraftCategory.glider,
        manufacturer="PZL Bielsko",
        model="Bocian",
    )
    offers_db.store_offer(sample_offer(url="https://offers.com/3"))

    # when
    offers_processed = reclassify_all()

    # then
    assert_that(offers_processed).is_equal_to(1)
    assert_that(len(offers_db.get_unclassified_offers())).is_equal_to(0)


def test_should_persist_manufacturer_and_model_if_classified(
    cosmos_db: CosmosClient,
) -> None:
    # given
    offers_db.store_offer(sample_offer(title="LS-1"))

    # when
    reclassify_all()

    # then
    ls1_offer = offers_db.get_offers()[0]
    assert_that(ls1_offer).is_not_none()
    assert_that(ls1_offer.category).is_equal_to(AircraftCategory.glider)
    assert_that(ls1_offer.manufacturer).is_equal_to("Rolladen Schneider")
    assert_that(ls1_offer.model).is_equal_to("LS1")
