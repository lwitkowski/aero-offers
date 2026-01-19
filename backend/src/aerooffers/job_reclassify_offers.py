from aerooffers.classifier import classifier
from aerooffers.my_logging import logging
from aerooffers.offers_db import classify_offer, get_unclassified_offers

logger = logging.getLogger("reclassify_job")
model_classifier = classifier.ModelClassifier()


def _reclassify(db_offers: list[dict]) -> None:
    for db_offer in db_offers:
        (category, manufacturer, model) = model_classifier.classify(db_offer["title"])
        logger.debug(
            "Classified '%s' as '%s' '%s'", db_offer["title"], manufacturer, model
        )

        classify_offer(
            offer_id=db_offer["id"],
            category=category,
            manufacturer=manufacturer,
            model=model,
        )


def reclassify_all() -> int:
    offers_processed = 0
    offset = 0
    limit = 100
    while True:
        offers = get_unclassified_offers(offset=offset, limit=limit)
        _reclassify(offers)

        offers_processed += len(offers)

        if len(offers) < limit:
            break
        else:
            offset += limit

    return offers_processed


if __name__ == "__main__":
    processed = reclassify_all()
    logger.info(f"Finished classifying {processed} offers")
