import unittest
from ddt import ddt
from price_parser import Price
from decimal import Decimal

import tests.test__testcontainers_setup
import db
import exchange_rates

@ddt
class ExchangeRatesTest(unittest.TestCase):

    def test_get_currency_code(self):
        self.assertEqual("EUR", exchange_rates.get_currency_code(Price.fromstring("12.000,00 €")))
        self.assertEqual("GBP", exchange_rates.get_currency_code(Price.fromstring("16,23 £")))
        self.assertEqual("CHF", exchange_rates.get_currency_code(Price.fromstring("12 SFr.")))
        self.assertEqual("AUD", exchange_rates.get_currency_code(Price.fromstring("12 A$")))

    def test_should_update_fx_rates_in_db(self):
        # given
        PRECISION = Decimal(10) ** -4

        # when
        exchange_rates.update_exchange_rates(readFile("tests/eurofxref-daily.xml"))

        # then
        fxRates = db.get_exchange_rates_as_dict(db.Session())
        self.assertEqual(fxRates["PLN"].quantize(PRECISION), Decimal(4.3250).quantize(PRECISION))


def readFile(name: str):
    with open(name, 'r') as file:
        return file.read()
