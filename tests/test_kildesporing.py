"""AP-027: hvert beregningssteg kan spores til en kilde eller et dokumentert beregningsvalg."""

import re
from pathlib import Path

from athletics_scoring.models import Gender, Result, ScoreResult
from athletics_scoring.tyrving import TyrvingCalculator

ROOT = Path(__file__).resolve().parent.parent
BV_HEADING = re.compile(r"^\| (BV-\d{3}) \|", re.MULTILINE)
BV_REF = re.compile(r"BV-\d{3}")

calculator = TyrvingCalculator()


def _refs(score: ScoreResult) -> list[str | None]:
    return [step.ref for step in score.calculation_steps]


def test_long_race_drops_hundredths_with_bv011() -> None:
    # Kontrolltall: tests/fixtures/tyrving_rules.json R2-01.
    score = calculator.calculate(
        "middle_800m", Gender.MALE, "15", Result(time_minutes=2, time_seconds=4.56)
    )
    assert score.points == 991
    step = next(s for s in score.calculation_steps if s.ref == "BV-011")
    assert step.value == 124.5


def test_no_bv011_step_when_nothing_is_dropped() -> None:
    score = calculator.calculate(
        "middle_800m", Gender.MALE, "15", Result(time_minutes=2, time_seconds=4.5)
    )
    assert "BV-011" not in _refs(score)


def test_manual_timing_and_rounding_refer_to_bv() -> None:
    score = calculator.calculate(
        "sprint_100m", Gender.MALE, "15", Result(time_seconds=12.0, manual_timing=True)
    )
    refs = _refs(score)
    assert "BV-012" in refs
    assert score.calculation_steps[-1].label == "points"
    assert score.calculation_steps[-1].ref == "BV-003"


def test_raw_points_refer_to_the_official_table_for_the_gender() -> None:
    keys = {doc["key"] for doc in calculator.sources()}
    for gender, expected in (
        (Gender.MALE, "nfif-tyrving-2014-gutter"),
        (Gender.FEMALE, "nfif-tyrving-2014-jenter"),
    ):
        score = calculator.calculate("long_jump", gender, "15", Result(distance_meters=5.0))
        step = next(s for s in score.calculation_steps if s.label == "points_raw")
        assert step.ref == expected
        assert expected in keys


def test_sources_match_sha256sums() -> None:
    sums = {}
    for line in (ROOT / "sources" / "SHA256SUMS").read_text("utf-8").splitlines():
        digest, path = line.split(maxsplit=1)
        sums[f"sources/{path}"] = digest
    documents = calculator.sources()
    assert len(documents) >= 2
    fields = {"key", "title", "publisher", "official_page", "document_url", "local_path", "sha256",
              "retrieved"}  # fmt: skip
    for doc in documents:
        assert set(doc) == fields
        assert doc["official_page"]
        assert doc["sha256"] == sums[doc["local_path"]]
    assert len({doc["key"] for doc in documents}) == len(documents)


def test_every_bv_in_code_is_documented() -> None:
    documented = set(BV_HEADING.findall((ROOT / "docs" / "BEREGNINGSVALG.md").read_text("utf-8")))
    used = {
        ref
        for path in (ROOT / "athletics_scoring").rglob("*.py")
        for ref in BV_REF.findall(path.read_text("utf-8"))
    }
    assert used, "fant ingen BV-numre i koden"
    assert used <= documented, sorted(used - documented)
