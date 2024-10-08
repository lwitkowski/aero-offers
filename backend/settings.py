import os

# database
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', 25432)
DB_NAME = os.getenv('DB_NAME', 'aircraft_offers')
DB_USER = os.getenv('DB_USER', 'aircraft_offers')
DB_PW = os.getenv('DB_PW', 'aircraft_offers')

# mailer
SEND_RESULT_MAIL = False
SMTP_USER = ""
SMTP_PASSWORD = ""
SMTP_HOST = ""

# scrapy pipeline components config, do not delete this
ITEM_PIPELINES = {
    'pipelines.PriceParser': 100,
    'pipelines.FilterSearchAndCharterOffers': 200,
    'pipelines.DuplicateDetection': 300,
    'pipelines.StoragePipeline': 400,
}
