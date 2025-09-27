import os

os.environ["AZURE_COSMOS_EMULATOR_IMAGE"] = (
    "mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-EN20250122"
)

from azure.cosmos import CosmosClient
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.cosmosdb import CosmosDBNoSQLEndpointContainer
from typing_extensions import Self

from settings import COSMOSDB_DB_NAME


class VnextCosmosDBNoSQLEndpointContainer(CosmosDBNoSQLEndpointContainer):
    def __init__(self, **kwargs):
        super().__init__(bind_ports=True, **kwargs)

    # vnext image doesn't print `Started`
    def _wait_until_ready(self) -> Self:
        wait_for_logs(container=self, predicate="Emulator is accessible")
        return self

    # this fails on vnext image, thus needs to be overridden
    def _download_cert(self) -> bytes:
        return bytes()


def pytest_sessionstart(session):
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
