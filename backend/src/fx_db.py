# -*- coding: UTF-8 -*-
from azure.cosmos import PartitionKey, ThroughputProperties

from db import database
from my_logging import *
from offer import OfferPageItem

container = database.create_container_if_not_exists(
    id="fx_rates",
    partition_key=PartitionKey(path="/id"),
    offer_throughput=ThroughputProperties(offer_throughput="400")
)

exchange_rates = dict()
for rate in container.read_all_items():
    exchange_rates[rate['currency']] = float(rate['rate'])


def update_exchange_rate(currency: str, rate: float):
    container.upsert_item({
        "id": currency,
        "currency": currency,
        "rate": rate
    })


def convert_price(offer: OfferPageItem):
    if offer.currency and offer.currency != "EUR":
        offer.price_in_euro = str(round(float(offer.price) / exchange_rates[offer.currency], 2))
        offer.exchange_rate = exchange_rates[offer.currency]
    else:
        offer.price_in_euro = offer.price
        offer.exchange_rate = 1.0


if __name__ == '__main__':
    logging.info("All rates from DB: {0}".format(exchange_rates))