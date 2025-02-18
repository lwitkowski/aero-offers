# -*- coding: UTF-8 -*-

import unittest
from datetime import date

import offers_db
from offer import AircraftCategory

from offer import Offer
from util import sample_offer


class DbTest(unittest.TestCase):

    def setUp(self):
        offers_db.truncate_all_tables()

    def test_should_store_and_fetch_offer(self):
        # given
        offers_db.store_offer(sample_offer(price="29500", currency="EUR"))

        # when
        all_offers = offers_db.get_offers()

        # then
        self.assertEqual(1, len(all_offers))
        glider_offer = all_offers[0]
        self.assertEqual(glider_offer.title, "Glider A")
        self.assertEqual(glider_offer.price.amount, "29500")
        self.assertEqual(glider_offer.price.currency, "EUR")

    def test_should_filter_offers_by_aircraft_type(self):
        # given
        offers_db.store_offer(sample_offer())

        # when
        gliders_only = offers_db.get_offers(category=AircraftCategory.glider)
        airplanes_only = offers_db.get_offers(category=AircraftCategory.airplane)

        # then
        self.assertEqual(len(gliders_only), 1)
        self.assertEqual(len(airplanes_only), 0)

    def test_should_filter_offers_by_manufacturer_and_model(self):
        # given
        stored_offer_id = offers_db.store_offer(sample_offer())
        offers_db.classify_offer(offer_id=stored_offer_id, category='glider', manufacturer='Schempp-Hirth', model='Mini-Nimbus')

        # when
        mini_nimbuses = offers_db.get_offers(manufacturer='Schempp-Hirth', model='Mini-Nimbus')
        asg29s = offers_db.get_offers(manufacturer='Alexander Schleicher', model='ASG 29 E')

        # then
        self.assertEqual(1, len(mini_nimbuses))
        self.assertEqual(0, len(asg29s))

    def test_should_not_reset_category_if_none(self):
        # given
        stored_offer_id = offers_db.store_offer(sample_offer())
        offers_db.classify_offer(offer_id=stored_offer_id, category='glider', manufacturer='Schempp-Hirth', model='Mini-Nimbus')

        # when
        offers_db.classify_offer(offer_id=stored_offer_id, category=None, manufacturer=None, model=None)

        # then
        offer_from_db: Offer = offers_db.get_offers()[0]
        self.assertEqual(offer_from_db.category, 'glider')

    def test_should_order_offers_by_published_date_desc(self):
        # given
        offers_db.store_offer(sample_offer(published_at=date(2024, 1, 2)))
        offers_db.store_offer(sample_offer(published_at=date(2024, 2, 1)))
        offers_db.store_offer(sample_offer(published_at=date(2023, 3, 15)))
        offers_db.store_offer(sample_offer(published_at=date(2024, 1, 31)))

        # when
        orders = offers_db.get_offers()

        # then
        self.assertEqual(orders[0].published_at, "2024-02-01")
        self.assertEqual(orders[1].published_at, "2024-01-31")
        self.assertEqual(orders[2].published_at, "2024-01-02")
        self.assertEqual(orders[3].published_at, "2023-03-15")

    def test_should_check_url_exists(self):
        # given offer exists in db
        offers_db.store_offer(sample_offer(url="https://offers.com/1"))

        # when
        url_exists = offers_db.offer_url_exists("https://offers.com/1")

        # then
        self.assertTrue(url_exists)
        self.assertFalse(offers_db.offer_url_exists("https://offers.com/2"))


if __name__ == '__main__':
    unittest.main()
