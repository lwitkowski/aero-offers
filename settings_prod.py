ITEM_PIPELINES = {
    'pipelines.DuplicateDetection': 100,
    'pipelines.FilterUnreasonablePrices': 200,
    'pipelines.FilterSearchAndCharterOffers': 300,
    'pipelines.StoragePipeline': 400,
}

# database
DB_USER = "aircraftoffers"
DB_PW = ""
DB_NAME = "aircraft_offers"
DB_HOST = "localhost"
DB_PORT = 5432

# mailer
SEND_RESULT_MAIL = True
SMTP_USER = ""
SMTP_PASSWORD = ""
SMTP_HOST = ""
