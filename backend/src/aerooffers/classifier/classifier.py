import json
import os
import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.metrics import distance
from nltk.util import ngrams

from aerooffers.my_logging import logging
from aerooffers.offer import AircraftCategory

nltk.download("stopwords")

logger = logging.getLogger("classifier")

_aircraft_types = [
    AircraftCategory.glider,
    AircraftCategory.tmg,
    AircraftCategory.ultralight,
    AircraftCategory.airplane,
    AircraftCategory.helicopter,
]


def get_all_models() -> dict[str, dict]:
    models_file = "models.json"
    with open(
        os.path.dirname(os.path.realpath(__file__)) + os.sep + models_file
    ) as json_file:
        manufacturers = json.load(json_file)
    return manufacturers


_manufacturers: dict[str, dict] = get_all_models()


def _build_manufacturers_with_only_one_type() -> dict[AircraftCategory, list[str]]:
    """Build a map of aircraft types to manufacturers that only produce that type."""
    type_to_string_map = {
        AircraftCategory.glider: "glider",
        AircraftCategory.tmg: "tmg",
        AircraftCategory.ultralight: "ultralight",
        AircraftCategory.airplane: "airplane",
        AircraftCategory.helicopter: "helicopter",
    }
    string_to_type_map = {v: k for k, v in type_to_string_map.items()}

    result: dict[AircraftCategory, list[str]] = {
        category: [] for category in _aircraft_types
    }

    for manufacturer, details in _manufacturers.items():
        models = details.get("models", {})
        if not models:
            continue

        # Filter to only aircraft types we care about
        relevant_types = {
            cat: models[cat]
            for cat in models.keys()
            if cat in string_to_type_map and models[cat]
        }

        # If manufacturer only has one aircraft type, add to map
        if len(relevant_types) == 1:
            aircraft_type_str = next(iter(relevant_types.keys()))
            aircraft_category = string_to_type_map[aircraft_type_str]
            result[aircraft_category].append(manufacturer)

    return result


_manufacturers_with_only_one_type: dict[AircraftCategory, list[str]] = (
    _build_manufacturers_with_only_one_type()
)


class ModelClassifier:
    _is_dg_model_re = re.compile(r"^DG[0-9]{3,4}$")
    _is_binder_model_re = re.compile(r"^(EB28|EB29)$")
    _is_schleicher_model_re = re.compile(r"AS[H|W|K|G]\s?[0-9]{2}(\sMi)?$")

    def _preprocess(self, input_text: str) -> str:
        # char - is used in model names (DG-100, ...)
        punctuation_regex = string.punctuation.replace("-", "").replace("/", "")
        logger.debug(f"removing punctuation using regex {punctuation_regex}")
        translator = str.maketrans("", "", punctuation_regex)
        return input_text.translate(translator)

    def _tokenize(self, text: str) -> list[str]:
        text = self._preprocess(text)
        tokens = text.split(" ")
        return [token for token in tokens if token.strip() != ""]

    def _join_single_characters(self, tokens: list[str]) -> list[str]:
        if len(tokens) < 2:
            return tokens
        joined_list = [""]
        i = 0
        while len(tokens) > 0:
            el = tokens.pop(0)
            current = joined_list[i]
            # push to left element if we are
            # a) at the end or
            # b) left is shorter than 2 chars or
            # c) the predecessor is a model name (dg 800 s, ash 25)
            if (
                self._is_dg_model_re.match(current)
                or self._is_binder_model_re.match(current + el)
                or (
                    (not current.isnumeric() and not el.isnumeric())
                    and len(current) < 2
                    or (len(tokens) == 0 and len(el) < 2)
                )
            ):
                joined_list[i] = current + el
            elif self._is_schleicher_model_re.match(current + el):
                if len(tokens) > 0 and tokens[0] == "Mi":
                    joined_list[i] = current + " " + el + " " + tokens.pop(0)
                else:
                    joined_list[i] = current + " " + el
            else:
                i = i + 1
                joined_list.append(el)
        return joined_list

    def _starts_with_manufacturer(self, input_text: str) -> str | None:
        # TODO refactor this
        for manufacturer in _manufacturers:
            if input_text.lower().startswith(manufacturer.lower()):
                return manufacturer
        return None

    def _build_tokens(self, input_text: str) -> list[str]:
        tokens = self._join_single_characters(self._tokenize(input_text))
        logger.debug(f"after joining single characters tokens are: {str(tokens)}")
        stop_words_en = stopwords.words("english")
        stop_words_de = stopwords.words("german")

        tokens = [word for word in tokens if word not in stop_words_de]
        return [word for word in tokens if word not in stop_words_en]

    def _build_grams(self, tokens: list[str]) -> list[str]:
        grams = list(ngrams(tokens, 1))
        bigrams = list(ngrams(tokens, 2))
        trigrams = list(ngrams(tokens, 3))
        if bigrams is not None:
            grams = grams + bigrams
        if trigrams is not None:
            grams = grams + trigrams
        return grams

    def _classify_against_models(
        self,
        grams: list[str],
        models: dict[str, list[str]],
        cutoff_score: float,
        manufacturer: str | None = None,
    ) -> tuple[str | None, str | None, AircraftCategory | None]:
        best_score = 0.0
        best_score_length = 0
        best_solution: tuple[str | None, str | None, AircraftCategory | None] = (
            None,
            None,
            None,
        )

        for aircraft_type in _aircraft_types:
            if aircraft_type not in models:
                continue
            for model in models[aircraft_type]:
                for gram in grams:
                    joined_gram = " ".join(gram)
                    if manufacturer is not None:
                        test_str = manufacturer + model
                    else:
                        test_str = model

                    if len(test_str) < 4 or len(joined_gram) < 4:
                        this_cutoff_score = 0.9
                    else:
                        this_cutoff_score = cutoff_score

                    ratio = distance.jaro_similarity(
                        joined_gram.lower(), test_str.lower()
                    )
                    logger.debug(
                        "Score: %s for gram: %s against %s %s",
                        ratio,
                        joined_gram,
                        manufacturer,
                        model,
                    )
                    # if the existing solution is a n-gram with n smaller than this n and same score
                    # this one will be the winner (longer match => more precise)
                    if (
                        ratio > this_cutoff_score
                        and ratio >= best_score
                        and len(joined_gram) >= best_score_length
                    ):
                        logger.debug(
                            "Found new best score %s with: %s %s",
                            ratio,
                            manufacturer,
                            model,
                        )
                        best_solution = (manufacturer, model, aircraft_type)
                        best_score = ratio
                        best_score_length = len(joined_gram)

        return best_solution

    def classify(
        self,
        offer_title: str,
    ) -> tuple[str | None, str | None, AircraftCategory | None]:
        """Try to get the correct manufacturer and model for an airplane offer

        :param offer_title: the title of the airplane offer
        :param spider: the spider name, used for fallback classification
        :return: triplet of: (manufacturer, model, aircraft_type)
        """
        tokens = self._build_tokens(offer_title)
        grams = self._build_grams(tokens)

        cutoff_score = 0.85

        for manufacturer, details in _manufacturers.items():
            models = details["models"]
            models = {
                key: value for (key, value) in models.items() if key in _aircraft_types
            }
            (found_manufacturer, model, aircraft_type) = self._classify_against_models(
                grams,
                models,
                cutoff_score,
                manufacturer=manufacturer,
            )
            if found_manufacturer is not None:
                return found_manufacturer, model, aircraft_type

        return None, None, None
