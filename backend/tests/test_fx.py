import unittest

import fx
from util import read_file


class ExchangeRatesTest(unittest.TestCase):
    def test_get_currency_code(self):
        self.assertEqual("EUR", fx.get_currency_code("€"))
        self.assertEqual("GBP", fx.get_currency_code("£"))
        self.assertEqual("CHF", fx.get_currency_code("Fr."))
        self.assertEqual("AUD", fx.get_currency_code("A$"))

    def test_should_read_fx_rates_from_xml_file(self):
        # when
        fx.update_exchange_rates(read_file("eurofxref-daily.xml"))

        # then
        self.assertEqual(4.3250, fx.exchange_rates["PLN"])
