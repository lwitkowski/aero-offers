import os
from datetime import date

from azure.cosmos import (
    ContainerProxy,
    IndexingMode,
    PartitionKey,
    ThroughputProperties,
)
from scrapy.http import HtmlResponse, Request

from aerooffers.db import lazy_database
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
    page_content: str = "<some html content>",
) -> OfferPageItem:
    return OfferPageItem(
        url=url,
        category=AircraftCategory.glider,
        title=title,
        published_at=published_at,
        page_content=page_content,
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


def create_offers_container_if_not_exists() -> ContainerProxy:
    return lazy_database().create_container_if_not_exists(
        id="offers",
        partition_key=PartitionKey(path="/id"),
        offer_throughput=ThroughputProperties(offer_throughput="600"),
        indexing_policy=dict(
            automatic=True,
            indexingMode=IndexingMode.Consistent,
            includedPaths=[
                dict(path="/published_at/?"),
                dict(path="/url/?"),
                dict(path="/classified/?"),
            ],
            excludedPaths=[dict(path="/*")],
            compositeIndexes=[
                [
                    dict(path="/category", order="ascending"),
                    dict(path="/published_at", order="descending"),
                ],
                [
                    dict(path="/manufacturer", order="ascending"),
                    dict(path="/model", order="ascending"),
                    dict(path="/published_at", order="descending"),
                ],
            ],
        ),
    )


def create_page_content_container_if_not_exists() -> ContainerProxy:
    return lazy_database().create_container_if_not_exists(
        id="offer_page_content",
        partition_key=PartitionKey(path="/id"),
        offer_throughput=ThroughputProperties(
            offer_throughput="400"
        ),  # both containers should use less than 100 to stay under free tier limit
        indexing_policy=dict(
            automatic=True,
            indexingMode=IndexingMode.Consistent,
            includedPaths=[],
            excludedPaths=[dict(path="/*")],
        ),
    )
