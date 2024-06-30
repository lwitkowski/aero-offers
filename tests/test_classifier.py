import unittest
from classifier.classifier import get_confusion_matrix, ModelClassifier


class ClassifierTest(unittest.TestCase):
    def setUp(self):
        self.model_classifier = ModelClassifier()

    def test_get_confusion_matrix(self):
        confusion_matrix = get_confusion_matrix([
            {
                "input": "Akaflieg Braunschweig SB 5",
                "manufacturer": "Akaflieg Braunschweig",
                "model": "SB 5"
            },
            {
                "input": "#1!?öläöäö",
                "manufacturer": "Akaflieg Braunschweig",
                "model": "SB 5"
            },
        ])
        self.assertGreater(len(confusion_matrix), 0)
