import json
import os
from collections.abc import Callable
from unittest.mock import MagicMock, patch

import pytest
from assertpy import assert_that

from aerooffers.classifier.gemini_llm_classifier import GeminiLLMClassifier
from aerooffers.offer import AircraftCategory


@pytest.fixture
def mock_gemini_response() -> Callable[[str], MagicMock]:
    def _create_mock_response(response_text: str) -> MagicMock:
        mock_response = MagicMock()
        mock_response.text = response_text
        return mock_response

    return _create_mock_response


@patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"})
def test_classify_many(mock_gemini_response: Callable[[str], MagicMock]) -> None:
    # given
    titles = {
        "offer1": "Stemme S6-RT",
        "offer2": "DG 800 B",
        "offer3": "Stemme S99",
    }
    api_response_json = json.dumps(
        [
            {"manufacturer": "Stemme", "model": "S6-RT", "aircraft_type": "tmg"},
            {
                "manufacturer": "DG Flugzeugbau",
                "model": "DG-800B",
                "aircraft_type": "glider",
            },
            {
                "manufacturer": "Stemme",
                "model": "S99",
                "aircraft_type": "tmg",
            },
        ]
    )
    classifier = GeminiLLMClassifier()

    # when
    with patch.object(
        classifier._client.models,
        "generate_content",
        return_value=mock_gemini_response(api_response_json),
    ):
        results = classifier.classify_many(titles)

    # then
    assert_that(results).is_not_none()
    assert_that(len(results)).is_equal_to(3)

    result1 = results.get("offer1")
    assert_that(result1).is_not_none()
    assert result1 is not None  # Type narrowing for mypy
    assert_that(result1.manufacturer).is_equal_to("Stemme")
    assert_that(result1.model).is_equal_to("S6-RT")
    assert_that(result1.aircraft_type).is_equal_to(AircraftCategory.tmg)

    result2 = results.get("offer2")
    assert_that(result2).is_not_none()
    assert result2 is not None  # Type narrowing for mypy
    assert_that(result2.manufacturer).is_equal_to("DG Flugzeugbau")
    assert_that(result2.model).is_equal_to("DG-800B")
    assert_that(result2.aircraft_type).is_equal_to(AircraftCategory.glider)

    result3 = results.get("offer3")
    assert_that(result3).is_not_none()
    assert result3 is not None  # Type narrowing for mypy
    # Model "S99" is not in models.json, so it should be set to None
    assert_that(result3.manufacturer).is_equal_to("Stemme")
    assert_that(result3.model).is_none()
    assert_that(result3.aircraft_type).is_equal_to(AircraftCategory.tmg)


@pytest.mark.skip(reason="Only for exploratory testing (tweaking prompts etc.)")
def test_using_real_gemini_api() -> None:
    from aerooffers.utils import load_env

    load_env()

    active_test_cases: dict[str, str] = {
        # "1": "PEGASE 90  mint condition",
        # "2": "Diana2 FES",
        # "3": "SZD55-1 FOR SALE",
        "4": "L1-f ready to fly",
        # "5": "Stemme S10",
    }

    classifier = GeminiLLMClassifier()

    # when
    print(f"\nClassifying {len(active_test_cases)} titles in batch...")
    results = classifier.classify_many(active_test_cases)

    # then
    for i, title in active_test_cases.items():
        result = results.get(i)
        if result is None:
            result_msg = "❌ No result returned"
        else:
            result_msg = f"classified as {result.aircraft_type} / {result.manufacturer} / {result.model}"

        print(f"[{i}] ('{title}'):  {result_msg}")
