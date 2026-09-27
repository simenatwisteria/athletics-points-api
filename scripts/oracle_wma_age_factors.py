"""Oracle for WMA Age Grading 2023: sources/wma/wma-2023-age-factors.pdf → fasit.

Leser PDF-side 5–16 på en annen måte enn ``extract_wma_age_factors.py``: som enkeltord med
koordinater, ikke som tekstlinjer. Hver faktor plasseres i kolonnen der overskriftsordene står
rett over den, og overskriften settes sammen ovenfra og ned («Short» + «Hurdles»). Alderen er ordet
lengst til venstre på raden, og kjønnet står i sidetittelen. Rekkefølgen på sidene og kolonnene
brukes ikke.

Fixturen har én rad per (kjønn, øvelse, alder) med faktoren slik den står i PDF-en, et
eksempelresultat per øvelse og det aldersjusterte resultatet: resultat × faktor, rundet opp til
hundredeler for løp og ned til hel centimeter for hopp og kast (BV-042, som BV-031). Regnet med
``Decimal``.

Importerer ikke ``athletics_scoring``. Skriver ``tests/fixtures/wma_age_factors_cases.json`` (ny,
ulåst).

    python scripts/oracle_wma_age_factors.py [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from pathlib import Path
from typing import Any

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "sources" / "wma" / "wma-2023-age-factors.pdf"
TARGET = ROOT / "tests" / "fixtures" / "wma_age_factors_cases.json"
TABLE_PAGES = range(4, 16)  # PDF-side 5–16, nullindeksert
FACTOR_RE = re.compile(r"^\d+\.\d{4}$")
CENTIMETRE = Decimal("0.01")

# Overskrift i PDF-en → (event_id, måltype, eksempelresultat i sekunder eller meter). Eksemplene er
# vanlige masters-resultater med to desimaler, så avrundingen blir prøvd.
COLUMNS: dict[str, tuple[str, str, str]] = {
    "60m": ("sprint_60m", "time", "8.47"),
    "100m": ("sprint_100m", "time", "13.50"),
    "200m": ("sprint_200m", "time", "27.83"),
    "400m": ("sprint_400m", "time", "63.21"),
    "800m": ("middle_800m", "time", "151.37"),
    "1000m": ("middle_1000m", "time", "198.44"),
    "1500m": ("middle_1500m", "time", "311.09"),
    "Mile": ("middle_mile", "time", "336.52"),
    "3000m": ("distance_3000m", "time", "657.13"),
    "5000m": ("distance_5000m", "time", "1143.77"),
    "10000m": ("distance_10000m", "time", "2391.58"),
    "60m Hurdles": ("hurdles_60m", "time", "10.36"),
    "Short Hurdles": ("hurdles_short", "time", "16.94"),
    "Long Hurdles": ("hurdles_long", "time", "68.25"),
    "Steeple Chase": ("steeplechase", "time", "421.66"),
    "High Jump": ("high_jump", "distance", "1.47"),
    "Pole Vault": ("pole_vault", "distance", "3.15"),
    "Long Jump": ("long_jump", "distance", "5.23"),
    "Triple Jump": ("triple_jump", "distance", "10.87"),
    "Shot Put": ("shot_put", "distance", "11.49"),
    "Discus": ("discus", "distance", "34.71"),
    "Hammer": ("hammer", "distance", "41.93"),
    "Javelin": ("javelin", "distance", "38.06"),
    "Weight": ("weight_throw", "distance", "14.58"),
    "3000m RaceWalk": ("racewalk_3000m", "time", "901.43"),
    "5000m RaceWalk": ("racewalk_5000m", "time", "1587.29"),
    "10k RaceWalk": ("racewalk_10000m", "time", "3321.07"),
    "20k RaceWalk": ("racewalk_20000m", "time", "7012.55"),
    "Half Marathon": ("half_marathon", "time", "5433.18"),
    "Marathon": ("marathon", "time", "11874.61"),
}
GENDER_WORD = {"WOMEN'S": "F", "MEN'S": "M"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _center(word: dict[str, Any]) -> float:
    return (float(word["x0"]) + float(word["x1"])) / 2


def read_page(page: Any) -> tuple[str, dict[str, dict[int, str]]]:
    """Kjønn og kolonne → alder → faktor for én side."""
    words = page.extract_words()
    title = [w for w in words if w["text"] in GENDER_WORD]
    if len(title) != 1:
        raise ValueError(f"PDF-side {page.page_number}: fant ikke kjønn i tittelen")
    gender = GENDER_WORD[title[0]["text"]]

    rows: dict[float, list[dict[str, Any]]] = {}
    for w in words:
        rows.setdefault(round(float(w["top"]), 0), []).append(w)
    table_rows = []
    for top, row in sorted(rows.items()):
        row.sort(key=lambda w: float(w["x0"]))
        values = row[1:]
        if row[0]["text"].isdigit() and values and all(FACTOR_RE.match(w["text"]) for w in values):
            table_rows.append((top, row))
    first_top = table_rows[0][0]
    header = [w for w in words if float(title[0]["top"]) + 2 < float(w["top"]) < first_top - 2]

    columns: dict[str, dict[int, str]] = {}
    for _, row in table_rows:
        age = int(row[0]["text"])
        for value in row[1:]:
            above = sorted(
                (
                    h
                    for h in header
                    if float(value["x0"]) - 8 <= _center(h) <= float(value["x1"]) + 8
                ),
                key=lambda h: float(h["top"]),
            )
            name = " ".join(h["text"] for h in above)
            if name not in COLUMNS:
                raise ValueError(f"PDF-side {page.page_number}, alder {age}: kolonne {name!r}")
            if age in columns.setdefault(name, {}):
                raise ValueError(f"PDF-side {page.page_number}: {name} {age} to ganger")
            columns[name][age] = value["text"]
    return gender, columns


def read_factors() -> dict[tuple[str, str], dict[int, str]]:
    """(kjønn, kolonne) → alder → faktor, for alle tabellsidene."""
    out: dict[tuple[str, str], dict[int, str]] = {}
    pages: dict[tuple[str, str], list[int]] = {}
    with pdfplumber.open(PDF) as pdf:
        for index in TABLE_PAGES:
            gender, columns = read_page(pdf.pages[index])
            for name, per_age in columns.items():
                target = out.setdefault((gender, name), {})
                if set(target) & set(per_age):
                    raise ValueError(f"{gender} {name}: samme alder på flere sider")
                target.update(per_age)
                pages.setdefault((gender, name), []).append(index + 1)
    for key, per_age in out.items():
        if sorted(per_age) != list(range(30, 111)):
            raise ValueError(f"{key}: aldrene er ikke 30–110")
    if {name for _, name in out} != set(COLUMNS) or len(out) != 2 * len(COLUMNS):
        raise ValueError("ikke alle kolonnene for begge kjønn")
    return out


def adjusted(result: Decimal, factor: Decimal, measure: str) -> Decimal:
    rounding = ROUND_CEILING if measure == "time" else ROUND_FLOOR
    return (result * factor).quantize(CENTIMETRE, rounding=rounding)


def build() -> dict[str, Any]:
    factors = read_factors()
    cases = []
    for (gender, name), per_age in sorted(factors.items()):
        event_id, measure, example = COLUMNS[name]
        for age, factor in sorted(per_age.items()):
            value = adjusted(Decimal(example), Decimal(factor), measure)
            cases.append([gender, event_id, age, factor, example, str(value)])
    return {
        "meta": {
            "generated_by": "scripts/oracle_wma_age_factors.py",
            "source": str(PDF.relative_to(ROOT)),
            "source_sha256": _sha256(PDF),
            "locked": False,
            "case_count": len(cases),
            "columns": {name: {"event_id": e, "measure": m} for name, (e, m, _) in COLUMNS.items()},
            "row_format": ["gender", "event_id", "age", "factor", "result", "adjusted"],
            "rounding": "løp rundes opp til 0,01 s, hopp og kast ned til hel cm (BV-042)",
        },
        "cases": cases,
    }


def render(data: dict[str, Any]) -> str:
    """Én case per linje."""
    head = json.dumps(data["meta"], ensure_ascii=False, indent=2)
    lines = ",\n".join("    " + json.dumps(case, ensure_ascii=False) for case in data["cases"])
    return (
        f'{{\n  "meta": {head.replace(chr(10), chr(10) + "  ")},\n  "cases": [\n{lines}\n  ]\n}}\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="feil hvis fixturen er utdatert")
    args = parser.parse_args()

    data = build()
    output = render(data)
    if json.loads(output) != data:
        raise ValueError("render() gir ikke samme data tilbake")
    target = TARGET.relative_to(ROOT)
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != output:
            print(f"{target} avviker fra kilden", file=sys.stderr)
            return 1
        print("OK")
        return 0
    if TARGET.exists():
        existing = json.loads(TARGET.read_text(encoding="utf-8"))
        if existing["meta"].get("locked"):
            print(f"{target} er låst — skriver ikke", file=sys.stderr)
            return 1
    TARGET.write_text(output, encoding="utf-8")
    print(f"Skrev {target} ({data['meta']['case_count']} caser)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
