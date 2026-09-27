"""MastersCombinedCalculator (AP-016) mot kontrolltallene og klassekolonnene i NFIF-tabellene."""

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
from athletics_scoring.masters_combined_events import MastersCombinedCalculator
from athletics_scoring.models import CombinedEventInput, Gender, Result

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = json.loads(
    (ROOT / "tests" / "fixtures" / "masters_combined_events_cases.json").read_text("utf-8")
)
M, F = Gender.MALE, Gender.FEMALE

calculator = MastersCombinedCalculator()

# Kontrolltallene i docs/active/AP-016-masters-mangekamp.md.
CONTROL = [
    ("Appendix B s. 1 M50 100 m", M, "M50", "sprint_100m", Result(time_seconds=13.12), 681, 11.85),
    ("Appendix B s. 1 W35 høyde", F, "W35", "high_jump", Result(distance_meters=1.47), 621, 1.50),
    ("NFIF 200m C M35", M, "M35", "sprint_200m", Result(time_seconds=19.44), 1200, 19.04),
    ("NFIF Kule F M50 6 kg", M, "M50", "shot_put", Result(distance_meters=18.70), 1200, 21.60),
]  # fmt: skip


@pytest.mark.parametrize(
    ("gender", "age_class", "event_id", "result", "points", "adjusted"),
    [c[1:] for c in CONTROL],
    ids=[c[0] for c in CONTROL],
)
def test_control_numbers(
    gender: Gender, age_class: str, event_id: str, result: Result, points: int, adjusted: float
) -> None:
    score = calculator.calculate(event_id, gender, age_class, result)
    assert score.points == points
    assert score.result_used == pytest.approx(adjusted)


def test_wrong_implement_is_rejected() -> None:
    result = Result(distance_meters=18.70)
    with pytest.raises(UnknownEventError, match=r"M50 bruker 6kg .*BV-034"):
        calculator.calculate("shot_put", M, "M50", result, implement="7,26kg")
    assert calculator.calculate("shot_put", M, "M50", result, implement="6 kg").points == 1200
    assert calculator.calculate("shot_put", M, "M50", result, implement="6.0kg").points == 1200
    assert calculator.calculate("javelin", M, "M50", Result(distance_meters=40.0),
                                implement="700g").implement == "0,7kg"  # fmt: skip
    with pytest.raises(UnknownEventError, match="91cm"):
        calculator.calculate("hurdles_100m", M, "M50", Result(time_seconds=16.0), implement="84cm")
    with pytest.raises(UnknownEventError):
        calculator.calculate("sprint_100m", M, "M50", Result(time_seconds=13.0), implement="1kg")


# --- fasit -----------------------------------------------------------------------------------


def test_all_fixture_cases() -> None:
    """Alle klassekolonnene i NFIF-arkene, unntatt det som står i fixturens meta. Null avvik."""
    failures = []
    for block in FIXTURE["blocks"]:
        gender = Gender(block["gender"])
        for row, cell, result, points in block["cases"]:
            score = calculator.calculate(
                block["event_id"],
                gender,
                block["age_class"],
                Result(**result, manual_timing=block["manual_timing"]),
                implement=block["implement"],
            )
            if score.points != points:
                failures.append((block["sheet"], block["column"], row, cell, points, score.points))
    assert not failures, (len(failures), failures[:10])


def test_fixture_covers_every_class_column() -> None:
    meta = FIXTURE["meta"]
    blocks = FIXTURE["blocks"]
    assert meta["locked"] is False
    assert meta["case_count"] == sum(len(b["cases"]) for b in blocks) == 427750
    assert meta["block_count"] == len(blocks) == 538
    # Hver (kjønn, øvelse, klasse) motoren tilbyr, har en blokk med automatisk tid eller distanse.
    auto = [b for b in blocks if not b["manual_timing"]]
    covered = {(b["gender"], b["event_id"], b["age_class"]) for b in auto}
    offered = {(e.gender.value, e.event_id, e.age_class) for e in calculator.list_events()}
    assert offered == covered
    # Klassens redskap i motoren er det samme som i arket.
    implements = {(e.gender.value, e.event_id, e.age_class): e.implement
                  for e in calculator.list_events()}  # fmt: skip
    for b in blocks:
        assert implements[(b["gender"], b["event_id"], b["age_class"])] == b["implement"]


