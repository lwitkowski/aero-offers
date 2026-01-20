import pytest
from assertpy import assert_that

from aerooffers.classifier.rule_based_classifier import RuleBasedClassifier
from aerooffers.offer import AircraftCategory

classifier = RuleBasedClassifier()


@pytest.mark.parametrize(
    (
        "offer_title",
        "expected_manufacturer",
        "expected_model",
        "expected_aircraft_type",
    ),
    [
        ("Stemme S6-RT", "Stemme", "S6-RT", AircraftCategory.tmg),
        ("DG 800 B", "DG Flugzeugbau", "DG-800B", AircraftCategory.glider),
        ("Vans Aircraft RV-6A", "Vans", "RV-6", AircraftCategory.airplane),
        ("ASK 21 D-6854", "Alexander Schleicher", "ASK 21", AircraftCategory.glider),
        ("ASW-24 WL", "Alexander Schleicher", "ASW 24", AircraftCategory.glider),
        ("DG 300", "DG Flugzeugbau", "DG-300", AircraftCategory.glider),
        (
            "TL Ultralight TL-3000 Sirius",
            "TL Ultralight",
            "TL-3000 Sirius",
            AircraftCategory.ultralight,
        ),
        ("Nimbus 3 25.5 m", "Schempp-Hirth", "Nimbus 3", AircraftCategory.glider),
        ("Nimbus 3 25,5m", "Schempp-Hirth", "Nimbus 3", AircraftCategory.glider),
        (
            "Nimbus 4DM, W-Nr. 50",
            "Schempp-Hirth",
            "Nimbus 4DM",
            AircraftCategory.glider,
        ),
        ("Ventus 2B", "Schempp-Hirth", "Ventus 2b", AircraftCategory.glider),
        ("JS1-C", "Jonker", "JS1 C", AircraftCategory.glider),
        # ("Cessna F-172 H ", "Cessna", "172", AircraftCategory.airplane),  # FAILING
        ("Cessna 172 D", "Cessna", "172", AircraftCategory.airplane),
        (
            "Ka 6 CR-Pe - Rarität in super Zustand",
            "Alexander Schleicher",
            "Ka6",
            AircraftCategory.glider,
        ),
        # ("Piper PA-46-500TP Meridian", None, None, AircraftCategory.airplane),  # FAILING
        (
            "Grumman American AA-5 Traveler",
            "Grumman American",
            "Grumman American AA-5",
            AircraftCategory.airplane,
        ),
        ("Club Libelle", "Glasflügel", "Club-Libelle", AircraftCategory.glider),
        ("Tecnam P-96 Golf", "Tecnam", "P96", AircraftCategory.airplane),
        ("ASG29E  18 M", "Alexander Schleicher", "ASG 29 E", AircraftCategory.glider),
        # ("Mooney M20F", None, None, AircraftCategory.airplane),  # FAILING
        ("Cessna 152", "Cessna", "152", AircraftCategory.airplane),
        # (
        #     "Eurocopter AS-365N Dauphin 2 project",
        #     None,
        #     None,
        #     AircraftCategory.helicopter,
        # ),  # FAILING
        (
            "Robin DR-315 Petit Prince",
            "Robin",
            "DR315 Petit Prince",
            AircraftCategory.airplane,
        ),
        ("Antares 20E", "Lange", "Antares 20E", AircraftCategory.glider),
        ("LS6a", "Rolladen Schneider", "LS6", AircraftCategory.glider),
        # ("Pipistrel Virus SW", None, None, AircraftCategory.ultralight),  # FAILING
        # ("Mooney M20K 252", None, None, AircraftCategory.airplane),  # FAILING
        # ("PZL-Okecie PZL-110 Koliber 150 A", None, None, AircraftCategory.airplane),  # FAILING
        # ("ARCUS M, MOTOR NEU", "Schempp-Hirth", "Arcus M", AircraftCategory.glider),  # FAILING
        ("SF25 C", "Scheibe", "SF 25", AircraftCategory.tmg),
        ("Wunderschöner G109b", "Grob", "G109b", AircraftCategory.tmg),
        (
            "Ka2B with closed trailer",
            "Alexander Schleicher",
            "Ka2",
            AircraftCategory.glider,
        ),
        (
            "Dg1000m engine 0h For sal",
            "DG Flugzeugbau",
            "DG-1000M",
            AircraftCategory.glider,
        ),
        ("Discus 2a", "Schempp-Hirth", "Discus 2a", AircraftCategory.glider),
        ("LS6", "Rolladen Schneider", "LS6", AircraftCategory.glider),
        ("DG-200", "DG Flugzeugbau", "DG-200", AircraftCategory.glider),
        ("SZD-36A Cobra", "PZL Bielsko", "SZD-36 Cobra", AircraftCategory.glider),
        ("ASW 15b for sale", "Alexander Schleicher", "ASW 15", AircraftCategory.glider),
        ("L_Spatz 55 m.geschl.Hänge", "Scheibe", "L-Spatz 55", AircraftCategory.glider),
        (
            "SZD-30 Pirat for Sale",
            "PZL Bielsko",
            "SZD-30 Pirat",
            AircraftCategory.glider,
        ),
        ("DG600M", "DG Flugzeugbau", "DG-600M", AircraftCategory.glider),
        ("Schleicher Ka6 CR", "Alexander Schleicher", "Ka6", AircraftCategory.glider),
        # ("AVO 68-R Samburo 100PS", None, None, AircraftCategory.glider),  # FAILING
        # (
        #     "Biete Rennlibelle H 301 B",
        #     "Glasflügel",
        #     "H-301 Libelle",
        #     AircraftCategory.glider,
        # ),  # FAILING
        ("ASW 22 BLE", "Alexander Schleicher", "ASW 22 BLE", AircraftCategory.glider),
        ("ASW 20 WL", "Alexander Schleicher", "ASW 20", AircraftCategory.glider),
        (
            "ASW19b - Ultra Complete -",
            "Alexander Schleicher",
            "ASW 19",
            AircraftCategory.glider,
        ),
        # ("Std. Jantar SZD41A", None, None, AircraftCategory.glider),  # FAILING
        # ("AS33es", "Alexander Schleicher", "AS 33", AircraftCategory.glider),  # FAILING
        # ("LS 4-a", "Rolladen Schneider", "LS4", AircraftCategory.glider),  # FAILING
        # ("SZD55-1 FOR SALE", "PZL Bielsko", "SZD-55-1 Promyk", AircraftCategory.glider),  # FAILING
        ("Diana2 FES", "Avionic", "Diana 2", AircraftCategory.glider),
        # (
        #     "Verkaufe ASH31 2018, s...",
        #     "Schempp-Hirth",
        #     "ASH 31 Mi",
        #     AircraftCategory.glider,
        # ),  # FAILING
        # ("HPH Shark 304 MS", "HPH", "304S SHARK", AircraftCategory.glider),  # FAILING
        # ("Schleppen und Reisen", None, None, AircraftCategory.glider),  # FAILING
        # ("H301 B Rennlibelle", "Glasflügel", "H-301 Libelle", AircraftCategory.glider),  # FAILING
        # ("KA-6cr PH-321", "Alexander Schleicher", "Ka6", AircraftCategory.glider),  # FAILING
    ],
)
def test_classify(
    offer_title: str,
    expected_manufacturer: str | None,
    expected_model: str | None,
    expected_aircraft_type: AircraftCategory,
) -> None:
    results = classifier.classify_many({"test_id": offer_title})
    result = results.get("test_id")

    assert_that(result).is_not_none()
    assert result is not None  # Type guard for mypy
    assert_that(result.manufacturer).is_equal_to(expected_manufacturer)
    assert_that(result.model).is_equal_to(expected_model)
    assert_that(result.aircraft_type).is_equal_to(expected_aircraft_type)
