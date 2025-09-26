# -*- coding: UTF-8 -*-
from azure.cosmos import CosmosClient
from settings import COSMOSDB_URL, COSMOSDB_CREDENTIAL, COSMOSDB_DB_NAME
from my_logging import logging

logger = logging.getLogger("db")
logger.info(
    "Connecting to CosmosDB, url={0}, db_name={1}".format(
        COSMOSDB_URL, COSMOSDB_DB_NAME
    )
)

client = CosmosClient(url=COSMOSDB_URL, credential=COSMOSDB_CREDENTIAL)
database = client.create_database_if_not_exists(COSMOSDB_DB_NAME)

logger.info("Connection established successfully")
