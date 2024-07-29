from classifier import classifier
import db
import argparse
from spiders import SoaringDeSpider
from my_logging import *

logger = logging.getLogger('reclassify_job')
aircraft_type_classifier = classifier.AircraftTypeClassifier()
model_classifier = classifier.ModelClassifier()


def reclassify(db_offer):
    # try to classify model first:
    expect_manufacturer = not db_offer.spider == SoaringDeSpider.SoaringDeSpider.name
    (manufacturer, model, aircraft_type) = model_classifier.classify(db_offer.title, expect_manufacturer,
                                                                     db_offer.detail_text)
    if manufacturer:
        logger.debug("Classified '%s' as '%s' '%s'", db_offer.title, manufacturer, model)
        db_offer.manufacturer = manufacturer
        db_offer.model = model
        db_offer.aircraft_type = aircraft_type
    else:
        db_offer.manufacturer = None
        db_offer.model = None
        aircraft_type = aircraft_type_classifier.classify(db_offer.title, db_offer.spider)
        logger.debug("Classified '%s' as '%s'", db_offer.title, aircraft_type)
        db_offer.aircraft_type = aircraft_type
    db_offer.classified = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--offer-id", type=int, help="only reclassify given offer id")
    args = parser.parse_args()

    session = db.Session()
    try:
        unclassifiedCount = session.query(db.AircraftOffer).filter(db.AircraftOffer.classified == False).count()
        logger.info("Found %d unclassified offers", unclassifiedCount)

        offers = session.query(db.AircraftOffer).yield_per(100).enable_eagerloads(False)

        if args.offer_id is not None:
            offers = offers.filter(db.AircraftOffer.id == args.offer_id)
        else:
            offers = offers.filter(db.AircraftOffer.classified == False)

        for offer in offers:
            reclassify(offer)
            session.flush()
        session.commit()
    finally:
        session.close()
