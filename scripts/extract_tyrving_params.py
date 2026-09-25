"""Tyrvingtabellen 2014: kildefiler → athletics_scoring/data/tyrving_parameters_2014.json.

1. Leser formlene (ikke bare verdiene) i hvert aldersark i regnearket og klassifiserer hver rad mot
   kjente formelmaler. En rad som ikke passer en mal gir feil — skriptet gjetter aldri.
2. Sammenligner hver rad med de offisielle PDF-ene (scripts/tyrving_pdf.py).
3. Ved avvik vinner PDF-en (beslutning 2026-09-25, docs/KILDEAVVIK.md). Regnearkets verdi tas
   vare på i ``pdf_override.excel`` på oppføringen.

    python scripts/extract_tyrving_params.py [--check]

``--check`` skriver ingenting, men feiler hvis JSON-fila i repoet avviker fra det kildene gir.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tyrving_pdf

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "sources" / "tyrving" / "tyrving-2014-redigerbar.xlsx"
TARGET = ROOT / "athletics_scoring" / "data" / "tyrving_parameters_2014.json"

SHEET_RE = re.compile(r"^(Gutter|Jenter) (\d{2}) år$")
GENDERS = {"Gutter": "M", "Jenter": "F"}

# Kolonner i aldersarkene (rad 4 er overskrift).
COL_NAME, COL_SPEC, COL_POINTS = "B", "C", "F"
COL_H1000, COL_QUOTIENT, COL_F1, COL_F2, COL_F3 = "H", "I", "J", "K", "L"

# Formelmaler, med radnummeret erstattet av '#'. Nøkkel: (M, N, O, P, I-formel).
NUMBER = "<tall>"
TEMPLATES: dict[tuple[str, str, str, str, str], dict[str, Any]] = {
    ("=E#*100", "=H#*100", "=N#-M#", "=1000+O#*I#", NUMBER): {
        "formula_type": "simple_quotient",
        "measure": "time",
        "scale": 100,
    },
    ("=(D#*60+E#)*10", "=H#*10", "=N#-M#", "=1000+O#*I#", NUMBER): {
        "formula_type": "simple_quotient",
        "measure": "time",
        "scale": 10,
    },
    ("=E#*100", "=H#*100", "=N#-M#", "=1000-O#*I#", NUMBER): {
        "formula_type": "simple_quotient",
        "measure": "distance",
        "scale": 100,
    },
    (
        "=E#*100",
        "=H#*100",
        "=N#-M#",
        "=IF(E#<0.8*H#,1000-((N#-0.8*N#)*K#+(O#-(N#-N#*0.8))*L#),1000-O#*I#)",
        "=IF(E#<0.8*H#,L#,Q#)",
    ): {"formula_type": "three_interval", "measure": "distance", "scale": 100},
}
Q_FORMULA = "=IF(E#>H#,J#,K#)"
POINTS_FORMULAS = {
    "=IF(P#<0,0,IF(E#=0,0,ROUNDDOWN(P#,0)))",
    "=IF(P#<0,0,IF(AND(E#=0,D#=0),0,ROUNDDOWN(P#,0)))",
}
OVERRIDE_REASON = (
    "Regnearket avviker fra den offisielle PDF-en. PDF-en vinner (beslutning 2026-09-25, "
    "docs/KILDEAVVIK.md). Regnearkets verdier står i «excel»."
)

RUNNING = {40: "sprint", 60: "sprint", 80: "sprint", 100: "sprint", 200: "sprint", 300: "sprint",
           400: "sprint", 600: "middle", 800: "middle", 1000: "middle", 1500: "middle",
           2000: "distance", 3000: "distance", 5000: "distance", 10000: "distance"}  # fmt: skip
NAMED = {
    "Høyde": "high_jump",
    "Høyde uten tilløp": "high_jump_standing",
    "Stav": "pole_vault",
    "Lengde": "long_jump",
    "Lengde uten tilløp": "long_jump_standing",
    "Tresteg": "triple_jump",
    "Kule": "shot_put",
    "Diskos": "discus",
    "Slegge": "hammer",
    "Spyd": "javelin",
    "Liten ball": "ball_throw",
    "Slengball": "swing_ball",
}


def normalize_spec(spec: object) -> str | None:
    """'2 kg' og '2kg' er samme utstyr; '91,4cm ' har etterfølgende mellomrom."""
    if spec is None:
        return None
    return re.sub(r"\s+", "", str(spec))


def format_implement(parts: tuple[tuple[float, str], ...]) -> str:
    """PDF-ens utstyr i regnearkets skrivemåte, f.eks. '0,5kg' eller '4kg/119,5cm'."""

    def number(value: float) -> str:
        return f"{value:g}".replace(".", ",")

    return "/".join(
        f"{number(value / 1000)}kg" if unit == "g" else f"{number(value)}{unit}"
        for value, unit in parts
    )


def event_id(name: str, spec: str | None) -> str:
    name = " ".join(name.split())
    if name in NAMED:
        return NAMED[name]
    match = re.fullmatch(r"(\d+) m( hekk| hinder)?", name)
    if not match:
        raise ValueError(f"Ukjent øvelse: {name!r}")
    distance, kind = int(match.group(1)), match.group(2)
    if kind == " hekk":
        return f"hurdles_{distance}m"
    if kind == " hinder":
        return f"steeplechase_{distance}m"
    if spec == "Kappgang":
        return f"racewalk_{distance}m"
    if distance not in RUNNING:
        raise ValueError(f"Ukjent løpsdistanse: {name!r}")
    return f"{RUNNING[distance]}_{distance}m"


def _formula(ws: Worksheet, col: str, row: int) -> str:
    value = ws[f"{col}{row}"].value
    if value is None:
        return ""
    if isinstance(value, int | float):
        return NUMBER
    return re.sub(rf"([A-Z]){row}(?!\d)", r"\1#", str(value))


def _number(ws: Worksheet, cell: str) -> float:
    value = ws[cell].value
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ValueError(f"{ws.title}!{cell} er ikke et tall: {value!r}")
    return value


def extract_sheet(ws: Worksheet) -> list[dict[str, Any]]:
    """Regnearkets rader, uendret. Rader der formelen og faktor 1-3 er i strid, merkes med
    ``_inconsistent`` og må rettes av PDF-en i ``extract``."""
    match = SHEET_RE.match(ws.title)
    if not match:
        raise ValueError(f"Uventet arknavn: {ws.title!r}")
    gender, age = GENDERS[match.group(1)], int(match.group(2))
    entries = []
    for row in range(1, ws.max_row + 1):
        if not str(ws[f"{COL_POINTS}{row}"].value or "").startswith("="):
            continue
        if _formula(ws, COL_POINTS, row) not in POINTS_FORMULAS:
            raise ValueError(f"{ws.title}!F{row}: ukjent poengformel")
        key = tuple(_formula(ws, col, row) for col in "MNOPI")
        if key not in TEMPLATES:
            raise ValueError(f"{ws.title} rad {row}: ukjent formelmal {key}")
        entry_type = dict(TEMPLATES[key])
        is_three_interval = entry_type["formula_type"] == "three_interval"
        has_factors = ws[f"{COL_F1}{row}"].value is not None
        q_formula = _formula(ws, "Q", row)
        if is_three_interval and (q_formula != Q_FORMULA or not has_factors):
            raise ValueError(f"{ws.title} rad {row}: ufullstendig tre-intervall-rad")
        # Enkel formel, men faktor 1-3 og Q-formel ligger igjen: regnearket er i strid med seg selv.
        inconsistent = not is_three_interval and (has_factors or q_formula != "")

        params: dict[str, float] = {"h1000": _number(ws, f"{COL_H1000}{row}")}
        if is_three_interval:
            params |= {
                "f1": _number(ws, f"{COL_F1}{row}"),
                "f2": _number(ws, f"{COL_F2}{row}"),
                "f3": _number(ws, f"{COL_F3}{row}"),
            }
        else:
            params["quotient"] = _number(ws, f"{COL_QUOTIENT}{row}")

        name = str(ws[f"{COL_NAME}{row}"].value)
        spec = normalize_spec(ws[f"{COL_SPEC}{row}"].value)
        entry: dict[str, Any] = {
            "event_id": event_id(name, spec),
            "name": " ".join(name.split()),
            "gender": gender,
            "age": age,
            "implement": None if spec == "Kappgang" else spec,
            **entry_type,
            "params": params,
            "source": {"sheet": ws.title, "row": row},
        }
        if inconsistent:
            entry["_inconsistent"] = True
        entries.append(entry)
    return entries


def apply_pdf(entries: list[dict[str, Any]], records: list[tyrving_pdf.PdfRecord]) -> None:
    """Retter regnearkets verdier med PDF-ens der de avviker (PDF vinner)."""
    differences = tyrving_pdf.compare(entries, records)
    structural = [d for d in differences if d.field in {"finnes i PDF", "mangler i regnearket"}]
    if structural:
        raise ValueError(f"Regneark og PDF har ikke samme rader: {structural}")
    by_row: dict[tuple[str, int], list[tyrving_pdf.Difference]] = {}
    for difference in differences:
        by_row.setdefault((difference.sheet, difference.row), []).append(difference)

    for entry in entries:
        key = (entry["source"]["sheet"], entry["source"]["row"])
        inconsistent = entry.pop("_inconsistent", False)
        if key not in by_row:
            if inconsistent:
                raise ValueError(f"{key}: regnearket er i strid med seg selv, men PDF-en er enig")
            continue
        record = next(
            r
            for r in records
            if r.gender == entry["gender"]
            and r.event_id == entry["event_id"]
            and entry["age"] in r.h1000
            and (
                r.implement == tyrving_pdf.canonical_implement(entry["implement"])
                or any(d.field == "implement" for d in by_row[key])
            )
        )
        excel: dict[str, Any] = {}
        fields = {d.field for d in by_row[key]}
        if "implement" in fields:
            excel["implement"] = entry["implement"]
            entry["implement"] = format_implement(record.implement)
        if "formula_type" in fields:
            excel["formula_type"] = entry["formula_type"]
            entry["formula_type"] = record.formula_type
        names = ("f1", "f2", "f3") if record.formula_type == "three_interval" else ("quotient",)
        pdf_params = {"h1000": record.h1000[entry["age"]]} | dict(
            zip(names, record.multipliers, strict=True)
        )
        if pdf_params != entry["params"]:
            excel["params"] = entry["params"]
            entry["params"] = pdf_params
        entry["pdf_override"] = {"reason": OVERRIDE_REASON, "excel": excel}


def extract(source: Path = SOURCE) -> dict[str, Any]:
    wb = openpyxl.load_workbook(source, data_only=False, read_only=False)
    entries: list[dict[str, Any]] = []
    for ws in wb.worksheets:
        if ws.title != "Forside":
            entries.extend(extract_sheet(ws))

    keys = [(e["event_id"], e["gender"], e["age"], e["implement"]) for e in entries]
    duplicates = {k for k in keys if keys.count(k) > 1}
    if duplicates:
        raise ValueError(f"Dupliserte kombinasjoner: {sorted(map(str, duplicates))}")

    apply_pdf(entries, tyrving_pdf.parse_all())

    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    sources = [source, *tyrving_pdf.PDFS.values()]
    return {
        "meta": {
            "scoring_system": "tyrving",
            "version": "2014",
            "source": "NFIF, Tyrvingtabellen (2014-utgave)",
            "sources": {str(p.relative_to(ROOT)): sha256(p) for p in sources},
            "conflict_policy": "PDF vinner ved avvik fra regnearket (docs/KILDEAVVIK.md)",
            "generated_by": "scripts/extract_tyrving_params.py",
            "entry_count": len(entries),
            "override_count": sum("pdf_override" in e for e in entries),
            "formula_types": {
                "simple_quotient": (
                    "tid: 1000 + (h1000*scale - result*scale) * quotient; "
                    "distanse: 1000 - (h1000*scale - result*scale) * quotient"
                ),
                "three_interval": (
                    "distanse, skalert med scale: f1 over h1000, f2 mellom h1000 og 80 % av h1000, "
                    "f3 under 80 %"
                ),
            },
        },
        "entries": entries,
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="feil hvis JSON-fila er utdatert")
    args = parser.parse_args()

    output = render(extract())
    target = TARGET.relative_to(ROOT)
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != output:
            print(f"{target} er utdatert — kjør skriptet uten --check", file=sys.stderr)
            return 1
        print("OK")
        return 0
    TARGET.write_text(output, encoding="utf-8")
    meta = json.loads(output)["meta"]
    print(f"Skrev {target} ({meta['entry_count']} kombinasjoner, {meta['override_count']} fra PDF)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