def test_fixture_skips_only_the_documented_source_errors() -> None:
    """BV-024, BV-035 og docs/KILDEAVVIK.md: ingenting annet er utelatt."""
    meta = FIXTURE["meta"]
    assert {(b["gender"], b["sheet"], b["event_id"]) for b in meta["skipped_blocks"]} == {
        ("M", "80-110m HK-m", "hurdles_80m"),
        ("F", "80-100mHK-m", "hurdles_80m"),
    }
    assert set(meta["skipped_sheets"]["M"]) == {"60m-m", "60m HK-m"}
    assert set(meta["skipped_sheets"]["F"]) == {"60m-m", "60mHK-m"}
    cells = Counter(
        (c["gender"], c["sheet"], c["column"], c["reason"].split(":")[0])
        for c in meta["skipped_cells"]
    )
    assert cells == {
        ("M", "200m", "N", "avkortet"): 20,
        ("M", "200m", "O", "avkortet"): 180,
        ("M", "200m", "O", "kan ikke leses som tid"): 20,
        ("M", "200m", "P", "kan ikke leses som tid"): 200,
        ("F", "100m-m", "P", "kolonnen har data, men ingen klasse i rad 2"): 1,
    }
    assert meta["skipped_cell_count"] == len(meta["skipped_cells"]) == 421


