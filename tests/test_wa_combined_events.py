"""CombinedEventsCalculator (AP-012) mot kontrolltallene og seniorkolonnen i NFIF-tabellene."""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from athletics_scoring import default_registry
from athletics_scoring.errors import (
    InvalidCombinedEventError,
    InvalidResultError,
    UnknownEventError,
)
from athletics_scoring.models import CombinedEventInput, Gender, Result
from athletics_scoring.wa_combined_events import CombinedEventsCalculator

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = json.loads(
    (ROOT / "tests" / "fixtures" / "wa_combined_events_cases.json").read_text("utf-8")
)
# Én case per rad: arkets felles felt pluss [radnummer, resultat i arket, result, poeng].
CASES = [
    {**{k: v for k, v in sheet.items() if k != "cases"}, "row": row, "cell": cell,
     "result": result, "points": points}
    for sheet in FIXTURE["sheets"]
    for row, cell, result, points in sheet["cases"]
]  # fmt: skip
M, F = Gender.MALE, Gender.FEMALE

calculator = CombinedEventsCalculator()

# Kontrolltallene i docs/ferdig/AP-012-wa-combined-events.md.
CONTROL = [
    ("IAAF s. 23", M, "senior", "sprint_100m", Result(time_seconds=10.40), 999),
    ("IAAF s. 23 manuell", M, "senior", "sprint_100m",
     Result(time_seconds=10.4, manual_timing=True), 942),
    ("IAAF s. 166 60 m manuell (BV-024)", M, "senior", "sprint_60m",
     Result(time_seconds=6.0, manual_timing=True), 1170),
    ("M 200 m", M, "senior", "sprint_200m", Result(time_seconds=23.79), 712),
    ("M 1500 m uten tillegg", M, "senior", "middle_1500m",
     Result(time_minutes=4, time_seconds=45.8, manual_timing=True), 644),
    ("M lengde", M, "senior", "long_jump", Result(distance_meters=5.17), 415),
    ("M diskos", M, "senior", "discus", Result(distance_meters=16.33), 204),
    ("M spyd", M, "senior", "javelin", Result(distance_meters=32.80), 339),
    ("K 200 m", F, "senior", "sprint_200m", Result(time_seconds=26.77), 731),
    ("K 800 m", F, "senior", "middle_800m", Result(time_minutes=2, time_seconds=54.1), 422),
    ("IAAF s. 159 K 1500 m", F, "senior", "middle_1500m",
     Result(time_minutes=4, time_seconds=34.99), 1000),
    ("J15 600 m", F, "J15", "middle_600m", Result(time_minutes=1, time_seconds=40.0), 843),
    ("J15 80 m hekk", F, "J15", "hurdles_80m", Result(time_seconds=12.0), 835),
    ("G15 800 m inne", M, "G15", "middle_800m", Result(time_minutes=2, time_seconds=10.0), 765),
    ("G15 100 m hekk", M, "G15", "hurdles_100m", Result(time_seconds=14.0), 824),
]  # fmt: skip


@pytest.mark.parametrize(
    ("gender", "age_class", "event_id", "result", "expected"),
    [c[1:] for c in CONTROL],
    ids=[c[0] for c in CONTROL],
)
def test_control_numbers(
    gender: Gender, age_class: str, event_id: str, result: Result, expected: int
) -> None:
    assert calculator.calculate(event_id, gender, age_class, result).points == expected


def test_all_fixture_cases() -> None:
    """Hele seniorkolonnen i NFIF-arkene, unntatt 60 m-manuell og 80-100mHK. Null avvik."""
    failures = []
    for case in CASES:
        result = Result(**case["result"], manual_timing=case["manual_timing"])
        points = calculator.calculate(
            case["event_id"], Gender(case["gender"]), case["age_class"], result
        ).points
        if points != case["points"]:
            failures.append((case["sheet"], case["row"], case["cell"], case["points"], points))
    assert not failures, failures[:10]


def test_fixture_covers_the_expected_rows() -> None:
    cases = CASES
    auto = Counter(c["gender"] for c in cases if not c["manual_timing"])
    assert auto == {"M": 15051, "F": 13929}
    assert sum(c["manual_timing"] for c in cases) == 1502
    assert FIXTURE["meta"]["case_count"] == len(cases) == 30482
    assert FIXTURE["meta"]["locked"] is False
    covered = {(c["gender"], c["event_id"]) for c in cases}
    standard = {(e.gender.value, e.event_id) for e in calculator.list_events(age_class="senior")}
    # Kvinner 100 m hekk har ingen seniorkolonne i NFIF-arkene (80-100mHK starter på W40).
    assert standard - covered == {("F", "hurdles_100m")}


