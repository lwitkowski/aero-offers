"""These scripts are intended to be used only from developer machine for ad-hoc one-time tasks, like data migrations etc."""

from aerooffers.my_logging import logging
from aerooffers.offers_db import get_poorly_classified_offers, unclassify_offer

logger = logging.getLogger("classified_offers_missing_fields_job")


def mark_poorly_classified_offers_for_reprocessing(count: int) -> None:
    """Unclassify offers that were poorly classified in the past by legacy rule-based classifier."""
    offers = get_poorly_classified_offers(offset=0, limit=count)

    if len(offers) == 0:
        logger.info("No classified offers missing manufacturer or model found")
        return

    logger.info(f"Unclassifying {len(offers)} offers missing manufacturer or model...")

    for offer in offers:
        offer_id = offer["id"]
        unclassify_offer(offer_id)
        logger.info(
            f"Unclassified offer {offer_id} with title '{offer['title']}', published at {offer['published_at']}"
        )

    logger.info(f"Successfully unclassified {len(offers)} offers")


if __name__ == "__main__":
    from aerooffers.utils import load_env

    load_env()

    mark_poorly_classified_offers_for_reprocessing(100)
