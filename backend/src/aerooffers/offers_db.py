from datetime import datetime, UTC
from typing import Any

from azure.cosmos.exceptions import CosmosResourceNotFoundError

from aerooffers.db import offers_container
from aerooffers.my_logging import logging
from aerooffers.offer import (
    AircraftCategory,
    Offer,
    OfferPageItem,
    OfferPrice,
    UnclassifiedOffer,
    url_to_id,
)

logger = logging.getLogger("offers_db")


def store_offer(offer: OfferPageItem, spider: str) -> str:
    offer_id = url_to_id(offer.url)

    # Store offer WITHOUT page_content
    offers_container().upsert_item(
        dict(
            id=offer_id,
            spider=spider,
            category=offer.category.name,
            url=offer.url,
            title=offer.title,
            published_at=offer.published_at.isoformat(),
            indexed_at=datetime.now(UTC).isoformat(),
            price=dict(
                amount=offer.price,
                currency=offer.currency,
                amount_in_euro=offer.price_in_euro,
                exchange_rate=offer.exchange_rate,
            ),
            location=offer.location,
            hours=offer.hours,
            starts=offer.starts,
            classified=False,
            manufacturer=None,
            model=None,
        )
    )

    return offer_id


def classify_offer(
    offer_id: str,
    classifier_name: str,
    manufacturer: str | None = None,
    model: str | None = None,
) -> None:
    operations: list[dict[str, Any]] = [
        dict(op="replace", path="/classified", value=True),
        dict(op="replace", path="/manufacturer", value=manufacturer),
        dict(op="replace", path="/model", value=model),
        dict(op="add", path="/classifier_name", value=classifier_name),
    ]

    offers_container().patch_item(
        partition_key=offer_id, item=offer_id, patch_operations=operations
    )


def unclassify_offer(offer_id: str) -> None:
    """Set classified flag to false for an offer."""
    operations: list[dict[str, Any]] = [
        dict(op="replace", path="/classified", value=False),
    ]

    offers_container().patch_item(
        partition_key=offer_id, item=offer_id, patch_operations=operations
    )


def offer_url_exists(url: str) -> bool:
    """
    Check if an offer with the given URL exists using a fast point read.
    Uses a deterministic ID derived from the URL for optimal performance.
    """
    try:
        offer_id = url_to_id(url)
        offers_container().read_item(item=offer_id, partition_key=offer_id)
        return True
    except CosmosResourceNotFoundError:
        return False
    except Exception as e:
        logger.error("database error, assuming we don't have this offer yet", e)
        return False


def get_offers(
    offset: int = 0,
    limit: int = 30,
    category: AircraftCategory | None = None,
    manufacturer: str | None = None,
    model: str | None = None,
) -> list[Offer]:
    query = "SELECT * FROM offers o "
    params: list[dict[str, object]] = []

    where = list()
    if category is not None:
        where.append("o.category = @category")
        params.append(dict(name="@category", value=category.name))
    else:
        where.append("o.category != null")

    if manufacturer is not None:
        where.append("o.manufacturer = @manufacturer")
        params.append(dict(name="@manufacturer", value=manufacturer))

    if model is not None:
        where.append("o.model = @model")
        params.append(dict(name="@model", value=model))

    if len(where) > 0:
        query += "WHERE " + " AND ".join(where) + " "

    query += "ORDER BY o.published_at DESC "

    query += "OFFSET @offset LIMIT @limit"
    params.append(dict(name="@offset", value=offset))
    params.append(dict(name="@limit", value=limit))

    db_offers = offers_container().query_items(
        query=query, parameters=params, enable_cross_partition_query=True
    )
    return list(
        map(
            lambda db_offer: Offer(
                url=db_offer["url"],
                category=db_offer["category"],
                title=db_offer["title"],
                published_at=db_offer["published_at"],
                price=OfferPrice(
                    amount=db_offer["price"]["amount"],
                    currency=db_offer["price"]["currency"],
                    amount_in_euro=db_offer["price"]["amount_in_euro"],
                    exchange_rate=db_offer["price"]["exchange_rate"],
                ),
                hours=db_offer["hours"],
                starts=db_offer["starts"],
                location=db_offer["location"],
                manufacturer=db_offer["manufacturer"],
                model=db_offer["model"],
                spider=db_offer.get("spider"),
            ),
            db_offers,
        )
    )


def get_unclassified_offers(limit: int = 100) -> list[UnclassifiedOffer]:
    query = (
        "SELECT o.id, o.title, o.category FROM offers o "
        "WHERE o.classified = false "
        "AND IS_DEFINED(o.category) "
        "AND o.category != null "
        "AND o.category != 'undefined' "
        "ORDER BY o.id ASC "
        "OFFSET 0 LIMIT @limit"
    )
    params = [dict(name="@limit", value=limit)]
    result_set = offers_container().query_items(
        query=query, parameters=params, enable_cross_partition_query=True
    )

    def _to_category(raw: object) -> AircraftCategory:
        if not isinstance(raw, str) or not raw:
            return AircraftCategory.unknown
        try:
            return AircraftCategory[raw]
        except (KeyError, ValueError):
            try:
                return AircraftCategory(raw)
            except (KeyError, ValueError):
                return AircraftCategory.unknown

    return [
        UnclassifiedOffer(
            id=result["id"],
            title=result["title"],
            category=_to_category(result.get("category")),
        )
        for result in result_set
    ]


if __name__ == "__main__":
    from aerooffers.utils import load_env

    load_env()

    print("First 30 gliders from DB: ", get_offers(category=AircraftCategory.glider))
    print("First 100 unclassified offers: ", get_unclassified_offers())
