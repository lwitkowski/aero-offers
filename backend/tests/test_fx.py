from assertpy import assert_that
from util import read_file

from aerooffers import fx


def test_get_currency_code() -> None:
    assert_that(fx.get_currency_code("€")).is_equal_to("EUR")
    assert_that(fx.get_currency_code("£")).is_equal_to("GBP")
    assert_that(fx.get_currency_code("Fr.")).is_equal_to("CHF")
    assert_that(fx.get_currency_code("A$")).is_equal_to("AUD")


def test_should_read_fx_rates_from_xml_file() -> None:
    # when
    fx.update_exchange_rates(read_file("eurofxref-daily.xml"))

    # then
    assert_that(fx.exchange_rates["PLN"]).is_equal_to(4.3250)
