"""These scripts are intended to be used only from developer machine for ad-hoc one-time tasks, like data migrations etc."""

from aerooffers.db import offers_container
from aerooffers.my_logging import logging
from aerooffers.offers_db import unclassify_offer

logger = logging.getLogger("classified_offers_missing_fields_job")


def _get_poorly_classified_offer_ids(offset: int = 0, limit: int = 100) -> list[str]:
    """Returns offers from db for which legacy rule-based classifier failed to classify correctly."""
    query = (
        "SELECT o.id FROM offers o "
        "WHERE o.classified = true "
        "AND o.category in ('glider', 'tmg') "
        "AND (o.manufacturer = null OR o.model = null) "
        "AND NOT IS_DEFINED(o.classifier_name) "
        "ORDER BY o._ts DESC "
        "OFFSET @offset LIMIT @limit"
    )
    params = [dict(name="@offset", value=offset), dict(name="@limit", value=limit)]
    result_set = offers_container().query_items(
        query=query, parameters=params, enable_cross_partition_query=True
    )
    return [result["id"] for result in result_set]


def _mark_poorly_classified_offers_for_reprocessing(count: int) -> None:
    """Unclassify offers that were poorly classified in the past by legacy rule-based classifier."""
    offer_ids = _get_poorly_classified_offer_ids(offset=0, limit=count)

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

    _mark_poorly_classified_offers_for_reprocessing(250)
