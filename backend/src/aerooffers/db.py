from azure.cosmos import (
    ContainerProxy,
    CosmosClient,
    DatabaseProxy,
    IndexingMode,
    PartitionKey,
    ThroughputProperties,
)

from aerooffers.my_logging import logging
from aerooffers.settings import COSMOSDB_CREDENTIAL, COSMOSDB_DB_NAME, COSMOSDB_URL

logger = logging.getLogger("db")

logging.getLogger("azure.cosmos").setLevel(logging.WARNING)

_database: DatabaseProxy | None = None


def lazy_database() -> DatabaseProxy:
    global _database
    if _database is not None:
        return _database

    logger.info(
        f"Connecting to CosmosDB, url={COSMOSDB_URL}, db_name={COSMOSDB_DB_NAME}"
    )

    client = CosmosClient(url=COSMOSDB_URL, credential=COSMOSDB_CREDENTIAL)
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
