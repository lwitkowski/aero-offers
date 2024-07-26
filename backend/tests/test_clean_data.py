import unittest
from clean_data import clean_model_name


class CleanDataTest(unittest.TestCase):

    def test_clean_model_name(self):
        test_data = {"Sehr gepflegte DG100": "DG100",
                     "Sehr gepflegter Ventus 2CM": "Ventus 2CM"}
        for model_input, output in test_data.items():
            self.assertEqual(output, clean_model_name(model_input))
