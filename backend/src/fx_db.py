# -*- coding: UTF-8 -*-
from azure.cosmos import PartitionKey, ThroughputProperties

from db import database
from my_logging import *

container = database.create_container_if_not_exists(
    id="fx_rates",
    partition_key=PartitionKey(path="/id"),
    offer_throughput=ThroughputProperties(offer_throughput="400")
)

def update_exchange_rate(currency: str, rate: str):
    container.upsert_item({
        "id": currency,
        "currency": currency,
        "rate": rate
    })


def get_exchange_rates_as_dict():
    all_exchange_rates = container.read_all_items()
    exchange_rates = dict()
    for rate in all_exchange_rates:
        exchange_rates[rate['currency']] = float(rate['rate'])
    return exchange_rates


def convert_prices(offers):
    exchange_rates = get_exchange_rates_as_dict()
    for offer in offers:
        price = offer["price"]

        if price["currency"] and price["currency"] != "EUR":
            # EZB exchange rates are base=EUR, quote=X
            price["amount_in_euro"] = str(round(float(price["amount"]) / exchange_rates[price["currency"]], 2))
            price["exchange_rate"] = exchange_rates[price["currency"]]
        else:
            price["amount_in_euro"] = price["amount"]
            price["exchange_rate"] = "1.0"
    return offers


if __name__ == '__main__':
    logging.info("All rates from DB: {0}".format(get_exchange_rates_as_dict()))