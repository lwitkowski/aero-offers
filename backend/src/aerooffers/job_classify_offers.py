import os

from aerooffers.classifier.classifiers import AircraftClassifier, ClassificationResult
from aerooffers.my_logging import logging
from aerooffers.offer import UnclassifiedOffer
from aerooffers.offers_db import classify_offer, get_unclassified_offers

logger = logging.getLogger("classify_job")


def _classify(
    unclassified_offers: list[UnclassifiedOffer], model_classifier: AircraftClassifier
) -> None:
    results = model_classifier.classify_many(unclassified_offers)

    # Process results
    for offer in unclassified_offers:
        offer_id = offer.id
        result = results.get(offer_id, ClassificationResult.unknown())

        if result.model is None:
            logger.warning(
                f"No classification result for offer {offer_id} with title '{offer.title}'"
            )
        else:
            logger.info(
                "Offer id %s with title '%s' successfully classified as '%s' '%s'",
                offer_id,
                offer.title,
                result.manufacturer,
                result.model,
            )

        classify_offer(
            offer_id=offer_id,
            classifier_name=model_classifier.name,
            manufacturer=result.manufacturer,
            model=result.model,
        )


def classify_pending(model_classifier: AircraftClassifier) -> int:
    logger.info(f"Using '{model_classifier.name}' classifier")

    offers_processed = 0
    limit = 10
    while True:
        offers = get_unclassified_offers(limit=limit)
        if len(offers) == 0:
            break

        logger.info(f"Loaded {len(offers)} unclassified offers, calling classifier...")

        _classify(unclassified_offers=offers, model_classifier=model_classifier)

        offers_processed += len(offers)

    if offers_processed == 0:
        logger.info("No unclassified offers found in the database")
    else:
        logger.info(f"Finished classifying {offers_processed} offers")

    return offers_processed


if __name__ == "__main__":
    from aerooffers.utils import load_env

    load_env()

    if os.getenv("USE_LLM_CLASSIFIER", "").lower() in ("true", "1", "yes"):
        from aerooffers.classifier.gemini_llm_classifier import GeminiLLMClassifier

        classifier: AircraftClassifier = GeminiLLMClassifier()
    else:
        from aerooffers.classifier.rule_based_classifier import RuleBasedClassifier

        classifier = RuleBasedClassifier()

    classify_pending(classifier)
