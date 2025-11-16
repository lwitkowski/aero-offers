import json
import unittest

from util import read_file

from classifier.classifier import AircraftTypeClassifier


class AircraftTypeClassifierTest(unittest.TestCase):
    def setUp(self):
        self.classifier = AircraftTypeClassifier()

    def test_aircraft_type_is_classified_even_when_model_is_unknown(self):
        json_file_content = read_file(
            "classifier/classifier_test_data_aircraft_type.json"
        )
        data = json.loads(json_file_content)
        for item in data:
            title = item["title"]
            spider = item["spider"]
            if "aircraft_type" in item:
                expected_type = item["aircraft_type"]
                aircraft_type = self.classifier.classify(title, spider)
                self.assertEqual(
                    expected_type,
                    aircraft_type,
                    f"Title: {title} Spider: {spider} should have been classified as {expected_type}, but was {aircraft_type}",
                )
