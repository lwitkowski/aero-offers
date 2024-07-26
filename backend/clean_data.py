import re
from db import AircraftOffer, Session
from my_logging import *

logger = logging.getLogger("clean_data")

session = Session()
aircraft_offers = session.query(AircraftOffer).all()

terms_to_remove = [
    r"zu verkaufen",
    r"gepflegt(e)?(r)?",
    r"schön(e)?(r)?",
    r"sehr",
    r"for sale",
    r"Biete",
]


def clean_model_name(model_name):
    cleaned_model_name = model_name
    for term in terms_to_remove:
        # logger.debug("Removing term case insensitive: {0}".format(term))
        cleaned_model_name = re.sub(term, "", cleaned_model_name, flags=re.IGNORECASE)
    return cleaned_model_name.strip()


if __name__ == '__main__':
    for offer in aircraft_offers:
        cleaned_model_name = clean_model_name(offer.model)
        offer.model = cleaned_model_name
        logger.debug("Before: {0} After: {1} ".format(offer.model, cleaned_model_name))
    session.flush()
    session.commit()
