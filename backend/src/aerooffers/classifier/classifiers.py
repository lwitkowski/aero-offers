import json
import os
from dataclasses import dataclass
from typing import Protocol

from aerooffers.offer import AircraftCategory


@dataclass(frozen=True)
class ClassificationResult:
    """Result of aircraft classification.

    :param aircraft_type: The type of aircraft (glider, airplane, etc.) or None
    :param manufacturer: The manufacturer name or None
    :param model: The model name or None
    """

    aircraft_type: AircraftCategory | None
    manufacturer: str | None
    model: str | None

    @classmethod
    def unknown(cls) -> "ClassificationResult":
        """Factory method to create an unknown classification result.

        :return: ClassificationResult with all fields set to None
        """
        return cls(
            aircraft_type=None,
            manufacturer=None,
            model=None,
        )


class AircraftClassifier(Protocol):
    def classify_many(self, titles: dict[str, str]) -> dict[str, ClassificationResult]:
        """Classify multiple aircraft offer titles in batch.

        :param titles: Dictionary mapping identifier to title
        :return: Dictionary mapping identifier to ClassificationResult
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
