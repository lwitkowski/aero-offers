ITEM_PIPELINES = {
    'pipelines.DuplicateDetection': 100,
    'pipelines.FilterUnreasonablePrices': 200,
    'pipelines.FilterSearchAndCharterOffers': 300,
    'pipelines.StoragePipeline': 400,
}

# database
DB_HOST = "postgres"
DB_PORT = 5432
DB_NAME = "aircraft_offers"
DB_USER = "aircraft_offers"
DB_PW = "aircraft_offers"

# mailer
SEND_RESULT_MAIL = False
SMTP_USER = ""
SMTP_PASSWORD = ""
SMTP_HOST = ""
