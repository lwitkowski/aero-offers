# -*- coding: UTF-8 -*-

import requests
import fx_db
import time
import defusedxml.ElementTree as ET
from price_parser import Price
from my_logging import *

logger = logging.getLogger('exchange_rates')
ECB_FX_RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

# ISO 4217
iso_code_mapping = {
    '€': 'EUR',
    '$': 'USD',
    'US$': 'USD',
    '£': 'GBP',
    'Fr.': 'CHF',
    'A$': 'AUD',
}


def fetch_exchange_rates_from_ecb():
    start_time = time.time()
    response = requests.get(ECB_FX_RATES_URL).text
    count = update_exchange_rates(response)
    fx_db.reload_fx()
    logger.info("Updated %d exchange rates in %.2fs", count, (time.time() - start_time))


def update_exchange_rates(xml_data):
    count = 0
    et = ET.fromstring(xml_data)
    for element in et.iter():
        curr_name = element.get('currency')
        if curr_name is None:
            continue
        curr_rate = float(element.get('rate'))
        fx_db.update_exchange_rate(currency=curr_name, rate=curr_rate)
        count += 1
    return count


def to_price_in_euro(price: str, currency: str):
    if currency and currency != "EUR":
        price_in_euro = str(round(float(price) / fx_db.exchange_rates[currency], 2))
        exchange_rate = fx_db.exchange_rates[currency]
    else:
        price_in_euro = price
        exchange_rate = 1.0
    return price_in_euro, exchange_rate


def get_currency_code(symbol):
    currency_str = symbol
    if isinstance(symbol, Price):
        currency_str = symbol.currency

    if currency_str in iso_code_mapping:
        return iso_code_mapping[currency_str]
    else:
        logging.error("Couldn't find currency code for currency symbol: {0}".format(str(symbol.currency)))
        return currency_str
