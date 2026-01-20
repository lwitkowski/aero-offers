import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.metrics import distance
from nltk.util import ngrams

from aerooffers.classifier.classifiers import (
    ClassificationResult,
    load_all_models,
)
from aerooffers.my_logging import logging
from aerooffers.offer import AircraftCategory

nltk.download("stopwords")

logger = logging.getLogger("classifier")

_manufacturers: dict[str, dict] = load_all_models()

_aircraft_types_set = {
    AircraftCategory.glider,
    AircraftCategory.tmg,
    AircraftCategory.ultralight,
    AircraftCategory.airplane,
    AircraftCategory.helicopter,
}
# Pre-filter models dicts to only include valid aircraft types
_manufacturers_filtered: dict[str, dict[AircraftCategory, list[str]]] = {
    mfr: {k: v for k, v in details["models"].items() if k in _aircraft_types_set}
    for mfr, details in _manufacturers.items()
}
_stop_words_en = stopwords.words("english")
_stop_words_de = stopwords.words("german")


class RuleBasedClassifier:
    """Rule-based classifier using fuzzy string matching and pattern recognition.

    This is the original/legacy classifier implementation that uses:
    - N-gram matching
    - Jaro similarity
    - Pattern-based normalization
    """

    _DEFAULT_CUTOFF_SCORE = 0.85
    _is_dg_model_re = re.compile(r"^DG[0-9]{3,4}$")
    _is_binder_model_re = re.compile(r"^(EB28|EB29)$")
    _is_schleicher_model_re = re.compile(r"AS[H|W|K|G]\s?[0-9]{2}(\sMi)?$")

    def classify_many(self, titles: dict[str, str]) -> dict[str, ClassificationResult]:
        """Classify multiple aircraft offer titles in batch.

        :param titles: Dictionary mapping identifier to title
        :return: Dictionary mapping identifier to ClassificationResult
        """
        # Classify each title individually
        results: dict[str, ClassificationResult] = {}
        for key, title in titles.items():
            results[key] = self._classify(title)

        return results

    def _classify(self, offer_title: str) -> ClassificationResult:
        """Try to get the correct manufacturer and model for an airplane offer

        :param offer_title: the title of the airplane offer
        :return: ClassificationResult with aircraft_type, manufacturer, and model
        """
        grams = self._build_grams(offer_title)

        for manufacturer, models in _manufacturers_filtered.items():
            (aircraft_type, _, model) = self._classify_against_models(
                grams,
                models,
            )
            if model is not None:
                return ClassificationResult(
                    aircraft_type=aircraft_type,
                    manufacturer=manufacturer,
                    model=model,
                )

        return ClassificationResult.unknown()

    def _classify_against_models(  # noqa: C901
        self,
        grams: list[str],
        models: dict[AircraftCategory, list[str]],
    ) -> tuple[AircraftCategory | None, str | None, str | None]:
        best_score = 0.0
        best_model_length = 0
        best_gram_length = 0
        best_solution: tuple[AircraftCategory | None, str | None, str | None] = (
            None,
            None,
            None,
        )

        for aircraft_type in models.keys():
            for model in models[aircraft_type]:
                for gram in grams:
                    joined_gram = " ".join(gram)
                    test_str = model

                    if len(test_str) < 4 or len(joined_gram) < 4:
                        this_cutoff_score = 0.9
                    else:
                        this_cutoff_score = RuleBasedClassifier._DEFAULT_CUTOFF_SCORE

                    joined_gram_lower = joined_gram.lower()
                    test_str_lower = test_str.lower()

                    # Try exact match first
                    if joined_gram_lower == test_str_lower:
                        ratio = 1.0
                    else:
                        # Normalize spaces for comparison (AS33 vs AS 33)
                        normalized_gram = self._normalize_for_matching(joined_gram)
                        normalized_model = self._normalize_for_matching(test_str)

                        # Check normalized exact match
                        if normalized_gram == normalized_model:
                            ratio = 0.98  # Slightly lower than exact match
                        else:
                            # Check for substring match (e.g., "172" in "F-172")
                            # Only if model length is reasonable proportion of gram length
                            # Avoid matching "300" inside "3000" - require model is at least 80% of gram or vice versa
                            model_in_gram = test_str_lower in joined_gram_lower
                            gram_in_model = joined_gram_lower in test_str_lower
                            length_ratio = min(
                                len(test_str_lower), len(joined_gram_lower)
                            ) / max(len(test_str_lower), len(joined_gram_lower))

                            if (
                                len(test_str_lower) >= 3
                                and (model_in_gram or gram_in_model)
                                and length_ratio >= 0.7
                            ):
                                ratio = 0.95  # High score for substring match (above all cutoffs)
                            else:
                                # Fall back to Jaro similarity
                                ratio = distance.jaro_similarity(
                                    joined_gram_lower, test_str_lower
                                )

                    # Original condition: ratio >= best_score and len(joined_gram) >= best_score_length
                    # Enhanced: when scores are essentially equal, prefer longer model name
                    if (
                        ratio > this_cutoff_score
                        and ratio >= best_score
                        and len(joined_gram) >= best_gram_length
                    ):
                        # If scores are essentially equal, only update if model name is longer
                        scores_essentially_equal = abs(ratio - best_score) < 0.01
                        if scores_essentially_equal:
                            # Only update if this model is longer or gram is longer
                            if (
                                len(test_str) <= best_model_length
                                and len(joined_gram) <= best_gram_length
                            ):
                                continue  # Skip - same score but not longer
                        # Accept this match (better score or longer model/gram)
                        best_solution = (aircraft_type, None, model)
                        best_score = ratio
                        best_model_length = len(test_str)
                        best_gram_length = len(joined_gram)

        return best_solution

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

    def _build_tokens(self, input_text: str) -> list[str]:
        tokens = self._join_single_characters(self._tokenize(input_text))
        tokens = [word for word in tokens if word not in _stop_words_de]
        return [word for word in tokens if word not in _stop_words_en]

    def _build_grams(self, input_test: str) -> list[str]:
        tokens: list[str] = self._build_tokens(input_test)
        grams = list(ngrams(tokens, 1))
        bigrams = list(ngrams(tokens, 2))
        trigrams = list(ngrams(tokens, 3))
        # Keep original order: 1-grams, 2-grams, 3-grams
        # This ensures shorter matches are checked first, then longer ones can override
        return grams + bigrams + trigrams

    def _normalize_for_matching(self, text: str) -> str:
        """Normalize text for matching: lowercase, remove spaces."""
        return text.lower().replace(" ", "")


# For backward compatibility
ModelClassifier = RuleBasedClassifier
