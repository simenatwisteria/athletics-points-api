"""Tyrvingtabellen 2014: regneark → athletics_scoring/data/tyrving_parameters_2014.json.

Leser formlene (ikke bare verdiene) i hvert aldersark og klassifiserer hver rad mot kjente
formelmaler. En rad som ikke passer en mal gir feil — skriptet gjetter aldri.

    python scripts/extract_tyrving_params.py [--check]

``--check`` skriver ingenting, men feiler hvis JSON-fila i repoet avviker fra det kilden gir.
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

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "sources" / "tyrving" / "tyrving-2014-redigerbar.xlsx"
TARGET = ROOT / "athletics_scoring" / "data" / "tyrving_parameters_2014.json"

SHEET_RE = re.compile(r"^(Gutter|Jenter) (\d{2}) år$")
GENDERS = {"Gutter": "M", "Jenter": "F"}

# Kolonner i aldersarkene (rad 4 er overskrift).
COL_NAME, COL_SPEC, COL_POINTS = "B", "C", "F"
COL_H1000, COL_QUOTIENT, COL_F1, COL_F2, COL_F3 = "H", "I", "J", "K", "L"

# Formelmaler, med radnummeret erstattet av '#'. Nøkkel: (M, N, O, P, I-formel, Q).
NUMBER = "<tall>"
TEMPLATES: dict[tuple[str, str, str, str, str, str], dict[str, Any]] = {
    ("=E#*100", "=H#*100", "=N#-M#", "=1000+O#*I#", NUMBER, ""): {
        "formula_type": "simple_quotient",
        "measure": "time",
        "scale": 100,
    },
    ("=(D#*60+E#)*10", "=H#*10", "=N#-M#", "=1000+O#*I#", NUMBER, ""): {
        "formula_type": "simple_quotient",
        "measure": "time",
        "scale": 10,
    },
    ("=E#*100", "=H#*100", "=N#-M#", "=1000-O#*I#", NUMBER, ""): {
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
        "=IF(E#>H#,J#,K#)",
    ): {"formula_type": "three_interval", "measure": "distance", "scale": 100},
}
POINTS_FORMULAS = {
    "=IF(P#<0,0,IF(E#=0,0,ROUNDDOWN(P#,0)))",
    "=IF(P#<0,0,IF(AND(E#=0,D#=0),0,ROUNDDOWN(P#,0)))",
}

# Rader der kildene er uenige. JSON-en gjengir regnearket uendret; alternativet fra de andre kildene
# legges ved som merknad. Hvilken kilde som vinner, avgjøres av Simen (docs/BACKLOG.md, AP-002).
# Skriptet feiler hvis en kjent konflikt forsvinner fra kilden, eller en ny dukker opp i formlene.
KNOWN_CONFLICTS: dict[tuple[str, int], dict[str, Any]] = {
    ("Jenter 17 år", 36): {
        "note": (
            "Regnearket regner Kule 3kg med 1000-O*I og I=1.2 hardkodet (enkel kvotient), men har "
            "faktor 1-3 = 0,3/0,6/1,2 i J-L som all annen kule. PDF-en viser tre-intervall. "
            "Samme formel i tyrving-2014.xls."
        ),
        "sources": ["sources/tyrving/tyrving-2014-jenter.pdf"],
        "alternative": {
            "formula_type": "three_interval",
            "params": {"h1000": 12.6, "f1": 0.3, "f2": 0.6, "f3": 1.2},
        },
    },
    ("Jenter 15 år", 36): {
        "note": (
            "Regnearket (.xlsx) har Spyd 0,4kg med 1000p = 42. Både tyrving-2014.xls og PDF-en har "
            "Spyd 500 g med 1000p = 38 for 15 år (400 g gjelder 10-14 år)."
        ),
        "sources": ["sources/tyrving/tyrving-2014.xls", "sources/tyrving/tyrving-2014-jenter.pdf"],
        "alternative": {
            "implement": "0,5kg",
            "params": {"h1000": 38, "f1": 0.13, "f2": 0.25, "f3": 0.5},
        },
    },
}

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


def _template_key(ws: Worksheet, row: int) -> tuple[str, str, str, str, str, str]:
    def formula(col: str) -> str:
        value = ws[f"{col}{row}"].value
        if value is None:
            return ""
        if isinstance(value, int | float):
            return NUMBER
        return re.sub(rf"([A-Z]){row}(?!\d)", r"\1#", str(value))

    return (formula("M"), formula("N"), formula("O"), formula("P"), formula("I"), formula("Q"))


def _number(ws: Worksheet, cell: str) -> float:
    value = ws[cell].value
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ValueError(f"{ws.title}!{cell} er ikke et tall: {value!r}")
    return value


def extract_sheet(ws: Worksheet) -> list[dict[str, Any]]:
    match = SHEET_RE.match(ws.title)
    if not match:
        raise ValueError(f"Uventet arknavn: {ws.title!r}")
    gender, age = GENDERS[match.group(1)], int(match.group(2))
    entries = []
    for row in range(1, ws.max_row + 1):
        points = ws[f"{COL_POINTS}{row}"].value
        if not (isinstance(points, str) and points.startswith("=")):
            continue
        if re.sub(rf"([A-Z]){row}(?!\d)", r"\1#", points) not in POINTS_FORMULAS:
            raise ValueError(f"{ws.title}!F{row}: ukjent poengformel {points!r}")
        key = _template_key(ws, row)
        conflict = KNOWN_CONFLICTS.get((ws.title, row))
        formula_conflict = conflict is not None and "formula_type" in conflict["alternative"]
        if formula_conflict:
            # Raden har en ubrukt Q-formel igjen fra tre-intervall-malen; P leser den ikke.
            key = (*key[:5], "")
        if key not in TEMPLATES:
            raise ValueError(f"{ws.title} rad {row}: ukjent formelmal {key}")
        entry_type = dict(TEMPLATES[key])

        has_factors = ws[f"{COL_F1}{row}"].value is not None
        is_three_interval = entry_type["formula_type"] == "three_interval"
        if has_factors != is_three_interval and not formula_conflict:
            raise ValueError(f"{ws.title} rad {row}: faktor 1-3 stemmer ikke med formelen")
        if formula_conflict and (is_three_interval or not has_factors):
            raise ValueError(f"{ws.title} rad {row}: kjent formelkonflikt finnes ikke lenger")

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
        if conflict:
            entry["conflict"] = conflict
        entries.append(entry)
    return entries


def extract(source: Path = SOURCE) -> dict[str, Any]:
    wb = openpyxl.load_workbook(source, data_only=False, read_only=False)
    entries: list[dict[str, Any]] = []
    for ws in wb.worksheets:
        if ws.title == "Forside":
            continue
        entries.extend(extract_sheet(ws))

    keys = [(e["event_id"], e["gender"], e["age"], e["implement"]) for e in entries]
    duplicates = {k for k in keys if keys.count(k) > 1}
    if duplicates:
        raise ValueError(f"Dupliserte kombinasjoner: {sorted(map(str, duplicates))}")
    found = {(ws, row) for ws, row in ((e["source"]["sheet"], e["source"]["row"]) for e in entries)}
    missing = set(KNOWN_CONFLICTS) - found
    if missing:
        raise ValueError(f"Kjente konflikter ikke funnet i kilden: {missing}")

    return {
        "meta": {
            "scoring_system": "tyrving",
            "version": "2014",
            "source": "NFIF, Tyrvingtabellen (2014-utgave), redigerbart regneark",
            "source_file": str(source.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "generated_by": "scripts/extract_tyrving_params.py",
            "entry_count": len(entries),
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
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="feil hvis JSON-fila er utdatert")
    args = parser.parse_args()

    output = render(extract())
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != output:
            target = TARGET.relative_to(ROOT)
            print(f"{target} er utdatert — kjør skriptet uten --check", file=sys.stderr)
            return 1
        print("OK")
        return 0
    TARGET.write_text(output, encoding="utf-8")
    count = json.loads(output)["meta"]["entry_count"]
    print(f"Skrev {TARGET.relative_to(ROOT)} ({count} kombinasjoner)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