def test_fixture_is_reproducible() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "oracle_wa_combined_events.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_parameters_are_reproducible() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "extract_wa_combined_events_params.py"), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


# --- manuell tid og avrunding (BV-024, BV-025) ---------------------------------------------------


def test_manual_60m_uses_024_not_nfif_020() -> None:
    score = calculator.calculate(
        "sprint_60m", M, "senior", Result(time_seconds=6.0, manual_timing=True)
    )
    assert score.points == 1170  # NFIF-arket (+0,20 s) gir 1187
    assert score.result_used == pytest.approx(6.24)


@pytest.mark.parametrize(
    ("event_id", "addition"),
    [("sprint_60m", 0.24), ("hurdles_110m", 0.24), ("sprint_200m", 0.24), ("sprint_400m", 0.14),
     ("middle_1000m", 0.0), ("middle_1500m", 0.0)],
)  # fmt: skip
def test_manual_timing_addition(event_id: str, addition: float) -> None:
    auto = Result(time_seconds=50.0)
    manual = Result(time_seconds=50.0, manual_timing=True)
    score = calculator.calculate(event_id, M, "senior", manual)
    assert score.result_used == pytest.approx(50.0 + addition)
    assert calculator.calculate(event_id, M, "senior", auto).result_used == pytest.approx(50.0)
    step = next(s for s in score.calculation_steps if s.label == "manual_timing_addition")
    assert step.ref == "BV-024"
    assert step.value == pytest.approx(addition)


def test_time_with_thousandths_is_rounded_up() -> None:
    score = calculator.calculate("sprint_100m", M, "senior", Result(time_seconds=10.391))
    assert score.result_used == pytest.approx(10.40)
    assert score.points == 999
    assert "BV-025" in [s.ref for s in score.calculation_steps]


def test_length_with_millimetres_is_rounded_down() -> None:
    score = calculator.calculate("long_jump", M, "senior", Result(distance_meters=5.179))
    assert score.result_used == pytest.approx(5.17)
    assert score.points == 415


def test_jumps_are_in_centimetres() -> None:
    # Appendix B s. 1: kvinner høyde 1,50 = 621 poeng.
    assert (
        calculator.calculate("high_jump", F, "senior", Result(distance_meters=1.50)).points == 621
    )


def test_appendix_b_lookup_examples() -> None:
    # Appendix B s. 1: menn 400 m 66,09 = 230, kvinner kule 12,34 = 684.
    assert (
        calculator.calculate("sprint_400m", M, "senior", Result(time_seconds=66.09)).points == 230
    )
    assert (
        calculator.calculate("shot_put", F, "senior", Result(distance_meters=12.34)).points == 684
    )


def test_worse_than_table_gives_zero() -> None:
    assert calculator.calculate("sprint_100m", M, "senior", Result(time_seconds=18.0)).points == 0
    assert calculator.calculate("sprint_100m", M, "senior", Result(time_seconds=25.0)).points == 0
    assert calculator.calculate("shot_put", M, "senior", Result(distance_meters=1.2)).points == 0


# --- sporbarhet (AP-027) ---------------------------------------------------------------------


def test_steps_refer_to_sources_and_bv() -> None:
    keys = {doc["key"] for doc in calculator.sources()}
    assert keys == {"wma-2023-appendix-b", "nfif-um-reglement-2026"}
    for gender, age_class, event_id, expected in (
        (M, "senior", "sprint_100m", "wma-2023-appendix-b"),
        (F, "senior", "middle_1500m", "BV-022"),
        (M, "G15", "hurdles_100m", "nfif-um-reglement-2026"),
    ):
        score = calculator.calculate(
            event_id,
            gender,
            age_class,
            Result(time_seconds=14.0) if event_id == "hurdles_100m" else Result(time_seconds=100.0),
        )
        steps = {s.label: s for s in score.calculation_steps}
        assert steps["points_raw"].ref == expected
        assert steps["points"].ref == "BV-003"


def test_sources_match_sha256sums() -> None:
    sums = {}
    for line in (ROOT / "sources" / "SHA256SUMS").read_text("utf-8").splitlines():
        digest, path = line.split(maxsplit=1)
        sums[f"sources/{path}"] = digest
    for doc in calculator.sources():
        assert doc["sha256"] == sums[doc["local_path"]]
        assert doc["document_url"]


def test_calculation_detail_shows_the_formula() -> None:
    # Rå poeng vises avkortet til fire desimaler, så visningen aldri runder opp over et heltall.
    score = calculator.calculate("sprint_100m", M, "senior", Result(time_seconds=10.40))
    assert score.calculation_detail == "25,4347 × (18 − 10,4)^1,81 = 999,3076 → 999"


