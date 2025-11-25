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
        "https://www.flugzeugmarkt.de/ultraleichtflugzeug-kaufen/comco-ikarus/c42b-competition-gebraucht-kaufen/3331.html",
    )


def test_parse_detail_page() -> None:
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file("spiders/samples/flugzeugmarkt_de_offer.html")
        )
    )
    assert_that(item.title).is_equal_to("Cessna TU206G")
    assert_that(item.published_at).is_equal_to(datetime.date(2019, 10, 8))
    assert_that(item.raw_price).is_equal_to("250.000 $")
    assert_that(item.hours).is_equal_to(1492)
    assert_that(item.page_content).contains("IFR Approved")
    assert_that(item.category).is_equal_to(AircraftCategory.airplane)
