import json
import string
import re
from nltk.util import ngrams
from nltk.corpus import stopwords
from my_logging import *
from nltk.metrics import distance

import nltk
nltk.download('stopwords')

logger = logging.getLogger('classifier')

aircraft_types = ["glider", "tmg", "ultralight", "airplane", "helicopter"]


def get_all_models():
    models_file = "models.json"
    with open(os.path.dirname(os.path.realpath(__file__)) + os.sep + models_file) as json_file:
        manufacturers = json.load(json_file)
    return manufacturers


class ModelClassifier:
    manufacturers = {}

    is_dg_model_re = re.compile(r'^DG[0-9]{3,4}$')
    is_binder_model_re = re.compile(r'^(EB28|EB29)$')
    is_schleicher_model_re = re.compile(r'AS[H|W|K|G]\s?[0-9]{2}(\sMi)?$')

    def __init__(self):
        self.manufacturers = get_all_models()

    def preprocess(self, input_text):
        # char - is used in model names (DG-100, ...)
        punctuation_regex = string.punctuation.replace("-", "").replace("/", "")
        logger.debug("removing punctuation using regex {0}".format(punctuation_regex))
        translator = str.maketrans('', '', punctuation_regex)
        return input_text.translate(translator)

    def tokenize(self, text):
        text = self.preprocess(text)
        tokens = text.split(" ")
        return [token for token in tokens if token.strip() != ""]

    def join_single_characters(self, l):
        if len(l) < 2:
            return l
        joined_list = [""]
        i = 0
        while len(l) > 0:
            el = l.pop(0)
            current = joined_list[i]
            # push to left element if we are
            # a) at the end or
            # b) left is shorter than 2 chars or
            # c) the predecessor is a model name (dg 800 s, ash 25)
            if self.is_dg_model_re.match(current) or \
                    self.is_binder_model_re.match(current + el):
                joined_list[i] = current + el
            elif (not current.isnumeric() and not el.isnumeric()) \
                    and len(current) < 2 or (len(l) == 0 and len(el) < 2):
                joined_list[i] = current + el
            elif self.is_schleicher_model_re.match(current + el):
                if len(l) > 0 and l[0] == "Mi":
                    joined_list[i] = current + " " + el + " " + l.pop(0)
                else:
                    joined_list[i] = current + " " + el
            else:
                i = i + 1
                joined_list.append(el)
        return joined_list

    def _starts_with_manufacturer(self, input_text):
        # TODO refactor this
        for manufacturer in self.manufacturers.keys():
            if input_text.lower().startswith(manufacturer.lower()):
                return manufacturer
        return None

    def _build_tokens(self, input_text):
        tokens = self.join_single_characters(self.tokenize(input_text))
        logger.debug("after joining single characters tokens are: {0}".format(str(tokens)))
        stop_words_en = stopwords.words('english')
        stop_words_de = stopwords.words('german')

        tokens = [word for word in tokens if word not in stop_words_de]
        return [word for word in tokens if word not in stop_words_en]

    def _build_grams(self, tokens):
        grams = list(ngrams(tokens, 1))
        bigrams = list(ngrams(tokens, 2))
        trigrams = list(ngrams(tokens, 3))
        if bigrams is not None:
            grams = grams + bigrams
        if trigrams is not None:
            grams = grams + trigrams
        return grams

    def _classify_against_models(self, grams, models, cutoff_score, expect_manufacturer=False, manufacturer=None):
        best_score = 0.0
        best_score_length = 0
        best_solution = None, None, None

        for aircraft_type in aircraft_types:
            if aircraft_type not in models:
                continue
            for model in models[aircraft_type]:
                for gram in grams:
                    joined_gram = " ".join(gram)
                    if expect_manufacturer:
                        test_str = manufacturer + model
                    else:
                        test_str = model

                    if len(test_str) < 4 or len(joined_gram) < 4:
                        this_cutoff_score = 0.9
                    else:
                        this_cutoff_score = cutoff_score

                    ratio = distance.jaro_similarity(joined_gram.lower(), test_str.lower())
                    logger.debug("Score: %s for gram: %s against %s %s", ratio, joined_gram, manufacturer, model)
                    # if the existing solution is a n-gram with n smaller than this n and same score
                    # this one will be the winner (longer match => more precise)
                    if ratio > this_cutoff_score and ratio >= best_score and len(joined_gram) >= best_score_length:
                        logger.debug("Found new best score %s with: %s %s", ratio, manufacturer, model)
                        best_solution = (manufacturer, model, aircraft_type)
                        best_score = ratio
                        best_score_length = len(joined_gram)

        return best_solution

    def classify(self, input_text, expect_manufacturer=True, detail_text=""):
        """
        Try to get the correct manufacturer and model for an airplane offer

        :param detail_text: the details of the airplane offer
        :param input_text: Strings like "Stemme S12-SW"
        :param expect_manufacturer: whether to test also only the models
        :return: triplet of: (manufacturer, model, aircraft_type)
        """
        tokens = self._build_tokens(input_text)
        grams = self._build_grams(tokens)

        if len(tokens) < 2 and expect_manufacturer:
            logger.warning("Found only 1 Token, classifying against model only")
            expect_manufacturer = False

        cutoff_score = 0.85

        manufacturer = self._starts_with_manufacturer(input_text)
        if manufacturer is not None:
            logger.info("Found Manufacturer: {0}".format(manufacturer))
            # reduce cutoff as we already have the manufacturer, classify rest against models of this manufacturer
            tokens = self._build_tokens(input_text[len(manufacturer):])
            grams = self._build_grams(tokens)

            cutoff_score = 0.75
            models = self.manufacturers[manufacturer]["models"]

            (manufacturer, model, aircraft_type) = self._classify_against_models(grams, models, cutoff_score,
                                                                                 expect_manufacturer=False,
                                                                                 manufacturer=manufacturer)
            return manufacturer, model, aircraft_type

        search_aircraft_types = aircraft_types
        if not expect_manufacturer:
            # try to reduce the possibilities here
            if detail_text is not None and " glider " in detail_text.lower():
                logger.debug("Reducing search to only glider/tmg models")
                search_aircraft_types = ["glider", "tmg"]

        for manufacturer, details in self.manufacturers.items():
            models = details["models"]
            models = {key: value for (key, value) in models.items() if key in search_aircraft_types}
            (manufacturer, model, aircraft_type) = self._classify_against_models(grams, models, cutoff_score,
                                                                                 expect_manufacturer=expect_manufacturer,
                                                                                 manufacturer=manufacturer)
            if manufacturer is not None:
                return manufacturer, model, aircraft_type
        return manufacturer, model, aircraft_type


class AircraftTypeClassifier:
    manufacturers_with_only_one_type = {
        "glider": ["Schleicher"],
        "ultralight": ["Comco Ikarus", "Pipistrel"],
        "airplane": ["Cessna", "Beechcraft", "Piper", "Mooney", "Pitts"],
        "helicopter": ["Eurocopter", "Airbus Helicopters"],
        "tmg": ["Stemme"]
    }

    def classify(self, title, spider):
        for aircraft_type, manufacturers in self.manufacturers_with_only_one_type.items():
            for manufacturer in manufacturers:
                if manufacturer in title:
                    return aircraft_type
        if spider == "planecheck_com":
            return "airplane"
        return "glider"
