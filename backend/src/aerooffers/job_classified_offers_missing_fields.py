from aerooffers.my_logging import logging
from aerooffers.offers_db import get_classified_offers_missing_fields, unclassify_offer

logger = logging.getLogger("classified_offers_missing_fields_job")


def unclassify_offers_missing_fields(count: int) -> int:
    """
    Unclassify offers that are classified but missing manufacturer or model.
    Only unclassifies offers without classifier_name stored in the database.
    Sets classified flag to false for these offers so they can be classified again.

    Returns:
        int: Number of offers unclassified
    """
    offers = get_classified_offers_missing_fields(offset=0, limit=count)

    if len(offers) == 0:
        logger.info("No classified offers missing manufacturer or model found")
        return 0

    logger.info(f"Unclassifying {len(offers)} offers missing manufacturer or model...")

    unclassified_count = 0
    for offer in offers:
        offer_id = offer["id"]
        try:
            unclassify_offer(offer_id)
            logger.info(f"Unclassified offer {offer_id} with title '{offer['title']}'")
            unclassified_count += 1
        except Exception as e:
            logger.error(f"Failed to unclassify offer {offer_id}: {e}")

    logger.info(f"Successfully unclassified {unclassified_count} offers")
    return unclassified_count


if __name__ == "__main__":
    from aerooffers.utils import load_env

    load_env()

    unclassify_offers_missing_fields(100)
