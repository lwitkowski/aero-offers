from datetime import date

from assertpy import assert_that
from util import fake_response_from_file

from aerooffers.offer import AircraftCategory, OfferPageItem
from aerooffers.spiders import SoaringDeSpider

spider = SoaringDeSpider.SoaringDeSpider()


def test_collect_urls_of_all_offer_on_listing_page() -> None:
    # given
    listing_page_http_response = fake_response_from_file(
        "spiders/samples/soaring_de_listing.html"
    )

    # when
    listing_page_parse_result = spider.parse(listing_page_http_response)

    # then
    detail_pages = [i for i in listing_page_parse_result]
    assert_that(detail_pages).is_length(107)

    assert_that(detail_pages[0].url).is_equal_to(
        "https://soaring.de/osclass/index.php?page=item&id=86069"
    )
    assert_that(detail_pages[0].meta["aircraft_category"]).is_equal_to(
        AircraftCategory.glider
    )

    # no broken links collected
    assert_that([page.url for page in detail_pages]).does_not_contain(
        "https://soaring.de/osclass/index.php?page=item&id="
    )


def test_parse_detail_page() -> None:
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file("spiders/samples/segelflug_de_offer.html")
        )
    )
    assert_that(item).is_not_none()
    assert_that(item.published_at).is_equal_to(date(2023, 11, 11))
    assert_that(item.title).is_equal_to("Glasflügel KESTREL 17m")
    assert_that(item.raw_price).is_equal_to("25.000,00 Euro €                  ")
    assert_that(item.url).is_equal_to("http://www.example.com")
    assert_that(item.location).is_equal_to("Ingolstadt, Bayern, Germany")
    assert_that(item.hours).is_equal_to(2522)
    assert_that(item.starts).is_equal_to(662)
    assert_that(item.page_content).is_not_none()


def test_parse_detail_page_with_html_tags() -> None:
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file(
                "spiders/samples/segelflug_de_offer_different_details.html"
            )
        )
    )

    assert_that(item.page_content).contains(
        "Because of organisational changes at BBAero"
    )


def test_parse_detail_page_for_tmg() -> None:
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file("spiders/samples/segelflug_de_offer_tmg.html")
        )
    )
    assert_that(item.title).is_equal_to("Dimona H36")
    assert_that(item.hours).is_equal_to(2880)
    assert_that(item.starts).is_equal_to(5672)
    assert_that(item.raw_price).is_equal_to(
        "22.000,00 Euro €\n                            "
    )


def test_parse_detail_page_for_ls3() -> None:
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file("spiders/samples/segelflug_de_offer_ls3.html")
        )
    )
    assert_that(item.title).contains("LS 3")
