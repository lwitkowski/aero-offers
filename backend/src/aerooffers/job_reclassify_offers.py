from aerooffers.classifier import classifier
from aerooffers.my_logging import logging
from aerooffers.offers_db import classify_offer, get_unclassified_offers
from aerooffers.spiders.SegelflugDeSpider import SegelflugDeSpider

logger = logging.getLogger("reclassify_job")
aircraft_type_classifier = classifier.AircraftTypeClassifier()
model_classifier = classifier.ModelClassifier()


def reclassify(db_offer: dict) -> None:
    expect_manufacturer = db_offer["spider"] != SegelflugDeSpider.name
    (manufacturer, model, category) = model_classifier.classify(
        db_offer["title"], expect_manufacturer, db_offer["page_content"]
    )
    if manufacturer:
        logger.debug(
            "Classified '%s' as '%s' '%s'", db_offer["title"], manufacturer, model
        )
        classify_offer(
            offer_id=db_offer["id"],
            category=category,
            manufacturer=manufacturer,
            model=model,
        )
    else:
        aircraft_type = aircraft_type_classifier.classify(
            db_offer["title"], db_offer["spider"]
        )
        logger.debug("Classified '%s' as '%s'", db_offer["title"], aircraft_type)
        classify_offer(
            offer_id=db_offer["id"],
            category=aircraft_type,
            manufacturer=None,
            model=None,
        )


def reclassify_all() -> int:
    offers_processed = 0
    offset = 0
    limit = 100
    while True:
        offers = get_unclassified_offers(offset=offset, limit=limit)
        for offer in offers:
            reclassify(offer)

        offers_processed += len(offers)

        if len(offers) < limit:
            break
        else:
            offset += limit

    return offers_processed


if __name__ == "__main__":
    processed = reclassify_all()
    logger.info(f"Finished classifying {processed} offers")