# --- klasser og øvelser ----------------------------------------------------------------------


def test_registered() -> None:
    assert isinstance(
        default_registry().get("wa_combined_events", "2001"), CombinedEventsCalculator
    )


def test_youth_events_only_for_their_classes() -> None:
    def ids(gender: Gender, age_class: str) -> set[str]:
        return {e.event_id for e in calculator.list_events(gender, age_class)}

    assert "middle_600m" in ids(F, "J15") and "middle_600m" in ids(F, "J16")
    assert "middle_600m" not in ids(F, "J17") | ids(F, "senior")
    assert "hurdles_80m" in ids(F, "J16") and "hurdles_80m" not in ids(F, "J17")
    assert "middle_800m" in ids(M, "G16") and "middle_800m" not in ids(M, "G17") | ids(M, "senior")
    assert "hurdles_100m" in ids(M, "G15") and "hurdles_100m" not in ids(M, "senior")
    assert len(ids(M, "senior")) == 16
    assert len(ids(F, "senior")) == 16  # 15 fra Appendix B + 1500 m
    assert ids(M, "G17") == ids(M, "senior")
    assert ids(F, "J15") == ids(F, "senior") | {"middle_600m", "hurdles_80m"}


def test_youth_event_rejected_for_other_classes() -> None:
    with pytest.raises(UnknownEventError, match="J15"):
        calculator.calculate("middle_600m", F, "senior", Result(time_seconds=100.0))
    with pytest.raises(UnknownEventError):
        calculator.calculate("middle_800m", M, "G17", Result(time_seconds=130.0))


def test_unknown_class_and_event() -> None:
    with pytest.raises(UnknownEventError, match="senior"):
        calculator.calculate("sprint_100m", M, "J15", Result(time_seconds=12.0))
    with pytest.raises(UnknownEventError):
        calculator.calculate("sprint_100m", M, "14", Result(time_seconds=12.0))
    with pytest.raises(UnknownEventError):
        calculator.calculate("triple_jump", M, "senior", Result(distance_meters=12.0))


def test_input_spec() -> None:
    events = {e.event_id: e.input for e in calculator.list_events(M, "senior")}
    assert events["sprint_400m"].manual_timing_allowed
    assert not events["middle_1500m"].manual_timing_allowed
    assert events["middle_1500m"].uses_minutes and not events["sprint_400m"].uses_minutes
    assert events["long_jump"].measure == "distance"
    assert events["sprint_100m"].plausible_min < 10.4 < events["sprint_100m"].plausible_max


@pytest.mark.parametrize(
    "result",
    [Result(distance_meters=10.0), Result(time_seconds=0.0), Result()],
)
def test_invalid_time_results(result: Result) -> None:
    with pytest.raises(InvalidResultError):
        calculator.calculate("sprint_100m", M, "senior", result)


def test_invalid_field_results() -> None:
    with pytest.raises(InvalidResultError):
        calculator.calculate("shot_put", M, "senior", Result(time_seconds=10.0))
    with pytest.raises(InvalidResultError):
        calculator.calculate(
            "shot_put", M, "senior", Result(distance_meters=10.0, manual_timing=True)
        )


def test_get_parameters() -> None:
    assert calculator.get_parameters("middle_1500m", F, "senior") == {
        "a": 0.02883,
        "b": 535.0,
        "c": 1.88,
    }


# --- mangekamp -------------------------------------------------------------------------------


def _event(event_id: str, **result: Any) -> CombinedEventInput:
    return CombinedEventInput(event_id, Result(**result))


def test_combined_sums_points() -> None:
    combined = calculator.calculate_combined(
        M,
        "senior",
        [_event("sprint_100m", time_seconds=10.40), _event("long_jump", distance_meters=5.17),
         _event("discus", distance_meters=16.33)],
    )  # fmt: skip
    assert combined.total == 999 + 415 + 204
    assert [s.points for s in combined.events] == [999, 415, 204]
    assert combined.scoring_system == "wa_combined_events"


def test_combined_youth() -> None:
    combined = calculator.calculate_combined(
        F,
        "J15",
        [_event("hurdles_80m", time_seconds=12.0), _event("middle_600m", time_seconds=100.0)],
    )
    assert combined.total == 835 + 843


def test_combined_rejects_empty_and_duplicates() -> None:
    with pytest.raises(InvalidCombinedEventError):
        calculator.calculate_combined(M, "senior", [])
    with pytest.raises(InvalidCombinedEventError, match="sprint_100m"):
        calculator.calculate_combined(M, "senior", [_event("sprint_100m", time_seconds=11.0)] * 2)
