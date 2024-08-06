import unittest
from ddt import ddt, data

import tests.test__testcontainers_setup
import db

@ddt
class DbTest(unittest.TestCase):

    def setUp(self):
        db.truncate_offers()

    def test_should_store_and_fetch_offer(self):
        # given
        sample_offer = buildOfferWithUrl("https://offers.com/1")

        # when
        db.store_offer(sample_offer)

        # then
        all_gliders_in_db = db.get_offers()
        self.assertEqual(len(all_gliders_in_db), 1)
        self.assertEqual(all_gliders_in_db[0]["title"], "Glider A")

    def test_should_filter_offers_by_aircraft_type(self):
        # given
        sample_offer = buildOfferWithUrl("https://offers.com/1")
        db.store_offer(sample_offer)

        # when
        gliders_only = db.get_offers(aircraft_type="glider")
        airplanes_only = db.get_offers(aircraft_type="airplane")

        # then
        self.assertEqual(len(gliders_only), 1)
        self.assertEqual(len(airplanes_only), 0)

    def test_should_filter_offers_by_manufacturer_and_model(self):
        # given
        sample_offer = buildOfferWithUrl("https://offers.com/1")
        db.store_offer(sample_offer)

        # when
        mini_nimbuses = db.get_offers(manufacturer="Schempp-Hirth", model="Mini-Nimbus")
        asg29s = db.get_offers(manufacturer="Alexander Schleicher", model="ASG 29 E")

        # then
        self.assertEqual(len(mini_nimbuses), 1)
        self.assertEqual(len(asg29s), 0)

    def test_should_check_url_exists(self):
        # given offer exists in db
        db.store_offer(buildOfferWithUrl("https://offers.com/1"))

        # when
        url_exists = db.offer_url_exists("https://offers.com/1")

        # then
        self.assertTrue(url_exists)
        self.assertFalse(db.offer_url_exists("https://offers.com/2"))


def buildOfferWithUrl(url):
    return db.AircraftOffer(
        title="Glider A",
        creation_datetime="2024-07-30 18:45:42.571 +0200",
        date="2024-07-27",
        price=29500.00,
        currency="€",
        currency_code="EUR",
        offer_url=url,
        spider="segelflug_de_kleinanzeigen",
        detail_text="does not matter to much",
        aircraft_type="glider",
        manufacturer="Schempp-Hirth",
        model="Mini-Nimbus"
    )


if __name__ == '__main__':
    unittest.main()
