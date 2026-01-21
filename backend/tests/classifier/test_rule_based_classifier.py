import pytest
from assertpy import assert_that

from aerooffers.classifier.rule_based_classifier import RuleBasedClassifier
from aerooffers.offer import AircraftCategory, UnclassifiedOffer

classifier = RuleBasedClassifier()


@pytest.mark.parametrize(
    (
        "offer_title",
        "category",
        "expected_manufacturer",
        "expected_model",
    ),
    [
        ("Stemme S6-RT", AircraftCategory.tmg, "Stemme", "S6-RT"),
        ("DG 800 B", AircraftCategory.glider, "DG Flugzeugbau", "DG-800B"),
        ("Vans Aircraft RV-6A", AircraftCategory.airplane, "Vans", "RV-6"),
        ("ASK 21 D-6854", AircraftCategory.glider, "Alexander Schleicher", "ASK 21"),
        ("ASW-24 WL", AircraftCategory.glider, "Alexander Schleicher", "ASW 24"),
        ("DG 300", AircraftCategory.glider, "DG Flugzeugbau", "DG-300"),
        (
            "TL Ultralight TL-3000 Sirius",
            AircraftCategory.ultralight,
            "TL Ultralight",
            "TL-3000 Sirius",
        ),
        ("Nimbus 3 25.5 m", AircraftCategory.glider, "Schempp-Hirth", "Nimbus 3"),
        ("Nimbus 3 25,5m", AircraftCategory.glider, "Schempp-Hirth", "Nimbus 3"),
        (
            "Nimbus 4DM, W-Nr. 50",
            AircraftCategory.glider,
            "Schempp-Hirth",
            "Nimbus 4DM",
        ),
        ("Ventus 2B", AircraftCategory.glider, "Schempp-Hirth", "Ventus 2b"),
        ("JS1-C", AircraftCategory.glider, "Jonker", "JS1 C"),
        # ("Cessna F-172 H ", AircraftCategory.airplane, "Cessna", "172"),  # FAILING
        ("Cessna 172 D", AircraftCategory.airplane, "Cessna", "172"),
        (
            "Ka 6 CR-Pe - Rarität in super Zustand",
            AircraftCategory.glider,
            "Alexander Schleicher",
            "Ka6",
        ),
        # ("Piper PA-46-500TP Meridian", AircraftCategory.airplane, None, None),  # FAILING
        (
            "Grumman American AA-5 Traveler",
            AircraftCategory.airplane,
            "Grumman American",
            "Grumman American AA-5",
        ),
        ("Club Libelle", AircraftCategory.glider, "Glasflügel", "Club-Libelle"),
        ("Tecnam P-96 Golf", AircraftCategory.airplane, "Tecnam", "P96"),
        ("ASG29E  18 M", AircraftCategory.glider, "Alexander Schleicher", "ASG 29 E"),
        # ("Mooney M20F", AircraftCategory.airplane, None, None),  # FAILING
        ("Cessna 152", AircraftCategory.airplane, "Cessna", "152"),
        # (
        #     "Eurocopter AS-365N Dauphin 2 project",
        #     AircraftCategory.helicopter,
        #     None,
        #     None,
        # ),  # FAILING
        (
            "Robin DR-315 Petit Prince",
            AircraftCategory.airplane,
            "Robin",
            "DR315 Petit Prince",
        ),
        ("Antares 20E", AircraftCategory.glider, "Lange", "Antares 20E"),
        ("LS6a", AircraftCategory.glider, "Rolladen Schneider", "LS6"),
        # ("Pipistrel Virus SW", AircraftCategory.ultralight, None, None),  # FAILING
        # ("Mooney M20K 252", AircraftCategory.airplane, None, None),  # FAILING
        # ("PZL-Okecie PZL-110 Koliber 150 A", AircraftCategory.airplane, None, None),  # FAILING
        # ("ARCUS M, MOTOR NEU", AircraftCategory.glider, "Schempp-Hirth", "Arcus M"),  # FAILING
        ("SF25 C", AircraftCategory.tmg, "Scheibe", "SF 25"),
        ("Wunderschöner G109b", AircraftCategory.tmg, "Grob", "G109b"),
        (
            "Ka2B with closed trailer",
            AircraftCategory.glider,
            "Alexander Schleicher",
            "Ka2",
        ),
        (
            "Dg1000m engine 0h For sal",
            AircraftCategory.glider,
            "DG Flugzeugbau",
            "DG-1000M",
        ),
        ("Discus 2a", AircraftCategory.glider, "Schempp-Hirth", "Discus 2a"),
        ("LS6", AircraftCategory.glider, "Rolladen Schneider", "LS6"),
        ("DG-200", AircraftCategory.glider, "DG Flugzeugbau", "DG-200"),
        ("SZD-36A Cobra", AircraftCategory.glider, "PZL Bielsko", "SZD-36 Cobra"),
        ("ASW 15b for sale", AircraftCategory.glider, "Alexander Schleicher", "ASW 15"),
        ("L_Spatz 55 m.geschl.Hänge", AircraftCategory.glider, "Scheibe", "L-Spatz 55"),
        (
            "SZD-30 Pirat for Sale",
            AircraftCategory.glider,
            "PZL Bielsko",
            "SZD-30 Pirat",
        ),
        ("DG600M", AircraftCategory.glider, "DG Flugzeugbau", "DG-600M"),
        ("Schleicher Ka6 CR", AircraftCategory.glider, "Alexander Schleicher", "Ka6"),
        # ("AVO 68-R Samburo 100PS", AircraftCategory.glider, None, None),  # FAILING
        # (
        #     "Biete Rennlibelle H 301 B",
        #     AircraftCategory.glider,
        #     "Glasflügel",
        #     "H-301 Libelle",
        # ),  # FAILING
        ("ASW 22 BLE", AircraftCategory.glider, "Alexander Schleicher", "ASW 22 BLE"),
        ("ASW 20 WL", AircraftCategory.glider, "Alexander Schleicher", "ASW 20"),
        (
            "ASW19b - Ultra Complete -",
            AircraftCategory.glider,
            "Alexander Schleicher",
            "ASW 19",
        ),
        # ("Std. Jantar SZD41A", AircraftCategory.glider, None, None),  # FAILING
        # ("AS33es", AircraftCategory.glider, "Alexander Schleicher", "AS 33"),  # FAILING
        # ("LS 4-a", AircraftCategory.glider, "Rolladen Schneider", "LS4"),  # FAILING
        # ("SZD55-1 FOR SALE", AircraftCategory.glider, "PZL Bielsko", "SZD-55-1 Promyk"),  # FAILING
        ("Diana2 FES", AircraftCategory.glider, "Avionic", "Diana 2"),
        # (
        #     "Verkaufe ASH31 2018, s...",
        #     AircraftCategory.glider,
        #     "Schempp-Hirth",
        #     "ASH 31 Mi",
        # ),  # FAILING
        # ("HPH Shark 304 MS", AircraftCategory.glider, "HPH", "304S SHARK"),  # FAILING
        # ("Schleppen und Reisen", AircraftCategory.glider, None, None),  # FAILING
        # ("H301 B Rennlibelle", AircraftCategory.glider, "Glasflügel", "H-301 Libelle"),  # FAILING
        # ("KA-6cr PH-321", AircraftCategory.glider, "Alexander Schleicher", "Ka6"),  # FAILING
    ],
)
def test_classify(
    offer_title: str,
    category: AircraftCategory,
    expected_manufacturer: str | None,
    expected_model: str | None,
) -> None:
    offers = [UnclassifiedOffer(id="test_id", title=offer_title, category=category)]
    results = classifier.classify_many(offers)
    result = results.get("test_id")

    assert_that(result).is_not_none()
    assert result is not None  # Type guard for mypy
    assert_that(result.manufacturer).is_equal_to(expected_manufacturer)
    assert_that(result.model).is_equal_to(expected_model)
