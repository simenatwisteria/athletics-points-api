"""TyrvingCalculator mot den låste fasiten (AP-005) og den låste regeltolkningen (AP-007)."""

import json
from pathlib import Path
from typing import Any

import pytest

from athletics_scoring.errors import (
    AmbiguousEventError,
    InvalidResultError,
    UnknownEventError,
    UnsupportedManualTimingError,
)
from athletics_scoring.models import Gender, Result
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