@pytest.mark.parametrize(
    "script", ["oracle_masters_combined_events.py", "extract_masters_combined_events_params.py"]
)
def test_generated_files_are_reproducible(script: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


# --- metoden (BV-024, BV-030, BV-031) --------------------------------------------------------


def _steps(score: Any) -> dict[str, Any]:
    return {s.label: s for s in score.calculation_steps}


def test_steps_show_factor_rounding_and_refs() -> None:
    score = calculator.calculate("sprint_100m", M, "M50", Result(time_seconds=13.12))
    steps = _steps(score)
    assert steps["age_factor"].value == pytest.approx(0.9031)
    assert steps["age_factor"].ref == "wma-2023-appendix-b"
    assert steps["age_adjusted"].value == pytest.approx(11.848672)
    assert steps["age_adjusted"].ref == "BV-030"
    assert steps["age_adjusted"].formula == "13,12 × 0,9031 = 11,848672"
    assert steps["age_adjusted_rounded"].value == pytest.approx(11.85)
    assert steps["age_adjusted_rounded"].ref == "BV-031"
    assert steps["points"].ref == "BV-003"
    assert [s.label for s in score.calculation_steps] == [
        "input", "age_factor", "age_adjusted", "age_adjusted_rounded", "difference", "points_raw",
        "points",
    ]  # fmt: skip
    assert score.calculation_detail.startswith("13,12 × 0,9031 = 11,848672 → 11,85; ")
    assert score.parameters["age_factor"] == 0.9031
    keys = {doc["key"] for doc in calculator.sources()}
    assert steps["age_factor"].ref in keys and steps["points_raw"].ref in keys


def test_runs_round_up_and_jumps_round_down() -> None:
    # 11,848672 ville gitt 11,84 med feil retning (682 poeng).
    assert calculator.calculate("sprint_100m", M, "M50", Result(time_seconds=13.12)).points == 681
    # 1,500135 rundet opp ville gitt 1,51.
    score = calculator.calculate("high_jump", F, "W35", Result(distance_meters=1.47))
    assert score.result_used == pytest.approx(1.50)


def test_manual_timing_is_added_before_the_factor() -> None:
    score = calculator.calculate(
        "sprint_100m", M, "M50", Result(time_seconds=12.9, manual_timing=True)
    )
    steps = _steps(score)
    assert steps["manual_timing_addition"].ref == "BV-024"
    # (12,9 + 0,24) × 0,9031 = 11,866734 → 11,87
    assert steps["age_adjusted"].value == pytest.approx(11.866734)
    assert score.result_used == pytest.approx(11.87)


@pytest.mark.parametrize(
    ("event_id", "gender", "age_class", "addition"),
    [("sprint_60m", M, "M50", 0.24), ("hurdles_80m", M, "M70", 0.24),
     ("hurdles_80m", F, "W40", 0.24), ("sprint_400m", F, "W60", 0.14),
     ("middle_1500m", M, "M60", 0.0)],
)  # fmt: skip
def test_manual_timing_addition_follows_bv024(
    event_id: str, gender: Gender, age_class: str, addition: float
) -> None:
    score = calculator.calculate(
        event_id, gender, age_class, Result(time_seconds=70.0, manual_timing=True)
    )
    assert _steps(score)["manual_timing_addition"].value == pytest.approx(addition)


def test_short_hurdles_use_the_senior_hurdles_table() -> None:
    params = calculator.get_parameters("hurdles_80m", M, "M70")
    assert {k: params[k] for k in ("a", "b", "c")} == {"a": 5.74352, "b": 28.5, "c": 1.92}
    assert params["age_factor"] == 1.0788
    women = calculator.get_parameters("hurdles_80m", F, "W40")
    assert {k: women[k] for k in ("a", "b", "c")} == {"a": 9.23076, "b": 26.7, "c": 1.835}


# --- klasser og øvelser ----------------------------------------------------------------------


def test_registered() -> None:
    assert isinstance(
        default_registry().get("masters_combined_events", "2023"), MastersCombinedCalculator
    )


def test_classes() -> None:
    assert calculator.age_classes(M) == [f"M{a}" for a in range(35, 101, 5)]
    assert calculator.age_classes(F) == [f"W{a}" for a in range(35, 101, 5)]


def test_hurdles_per_class() -> None:
    def ids(gender: Gender, age_class: str) -> set[str]:
        return {e.event_id for e in calculator.list_events(gender, age_class)}

    hurdles = {"hurdles_60m", "hurdles_80m", "hurdles_100m", "hurdles_110m"}
    assert ids(M, "M45") & hurdles == {"hurdles_60m", "hurdles_110m"}
    assert ids(M, "M50") & hurdles == {"hurdles_60m", "hurdles_100m"}
    assert ids(M, "M70") & hurdles == {"hurdles_60m", "hurdles_80m"}
    assert ids(F, "W35") & hurdles == {"hurdles_60m", "hurdles_100m"}
    assert ids(F, "W40") & hurdles == {"hurdles_60m", "hurdles_80m"}
    assert ids(F, "W100") & hurdles == {"hurdles_60m"}
    assert len(ids(M, "M35")) == 16 and len(ids(F, "W35")) == 16


def test_unknown_class_and_event() -> None:
    with pytest.raises(UnknownEventError, match="M35"):
        calculator.calculate("sprint_100m", M, "senior", Result(time_seconds=12.0))
    with pytest.raises(UnknownEventError):
        calculator.calculate("sprint_100m", M, "W50", Result(time_seconds=12.0))
    with pytest.raises(UnknownEventError, match="M50"):
        calculator.calculate("hurdles_110m", M, "M50", Result(time_seconds=16.0))
    with pytest.raises(UnknownEventError):
        calculator.calculate("triple_jump", M, "M50", Result(distance_meters=12.0))


def test_invalid_results() -> None:
    with pytest.raises(InvalidResultError):
        calculator.calculate("sprint_100m", M, "M50", Result(distance_meters=10.0))
    with pytest.raises(InvalidResultError):
        calculator.calculate("shot_put", M, "M50", Result(distance_meters=10.0, manual_timing=True))


def test_input_spec() -> None:
    events = {e.event_id: e for e in calculator.list_events(M, "M70")}
    assert events["shot_put"].implement == "4kg"
    assert events["hurdles_80m"].implement == "76cm"
    assert events["hurdles_80m"].formula_type == "track"
    assert events["hurdles_80m"].input.manual_timing_allowed
    assert events["middle_1500m"].input.uses_minutes
    spec = events["sprint_100m"].input
    assert spec.plausible_min < 13.5 < spec.plausible_max


# --- mangekamp -------------------------------------------------------------------------------


def test_combined_sums_points() -> None:
    combined = calculator.calculate_combined(
        M,
        "M50",
        [CombinedEventInput("sprint_100m", Result(time_seconds=13.12)),
         CombinedEventInput("shot_put", Result(distance_meters=18.70), implement="6kg")],
    )  # fmt: skip
    assert combined.total == 681 + 1200
    assert combined.scoring_system == "masters_combined_events"


def test_combined_rejects_empty_and_duplicates() -> None:
    with pytest.raises(InvalidCombinedEventError):
        calculator.calculate_combined(M, "M50", [])
    event = CombinedEventInput("sprint_100m", Result(time_seconds=13.0))
    with pytest.raises(InvalidCombinedEventError, match="sprint_100m"):
        calculator.calculate_combined(M, "M50", [event, event])
