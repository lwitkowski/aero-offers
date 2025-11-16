import os
from datetime import date

from scrapy.http import HtmlResponse, Request

from aerooffers.offer import AircraftCategory, OfferPageItem


def sample_offer(
    url: str = "https://offers.com/1",
    title: str = "Glider A",
    published_at: date = date(2024, 7, 27),
    raw_price: str | None = None,
    price: str = "29500",
    currency: str = "EUR",
    location: str | None = None,
    hours: int | None = None,
    starts: int | None = None,
) -> OfferPageItem:
    return OfferPageItem(
        url=url,
        category=AircraftCategory.glider,
        title=title,
        published_at=published_at,
        page_content="does not matter",
        raw_price=raw_price,
        price=price,
        currency=currency,
        location=location,
        hours=hours,
        starts=starts,
    )


def read_file(name: str, encoding: str = "utf8") -> str:
    if name[0] != "/":
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, name)
    else:
        file_path = os.path.join(os.path.dirname(__file__), name)

    with open(file_path, encoding=encoding) as file_handle:
        file_content = file_handle.read()
        return file_content


def fake_response_from_file(
    file_name: str, url: str = "http://www.example.com", encoding: str = "utf8"
) -> HtmlResponse:
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    :param encoding:
    :param encoding:
    """

    request = Request(url=url, encoding=encoding)
    file_content = read_file(name=file_name, encoding=encoding)

    response = HtmlResponse(
        url=url, request=request, encoding=encoding, body=file_content
    )
    response.meta["aircraft_category"] = AircraftCategory.glider
    return response
