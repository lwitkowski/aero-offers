"""These scripts are intended to be used only from developer machine for ad-hoc one-time tasks, like data migrations etc."""

from aerooffers.my_logging import logging
from aerooffers.offers_db import get_poorly_classified_offer_ids, unclassify_offer

logger = logging.getLogger("classified_offers_missing_fields_job")


def mark_poorly_classified_offers_for_reprocessing(count: int) -> None:
    """Unclassify offers that were poorly classified in the past by legacy rule-based classifier."""
    offer_ids = get_poorly_classified_offer_ids(offset=0, limit=count)

    if len(offer_ids) == 0:
        logger.info("No classified offers missing manufacturer or model found")
        return

    logger.info(
        f"Unclassifying {len(offer_ids)} offers missing manufacturer or model..."
    )

    for offer_id in offer_ids:
        unclassify_offer(offer_id)
        logger.info(f"Unclassified offer {offer_id}")

    logger.info(f"Successfully unclassified {len(offer_ids)} offers")


if __name__ == "__main__":
    from aerooffers.utils import load_env

    load_env()

    mark_poorly_classified_offers_for_reprocessing(5)
