import uuid
from datetime import datetime, UTC
from typing import Any

from aerooffers.db import offers_container
from aerooffers.my_logging import logging
from aerooffers.offer import AircraftCategory, Offer, OfferPageItem, OfferPrice

logger = logging.getLogger("offers_db")


def store_offer(
    offer: OfferPageItem,
    spider: str = "unknown",
) -> str:
    offer_id = str(uuid.uuid4())
    offers_container().upsert_item(
        dict(
            id=offer_id,
            spider=spider,
            category=offer.category.name,
            url=offer.url,
            title=offer.title,
            published_at=str(offer.published_at),
            indexed_at=str(datetime.now(UTC)),
            price=dict(
                amount=offer.price,
                currency=offer.currency,
                amount_in_euro=offer.price_in_euro,
                exchange_rate=offer.exchange_rate,
            ),
            location=offer.location,
            hours=offer.hours,
            starts=offer.starts,
            page_content=offer.page_content,
            classified=False,
            manufacturer=None,
            model=None,
        )
    )
    return offer_id


def classify_offer(
    offer_id: str,
    category: AircraftCategory | None = None,
    manufacturer: str | None = None,
    model: str | None = None,
) -> None:
    operations: list[dict[str, Any]] = [
        dict(op="replace", path="/classified", value=True),
        dict(op="replace", path="/manufacturer", value=manufacturer),
        dict(op="replace", path="/model", value=model),
    ]

    if category is not None:
        operations.append(
            dict[str, Any](op="replace", path="/category", value=str(category))
        )

    offers_container().patch_item(
        partition_key=offer_id, item=offer_id, patch_operations=operations
    )


def offer_url_exists(url: str) -> bool:
    try:
        offer = offers_container().query_items(
            query="SELECT o.id FROM offers o WHERE o.url = @url OFFSET 0 LIMIT 1",
            parameters=[dict(name="@url", value=url)],
            enable_cross_partition_query=True,
        )
        return next(offer, None) is not None
    except Exception as e:
        logger.error("database error, assuming we don't have this offer already")
        logger.error(e)
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
            ),
            db_offers,
        )
    )


def get_unclassified_offers(offset: int = 0, limit: int = 100) -> list[Any]:
    query = (
        "SELECT * FROM offers o WHERE o.classified = false OFFSET @offset LIMIT @limit"
    )
    params = [dict(name="@offset", value=offset), dict(name="@limit", value=limit)]
    return list(
        offers_container().query_items(
            query=query, parameters=params, enable_cross_partition_query=True
        )
    )


if __name__ == "__main__":
    print("All gliders from DB: ", get_offers(category=AircraftCategory.glider))
    print("Unclassified offers: ", get_unclassified_offers())
