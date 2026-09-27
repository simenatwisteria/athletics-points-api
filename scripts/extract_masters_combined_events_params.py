"""Masters mangekamp: kildefiler → athletics_scoring/data/masters_combined_events_2023.json.

- Aldersfaktorer per 5-årsklasse (BV-032): WMA Appendix B, PDF-side 4 (kvinner) og 5 (menn), lest
  med ``pdfplumber``. Kolonnerekkefølgen står som konstanter her, og noen kjente verdier fra
  oppgavefila og Appendix B s. 1 kontrolleres før noe skrives.
- Klasser, redskap og hekkehøyde per klasse (BV-034): raden «Vekt:»/«Hhøyde» i NFIFs
  masters-mangekamptabeller. Arkoppsettet deles med ``oracle_masters_combined_events.py``.
- Hvilken tabell i Combined Events hver øvelse slås opp i: hekk under senior-distansen bruker
  «Short Hurdles»-faktoren og tabellen for 110 m hekk (menn) eller 100 m hekk (kvinner). Avklart
  mot NFIF-arkene i AP-016.

    python scripts/extract_masters_combined_events_params.py [--check]

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
import pdfplumber
from oracle_masters_combined_events import (
    AGES,
    CLASS_PREFIX,
    IMPLEMENT_LABELS,
    SHEETS,
    SOURCES,
    _col,
    _implement,
    _text,
)

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "athletics_scoring" / "data" / "masters_combined_events_2023.json"
APPENDIX_B = ROOT / "sources" / "wma" / "wma-2023-appendix-b-combined-events.pdf"

APPENDIX_B_KEY = "wma-2023-appendix-b"
NFIF_KEYS = {"M": "nfif-masters-mangekamp-menn", "F": "nfif-masters-mangekamp-kvinner"}
NFIF_PAGE = "https://www.friidrett.no/aktiviteter/masters/poengberegning/"
NFIF_URL = "https://www.friidrett.no/contentassets/d8222e75a783431481bdf30d9fa02720/"
SOURCE_DOCUMENTS: list[dict[str, Any]] = [
    {
        "key": APPENDIX_B_KEY,
        "title": (
            "WMA Rulebook 2023, Appendix B: Scoring of WMA Combined Events "
            "(metode s. 1, aldersfaktorer PDF-side 4–5)"
        ),
        "publisher": "World Masters Athletics (WMA)",
        "official_page": "https://world-masters-athletics.org/",
        "document_url": (
            "https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-WMA-Appendix-B.pdf"
        ),
        "path": APPENDIX_B,
        "retrieved": "2026-09-26",
    },
    {
        "key": NFIF_KEYS["M"],
        "title": "Mangekamptabellen for menn (masters, redskap per klasse i raden «Vekt:»)",
        "publisher": "Norges Friidrettsforbund (NFIF)",
        "official_page": NFIF_PAGE,
        "document_url": f"{NFIF_URL}mangekamptabellen-for-menn.xlsx",
        "path": SOURCES["M"],
        "retrieved": "2026-09-26",
    },
    {
        "key": NFIF_KEYS["F"],
        "title": "Mangekamptabellen for kvinner (masters, redskap per klasse i raden «Vekt:»)",
        "publisher": "Norges Friidrettsforbund (NFIF)",
        "official_page": NFIF_PAGE,
        "document_url": f"{NFIF_URL}mangekamptabellen-for-kvinner.xlsm",
        "path": SOURCES["F"],
        "retrieved": "2026-09-26",
    },
]

# Kolonnene i faktortabellene, i rekkefølgen på PDF-sidene (lik for kvinner og menn).
TRACK_COLUMNS = ["60m", "100m", "200m", "400m", "800m", "1000m", "1500m", "60m Hurdles",
                 "Short Hurdles"]  # fmt: skip
FIELD_COLUMNS = ["High Jump", "Pole Vault", "Long Jump", "Shot Put", "Discus", "Hammer", "Javelin",
                 "Weight"]  # fmt: skip
FACTOR_PAGES = {"F": 3, "M": 4}  # PDF-side 4 og 5, nullindeksert
TABLE_AGES = [str(age) for age in range(35, 111, 5)]

# event_id → (navn, tabelløvelse i Combined Events, faktorkolonne). Per kjønn.
EVENTS: dict[str, dict[str, tuple[str, str, str]]] = {
    "M": {
        "sprint_60m": ("60 m", "sprint_60m", "60m"),
        "sprint_100m": ("100 m", "sprint_100m", "100m"),
        "sprint_200m": ("200 m", "sprint_200m", "200m"),
        "sprint_400m": ("400 m", "sprint_400m", "400m"),
        "middle_1000m": ("1000 m", "middle_1000m", "1000m"),
        "middle_1500m": ("1500 m", "middle_1500m", "1500m"),
        "hurdles_60m": ("60 m hekk", "hurdles_60m", "60m Hurdles"),
        "hurdles_110m": ("110 m hekk", "hurdles_110m", "Short Hurdles"),
        "hurdles_100m": ("100 m hekk", "hurdles_110m", "Short Hurdles"),
        "hurdles_80m": ("80 m hekk", "hurdles_110m", "Short Hurdles"),
        "high_jump": ("Høyde", "high_jump", "High Jump"),
        "pole_vault": ("Stav", "pole_vault", "Pole Vault"),
        "long_jump": ("Lengde", "long_jump", "Long Jump"),
        "shot_put": ("Kule", "shot_put", "Shot Put"),
        "discus": ("Diskos", "discus", "Discus"),
        "hammer": ("Slegge", "hammer", "Hammer"),
        "javelin": ("Spyd", "javelin", "Javelin"),
        "weight_throw": ("Vektkast", "weight_throw", "Weight"),
    },
    "F": {
        "sprint_60m": ("60 m", "sprint_60m", "60m"),
        "sprint_100m": ("100 m", "sprint_100m", "100m"),
        "sprint_200m": ("200 m", "sprint_200m", "200m"),
        "sprint_400m": ("400 m", "sprint_400m", "400m"),
        "middle_800m": ("800 m", "middle_800m", "800m"),
        "middle_1500m": ("1500 m", "middle_1500m", "1500m"),
        "hurdles_60m": ("60 m hekk", "hurdles_60m", "60m Hurdles"),
        "hurdles_100m": ("100 m hekk", "hurdles_100m", "Short Hurdles"),
        "hurdles_80m": ("80 m hekk", "hurdles_100m", "Short Hurdles"),
        "high_jump": ("Høyde", "high_jump", "High Jump"),
        "pole_vault": ("Stav", "pole_vault", "Pole Vault"),
        "long_jump": ("Lengde", "long_jump", "Long Jump"),
        "shot_put": ("Kule", "shot_put", "Shot Put"),
        "discus": ("Diskos", "discus", "Discus"),
        "hammer": ("Slegge", "hammer", "Hammer"),
        "javelin": ("Spyd", "javelin", "Javelin"),
        "weight_throw": ("Vektkast", "weight_throw", "Weight"),
    },
}
# Kjente verdier (oppgavefila AP-016 og Appendix B s. 1). Kontrollerer kolonnerekkefølgen.
KNOWN_FACTORS = [
    ("M", "50", "100m", "0.9031"),
    ("M", "35", "200m", "0.9791"),
    ("M", "50", "Shot Put", "1.1551"),
    ("F", "35", "High Jump", "1.0205"),
]
ROW_RE = re.compile(r"^(\d{2,3})((?: \d+\.\d{4})+)$", re.MULTILINE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_sha256sums() -> None:
    sums = {}
    for line in (ROOT / "sources" / "SHA256SUMS").read_text("utf-8").splitlines():
        digest, path = line.split(maxsplit=1)
        sums[ROOT / "sources" / path] = digest
    for doc in SOURCE_DOCUMENTS:
        if _sha256(doc["path"]) != sums[doc["path"]]:
            raise ValueError(f"{doc['path']} stemmer ikke med sources/SHA256SUMS")


def read_factors() -> dict[str, dict[str, dict[str, str]]]:
    """Kjønn → faktorkolonne → alder → faktor (tekst med fire desimaler), 35–100."""
    out: dict[str, dict[str, dict[str, str]]] = {}
    with pdfplumber.open(APPENDIX_B) as pdf:
        for gender, page in FACTOR_PAGES.items():
            rows = ROW_RE.findall(pdf.pages[page].extract_text() or "")
            ages = [age for age, _ in rows]
            if ages != TABLE_AGES * 2:
                raise ValueError(f"PDF-side {page + 1}: uventede aldersrader {ages}")
            columns: dict[str, dict[str, str]] = {}
            for i, (age, values) in enumerate(rows):
                names = TRACK_COLUMNS if i < len(TABLE_AGES) else FIELD_COLUMNS
                numbers = values.split()
                if len(numbers) != len(names):
                    raise ValueError(f"PDF-side {page + 1}, alder {age}: {len(numbers)} tall")
                if age in AGES:
                    for name, number in zip(names, numbers, strict=True):
                        columns.setdefault(name, {})[age] = number
            out[gender] = columns
    for gender, age, column, expected in KNOWN_FACTORS:
        if out[gender][column][age] != expected:
            raise ValueError(f"{gender}{age} {column}: {out[gender][column][age]} ≠ {expected}")
    return out


def read_classes() -> dict[str, dict[str, dict[str, str | None]]]:
    """Kjønn → event_id → klasse → redskap, fra arkene med automatisk tid (og tekniske øvelser)."""
    out: dict[str, dict[str, dict[str, str | None]]] = {}
    for gender, path in SOURCES.items():
        wb = openpyxl.load_workbook(path, data_only=True)
        events = out.setdefault(gender, {})
        for title, (blocks, manual, unit) in SHEETS[gender].items():
            if manual:
                continue
            rows = list(wb[title].iter_rows(min_row=1, max_row=3, values_only=True))
            if unit is not None and not (_text(rows[2][0]) or "").startswith(IMPLEMENT_LABELS):
                raise ValueError(f"{path.name} {title}: rad 3 er ikke «Vekt:»/«Hhøyde»")
            for event_id, _, first, last in blocks:
                classes = events.setdefault(event_id, {})
                for c in range(_col(first), _col(last) + 1):
                    age = _text(rows[1][c])
                    if age is None:
                        continue
                    if age not in AGES:
                        raise ValueError(f"{path.name} {title}: uventet klasse {age!r}")
                    implement = None if unit is None else _implement(str(_text(rows[2][c])), unit)
                    classes[f"{CLASS_PREFIX[gender]}{age}"] = implement
    return out


def extract() -> dict[str, Any]:
    _check_sha256sums()
    factors = read_factors()
    classes = read_classes()
    entries = []
    for gender, events in EVENTS.items():
        if set(events) != set(classes[gender]):
            raise ValueError(f"{gender}: øvelsene i arkene avviker: {sorted(classes[gender])}")
        page = FACTOR_PAGES[gender] + 1
        for event_id, (name, table_event_id, column) in events.items():
            per_class = {
                age_class: {
                    "factor": float(factors[gender][column][age_class[1:]]),
                    "implement": implement,
                }
                for age_class, implement in sorted(
                    classes[gender][event_id].items(), key=lambda item: int(item[0][1:])
                )
            }
            entries.append(
                {
                    "event_id": event_id,
                    "name": name,
                    "gender": gender,
                    "table_event_id": table_event_id,
                    "factor_column": column,
                    "classes": per_class,
                    "source": {"ref": APPENDIX_B_KEY, "location": f"PDF-side {page}, «{column}»"},
                    "implement_source": {"ref": NFIF_KEYS[gender], "location": "raden «Vekt:»"},
                }
            )
    return {
        "meta": {
            "scoring_system": "masters_combined_events",
            "version": "2023",
            "source": "WMA Appendix B 2023 (BV-030) med IAAF/WA Combined Events-tabellen",
            "source_documents": [
                {
                    "key": doc["key"],
                    "title": doc["title"],
                    "publisher": doc["publisher"],
                    "official_page": doc["official_page"],
                    "document_url": doc["document_url"],
                    "local_path": str(doc["path"].relative_to(ROOT)),
                    "sha256": _sha256(doc["path"]),
                    "retrieved": doc["retrieved"],
                }
                for doc in SOURCE_DOCUMENTS
            ],
            "generated_by": "scripts/extract_masters_combined_events_params.py",
            "entry_count": len(entries),
            "age_classes": {
                gender: [f"{CLASS_PREFIX[gender]}{age}" for age in AGES] for gender in SOURCES
            },
        },
        "entries": entries,
    }


def render(data: dict[str, Any]) -> str:
    """Innrykk, men én klasse per linje."""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    text = re.sub(
        r'(\n\s+"[MW]\d+": )\{\n\s+"factor": ([\d.]+),\n\s+"implement": ([^\n]+)\n\s+\}',
        r'\1{"factor": \2, "implement": \3}',
        text,
    )
    return text + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="feil hvis JSON-fila er utdatert")
    args = parser.parse_args()

    data = extract()
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
    print(f"Skrev {target} ({data['meta']['entry_count']} øvelser)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
