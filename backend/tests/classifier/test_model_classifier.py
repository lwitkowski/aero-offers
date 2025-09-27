import unittest

from ddt import data, ddt, unpack

from classifier import classifier


@ddt
class ModelClassifierTest(unittest.TestCase):
    def setUp(self):
        self.model_classifier = classifier.ModelClassifier()

    @unpack
    @data(
        (["Hello", "world"], "Hello  world"),
        (["Nimbus", "3", "255", "m"], "Nimbus 3 25.5 m"),
    )
    def test_tokenize(self, tokens, input_str):
        self.assertEqual(tokens, self.model_classifier.tokenize(input_str))

    def test_is_schleicher_model_re(self):
        self.assertTrue(self.model_classifier.is_schleicher_model_re.match("ASW 19"))
        self.assertTrue(self.model_classifier.is_schleicher_model_re.match("ASW19"))
        self.assertIsNone(self.model_classifier.is_schleicher_model_re.match("HSK15"))

    @unpack
    @data(
        (["ab", "cd"], ["a", "b", "cd"]),
        (["DG", "800B"], ["DG", "800", "B"]),
        # (["ka", "2b", "gut"], ["ka", "2", "b", "gut"]),
        (["robin", "dr", "400/180", "regent"], ["robin", "dr", "400/180", "regent"]),
        (["DG800S", "HB-2352"], ["DG800", "S", "HB-2352"]),
        (["ASH 25"], ["ASH", "25"]),
        (["ASH 25 Mi"], ["ASH", "25", "Mi"]),
        (["ASW 17"], ["ASW", "17"]),
        (["EB28"], ["EB", "28"]),
        (["ASK 21", "D-1234"], ["ASK", "21", "D-1234"]),
        (["DG-100", "for", "sale"], ["DG-100", "for", "sale"]),
        (["Nimbus", "3", "255m"], ["Nimbus", "3", "255", "m"]),
    )
    def test_join_single_characters(self, output_list, input_list):
        self.assertEqual(
            output_list, self.model_classifier.join_single_characters(input_list)
        )

    def test_preprocess_removes_punctuation(self):
        self.assertEqual(
            "Hello World", self.model_classifier.preprocess("Hello, World!")
        )

    @unpack
    @data(
        ("Stemme S6-RT", "Stemme", "S6-RT"),
        ("DG 800 B", "DG Flugzeugbau", "DG-800B"),
        ("Vans Aircraft RV-6A", "Vans", "RV-6"),
        ("ASK 21 D-6854", "Alexander Schleicher", "ASK 21"),
        ("ASW-24 WL", "Alexander Schleicher", "ASW 24"),
        ("DG 300", "DG Flugzeugbau", "DG-300"),
        ("TL Ultralight TL-3000 Sirius", "TL Ultralight", "TL-3000 Sirius"),
        ("Nimbus 3 25.5 m", "Schempp-Hirth", "Nimbus 3"),
        ("Nimbus 3 25,5m", "Schempp-Hirth", "Nimbus 3"),
        (
            "Nimbus 4DM, W-Nr. 50, 1.600h, Motor grundüberholt, ARC neu",
            "Schempp-Hirth",
            "Nimbus 4DM",
        ),
        ("Ventus 2B", "Schempp-Hirth", "Ventus 2b"),
        ("JS1-C", "Jonker", "JS1 C"),
    )
    def test_single_models_regression(
        self, input_str, expected_manufacturer, expected_model
    ):
        (manufacturer, model, _) = self.model_classifier.classify(
            input_str, expect_manufacturer=False
        )
        self.assertEqual(expected_manufacturer, manufacturer)
        self.assertEqual(expected_model, model)

    def test_with_no_detail_text(self):
        self.model_classifier.classify(
            "DG-100", expect_manufacturer=False, detail_text=None
        )
