"""TyrvingCalculator mot den låste fasiten (AP-005) og den låste regeltolkningen (AP-007)."""

import json
from pathlib import Path
from typing import Any

import pytest

from athletics_scoring.errors import (
    AmbiguousEventError,
    InvalidCombinedEventError,
    InvalidResultError,
    UnknownEventError,
    UnsupportedManualTimingError,
)
from athletics_scoring.models import CombinedEventInput, Gender, Result
from athletics_scoring.tyrving import TyrvingCalculator

ROOT = Path(__file__).resolve().parent.parent
CASES = json.loads((ROOT / "tests" / "fixtures" / "tyrving_cases.json").read_text("utf-8"))
RULES = json.loads((ROOT / "tests" / "fixtures" / "tyrving_rules.json").read_text("utf-8"))
ERRORS = {
    "invalid_result": InvalidResultError,
    "manual_timing_unsupported": UnsupportedManualTimingError,
}

calculator = TyrvingCalculator()


def _calculate(case: dict[str, Any], manual_timing: bool = False) -> Any:
    return calculator.calculate(
        case["event_id"],
        Gender(case["gender"]),
        str(case["age"]),
        Result(**case["result"], manual_timing=manual_timing),
        implement=case["implement"],
    )


def test_all_fixture_cases() -> None:
    """Alle 2472 caser fra oracle. Flyttallskanten testes mot eksakt verdi (beslutning AP-005)."""
    failures = []
    for case in CASES["cases"]:
        expected = case["float_edge"]["points_if_exact"] if "float_edge" in case else case["points"]
        points = _calculate(case).points
        if points != expected:
            failures.append((case["source"], case["result"], expected, points))
    assert not failures, failures[:10]
    assert len(CASES["cases"]) == 2472


@pytest.mark.parametrize("case", RULES["cases"], ids=lambda c: c["id"])
def test_rule_cases(case: dict[str, Any]) -> None:
    given = case["input"]
    score = _calculate(given, manual_timing=given["manual_timing"])
    assert score.points == case["points"]
    assert score.result_used == pytest.approx(case["effective_result"], abs=1e-9)


@pytest.mark.parametrize("case", RULES["error_cases"], ids=lambda c: c["id"])
def test_error_cases(case: dict[str, Any]) -> None:
    given = case["input"]
    with pytest.raises(ERRORS[case["error"]]):
        _calculate(given, manual_timing=given["manual_timing"])


def test_implement_required_when_ambiguous() -> None:
    result = Result(time_seconds=15.0)
    with pytest.raises(AmbiguousEventError, match="100,0cm/9,14m"):
        calculator.calculate("hurdles_110m", Gender.MALE, "17", result)
    score = calculator.calculate(
        "hurdles_110m", Gender.MALE, "17", result, implement="100,0cm / 9,14m"
    )
    assert score.implement == "100,0cm/9,14m"


def test_unknown_event_and_implement() -> None:
    with pytest.raises(UnknownEventError):
        calculator.calculate("sprint_400m", Gender.MALE, "10", Result(time_seconds=70.0))
    with pytest.raises(UnknownEventError):
        calculator.calculate(
            "shot_put", Gender.MALE, "15", Result(distance_meters=12.0), implement="7,26kg"
        )
    with pytest.raises(UnknownEventError):
        calculator.calculate("sprint_60m", Gender.MALE, "senior", Result(time_seconds=7.0))


def test_wrong_result_type_is_rejected() -> None:
    with pytest.raises(InvalidResultError):
        calculator.calculate("long_jump", Gender.FEMALE, "15", Result(time_seconds=5.0))
    with pytest.raises(InvalidResultError):
        calculator.calculate("sprint_60m", Gender.FEMALE, "15", Result(distance_meters=5.0))
    with pytest.raises(InvalidResultError):
        calculator.calculate(
            "long_jump", Gender.FEMALE, "15", Result(distance_meters=5.0, manual_timing=True)
        )


def test_score_result_explains_calculation() -> None:
    score = calculator.calculate("shot_put", Gender.MALE, "15", Result(distance_meters=10.0))
    assert score.points == 547
    assert score.formula_type == "three_interval"
    assert score.calculation_detail.endswith("= 547,6 → 547")
    labels = [step.label for step in score.calculation_steps]
    assert labels == ["eighty_percent", "points_raw", "points"]


def test_list_events_and_parameters() -> None:
    assert len(calculator.list_events()) == 560
    assert len(calculator.list_events(Gender.FEMALE, "15")) == len(
        [e for e in calculator.list_events() if e.gender is Gender.FEMALE and e.age_class == "15"]
    )
    assert calculator.get_parameters("sprint_60m", Gender.MALE, "15") == {
        "h1000": 7.55,
        "quotient": 2.7,
    }
    # PDF-en vinner der regnearket avviker (docs/KILDEAVVIK.md).
    assert calculator.get_parameters("distance_2000m", Gender.MALE, "19")["quotient"] == 0.45
    assert calculator.get_parameters("javelin", Gender.FEMALE, "15")["h1000"] == 38.0


