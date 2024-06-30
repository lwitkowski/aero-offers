import unittest
import db


class DbTest(unittest.TestCase):

    def test_filter_for_aircraft_type(self):
        result = db.get_offers_dict(order_by=None, limit=10, offset=None, aircraft_type="glider")
        self.assertEqual(10, len(result))

    # TODO add tests for database-related stuff here
