# -*- coding: UTF-8 -*-

import unittest

import tests.test__testcontainers_setup
import offers_db
from offer import AircraftCategory
from tests.util import offer_with_url


class DbTest(unittest.TestCase):

    def setUp(self):
        offers_db.truncate_all_tables()

    def test_should_store_and_fetch_offer(self):
        # given
        sample_offer = offer_with_url("https://offers.com/1")
        sample_offer.price = "29500"
        sample_offer.currency = "EUR"

        # when
        offers_db.store_offer(sample_offer)
        all_offers = offers_db.get_offers()

        # then
        self.assertEqual(1, len(all_offers))
        glider_offer = all_offers[0]
        self.assertEqual("Glider A", glider_offer["title"])
        self.assertEqual("29500", glider_offer["price"]["amount"])
        self.assertEqual("EUR", glider_offer["price"]["currency"])

    def test_should_filter_offers_by_aircraft_type(self):
        # given
        sample_offer = offer_with_url("https://offers.com/1")
        offers_db.store_offer(sample_offer)

        # when
        gliders_only = offers_db.get_offers(category=AircraftCategory.glider)
        airplanes_only = offers_db.get_offers(category=AircraftCategory.airplane)

        # then
        self.assertEqual(len(gliders_only), 1)
        self.assertEqual(len(airplanes_only), 0)

    def test_should_filter_offers_by_manufacturer_and_model(self):
        # given
        stored_offer_id = offers_db.store_offer(offer_with_url("https://offers.com/1"))
        offers_db.classify_offer(offer_id=stored_offer_id, category='glider', manufacturer='Schempp-Hirth', model='Mini-Nimbus')

        # when
        mini_nimbuses = offers_db.get_offers(manufacturer='Schempp-Hirth', model='Mini-Nimbus')
        asg29s = offers_db.get_offers(manufacturer='Alexander Schleicher', model='ASG 29 E')

        # then
        self.assertEqual(1, len(mini_nimbuses))
        self.assertEqual(0, len(asg29s))

    def test_should_check_url_exists(self):
        # given offer exists in db
        offers_db.store_offer(offer_with_url("https://offers.com/1"))

        # when
        url_exists = offers_db.offer_url_exists("https://offers.com/1")

        # then
        self.assertTrue(url_exists)
        self.assertFalse(offers_db.offer_url_exists("https://offers.com/2"))


if __name__ == '__main__':
    unittest.main()
