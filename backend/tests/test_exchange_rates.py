import unittest
from price_parser import Price
from exchange_rates import get_currency_code


class ExchangeRatesTest(unittest.TestCase):

    def test_get_currency_code(self):
        self.assertEqual("EUR", get_currency_code(Price.fromstring("12.000,00 €")))
        self.assertEqual("GBP", get_currency_code(Price.fromstring("16,23 £")))
        self.assertEqual("CHF", get_currency_code(Price.fromstring("12 SFr.")))
