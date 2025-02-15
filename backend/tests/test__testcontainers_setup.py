# This module's name (double __) makes python unittest runner to execute this BEFORE db module (or any other modules depending on 'db') otherwise db module
# will NOT connect properly to CosmosDb instance initialized here
import os

#os.environ["AZURE_COSMOS_EMULATOR_IMAGE"] = 'mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-preview'

from testcontainers.cosmosdb import CosmosDBNoSQLEndpointContainer
from settings import COSMOSDB_DB_NAME

# cosmosdb
#print("Starting CosmosDb")
#with CosmosDBNoSQLEndpointContainer() as emulator:
#    print("CosmosDb started, url=" + emulator.url)
#    emulator.insecure_sync_client().create_database_if_not_exists(COSMOSDB_DB_NAME)
#    os.environ["COSMOSDB_URL"] = emulator.url
#    os.environ["COSMOSDB_CREDENTIAL"] = emulator.key
