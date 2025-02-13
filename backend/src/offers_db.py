# -*- coding: UTF-8 -*-
import uuid

from azure.cosmos import PartitionKey, ThroughputProperties

from db import database
from fx_db import convert_prices
from my_logging import *
from offer import OfferPageItem, AircraftCategory

logger = logging.getLogger('offers_db')


container = database.create_container_if_not_exists(
    id="offers",
    partition_key=PartitionKey(path="/id"),
    offer_throughput=ThroughputProperties(offer_throughput="600")
)


def truncate_all_tables():
    database.create_container_if_not_exists(id="offers", partition_key=PartitionKey(path="/id"))
    database.delete_container(container="offers")
    database.create_container_if_not_exists(id="offers", partition_key=PartitionKey(path="/id"))


def store_offer(
        offer: OfferPageItem,
        spider: str = 'unknown',
):
    id = str(uuid.uuid4())
    container.upsert_item(dict(
        id=id,
        spider=spider,
        category=offer.category.name,
        url=offer.url,
        title=offer.title,
        published_at=str(offer.published_at),
        price=dict(
            amount=offer.price,
            currency=offer.currency
        ),
        location=offer.location,
        hours=offer.hours,
        starts=offer.starts,
        page_content=offer.page_content,

        classified=False,
        manufacturer=None,
        model=None,
    ))
    return id


def classify_offer(
    offer_id: str,
    category: str,
    manufacturer: str = None,
    model: str = None,
):
    container.patch_item(
        partition_key=offer_id,
        item=offer_id,
        patch_operations=[
            dict(op="replace", path="/classified", value=True),
            dict(op="replace", path="/category", value=category),
            dict(op="replace", path="/manufacturer", value=manufacturer),
            dict(op="replace", path="/model", value=model)
        ]
    )


def offer_url_exists(url):
    try:
        offer = container.query_items(
            query='SELECT o.id FROM offers o WHERE o.url = @url OFFSET 0 LIMIT 1',
            parameters=[dict(name='@url', value=url)],
            enable_cross_partition_query=True
        )
        return next(offer, None) is not None
    except Exception as e:
        logger.error("database error, assuming we don't have this offer already")
        logger.error(e)
        return False


def get_offers(offset: int = 0, limit: int = 30, category: AircraftCategory = None, manufacturer: str = None, model: str =None):
    query = 'SELECT * FROM offers o '
    params = list()

    where = list()
    if category is not None:
        where.append('o.category = @category')
        params.append(dict(name='@category', value=category.name))
    else:
        where.append('o.category != null')

    if manufacturer is not None:
        where.append('o.manufacturer = @manufacturer')
        params.append(dict(name='@manufacturer', value=manufacturer))

    if model is not None:
        where.append('o.model = @model')
        params.append(dict(name='@model', value=model))

    if len(where) > 0:
        query += 'WHERE ' + ' AND '.join(where) + ' '

    query += 'ORDER BY o.date DESC '

    query += 'OFFSET @offset LIMIT @limit'
    params.append(dict(name='@offset', value=offset))
    params.append(dict(name='@limit', value=limit))

    db_offers = container.query_items(query=query, parameters=params, enable_cross_partition_query=True)
    ui_offers = list()
    for db_offer in db_offers:
        ui_offers.append({
            "id": db_offer['id'],
            "url": db_offer['url'],
            "category": db_offer['category'],
            "title": db_offer['title'],
            "published_at": db_offer['published_at'],
            "price": {
                "amount": db_offer['price']['amount'],
                "currency": db_offer['price']['currency'],
            },
            "hours": db_offer['hours'],
            "starts": db_offer['starts'],
            "location": db_offer['location'],
            "manufacturer": db_offer['manufacturer'],
            "model": db_offer['model']
        })

    return convert_prices(ui_offers)


def get_unclassified_offers():
    query = 'SELECT * FROM offers o WHERE o.classified = false OFFSET 0 LIMIT 100'
    return list(container.query_items(query=query, enable_cross_partition_query=True))


if __name__ == '__main__':
    print("All gliders from DB: ", get_offers(category=AircraftCategory.glider))
    print("Unclassified offers: ", get_unclassified_offers())
