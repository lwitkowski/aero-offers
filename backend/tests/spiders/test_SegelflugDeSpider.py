from datetime import date

from assertpy import assert_that
from util import fake_response_from_file

from aerooffers.offer import AircraftCategory, OfferPageItem
from aerooffers.spiders import SegelflugDeSpider

spider = SegelflugDeSpider.SegelflugDeSpider()


def test_collect_urls_of_all_offer_on_listing_page() -> None:
    # given
    listing_page_http_response = fake_response_from_file(
        "spiders/samples/segelflug_de_listing.html",
        url="https://www.segelflug.de/index.php/de/kleinanzeigen/filterseite-de/com-djclassifieds-cat-sailplanes,5",
    )

    # when
    listing_page_parse_result = spider.parse(listing_page_http_response)

    # then
    detail_pages = [i for i in listing_page_parse_result]
    assert_that(detail_pages).is_length(48)

    assert_that(detail_pages[0].url).is_equal_to(
        "https://www.segelflug.de/index.php/de/kleinanzeigen/filterseite-de/ad/com-djclassifieds-cat-sailplanes,5/newfotosls8aneo15mjuniorenwmteamflugzeug2022,753"
    )
    assert_that(detail_pages[0].meta["aircraft_category"]).is_equal_to(
        AircraftCategory.glider
    )


def test_parse_detail_page() -> None:
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file("spiders/samples/segelflug_de_offer.html")
        )
    )
    assert_that(item).is_not_none()
    assert_that(item.published_at).is_equal_to(date(2025, 11, 6))
    assert_that(item.title).is_equal_to("Schöne LS 8-18")
    assert_that(item.raw_price).is_equal_to("79.000 CHF")
    assert_that(item.url).is_equal_to("http://www.example.com")
    assert_that(item.location).is_equal_to("Europe, Switzerland")
    assert_that(item.hours).is_equal_to(2521)
    assert_that(item.starts).is_equal_to(971)
    assert_that(item.page_content).is_not_none()


def test_parse_detail_page_for_tmg() -> None:
    response = fake_response_from_file("spiders/samples/segelflug_de_offer_tmg.html")
    response.meta["aircraft_category"] = AircraftCategory.airplane
    item: OfferPageItem = next(spider._parse_detail_page(response))
    assert_that(item.title).is_equal_to("Wunderschöner G109b")
    assert_that(item.raw_price).is_equal_to("35.000 €")
    assert_that(item.published_at).is_equal_to(date(2026, 1, 16))
    assert_that(item.category).is_equal_to(AircraftCategory.airplane)
    assert_that(item.hours).is_equal_to(6682)
    assert_that(item.starts).is_equal_to(13174)
    assert_that(item.location).is_equal_to("Europe, Deutschland")


def test_parse_detail_page_for_discus() -> None:
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file("spiders/samples/segelflug_de_offer_ls3.html")
        )
    )
    assert_that(item).is_not_none()
    assert_that(item.title).is_equal_to("Discus 2a")
    assert_that(item.raw_price).is_equal_to("95.000 €")
    assert_that(item.published_at).is_equal_to(date(2026, 1, 16))
    assert_that(item.category).is_equal_to(AircraftCategory.glider)
    assert_that(item.location).is_equal_to("Europe, Deutschland")
    assert_that(item.hours).is_none()
    assert_that(item.starts).is_none()
    assert_that(item.page_content).is_not_none()


def test_parse_detail_page_for_cobra() -> None:
    item: OfferPageItem = next(
        spider._parse_detail_page(
            fake_response_from_file("spiders/samples/segelflug_de_offer_cobra.html")
        )
    )
    assert_that(item).is_not_none()
    assert_that(item.title).is_equal_to("SZD-36A Cobra")
    assert_that(item.raw_price).is_equal_to("4.990 €")
    assert_that(item.published_at).is_equal_to(date(2026, 1, 15))
    assert_that(item.category).is_equal_to(AircraftCategory.glider)
    assert_that(item.location).is_equal_to("Europe")
    assert_that(item.hours).is_equal_to(1724)
    assert_that(item.starts).is_equal_to(672)
    assert_that(item.page_content).is_not_none()
