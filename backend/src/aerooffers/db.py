import os

from azure.cosmos import (
    ContainerProxy,
    CosmosClient,
    DatabaseProxy,
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
