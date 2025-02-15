import os
import platform

os.environ['AZURE_COSMOS_EMULATOR_IMAGE'] = 'mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-EN20250122'

from typing_extensions import Self
from testcontainers.core.waiting_utils import wait_for_logs

from testcontainers.cosmosdb import CosmosDBNoSQLEndpointContainer
from settings import COSMOSDB_DB_NAME
from azure.cosmos import CosmosClient

class OsxCosmosDBNoSQLEndpointContainer(CosmosDBNoSQLEndpointContainer):

    def __init__(self, **kwargs):
        super().__init__(bind_ports=True, **kwargs)

    # vnext-preview doesn't print `Started`
    def _wait_until_ready(self) -> Self:
        wait_for_logs(container=self, predicate="Emulator is accessible")
        return self

    # this fails on vnext-preview, thus needs to be overridden
    def _download_cert(self) -> bytes:
        return bytes()


def pytest_sessionstart(session):
    print("Starting CosmosDb TestContainers, db name=" + COSMOSDB_DB_NAME)

    emulator = OsxCosmosDBNoSQLEndpointContainer()
    emulator.start()

    cosmos_db_url = f"http://{emulator.host}:{emulator.port}"
    print("CosmosDb started, url=" + cosmos_db_url)

    os.environ["COSMOSDB_URL"] = cosmos_db_url
    os.environ["COSMOSDB_CREDENTIAL"] = emulator.key

    client = CosmosClient(url=cosmos_db_url, credential=emulator.key, connection_verify=False)
    client.create_database_if_not_exists(COSMOSDB_DB_NAME)

    print("Test database initialized")
