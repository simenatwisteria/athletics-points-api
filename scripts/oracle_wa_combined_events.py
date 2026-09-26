"""WA Combined Events: seniorkolonnen i NFIFs masters-tabeller → fasit.

Skriver ``tests/fixtures/wa_combined_events_cases.json``. Kolonnen «Sr» (kolonne B) i NFIFs
mangekamptabeller for masters er ren Combined Events (BV-022). Arkene har to oppsett:

- poeng i kolonne A og resultat i kolonne B (de fleste løp og kast)
- resultat i kolonne A og poeng i kolonne B (høyde, stav, lengde og de fleste «-m»-arkene);
  gjenkjennes på «Resultat»/«Res.» i kolonne A over dataradene

Hver rad blir én case: resultat → poeng. Arkene for manuell tid på 60 m og 60 m hekk bruker
+0,20 s og er ikke fasit (BV-024, docs/KILDEAVVIK.md). ``80-100mHK`` (kvinner) har ingen
seniorkolonne.

Importerer ikke athletics_scoring.

    python scripts/oracle_wa_combined_events.py [--check]

``--check`` skriver ingenting, men feiler hvis fixture-fila i repoet avviker fra det kildene gir.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "tests" / "fixtures" / "wa_combined_events_cases.json"
SOURCES = {
    "M": ROOT / "sources" / "masters" / "nfif-masters-mangekamp-menn.xlsx",
    "F": ROOT / "sources" / "masters" / "nfif-masters-mangekamp-kvinner.xlsm",
}

# Ark → (event_id, manuell tid).
SHEETS: dict[str, dict[str, tuple[str, bool]]] = {
    "M": {
        "60m": ("sprint_60m", False),
        "100m": ("sprint_100m", False),
        "100m-m": ("sprint_100m", True),
        "200m": ("sprint_200m", False),
        "200m-m": ("sprint_200m", True),
        "400m": ("sprint_400m", False),
        "400m-m": ("sprint_400m", True),
        "1000m": ("middle_1000m", False),
        "1500m": ("middle_1500m", False),
        "60m HK": ("hurdles_60m", False),
        "80-110m HK": ("hurdles_110m", False),
        "80-110m HK-m": ("hurdles_110m", True),
        "Høyde": ("high_jump", False),
        "Stav": ("pole_vault", False),
        "Lengde": ("long_jump", False),
        "Kule": ("shot_put", False),
        "Diskos": ("discus", False),
        "Spyd": ("javelin", False),
        "Slegge": ("hammer", False),
        "Vektkast": ("weight_throw", False),
    },
    "F": {
        "60m": ("sprint_60m", False),
        "100m": ("sprint_100m", False),
        "100m-m": ("sprint_100m", True),
        "200m": ("sprint_200m", False),
        "200m-m": ("sprint_200m", True),
        "400m": ("sprint_400m", False),
        "400m-m": ("sprint_400m", True),
        "800m": ("middle_800m", False),
        "1500m": ("middle_1500m", False),
        "60mHK": ("hurdles_60m", False),
        "Høyde": ("high_jump", False),
        "Lengde": ("long_jump", False),
        "Stav": ("pole_vault", False),
        "Kule": ("shot_put", False),
        "Diskos": ("discus", False),
        "Spyd": ("javelin", False),
        "Slegge": ("hammer", False),
        "Vektkast": ("weight_throw", False),
    },
}
# Ark som bevisst ikke brukes, med grunn. Alle andre ark enn MKTAB må stå i SHEETS eller her.
SKIPPED: dict[str, dict[str, str]] = {
    "M": {
        "60m-m": "+0,20 s i stedet for +0,24 s (BV-024)",
        "60m HK-m": "+0,20 s i stedet for +0,24 s (BV-024)",
    },
    "F": {
        "60m-m": "+0,20 s i stedet for +0,24 s (BV-024)",
        "60mHK-m": "+0,20 s i stedet for +0,24 s (BV-024)",
        "80-100mHK": "ingen seniorkolonne (starter på W40)",
        "80-100mHK-m": "ingen seniorkolonne (starter på W40)",
    },
}
TIME_RE = re.compile(r"^(?:(\d+)\.)?(\d{1,2}\.\d{1,2})$")
FIELD_EVENTS = {"high_jump", "pole_vault", "long_jump", "shot_put", "discus", "javelin", "hammer",
                "weight_throw"}  # fmt: skip


def _text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, float):
        return repr(value)
    text = str(value).strip()
    return text or None


def _points(text: str) -> int:
    if not text.isdigit():
        raise ValueError(f"ikke et poengtall: {text!r}")
    return int(text)


def _result(text: str, event_id: str) -> dict[str, float | int]:
    if event_id in FIELD_EVENTS:
        return {"distance_meters": float(Decimal(text))}
    match = TIME_RE.match(text)
    if match is None:
        raise ValueError(f"ikke en tid: {text!r}")
    minutes, seconds = match.groups()
    if minutes is None:
        return {"time_seconds": float(Decimal(seconds))}
    return {"time_minutes": int(minutes), "time_seconds": float(Decimal(seconds))}


def read_sheet(ws: Any, event_id: str) -> list[list[Any]]:
    """Radene i seniorkolonnen som ``[radnummer, resultat i arket, result, poeng]``."""
    rows = list(ws.iter_rows(max_col=2, values_only=True))
    if _text(rows[1][1]) != "Sr":
        raise ValueError(f"{ws.title}: kolonne B er ikke «Sr»")
    result_first = any((_text(r[0]) or "").startswith("Res") for r in rows[:5])
    cases = []
    for number, (col_a, col_b) in enumerate(rows, start=1):
        a, b = _text(col_a), _text(col_b)
        if a is None or b is None or not re.match(r"^\d", a):
            continue
        result_text, points_text = (a, b) if result_first else (b, a)
        cases.append([number, result_text, _result(result_text, event_id), _points(points_text)])
    if not cases:
        raise ValueError(f"{ws.title}: ingen rader")
    return cases


def generate() -> dict[str, Any]:
    sheets: list[dict[str, Any]] = []
    for gender, path in SOURCES.items():
        wb = openpyxl.load_workbook(path, data_only=True)
        titles = {ws.title for ws in wb.worksheets} - {"MKTAB"}
        unknown = titles - set(SHEETS[gender]) - set(SKIPPED[gender])
        if unknown or not set(SHEETS[gender]) <= titles:
            raise ValueError(f"{path.name}: uventede eller manglende ark {sorted(unknown)}")
        for title, (event_id, manual) in SHEETS[gender].items():
            sheets.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "sheet": title,
                    "gender": gender,
                    "event_id": event_id,
                    "age_class": "senior",
                    "manual_timing": manual,
                    "cases": read_sheet(wb[title], event_id),
                }
            )
    return {
        "meta": {
            "scoring_system": "wa_combined_events",
            "version": "2001",
            "generated_by": "scripts/oracle_wa_combined_events.py",
            "description": "Seniorkolonnen («Sr») i NFIFs masters-mangekamptabeller",
            "case_format": "[radnummer, resultat i arket, result (models.Result), poeng]",
            "sources": {
                str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in SOURCES.values()
            },
            "skipped_sheets": {g: dict(s) for g, s in SKIPPED.items()},
            "case_count": sum(len(s["cases"]) for s in sheets),
            "locked": False,
        },
        "sheets": sheets,
    }


def render(data: dict[str, Any]) -> str:
    """Meta og arkhoder med innrykk, én case per linje (holder fila liten og diffbar)."""

    def compact(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))

    meta = json.dumps(data["meta"], ensure_ascii=False, indent=2).replace("\n", "\n  ")
    lines = ["{", f'  "meta": {meta},', '  "sheets": [']
    for i, sheet in enumerate(data["sheets"]):
        head = ", ".join(f"{compact(k)}: {compact(v)}" for k, v in sheet.items() if k != "cases")
        rows = ",\n".join(f"      {compact(case)}" for case in sheet["cases"])
        end = "," if i < len(data["sheets"]) - 1 else ""
        lines.append(f'    {{{head}, "cases": [\n{rows}\n    ]}}{end}')
    lines += ["  ]", "}"]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="feil hvis fixture-fila er utdatert")
    args = parser.parse_args()

    data = generate()
    output = render(data)
    if json.loads(output) != data:
        raise ValueError("render() gir ikke samme data tilbake")
    target = TARGET.relative_to(ROOT)
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != output:
            print(f"{target} er utdatert — kjør skriptet uten --check", file=sys.stderr)
            return 1
        print("OK")
        return 0
    TARGET.write_text(output, encoding="utf-8")
    print(f"Skrev {target} ({data['meta']['case_count']} caser)")
    for sheet in data["sheets"]:
        print(f"  {sheet['gender']} {sheet['sheet']}: {len(sheet['cases'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
