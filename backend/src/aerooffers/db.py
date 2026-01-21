import os

from azure.cosmos import (
    ContainerProxy,
    CosmosClient,
    DatabaseProxy,
    IndexingMode,
    PartitionKey,
    ThroughputProperties,
)

from aerooffers.my_logging import logging

logger = logging.getLogger("db")
logging.getLogger("azure.cosmos").setLevel(logging.WARNING)


COSMOSDB_DB_NAME = "aerooffers"

_database: DatabaseProxy | None = None


def lazy_database() -> DatabaseProxy:
    global _database
    if _database is not None:
        return _database

    cosmosdb_url = os.getenv("COSMOSDB_URL")
    cosmosdb_credential = os.getenv("COSMOSDB_CREDENTIAL")

    if not cosmosdb_url:
        raise ValueError("COSMOSDB_URL environment variable is required")
    if not cosmosdb_credential:
        raise ValueError("COSMOSDB_CREDENTIAL environment variable is required")

    logger.info(
        f"Connecting to CosmosDB, url={cosmosdb_url}, db_name={COSMOSDB_DB_NAME}"
    )

    client = CosmosClient(url=cosmosdb_url, credential=cosmosdb_credential)
    _database = client.create_database_if_not_exists(COSMOSDB_DB_NAME)

    logger.info("Connection established successfully")
    return _database


_offers_container: ContainerProxy | None = None


def offers_container() -> ContainerProxy:
    global _offers_container
    if _offers_container is not None:
        return _offers_container

    _offers_container = lazy_database().get_container_client(container="offers")
    return _offers_container


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


_page_content_container: ContainerProxy | None = None


def page_content_container() -> ContainerProxy:
    global _page_content_container
    if _page_content_container is not None:
        return _page_content_container

    _page_content_container = lazy_database().get_container_client(
        container="offer_page_content"
    )
    return _page_content_container


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
