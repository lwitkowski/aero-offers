from classifier import classifier
import offers_db
from my_logging import *
from spiders.SoaringDeSpider import SoaringDeSpider

logger = logging.getLogger('reclassify_job')
aircraft_type_classifier = classifier.AircraftTypeClassifier()
model_classifier = classifier.ModelClassifier()


def reclassify(db_offer):
    expect_manufacturer = not db_offer['spider'] == SoaringDeSpider.name
    (manufacturer, model, category) = model_classifier.classify(db_offer['title'], expect_manufacturer,
                                                                     db_offer['page_content'])
    if manufacturer:
        logger.debug("Classified '%s' as '%s' '%s'", db_offer['title'], manufacturer, model)
        offers_db.classify_offer(offer_id=db_offer['id'], category=category, manufacturer=manufacturer, model=model)
    else:
        aircraft_type = aircraft_type_classifier.classify(db_offer['title'], db_offer['spider'])
        logger.debug("Classified '%s' as '%s'", db_offer['title'], aircraft_type)
        offers_db.classify_offer(offer_id=db_offer['id'], category=category, manufacturer=None, model=None)


if __name__ == '__main__':
    offers = offers_db.get_unclassified_offers()
    for offer in offers:
        reclassify(offer)

    logger.info("Finished classifying {0} offers".format(len(offers)))
