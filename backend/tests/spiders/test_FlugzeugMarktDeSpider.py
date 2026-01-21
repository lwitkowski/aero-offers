import datetime

from assertpy import assert_that
from util import fake_response_from_file

from aerooffers.offer import AircraftCategory, OfferPageItem
from aerooffers.spiders.FlugzeugMarktDeSpider import FlugzeugMarktDeSpider

spider = FlugzeugMarktDeSpider()


def test_collect_urls_of_all_offer_on_listing_page() -> None:
    # given
    listing_page_http_response = fake_response_from_file(
        "spiders/samples/flugzeugmarkt_de_listing.html"
    )

    # when
    listing_page_parse_result = spider.parse(listing_page_http_response)

    # then
    detail_pages = [i for i in listing_page_parse_result]
    assert_that(detail_pages).is_length(20)

    assert_that(detail_pages[0].url).is_equal_to(
        "https://www.flugzeugmarkt.de/segelflugzeuge/alexander-schleicher/ask-21/kaufen-3771.html",
    )
    assert_that(detail_pages[3].url).is_equal_to(
        "https://www.flugzeugmarkt.de/segelflugzeuge/schempp-hirth/ventus-b/kaufen-3730.html",
    )


def test_parse_detail_page() -> None:
    # given
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file("spiders/samples/flugzeugmarkt_de_offer.html")
        )
    )

    # then
    assert_that(item.title).is_equal_to("Schempp-Hirth Ventus b")
    assert_that(item.published_at).is_equal_to(datetime.date(2025, 12, 2))
    assert_that(item.raw_price).is_equal_to("33.000 €")
    assert_that(item.hours).is_equal_to(32767)
    assert_that(item.starts).is_equal_to(1182)
    assert_that(item.location).is_equal_to("Verviers")
    assert_that(item.page_content).contains("For sale: Ventus B")
    assert_that(item.category).is_equal_to(AircraftCategory.glider)
