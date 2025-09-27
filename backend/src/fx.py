# -*- coding: UTF-8 -*-

# This module is used only when offers are updated, so fx rates are no longer stored in database - they are loaded from
# ECB when needed

import time

import requests
from defusedxml import ElementTree
from price_parser import Price

from my_logging import logging

logger = logging.getLogger("fx")
ECB_FX_RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

# ISO 4217
iso_code_mapping = {
    "€": "EUR",
    "$": "USD",
    "US$": "USD",
    "£": "GBP",
    "Fr.": "CHF",
    "A$": "AUD",
}

exchange_rates = dict()


def update_exchange_rates(xml_data):
    exchange_rates.clear()
    count = 0
    et = ElementTree.fromstring(xml_data)
    for element in et.iter():
        curr_name = element.get("currency")
        if curr_name is None:
            continue
        curr_rate = float(element.get("rate"))
        exchange_rates[curr_name] = curr_rate
        count += 1
    return count


def fetch_exchange_rates_from_ecb():
    start_time = time.time()
    xml_response = requests.get(ECB_FX_RATES_URL).text
    count = update_exchange_rates(xml_response)

    logger.info("Fetched %d exchange rates in %.2fs", count, (time.time() - start_time))


fetch_exchange_rates_from_ecb()


def to_price_in_euro(price: Price):
    offer_currency = get_currency_code(price.currency)
    if offer_currency and offer_currency != "EUR":
        price_in_euro = str(
            round(float(str(price.amount)) / exchange_rates[offer_currency], 2)
        )
        exchange_rate = exchange_rates[offer_currency]
    else:
        price_in_euro = str(price.amount)
        exchange_rate = 1.0
    return str(price.amount), offer_currency, price_in_euro, exchange_rate


def get_currency_code(currency_str):
    if currency_str in iso_code_mapping:
        return iso_code_mapping[currency_str]
    else:
        logging.error(
            "Couldn't find currency code for currency symbol: {0}".format(currency_str)
        )
        return currency_str


if __name__ == "__main__":
    logging.info("All rates from DB: {0}".format(exchange_rates))
