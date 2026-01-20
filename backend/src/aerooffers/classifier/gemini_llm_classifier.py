import json
import os

from google import genai
from google.genai.types import GenerateContentConfig

from aerooffers.classifier.classifiers import (
    ClassificationResult,
    load_all_models,
)
from aerooffers.my_logging import logging
from aerooffers.offer import AircraftCategory

logger = logging.getLogger("classifier.gemini_llm")

# Valid aircraft types for classification (exclude "unknown")
_VALID_AIRCRAFT_TYPES = [AircraftCategory.glider, AircraftCategory.tmg]


class GeminiLLMClassifier:
    """LLM-based classifier using Google Gemini API.

    Implements the AircraftClassifier protocol.
    """

    name: str = "gemini_llm"
    """A concise identifier for this classifier."""

    _DEFAULT_MODEL = "gemini-2.5-flash-lite"
    _TEMPERATURE = 0

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable required. "
                "Get your API key from https://aistudio.google.com/app/apikey"
            )
        self._client = genai.Client(api_key=api_key)
        self._models_data = load_all_models()
        self._models_list_text = self._build_models_list_text()

    def _build_models_list_text(self) -> str:
        """Build formatted text listing all known manufacturers and models."""
        lines: list[str] = ["KNOWN MANUFACTURERS AND MODELS:", ""]

        for manufacturer, details in sorted(self._models_data.items()):
            models_by_type = details["models"]
            manufacturer_lines: list[str] = list()
            for aircraft_type in _VALID_AIRCRAFT_TYPES:
                if aircraft_type in models_by_type and models_by_type[aircraft_type]:
                    models = models_by_type[aircraft_type]
                    models_str = ", ".join(f'"{model}"' for model in sorted(models))
                    manufacturer_lines.append(f"  {aircraft_type}: {models_str}")

            if len(manufacturer_lines) > 0:
                lines.append(f"Manufacturer: {manufacturer}")
                lines += manufacturer_lines
                lines.append("")

        return "\n".join(lines)

    def _build_system_prompt(self) -> str:
        """Build system prompt with examples and known models."""
        return f"""You are an expert classifying gliders and TMGs based on sell ads titles.

Your task is to extract:
1. manufacturer - must match exactly one of the known manufacturers (case-sensitive)
2. model - must match exactly one of the known models for that manufacturer (case-sensitive)
3. aircraft_type - one of: {", ".join(_VALID_AIRCRAFT_TYPES)}

IMPORTANT RULES:
- manufacturer and model must match EXACTLY from the list below (case-sensitive)
- If you cannot find an exact match, return null for manufacturer and/or model
- Always determine aircraft_type if possible (even if manufacturer/model is null)
- Handle variations like "DG 800 B" → manufacturer: "DG Flugzeugbau", model: "DG-800B"
- Handle spaces/hyphens: "ASK 21" = "ASK 21" (exact match required)
- Extract core model numbers: "Cessna F-172 H" → manufacturer: "Cessna", model: "172"
- You will receive MULTIPLE titles as separate prompts. Return an array of results, one for each title in the same order as received.
Each result should follow the format below.

EXAMPLES:
- "Stemme S6-RT" → manufacturer: "Stemme", model: "S6-RT", aircraft_type: "tmg"
- "DG 800 B" → manufacturer: "DG Flugzeugbau", model: "DG-800B", aircraft_type: "glider"
- "ASK 21 D-6854" → manufacturer: "Alexander Schleicher", model: "ASK 21", aircraft_type: "glider"
- "Ka 6 CR-Pe" → manufacturer: "Alexander Schleicher", model: "Ka6", aircraft_type: "glider"

{self._models_list_text}

Remember: manufacturer and model must match EXACTLY from the list above."""

    def _build_response_schema(self) -> dict:
        """Build JSON schema for classification results array."""
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "manufacturer": {
                        "type": "string",
                        "nullable": True,
                        "description": "Exact manufacturer name from the known list, or null",
                    },
                    "model": {
                        "type": "string",
                        "nullable": True,
                        "description": "Exact model name from the known list for that manufacturer, or null",
                    },
                    "aircraft_type": {
                        "type": "string",
                        "enum": _VALID_AIRCRAFT_TYPES,
                        "description": "Type of aircraft",
                    },
                },
                "required": ["manufacturer", "model", "aircraft_type"],
            },
        }

    def classify_many(self, titles: dict[str, str]) -> dict[str, ClassificationResult]:
        """Classify multiple aircraft offer titles in batch using a single API call.

        Each title is sent as a separate prompt part in one API call.

        :param titles: Dictionary mapping identifier to title
        :return: Dictionary mapping identifier to ClassificationResult
        """
        if not titles:
            return {}

        keys = list(titles.keys())
        titles_list = list(titles.values())

        # Build multiple prompts - one per title
        # Each title becomes a separate content part in the API call
        prompts = [
            f"Extract aircraft information from this title: {title}"
            for title in titles_list
        ]

        response = self._client.models.generate_content(
            model=self._DEFAULT_MODEL,
            contents=prompts,
            config=GenerateContentConfig(
                system_instruction=self._build_system_prompt(),
                response_mime_type="application/json",
                response_schema=self._build_response_schema(),
                temperature=self._TEMPERATURE,
            ),
        )

        if response.text is None:
            error_msg = "Gemini API returned None response text"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return self._process_api_response(response.text, keys, titles_list)

    def _process_api_response(
        self, response_text: str, keys: list[str], titles_list: list[str]
    ) -> dict[str, ClassificationResult]:
        try:
            results_array = json.loads(response_text)
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse Gemini API response as JSON: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        if not isinstance(results_array, list):
            error_msg = f"Expected array of results, got: {type(results_array)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        results: dict[str, ClassificationResult] = {}
        for i, result in enumerate(results_array):
            if i >= len(keys):
                break

            key = keys[i]
            title = titles_list[i]

            classification_result = self._validate_and_normalize_result(result, title)
            logger.debug(f"Gemini classified '{title}' as {classification_result}")
            results[key] = classification_result

        # Fill in missing results if we got fewer results than expected
        if len(results) < len(keys):
            logger.warning(
                f"Expected {len(keys)} results, got {len(results)}. "
                f"Filling missing results with unknown classification."
            )
            for key in keys:
                if key not in results:
                    results[key] = ClassificationResult.unknown()

        return results

    def _validate_and_normalize_result(
        self, result: dict, title: str
    ) -> ClassificationResult:
        """Validate and normalize a classification result.

        :param result: Raw result from API
        :param title: Original title being classified
        :return: Tuple of (manufacturer, model, aircraft_type)
        """
        manufacturer = result.get("manufacturer")
        model = result.get("model")

        if manufacturer:
            # Verify manufacturer exists and model is valid for that manufacturer
            if manufacturer not in self._models_data:
                logger.warning(
                    f"Gemini returned unknown manufacturer: {manufacturer} for '{title}'"
                )
                manufacturer = None
                model = None
            elif model:
                # Verify model exists for this manufacturer
                models_by_type = self._models_data[manufacturer].get("models", {})
                all_models = [
                    m for models_list in models_by_type.values() for m in models_list
                ]
                if model not in all_models:
                    logger.warning(
                        f"Gemini returned unknown model '{model}' for manufacturer "
                        f"'{manufacturer}' in '{title}'"
                    )
                    model = None

        aircraft_type_str = result.get("aircraft_type")
        category = AircraftCategory(aircraft_type_str) if aircraft_type_str else None

        return ClassificationResult(category, manufacturer, model)
