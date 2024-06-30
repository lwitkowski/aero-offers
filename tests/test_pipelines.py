import unittest
import pipelines
from scrapy.exceptions import DropItem
from ddt import ddt, data


@ddt
class PipelineProcessingTest(unittest.TestCase):

    @data(
        "Suche Stemme S12",
        "Looking for Stemme S12",
        "Discus CS - SUCHE"
    )
    def test_search_offers_are_dropped(self, offer_title):
        offer = {"title": offer_title}
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        self.assertRaises(DropItem, offer_filter.process_item, offer, None)

    @data(
        "Arcus M Charter in Bitterwasser ab dem 11.01.20",
        "Ventus cM Charter",
        "DuoDiscus-Turbo in Top Zustand zu verchartern mit Vorsaisonpreis !",
        "ASG29E with 15m and 18m wingtips for rent",
    )
    def test_charter_offers_are_dropped(self, offer_title):
        offer = {"title": offer_title}
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        self.assertRaises(DropItem, offer_filter.process_item, offer, None)

    @data(
        "DG101 G - Competition ready",
        "Biete tolles Flugzeug"
    )
    def test_regular_offers_are_not_dropped(self, offer_title):
        offer = {"title": offer_title}
        offer_filter = pipelines.FilterSearchAndCharterOffers()
        offer_filter.process_item(offer, None)
