# This module's name (double __) makes python unittest runner to execute this BEFORE db module (or any other modules depending on 'db') otherwise db module
# will NOT connect properly to CosmosDb instance initialized here
import os

from testcontainers.cosmosdb import CosmosDBNoSQLEndpointContainer
from settings import COSMOSDB_DB_NAME

# cosmosdb
print("Starting CosmosDb")

emulator = CosmosDBNoSQLEndpointContainer()
emulator.start()

print("CosmosDb started, url=" + emulator.url)
emulator.insecure_sync_client().create_database_if_not_exists(COSMOSDB_DB_NAME)
print("CosmosDb db created")
os.environ["COSMOSDB_URL"] = emulator.url
os.environ["COSMOSDB_CREDENTIAL"] = emulator.key