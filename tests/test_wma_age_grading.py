"""WmaAgeGradingCalculator (AP-014) mot kontrolltallene og alle faktorene i WMA 2023 Age Factors."""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from athletics_scoring import default_registry
from athletics_scoring.errors import (
    InvalidResultError,
    UnknownEventError,
    UnsupportedManualTimingError,
)
from athletics_scoring.models import Gender, Result
from athletics_scoring.wma_age_grading import WmaAgeGradingCalculator

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = json.loads(
    (ROOT / "tests" / "fixtures" / "wma_age_factors_cases.json").read_text("utf-8")
)
M, F = Gender.MALE, Gender.FEMALE

calculator = WmaAgeGradingCalculator()


# --- kontrolltall (docs/active/AP-014-wma-age-grading.md) -------------------------------------


def test_women_45_100m() -> None:
    score = calculator.calculate("sprint_100m", F, "45", Result(time_seconds=13.50))
    assert score.parameters["age_factor"] == 0.9441
    assert score.result_used == 12.75  # 12,74535 rundet opp
    assert score.points == 0


def test_men_71_100m() -> None:
    score = calculator.calculate("sprint_100m", M, "71", Result(time_seconds=15.00))
    assert score.parameters["age_factor"] == 0.7803
    assert score.result_used == 11.71  # 11,7045 rundet opp


def test_women_45_60m_equals_five_year_factor() -> None:
    assert calculator.get_parameters("sprint_60m", F, "45") == {"age_factor": 0.9613}
    masters = default_registry().get("masters_combined_events", "2023")
    assert masters.get_parameters("sprint_60m", F, "W45")["age_factor"] == 0.9613


@pytest.mark.parametrize("age", ["29", "111", "45.5", "W45", ""])
def test_age_outside_table_is_rejected(age: str) -> None:
    with pytest.raises(UnknownEventError, match="BV-040"):
        calculator.calculate("sprint_100m", F, age, Result(time_seconds=13.5))


# --- beregningen --------------------------------------------------------------------------------


def test_field_events_round_down_to_centimetre() -> None:
    # Menn 60 år diskos 0,9653 (s. 13): 40,00 × 0,9653 = 38,612 → 38,61.
    score = calculator.calculate("discus", M, "60", Result(distance_meters=40.0))
    assert score.parameters["age_factor"] == 0.9653
    assert score.result_used == 38.61


def test_factor_above_one_for_running_is_used_as_is() -> None:
    # Menn 60 år lang hekk 1,1628 (s. 13): 50,00 × 1,1628 = 58,14.
    score = calculator.calculate("hurdles_long", M, "60", Result(time_seconds=50.0))
    assert score.result_used == 58.14


def test_minutes_are_included() -> None:
    score = calculator.calculate("marathon", M, "30", Result(time_minutes=180, time_seconds=0.01))
    assert score.result_used == 10800.01


def test_steps_refer_to_bv_and_source() -> None:
    score = calculator.calculate("sprint_100m", F, "45", Result(time_seconds=13.50))
    refs = {step.label: step.ref for step in score.calculation_steps}
    assert refs["age"] == "BV-040"
    assert refs["age_factor"] == "wma-2023-age-factors"
    assert refs["age_adjusted"] == "BV-041"
    assert refs["age_adjusted_rounded"] == "BV-042"
    assert "wma-2023-age-factors" in {doc["key"] for doc in calculator.sources()}
    assert score.calculation_detail == "13,5 × 0,9441 = 12,74535 → 12,75"


def test_invalid_input_is_rejected() -> None:
    with pytest.raises(UnsupportedManualTimingError):
        calculator.calculate("sprint_100m", M, "50", Result(time_seconds=13.0, manual_timing=True))
    with pytest.raises(InvalidResultError):
        calculator.calculate("sprint_100m", M, "50", Result(distance_meters=13.0))
    with pytest.raises(InvalidResultError):
        calculator.calculate("long_jump", M, "50", Result(time_seconds=5.0))
    with pytest.raises(InvalidResultError):
        calculator.calculate("long_jump", M, "50", Result(distance_meters=0.0))
    with pytest.raises(UnknownEventError):
        calculator.calculate("shot_put", M, "50", Result(distance_meters=12.0), implement="6kg")
    with pytest.raises(UnknownEventError):
        calculator.calculate("hurdles_110m", M, "50", Result(time_seconds=16.0))


def test_list_events() -> None:
    events = calculator.list_events(gender=F, age_class="45")
    assert len(events) == 30
    assert {e.age_class for e in events} == {"45"}
    assert len(calculator.list_events()) == 2 * 30 * 81
    marathon = next(e for e in events if e.event_id == "marathon")
    assert marathon.input.uses_minutes and not marathon.input.manual_timing_allowed
    assert calculator.ages()[0] == "30" and calculator.ages()[-1] == "110"


def test_registered() -> None:
    assert isinstance(default_registry().get("wma_age_grading"), WmaAgeGradingCalculator)


# --- fasit --------------------------------------------------------------------------------------


def test_all_fixture_cases() -> None:
    """Alle faktorene i PDF-en, lest av oraclet med ordkoordinater. Null avvik."""
    failures = []
    for gender, event_id, age, factor, example, adjusted in FIXTURE["cases"]:
        g = Gender(gender)
        measure = FIXTURE["meta"]["columns"]
        is_time = (
            next(c["measure"] for c in measure.values() if c["event_id"] == event_id) == "time"
        )
        result = (
            Result(time_seconds=float(example))
            if is_time
            else Result(distance_meters=float(example))
        )
        score = calculator.calculate(event_id, g, str(age), result)
        if score.parameters["age_factor"] != float(factor) or score.result_used != float(adjusted):
            failures.append((gender, event_id, age, factor, adjusted, score.result_used))
    assert not failures, (len(failures), failures[:10])


def test_fixture_covers_every_factor() -> None:
    meta = FIXTURE["meta"]
    assert meta["locked"] is False
    assert meta["case_count"] == len(FIXTURE["cases"]) == 2 * 30 * 81
    keys = {(g, e, a) for g, e, a, *_ in FIXTURE["cases"]}
    assert len(keys) == len(FIXTURE["cases"])
    assert {
        (e.gender.value, e.event_id, int(e.age_class)) for e in calculator.list_events()
    } == keys


def test_factor_digits_match_source_text() -> None:
    for _, _, _, factor, _, _ in FIXTURE["cases"]:
        assert re.fullmatch(r"\d\.\d{4}|\d{2}\.\d{4}", factor), factor


@pytest.mark.parametrize("script", ["extract_wma_age_factors.py", "oracle_wma_age_factors.py"])
def test_generated_files_are_reproducible(script: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
