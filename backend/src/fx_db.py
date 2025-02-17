# -*- coding: UTF-8 -*-
from azure.cosmos import PartitionKey, ThroughputProperties

from db import database
from my_logging import *

container = database.create_container_if_not_exists(
    id="fx_rates",
    partition_key=PartitionKey(path="/id"),
    offer_throughput=ThroughputProperties(offer_throughput="400")
)

exchange_rates = dict()


def reload_fx():
    for rate in container.read_all_items():
        exchange_rates[rate['currency']] = float(rate['rate'])


reload_fx()


def update_exchange_rate(currency: str, rate: float):
    container.upsert_item({
        "id": currency,
        "currency": currency,
        "rate": rate
    })


if __name__ == '__main__':
    logging.info("All rates from DB: {0}".format(exchange_rates))