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
        classified_offer_id = offers_db.store_offer(
            sample_offer(url="https://offers.com/1")
        )
        offers_db.classify_offer(
            offer_id=classified_offer_id,
            category="glider",
            manufacturer="PZL Bielsko",
            model="Bocian",
        )
        second_classified_offer_id = offers_db.store_offer(
            sample_offer(url="https://offers.com/2")
        )
        offers_db.classify_offer(
            offer_id=second_classified_offer_id,
            category="glider",
            manufacturer="PZL Bielsko",
            model="Bocian",
        )
        offers_db.store_offer(sample_offer(url="https://offers.com/3"))

        # when
        offers_processed = reclassify_all()

        # then
        self.assertEqual(offers_processed, 1)
        self.assertEqual(len(offers_db.get_unclassified_offers()), 0)

    def test_should_persist_manufacturer_and_model_if_classified(self):
        # given
        offers_db.store_offer(sample_offer(title="LS-1"))

        # when
        reclassify_all()

        # then
        ls1_offer = offers_db.get_offers()[0]
        self.assertIsNotNone(ls1_offer)
        self.assertEqual(ls1_offer.category, "glider")
        self.assertEqual(ls1_offer.manufacturer, "Rolladen Schneider")
        self.assertEqual(ls1_offer.model, "LS1")

    def test_should_persist_at_least_category_if_title_indicates_it_clearly(self):
        # given
        offers_db.store_offer(sample_offer(title="Stemme"))  # Stemme produces only TMGs

        # when
        reclassify_all()

        # then
        offer = offers_db.get_offers()[0]
        self.assertIsNotNone(offer)
        self.assertEqual(offer.category, "tmg")
        self.assertIsNone(offer.manufacturer)
        self.assertIsNone(offer.model)


if __name__ == "__main__":
    pytest.main()
