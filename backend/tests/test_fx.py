import unittest
from price_parser import Price

import fx
import fx_db
from util import read_file


class ExchangeRatesTest(unittest.TestCase):

    def test_get_currency_code(self):
        self.assertEqual("EUR", fx.get_currency_code(Price.fromstring("12.000,00 €")))
        self.assertEqual("GBP", fx.get_currency_code(Price.fromstring("16,23 £")))
        self.assertEqual("CHF", fx.get_currency_code(Price.fromstring("12 SFr.")))
        self.assertEqual("AUD", fx.get_currency_code(Price.fromstring("12 A$")))

    def test_should_update_fx_rates_in_db(self):
        # when
        fx.update_exchange_rates(read_file("eurofxref-daily.xml"))
        fx_db.reload_fx()

        # then
        fx_rates = fx_db.exchange_rates
        self.assertEqual(4.3250, fx_rates["PLN"])
