import requests
import db
import time
import defusedxml.ElementTree as ET
from price_parser import Price
from my_logging import *

logger = logging.getLogger('exchange_rates')
ECB_FX_RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"


def fetch_exchange_rates_from_ecb():
    start_time = time.time()
    response = requests.get(ECB_FX_RATES_URL).text
    count = update_exchange_rates(response)
    logger.info("Updated %d exchange rates in %.2fs", count, (time.time() - start_time))


def update_exchange_rates(xmlData):
    count = 0
    et = ET.fromstring(xmlData)
    for element in et.iter():
        curr_name = element.get('currency')
        if curr_name is None:
            continue
        curr_rate = element.get('rate')
        db.update_exchange_rate(db.ExchangeRate(currency=curr_name, rate=curr_rate))
        count += 1
    return count


def get_currency_code(o):
    currency_str = o
    if isinstance(o, Price):
        currency_str = o.currency

    # ISO 4217
    iso_code_mapping = {
        '€': 'EUR',
        '$': 'USD',
        'US$': 'USD',
        '£': 'GBP',
        'Fr.': 'CHF',
        'A$': 'AUD',
    }
    if currency_str in iso_code_mapping:
        return iso_code_mapping[currency_str]
    else:
        logging.error("Couldn't find currency code for currency symbol: {0}".format(str(o.currency)))
        return currency_str

