import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from db import database
from fx import to_price_in_euro
from my_logging import *

logger = logging.getLogger('data_migration')

postgres_connection = psycopg2.connect(
    database="aircraft_offers", user='aircraft_offers', password='aircraft_offers', host='localhost', port='25432', cursor_factory=RealDictCursor
)


def read_offers_from_postgres(offset: int, limit: int):
    cursor = postgres_connection.cursor()
    cursor.execute(f"SELECT * FROM aircraft_offer ORDER BY id OFFSET {offset} LIMIT {limit}")
    return cursor.fetchall()


cosmosdb_container = database.get_container_client(container="offers")


if __name__ == '__main__':
    # this script migrates and enhances data from postgres database (pre 16.02.2025) to CosmosDb
    offers_processed = 0
    offset = 0
    items_per_batch = 100
    while True:
        postgres_offers = read_offers_from_postgres(offset=offset, limit=items_per_batch)
        for postgres_offer in postgres_offers:
            (price_in_euro, exchange_rate) = to_price_in_euro(str(postgres_offer['price']), postgres_offer['currency_code'])

            cosmos_offer = dict(
                id=str(uuid.uuid4()),
                spider=postgres_offer['spider'],
                category=postgres_offer['aircraft_type'],
                url=postgres_offer['offer_url'],
                title=postgres_offer['title'],
                published_at=str(postgres_offer['date']),
                price=dict(
                    amount=str(postgres_offer['price']),
                    currency=postgres_offer['currency_code'],
                    amount_in_euro=price_in_euro,
                    exchange_rate=exchange_rate,
                ),
                location=postgres_offer['location'],
                hours=int(postgres_offer['hours']) if postgres_offer['hours'] is not None else None,
                starts=int(postgres_offer['starts']) if postgres_offer['starts'] is not None else None,
                page_content=postgres_offer['detail_text'],
                indexed_at=str(postgres_offer['creation_datetime']),
                classified=True,
                manufacturer=postgres_offer['manufacturer'],
                model=postgres_offer['model'],
            )

            #logger.info(str(cosmos_offer))
            cosmosdb_container.upsert_item(cosmos_offer)

        offers_processed += len(postgres_offers)

        if len(postgres_offers) < items_per_batch:
            break
        else:
            offset += items_per_batch
    postgres_connection.close()

    logger.info("Finished migrating {0} offers".format(offers_processed))
