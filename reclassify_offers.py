from classifier import classifier
import db
import argparse
from spiders import SegelflugDeSpider

aircraft_type_classifier = classifier.AircraftTypeClassifier()
model_classifier = classifier.ModelClassifier()


def reclassify(db_offer):
    # try to classify model first:
    expect_manufacturer = not db_offer.spider == SegelflugDeSpider.SegelflugDeSpider.name
    (manufacturer, model, aircraft_type) = model_classifier.classify(db_offer.title, expect_manufacturer,
                                                                     db_offer.detail_text)
    if manufacturer:
        print("Classified {0} as {1} {2}".format(db_offer.title, manufacturer, model))
        db_offer.manufacturer = manufacturer
        db_offer.model = model
        db_offer.aircraft_type = aircraft_type
    else:
        db_offer.manufacturer = None
        db_offer.model = None
        aircraft_type = aircraft_type_classifier.classify(db_offer.title, db_offer.spider)
        print("Classified {0} as {1}".format(db_offer.title, aircraft_type))
        db_offer.aircraft_type = aircraft_type


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--offer-id", type=int, help="only reclassify given offer id")
    args = parser.parse_args()

    session = db.Session()
    try:
        offers = session.query(db.AircraftOffer).yield_per(100).enable_eagerloads(False)
        if args.offer_id is not None:
            offers = offers.filter(db.AircraftOffer.id == args.offer_id)
        for offer in offers:
            reclassify(offer)
            session.flush()
        session.commit()
    finally:
        session.close()
