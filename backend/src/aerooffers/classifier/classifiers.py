import json
import os
from dataclasses import dataclass
from typing import Protocol

from aerooffers.offer import UnclassifiedOffer


@dataclass(frozen=True)
class ClassificationResult:
    """Result of aircraft classification.

    :param manufacturer: The manufacturer name or None
    :param model: The model name or None
    """

    manufacturer: str | None
    model: str | None

    @classmethod
    def unknown(cls) -> "ClassificationResult":
        """Factory method to create an unknown classification result.

        :return: ClassificationResult with all fields set to None
        """
        return cls(
            manufacturer=None,
            model=None,
        )


class AircraftClassifier(Protocol):
    name: str
    """A concise identifier for this classifier."""

    def classify_many(
        self,
        offers: list[UnclassifiedOffer],
    ) -> dict[str, ClassificationResult]:
        """Classify multiple aircraft offer titles in batch.

        :param offers: List of UnclassifiedOffer objects to classify.
                       Category from offers can be used to optimize search
                       (e.g., only search glider models if category is glider).
                       Category must not be changed/overridden by classifier.
        :return: Dictionary mapping offer id to ClassificationResult
        """
        ...


def load_all_models() -> dict[str, dict]:
    """Load all aircraft models from models.json.

    :return: Dictionary mapping manufacturer names to their models
    """
    models_file = "models.json"
    models_path = os.path.dirname(os.path.realpath(__file__)) + os.sep + models_file
    with open(models_path) as json_file:
        manufacturers = json.load(json_file)
    return manufacturers
