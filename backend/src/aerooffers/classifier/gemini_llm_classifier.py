import json
import os

from google import genai
from google.genai.types import GenerateContentConfig

from aerooffers.classifier.classifiers import (
    ClassificationResult,
    load_all_models,
)
from aerooffers.my_logging import logging
from aerooffers.offer import AircraftCategory, UnclassifiedOffer

logger = logging.getLogger("classifier.gemini_llm")


class GeminiLLMClassifier:
    """LLM-based classifier using Google Gemini API."""

    name: str = "gemini_llm"

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

    def _get_category_examples(self, category: AircraftCategory) -> str:
        """Get category-specific examples for the system prompt."""
        examples_by_category: dict[AircraftCategory, list[str]] = {
            AircraftCategory.glider: [
                '"DG 800 B" → manufacturer: "DG Flugzeugbau", model: "DG-800B"',
                '"ASK 21 D-6854" → manufacturer: "Alexander Schleicher", model: "ASK 21"',
                '"Ka 6 CR-Pe" → manufacturer: "Alexander Schleicher", model: "Ka6"',
                '"Nimbus 3 25.5 m" → manufacturer: "Schempp-Hirth", model: "Nimbus 3"',
            ],
            AircraftCategory.tmg: [
                '"Stemme S6-RT" → manufacturer: "Stemme", model: "S6-RT"',
                '"G109b" → manufacturer: "Grob", model: "G109b"',
                '"SF 25 C" → manufacturer: "Scheibe", model: "SF 25"',
            ],
            AircraftCategory.airplane: [
                '"Cessna F-172 H" → manufacturer: "Cessna", model: "172"',
                '"Piper PA-28" → manufacturer: "Piper", model: "PA-28"',
            ],
            AircraftCategory.ultralight: [
                '"TL-3000 Sirius" → manufacturer: "TL Ultralight", model: "TL-3000 Sirius"',
                '"Pipistrel Virus" → manufacturer: "Pipistrel", model: "Virus"',
            ],
            AircraftCategory.helicopter: [
                '"Robinson R44" → manufacturer: "Robinson Helicopter", model: "R44"',
            ],
        }

        examples = examples_by_category.get(category, [])

        return "\n".join(f"- {example}" for example in examples)

    def _build_models_list_text_for_category(self, category: AircraftCategory) -> str:
        """Build formatted text listing manufacturers and models for a specific category."""
        lines: list[str] = ["KNOWN MANUFACTURERS AND MODELS:", ""]

        for manufacturer, details in sorted(self._models_data.items()):
            models_by_type = details["models"]
            if category in models_by_type and models_by_type[category]:
                models = models_by_type[category]
                models_str = ", ".join(f"{model}" for model in sorted(models))
                lines.append(f"{manufacturer}: {models_str}")

        return "\n".join(lines)

    def _build_system_prompt_for_category(self, category: AircraftCategory) -> str:
        """Build system prompt optimized for a specific category."""
        category_name = category.value
        models_list_text = self._build_models_list_text_for_category(category)
        examples = self._get_category_examples(category)

        return f"""You are an expert classifying aircraft of type '{category_name}' based on sell ads titles.

Your task is to find - for given title - best match:
1. manufacturer - must match exactly one of the known manufacturers (case-sensitive)
2. model - must match exactly one of the known models for that manufacturer (case-sensitive)

IMPORTANT RULES:
- below you are given a list of available models for each manufacturer, in format `manufacturer: model1, model2, ...`
- manufacturer and model must match EXACTLY from the list below (case-sensitive)
- If you cannot find an exact match, return null for manufacturer and/or model
- Handle variations like "DG 800 B" → manufacturer: "DG Flugzeugbau", model: "DG-800B"
- Handle spaces/hyphens: "ASK 21" = "ASK 21" (exact match required)
- Extract core model numbers: "Cessna F-172 H" → manufacturer: "Cessna", model: "172"
- You will receive MULTIPLE titles as separate prompts. Return an array of results, one for each title in the same order as received.
Each result should follow the format below.

EXAMPLES:
{examples}

{models_list_text}

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
                },
                "required": ["manufacturer", "model"],
            },
        }

    def classify_many(
        self,
        offers: list[UnclassifiedOffer],
    ) -> dict[str, ClassificationResult]:
        if not offers:
            return {}

        # Group offers by category
        offers_by_category: dict[AircraftCategory, list[UnclassifiedOffer]] = {}
        for offer in offers:
            category = offer.category
            if category not in offers_by_category:
                offers_by_category[category] = []
            offers_by_category[category].append(offer)

        # Log summary of categories to be processed
        category_summary = ", ".join(
            f"{category.value}: {len(category_offers)}"
            for category, category_offers in sorted(offers_by_category.items())
        )
        logger.info(
            f"Classifying {len(offers)} offers grouped by category: {category_summary}"
        )

        # Process each category group separately
        all_results: dict[str, ClassificationResult] = {}
        for category, category_offers in offers_by_category.items():
            category_results = self._classify_category_group(category, category_offers)
            all_results.update(category_results)

        return all_results

    def _classify_category_group(
        self,
        category: AircraftCategory,
        offers: list[UnclassifiedOffer],
    ) -> dict[str, ClassificationResult]:
        """Classify a group of offers that all belong to the same category."""
        if not offers:
            return {}

        ids = [offer.id for offer in offers]
        titles_list = [offer.title for offer in offers]

        # Build prompts - one per title
        prompts = [
            f"Identify aircraft from this title: {title}" for title in titles_list
        ]

        # Use category-specific system prompt
        system_prompt = self._build_system_prompt_for_category(category)

        response = self._client.models.generate_content(
            model=self._DEFAULT_MODEL,
            contents=prompts,
            config=GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=self._build_response_schema(),
                temperature=self._TEMPERATURE,
            ),
        )

        if response.text is None:
            error_msg = "Gemini API returned None response text"
            logger.error(error_msg)
            raise ValueError(error_msg)

        categories_dict = {offer_id: category for offer_id in ids}
        return self._process_api_response(
            response.text, ids, titles_list, categories_dict
        )

    def _process_api_response(
        self,
        response_text: str,
        offer_ids: list[str],
        titles_list: list[str],
        categories: dict[str, AircraftCategory],
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
            if i >= len(offer_ids):
                break

            offer_id = offer_ids[i]
            title = titles_list[i]
            category = categories.get(offer_id)
            if category is None:
                logger.warning(
                    f"No category found for offer {offer_id}, using unknown as fallback"
                )
                category = AircraftCategory.unknown

            classification_result = self._validate_and_normalize_result(
                result, title, category
            )
            logger.debug(f"Gemini classified '{title}' as {classification_result}")
            results[offer_id] = classification_result

        # Fill in missing results if we got fewer results than expected
        if len(results) < len(offer_ids):
            logger.warning(
                f"Expected {len(offer_ids)} results, got {len(results)}. "
                f"Filling missing results with unknown classification."
            )
            for offer_id in offer_ids:
                if offer_id not in results:
                    results[offer_id] = ClassificationResult.unknown()

        return results

    def _validate_and_normalize_result(
        self,
        result: dict,
        title: str,
        category: AircraftCategory,
    ) -> ClassificationResult:
        """Validate and normalize a classification result."""
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
                # If category is provided, only check models in that category
                if category:
                    models_to_check = models_by_type.get(category, [])
                    if model not in models_to_check:
                        logger.warning(
                            f"Gemini returned model '{model}' for manufacturer "
                            f"'{manufacturer}' that doesn't match category '{category}' in '{title}'"
                        )
                        model = None
                else:
                    # Check all models across all categories
                    all_models = [
                        m
                        for models_list in models_by_type.values()
                        for m in models_list
                    ]
                    if model not in all_models:
                        logger.warning(
                            f"Gemini returned unknown model '{model}' for manufacturer "
                            f"'{manufacturer}' in '{title}'"
                        )
                        model = None

        return ClassificationResult(manufacturer=manufacturer, model=model)
