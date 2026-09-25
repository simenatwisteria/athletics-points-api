"""Tyrving-parametrene mot de offisielle PDF-ene, som vinner ved konflikt (docs/KILDEAVVIK.md)."""

import json
import math
import shutil
import subprocess
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


# NFIFs gjeldende regneark (.xls) mot PDF-ene: avvikene som skal meldes til forbundet.
EXPECTED_XLS_VS_PDF = {
    ("Gutter 19 år", 16, "quotient", 0.5, 0.45),
    ("Jenter 17 år", 36, "formula_type", "simple_quotient", "three_interval"),
    ("Jenter 17 år", 36, "f1", None, 0.3),
    ("Jenter 17 år", 36, "f2", None, 0.6),
    ("Jenter 17 år", 36, "f3", None, 1.2),
}


@pytest.mark.skipif(shutil.which("soffice") is None, reason="krever LibreOffice (soffice)")
def test_current_nfif_xls_against_pdf(records: list[tyrving_pdf.PdfRecord], tmp_path: Path) -> None:
    import openpyxl
    from extract_tyrving_params import extract_sheet

    source = ROOT / "sources" / "tyrving" / "tyrving-2014.xls"
    shutil.copy(source, tmp_path / source.name)
    subprocess.run(
        ["soffice", f"-env:UserInstallation={(tmp_path / 'profile').as_uri()}", "--headless",
         "--convert-to", "xlsx", "--outdir", str(tmp_path), str(tmp_path / source.name)],
        check=True,
        capture_output=True,
    )  # fmt: skip
    workbook = openpyxl.load_workbook(tmp_path / "tyrving-2014.xlsx")
    entries = [e for ws in workbook.worksheets[1:] for e in extract_sheet(ws)]
    assert len(entries) == 560
    differences = {
        (d.sheet, d.row, d.field, d.excel, d.pdf) for d in tyrving_pdf.compare(entries, records)
    }
    assert differences == EXPECTED_XLS_VS_PDF
