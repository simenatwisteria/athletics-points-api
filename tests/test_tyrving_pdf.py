"""Tyrving-parametrene mot de offisielle PDF-ene, som vinner ved konflikt (docs/KILDEAVVIK.md)."""

import json
import math
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import tyrving_pdf  # noqa: E402

PARAMS = ROOT / "athletics_scoring" / "data" / "tyrving_parameters_2014.json"

# Skrivefeil i PDF-ene som leseren tolker (docs/KILDEAVVIK.md). Endres lista, må Simen se på det.
EXPECTED_TYPOS = {
    ("M", "20000m Kappgang"): 2,
    ("M", "1500 mH 76,2cm"): 1,
    ("M", "Slegge 2 kg 110 cm"): 1,
}


@pytest.fixture(scope="module")
def records() -> list[tyrving_pdf.PdfRecord]:
    return tyrving_pdf.parse_all()


@pytest.fixture(scope="module")
def entries() -> list[dict[str, Any]]:
    data: dict[str, Any] = json.loads(PARAMS.read_text(encoding="utf-8"))
    return list(data["entries"])


def test_every_entry_equals_pdf(
    entries: list[dict[str, Any]], records: list[tyrving_pdf.PdfRecord]
) -> None:
    assert tyrving_pdf.compare(entries, records) == []


def test_pdf_covers_all_560_combinations(records: list[tyrving_pdf.PdfRecord]) -> None:
    assert sum(len(r.h1000) for r in records) == 560


def test_pdf_is_internally_consistent(records: list[tyrving_pdf.PdfRecord]) -> None:
    """80 %-verdiene og poengene under 80 % må følge av 1000p-verdien og f2.

    Bekrefter både PDF-en og at leseren knytter verdiene til riktig alder.
    """
    checked = 0
    for record in records:
        if record.formula_type != "three_interval":
            continue
        f2 = record.multipliers[1]
        for age, h1000 in record.h1000.items():
            eighty = float(record.checks["80"][age].replace(",", "."))
            points = int(record.checks["p"][age])
            assert eighty == round(0.8 * h1000, 2), (record.label, age)
            assert points == math.floor(1000 - (h1000 - 0.8 * h1000) * 100 * f2 + 1e-9)
            checked += 1
    assert checked == 116


def test_typos_are_the_known_ones(records: list[tyrving_pdf.PdfRecord]) -> None:
    typos = {(r.gender, r.label): len(r.typos) for r in records if r.typos}
    assert typos == EXPECTED_TYPOS


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("7.55", 7.55),
        ("1:52.00", 112.0),
        ("5:20.0", 320.0),
        ("1:53:30.0", 6810.0),
        ("1:40.00.0", 6000.0),
        ("4.48.00", 288.0),
        ("30,40", 30.4),
    ],
)
def test_parse_result(text: str, expected: float) -> None:
    assert tyrving_pdf.parse_result(text)[0] == pytest.approx(expected)