def test_registry_integration() -> None:
    from athletics_scoring.registry import Registry

    registry = Registry()
    registry.register(calculator)
    assert registry.get("tyrving") is calculator


# --- AP-009: inndata-metadata og mangekamp under 15 år -------------------------------------------


def _info(event_id: str, gender: Gender, age: str) -> Any:
    return next(e for e in calculator.list_events(gender, age) if e.event_id == event_id)


def test_input_spec() -> None:
    sprint = _info("sprint_100m", Gender.MALE, "15").input
    assert (sprint.measure, sprint.resolution, sprint.uses_minutes) == ("time", 0.01, False)
    assert sprint.manual_timing_allowed
    assert not _info("sprint_40m", Gender.MALE, "10").input.manual_timing_allowed
    assert _info("hurdles_400m", Gender.MALE, "19").input.manual_timing_allowed
    middle = _info("middle_800m", Gender.MALE, "15").input
    assert (middle.resolution, middle.uses_minutes, middle.manual_timing_allowed) == (
        0.1,
        True,
        False,
    )
    jump = _info("long_jump", Gender.FEMALE, "15").input
    assert (jump.measure, jump.resolution, jump.manual_timing_allowed) == ("distance", 0.01, False)


def test_input_spec_matches_calculator_behaviour() -> None:
    """Der metadata sier at manuell tid er lov, må kalkulatoren godta det, og omvendt."""
    for info in calculator.list_events():
        if info.input.measure != "time" or info.input.uses_minutes:
            continue
        result = Result(time_seconds=60.0, manual_timing=True)
        if info.input.manual_timing_allowed:
            calculator.calculate(
                info.event_id, info.gender, info.age_class, result, implement=info.implement
            )
        else:
            with pytest.raises(UnsupportedManualTimingError):
                calculator.calculate(
                    info.event_id, info.gender, info.age_class, result, implement=info.implement
                )


def test_combined_sums_event_points() -> None:
    events = [
        CombinedEventInput("hurdles_60m", Result(time_seconds=10.5), implement="76,2cm/7,5m"),
        CombinedEventInput("high_jump", Result(distance_meters=1.52)),
        CombinedEventInput("shot_put", Result(distance_meters=11.2), implement="2kg"),
        CombinedEventInput("long_jump", Result(distance_meters=5.0)),
        CombinedEventInput("middle_600m", Result(time_minutes=1, time_seconds=42.0)),
    ]
    combined = calculator.calculate_combined(Gender.FEMALE, "13", events)
    single = [
        calculator.calculate(e.event_id, Gender.FEMALE, "13", e.result, e.implement).points
        for e in events
    ]
    assert [s.points for s in combined.events] == single
    assert combined.total == sum(single)
    assert combined.scoring_system == "tyrving"


def test_combined_rejects_invalid_input() -> None:
    with pytest.raises(InvalidCombinedEventError):
        calculator.calculate_combined(Gender.MALE, "13", [])
    with pytest.raises(InvalidCombinedEventError, match="World Athletics"):
        calculator.calculate_combined(
            Gender.MALE, "15", [CombinedEventInput("long_jump", Result(distance_meters=6.0))]
        )
    twice = [CombinedEventInput("long_jump", Result(distance_meters=5.0))] * 2
    with pytest.raises(InvalidCombinedEventError, match="long_jump"):
        calculator.calculate_combined(Gender.MALE, "13", twice)


# --- Rimelig område (brukerhjelp, beslutning 2026-09-26) ------------------------------------------


@pytest.mark.parametrize(
    ("event_id", "gender", "age", "expected"),
    [
        ("sprint_60m", Gender.MALE, "15", (4.53, 22.65)),
        ("shot_put", Gender.MALE, "15", (3.06, 24.48)),
        ("middle_800m", Gender.MALE, "15", (74.4, 372.0)),
        ("hurdles_60m", Gender.FEMALE, "13", (6.06, 30.3)),
    ],
)
def test_plausible_range(event_id: str, gender: Gender, age: str, expected: Any) -> None:
    spec = _info(event_id, gender, age).input
    assert (spec.plausible_min, spec.plausible_max) == pytest.approx(expected)


def test_plausible_range_contains_1000_level_for_all_events() -> None:
    for info in calculator.list_events():
        h1000 = calculator.get_parameters(
            info.event_id, info.gender, info.age_class, info.implement
        )["h1000"]
        assert info.input.plausible_min < h1000 < info.input.plausible_max, info


def test_score_flags_results_outside_plausible_range() -> None:
    def score(seconds: float) -> Any:
        return calculator.calculate(
            "hurdles_60m",
            Gender.FEMALE,
            "13",
            Result(time_seconds=seconds),
            implement="76,2cm/7,5m",
        )

    halfway = score(1.09)  # «1-0-9» underveis til 10,90
    assert not halfway.within_plausible_range
    assert halfway.points == 2711  # poeng beregnes likevel; flagget er brukerhjelp
    assert score(10.9).within_plausible_range
    assert score(10.9).points == 848
    assert not score(31.0).within_plausible_range
