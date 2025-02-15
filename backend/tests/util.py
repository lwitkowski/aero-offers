import os
from datetime import date

from scrapy.http import HtmlResponse, Request
from offer import OfferPageItem, AircraftCategory


def sample_offer():
    return OfferPageItem(
        url="https://offers.com/1",
        category=AircraftCategory.glider,
        title="Glider A",
        published_at=date(2024, 7, 27),
        page_content="does not matter",
    )


def offer_with_url(url):
    offer = sample_offer()
    offer.url = url
    return offer


def offer_with_raw_price(raw_price):
    offer = sample_offer()
    offer.raw_price = raw_price
    return offer


def read_file(name: str, encoding='utf8'):
    if not name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, name)
    else:
        file_path = os.path.join(os.path.dirname(__file__), name)

    file_handle = open(file_path, 'r', encoding=encoding)
    file_content = file_handle.read()
    file_handle.close()
    return file_content


def fake_response_from_file(file_name, url=None, encoding='utf8'):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    :param encoding:
    :param encoding:
    """
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url, encoding=encoding)
    file_content = read_file(name=file_name, encoding=encoding)

    response = HtmlResponse(url=url,
                            request=request,
                            encoding=encoding,
                            body=file_content)
    response.meta["aircraft_category"] = AircraftCategory.glider
    return response
