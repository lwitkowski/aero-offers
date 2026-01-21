import json
import os
from collections.abc import Callable
from unittest.mock import MagicMock, patch

import pytest
from assertpy import assert_that

from aerooffers.classifier.gemini_llm_classifier import GeminiLLMClassifier
from aerooffers.offer import AircraftCategory, UnclassifiedOffer


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
    offers = [
        UnclassifiedOffer(
            id="offer1", title="Stemme S6-RT", category=AircraftCategory.tmg
        ),
        UnclassifiedOffer(
            id="offer2", title="DG 800 B", category=AircraftCategory.glider
        ),
        UnclassifiedOffer(
            id="offer3", title="Stemme S99", category=AircraftCategory.tmg
        ),
    ]
    # TMG offers response (offer1 and offer3)
    tmg_response_json = json.dumps(
        [
            {"manufacturer": "Stemme", "model": "S6-RT"},
            {"manufacturer": "Stemme", "model": "S99"},
        ]
    )
    # Glider offers response (offer2)
    glider_response_json = json.dumps(
        [
            {"manufacturer": "DG Flugzeugbau", "model": "DG-800B"},
        ]
    )
    classifier = GeminiLLMClassifier()

    # when
    call_count = 0

    def mock_generate_content(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # First call should be for TMG category (2 offers), second for glider (1 offer)
        if call_count == 1:
            return mock_gemini_response(tmg_response_json)
        else:
            return mock_gemini_response(glider_response_json)

    with patch.object(
        classifier._client.models,
        "generate_content",
        side_effect=mock_generate_content,
    ):
        results = classifier.classify_many(offers)

    # then
    # Verify that separate API calls were made for each category
    assert_that(call_count).is_equal_to(2)

    assert_that(results).is_not_none()
    assert_that(len(results)).is_equal_to(3)

    result1 = results.get("offer1")
    assert_that(result1).is_not_none()
    assert result1 is not None  # Type narrowing for mypy
    assert_that(result1.manufacturer).is_equal_to("Stemme")
    assert_that(result1.model).is_equal_to("S6-RT")

    result2 = results.get("offer2")
    assert_that(result2).is_not_none()
    assert result2 is not None  # Type narrowing for mypy
    assert_that(result2.manufacturer).is_equal_to("DG Flugzeugbau")
    assert_that(result2.model).is_equal_to("DG-800B")

    result3 = results.get("offer3")
    assert_that(result3).is_not_none()
    assert result3 is not None  # Type narrowing for mypy
    # Model "S99" is not in models.json, so it should be set to None
    assert_that(result3.manufacturer).is_equal_to("Stemme")
    assert_that(result3.model).is_none()


@pytest.mark.skip(reason="Only for exploratory testing (tweaking prompts etc.)")
def test_using_real_gemini_api() -> None:
    from aerooffers.utils import load_env

    load_env()

    active_test_cases = [
        # UnclassifiedOffer(id="1", title="PEGASE 90  mint condition", category=AircraftCategory.glider),
        # UnclassifiedOffer(id="2", title="Diana2 FES", category=AircraftCategory.glider),
        # UnclassifiedOffer(id="3", title="SZD55-1 FOR SALE", category=AircraftCategory.glider),
        UnclassifiedOffer(
            id="4", title="L1-f ready to fly", category=AircraftCategory.glider
        ),
        # UnclassifiedOffer(id="5", title="Stemme S10", category=AircraftCategory.glider),
    ]

    classifier = GeminiLLMClassifier()

    # when
    print(f"\nClassifying {len(active_test_cases)} titles in batch...")
    results = classifier.classify_many(active_test_cases)

    # then
    for offer in active_test_cases:
        result = results.get(offer.id)
        if result is None:
            result_msg = "❌ No result returned"
        else:
            result_msg = f"classified as {result.manufacturer} / {result.model}"

        print(f"[{offer.id}] ('{offer.title}'):  {result_msg}")
