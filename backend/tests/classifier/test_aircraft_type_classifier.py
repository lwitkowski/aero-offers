import json

from assertpy import assert_that
from util import read_file

from aerooffers.classifier.classifier import AircraftTypeClassifier


def test_aircraft_type_is_classified_even_when_model_is_unknown() -> None:
    json_file_content = read_file("classifier/classifier_test_data_aircraft_type.json")
    data = json.loads(json_file_content)
    classifier = AircraftTypeClassifier()

    for item in data:
        title = item["title"]
        spider = item["spider"]
        if "aircraft_type" in item:
            expected_type = item["aircraft_type"]
            aircraft_type = classifier.classify(title, spider)
            assert_that(aircraft_type).is_equal_to(expected_type)
