# -*- coding: UTF-8 -*-

import unittest
import pytest

import offers_db
from job_reclassify_offers import reclassify_all
from util import sample_offer


class ReclassifyOffersJobTest(unittest.TestCase):

    def setUp(self):
        offers_db.truncate_all_tables()

    def test_reclassify_only_unclassified_offers(self):
        # given
        classified_offer_id = offers_db.store_offer(sample_offer(url="https://offers.com/1"))
        offers_db.classify_offer(offer_id=classified_offer_id, category='glider', manufacturer='PZL Bielsko', model='Bocian')
        second_classified_offer_id = offers_db.store_offer(sample_offer(url="https://offers.com/2"))
        offers_db.classify_offer(offer_id=second_classified_offer_id, category='glider', manufacturer='PZL Bielsko', model='Bocian')
        unclassified_offer_id = offers_db.store_offer(sample_offer(url="https://offers.com/3"))

        # when
        offers_processed = reclassify_all()

        # then
        assert offers_processed == 1
        assert len(offers_db.get_unclassified_offers()) == 0


if __name__ == '__main__':
    pytest.main()
