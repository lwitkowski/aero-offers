import os

from aerooffers.db import create_offers_container_if_not_exists

os.environ["AZURE_COSMOS_EMULATOR_IMAGE"] = (
    "mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-EN20250122"
)

import os
from collections.abc import Generator
from typing import Self

import pytest
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.cosmosdb import CosmosDBNoSQLEndpointContainer


class VnextCosmosDBNoSQLEndpointContainer(CosmosDBNoSQLEndpointContainer):
    def __init__(self, **kwargs) -> None:  # type: ignore
        super().__init__(bind_ports=True, **kwargs)

    # vnext image doesn't print `Started`
    def _wait_until_ready(self) -> Self:
        wait_for_logs(
            container=self, predicate=LogMessageWaitStrategy("Emulator is accessible")
        )
        return self

    # this fails on vnext image, thus needs to be overridden
    def _download_cert(self) -> bytes:
        return b""


@pytest.fixture(scope="session")
def session_cosmos_db() -> Generator[CosmosClient, None, None]:
    from aerooffers.db import COSMOSDB_DB_NAME

    print("Starting CosmosDb TestContainers, db name=" + COSMOSDB_DB_NAME)

    emulator = VnextCosmosDBNoSQLEndpointContainer()
    emulator.start()

    cosmos_db_url = f"http://{emulator.host}:{emulator.port}"
    print("CosmosDb started, url=" + cosmos_db_url)

    os.environ["COSMOSDB_URL"] = cosmos_db_url
    os.environ["COSMOSDB_CREDENTIAL"] = emulator.key

    client = CosmosClient(
        url=cosmos_db_url, credential=emulator.key, connection_verify=False
    )
    client.create_database_if_not_exists(COSMOSDB_DB_NAME)
    print("Test database initialized")

    yield client

    emulator.stop(force=True, delete_volume=True)


@pytest.fixture
def cosmos_db(session_cosmos_db: CosmosClient) -> CosmosClient:
    _truncate_all_tables()
    return session_cosmos_db


def _truncate_all_tables() -> None:
    from aerooffers.db import lazy_database

    try:
        lazy_database().delete_container(container="offers")
    except CosmosResourceNotFoundError:
        print("ntbd")

    create_offers_container_if_not_exists()
