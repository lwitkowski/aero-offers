from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env file in backend directory (settings.py is in src/aerooffers/)
# Path: src/aerooffers/settings.py -> src/aerooffers -> src -> backend -> .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path, override=False)

# scrapy pipeline components config, do not delete this
ITEM_PIPELINES = {
    "aerooffers.pipelines.SkipSearchAndCharterOffers": 100,
    "aerooffers.pipelines.SkipDuplicates": 200,
    "aerooffers.pipelines.ParsePrice": 300,
    "aerooffers.pipelines.StoreOffer": 400,
}

# Scrapy logging configuration
# Set to INFO to prevent DEBUG messages from appearing
# This works together with logging.conf to control log levels
LOG_LEVEL = "INFO"
