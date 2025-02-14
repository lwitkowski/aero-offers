import os

# database
COSMOSDB_URL = os.getenv('COSMOSDB_URL', 'http://localhost:8081')
COSMOSDB_CREDENTIAL = os.getenv('COSMOSDB_CREDENTIAL', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==')
COSMOSDB_DB_NAME = "aerooffers"

# mailer
SEND_RESULT_MAIL = False
SMTP_USER = ""
SMTP_PASSWORD = ""
SMTP_HOST = ""

# scrapy pipeline components config, do not delete this
ITEM_PIPELINES = {
    'pipelines.FilterSearchAndCharterOffers': 100,
    'pipelines.DuplicateDetection': 200,
    'pipelines.PriceParser': 300,
    'pipelines.StoragePipeline': 400,
}
