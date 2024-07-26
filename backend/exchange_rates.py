import requests
import db
import defusedxml.ElementTree as ET
from price_parser import Price
from my_logging import *

logger = logging.getLogger('exchange_rates')
ECB_FX_RATES_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"


def fetch_exchange_rates_from_ecb():
    response = requests.get(ECB_FX_RATES_URL).text
    et = ET.fromstring(response)
    for element in et.iter():
        curr_name = element.get('currency')
        if curr_name is None:
            continue
        curr_rate = element.get('rate')
        logger.debug("Fetched exchange rate: {0} for currency {1}".format(str(curr_rate), str(curr_name)))
        db.update_exchange_rate(db.ExchangeRate(currency=curr_name, rate=curr_rate))


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
        'Fr.': 'CHF'
    }
    if currency_str in iso_code_mapping:
        return iso_code_mapping[currency_str]
    else:
        logging.error("Couldn't find currency code for currency symbol: {0}".format(str(o.currency)))
        return currency_str


if __name__ == '__main__':
    print(get_currency_code(Price.fromstring("12 adsf")))

