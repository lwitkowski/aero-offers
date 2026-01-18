from aerooffers.classifier import classifier
from aerooffers.my_logging import logging
from aerooffers.offers_db import classify_offer, get_unclassified_offers

logger = logging.getLogger("reclassify_job")
model_classifier = classifier.ModelClassifier()


def reclassify(db_offer: dict) -> None:
    (manufacturer, model, category) = model_classifier.classify(
        db_offer["title"], spider=db_offer["spider"]
    )
    logger.debug("Classified '%s' as '%s' '%s'", db_offer["title"], manufacturer, model)

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
