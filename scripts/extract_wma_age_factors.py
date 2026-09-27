"""WMA Age Grading: ettårige aldersfaktorer → athletics_scoring/data/wma_age_factors_2023.json.

Leser PDF-side 5–16 i ``sources/wma/wma-2023-age-factors.pdf`` som tekstlinjer med ``pdfplumber``
(BV-040). Hver side har én aldersrad per linje (30–70 eller 71–110). Sidene kommer i par per kjønn
og blokk:

1. 60 m–10 000 m, inkludert mile (11 kolonner)
2. 60 m hekk, kort og lang hekk, hinder, hopp, kule, diskos og slegge (11 kolonner)
3. spyd, vektkast, kappgang og gateløp (8 kolonner)

Kolonneoverskriftene kontrolleres mot konstantene her, og skriptet feiler hvis en side har et annet
antall rader eller kolonner enn forventet. ``oracle_wma_age_factors.py`` leser de samme sidene på en
annen måte (ord med koordinater), og testene krever at de to lesingene er enige.

    python scripts/extract_wma_age_factors.py [--check]

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

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "athletics_scoring" / "data" / "wma_age_factors_2023.json"
PDF = ROOT / "sources" / "wma" / "wma-2023-age-factors.pdf"
SOURCE_KEY = "wma-2023-age-factors"
SOURCE_DOCUMENT: dict[str, Any] = {
    "key": SOURCE_KEY,
    "title": "WMA 2023 Age Factors: ettårige aldersfaktorer (PDF-side 5–10 kvinner, 11–16 menn)",
    "publisher": "World Masters Athletics (WMA)",
    "official_page": "https://world-masters-athletics.org/",
    "document_url": (
        "https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf"
    ),
    "path": PDF,
    "retrieved": "2026-09-26",
}

FIRST_PAGE = {"F": 4, "M": 10}  # PDF-side 5 og 11, nullindeksert
TITLE = {"F": "2023 WOMEN'S ONE-YEAR AGE FACTORS", "M": "2023 MEN'S ONE-YEAR AGE FACTORS"}
PAGE_AGES = [list(range(30, 71)), list(range(71, 111))]
AGES = list(range(30, 111))

# Overskriftslinjene slik de står i teksten, og kolonnene i rekkefølge: (overskrift, event_id,
# navn, måltype). Lik for kvinner og menn.
BLOCKS: list[tuple[list[str], list[tuple[str, str, str, str]]]] = [
    (
        ["Age 60m 100m 200m 400m 800m 1000m 1500m Mile 3000m 5000m 10000m"],
        [
            ("60m", "sprint_60m", "60 m", "time"),
            ("100m", "sprint_100m", "100 m", "time"),
            ("200m", "sprint_200m", "200 m", "time"),
            ("400m", "sprint_400m", "400 m", "time"),
            ("800m", "middle_800m", "800 m", "time"),
            ("1000m", "middle_1000m", "1000 m", "time"),
            ("1500m", "middle_1500m", "1500 m", "time"),
            ("Mile", "middle_mile", "Engelsk mil", "time"),
            ("3000m", "distance_3000m", "3000 m", "time"),
            ("5000m", "distance_5000m", "5000 m", "time"),
            ("10000m", "distance_10000m", "10 000 m", "time"),
        ],
    ),
    (
        [
            "60m Short Long Steeple High Pole Long Triple Shot",
            "Age Discus Hammer",
            "Hurdles Hurdles Hurdles Chase Jump Vault Jump Jump Put",
        ],
        [
            ("60m Hurdles", "hurdles_60m", "60 m hekk", "time"),
            ("Short Hurdles", "hurdles_short", "Kort hekk", "time"),
            ("Long Hurdles", "hurdles_long", "Lang hekk", "time"),
            ("Steeple Chase", "steeplechase", "Hinder", "time"),
            ("High Jump", "high_jump", "Høyde", "distance"),
            ("Pole Vault", "pole_vault", "Stav", "distance"),
            ("Long Jump", "long_jump", "Lengde", "distance"),
            ("Triple Jump", "triple_jump", "Tresteg", "distance"),
            ("Shot Put", "shot_put", "Kule", "distance"),
            ("Discus", "discus", "Diskos", "distance"),
            ("Hammer", "hammer", "Slegge", "distance"),
        ],
    ),
    (
        [
            "3000m 5000m 10k 20k Half",
            "Age Javelin Weight Marathon",
            "RaceWalk RaceWalk RaceWalk RaceWalk Marathon",
        ],
        [
            ("Javelin", "javelin", "Spyd", "distance"),
            ("Weight", "weight_throw", "Vektkast", "distance"),
            ("3000m RaceWalk", "racewalk_3000m", "3000 m kappgang", "time"),
            ("5000m RaceWalk", "racewalk_5000m", "5000 m kappgang", "time"),
            ("10k RaceWalk", "racewalk_10000m", "10 000 m kappgang", "time"),
            ("20k RaceWalk", "racewalk_20000m", "20 000 m kappgang", "time"),
            ("Half Marathon", "half_marathon", "Halvmaraton", "time"),
            ("Marathon", "marathon", "Maraton", "time"),
        ],
    ),
]
# Kjente verdier (oppgavefila AP-014). Kontrollerer kolonnerekkefølgen før noe skrives.
KNOWN_FACTORS = [
    ("F", 45, "sprint_100m", "0.9441"),
    ("M", 71, "sprint_100m", "0.7803"),
    ("F", 45, "sprint_60m", "0.9613"),
    ("M", 60, "hurdles_long", "1.1628"),
    ("M", 60, "steeplechase", "1.2613"),
    ("M", 60, "discus", "0.9653"),
]
ROW_RE = re.compile(r"^(\d{2,3})((?: \d+\.\d{4})+)$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_sha256sums() -> None:
    sums = {}
    for line in (ROOT / "sources" / "SHA256SUMS").read_text("utf-8").splitlines():
        digest, path = line.split(maxsplit=1)
        sums[ROOT / "sources" / path] = digest
    if _sha256(PDF) != sums[PDF]:
        raise ValueError(f"{PDF} stemmer ikke med sources/SHA256SUMS")


def _read_page(text: str, page: int, gender: str, block: int, half: int) -> dict[int, list[str]]:
    """Aldersradene på én side: alder → faktorer som tekst med fire desimaler."""
    headers, columns = BLOCKS[block]
    lines = text.splitlines()
    if lines[0] != TITLE[gender]:
        raise ValueError(f"PDF-side {page}: uventet tittel {lines[0]!r}")
    if lines[1 : 1 + len(headers)] != headers:
        raise ValueError(f"PDF-side {page}: uventede overskrifter {lines[1 : 1 + len(headers)]}")
    rows: dict[int, list[str]] = {}
    for line in lines[1 + len(headers) :]:
        match = ROW_RE.match(line)
        if match is None:
            if not line.startswith("Page "):
                raise ValueError(f"PDF-side {page}: uventet linje {line!r}")
            continue
        numbers = match.group(2).split()
        if len(numbers) != len(columns):
            raise ValueError(f"PDF-side {page}, alder {match.group(1)}: {len(numbers)} tall")
        rows[int(match.group(1))] = numbers
    if list(rows) != PAGE_AGES[half]:
        raise ValueError(f"PDF-side {page}: uventede aldersrader {list(rows)}")
    return rows


def read_factors() -> dict[str, dict[str, dict[int, str]]]:
    """Kjønn → event_id → alder → faktor (tekst med fire desimaler), 30–110."""
    out: dict[str, dict[str, dict[int, str]]] = {}
    with pdfplumber.open(PDF) as pdf:
        if len(pdf.pages) != 16:
            raise ValueError(f"{PDF.name}: {len(pdf.pages)} sider, ventet 16")
        for gender, first in FIRST_PAGE.items():
            events = out.setdefault(gender, {})
            for block, (_, columns) in enumerate(BLOCKS):
                for half in (0, 1):
                    index = first + 2 * block + half
                    text = pdf.pages[index].extract_text() or ""
                    rows = _read_page(text, index + 1, gender, block, half)
                    for age, numbers in rows.items():
                        for (_, event_id, _, _), number in zip(columns, numbers, strict=True):
                            events.setdefault(event_id, {})[age] = number
    for gender, age, event_id, expected in KNOWN_FACTORS:
        if out[gender][event_id][age] != expected:
            raise ValueError(f"{gender}{age} {event_id}: {out[gender][event_id][age]} ≠ {expected}")
    return out


def extract() -> dict[str, Any]:
    _check_sha256sums()
    factors = read_factors()
    entries = []
    for gender, first in FIRST_PAGE.items():
        for block, (_, columns) in enumerate(BLOCKS):
            pages = f"PDF-side {first + 2 * block + 1}–{first + 2 * block + 2}"
            for column, event_id, name, measure in columns:
                per_age = factors[gender][event_id]
                if sorted(per_age) != AGES:
                    raise ValueError(f"{gender} {event_id}: mangler aldre")
                entries.append(
                    {
                        "event_id": event_id,
                        "name": name,
                        "gender": gender,
                        "measure": measure,
                        "factor_column": column,
                        "source": {"ref": SOURCE_KEY, "location": f"{pages}, «{column}»"},
                        "factors": {str(age): float(per_age[age]) for age in AGES},
                    }
                )
    return {
        "meta": {
            "scoring_system": "wma_age_grading",
            "version": "2023",
            "source": "WMA 2023 Age Factors, ettårige faktorer (BV-040)",
            "source_documents": [
                {
                    "key": SOURCE_DOCUMENT["key"],
                    "title": SOURCE_DOCUMENT["title"],
                    "publisher": SOURCE_DOCUMENT["publisher"],
                    "official_page": SOURCE_DOCUMENT["official_page"],
                    "document_url": SOURCE_DOCUMENT["document_url"],
                    "local_path": str(PDF.relative_to(ROOT)),
                    "sha256": _sha256(PDF),
                    "retrieved": SOURCE_DOCUMENT["retrieved"],
                }
            ],
            "generated_by": "scripts/extract_wma_age_factors.py",
            "entry_count": len(entries),
            "ages": [AGES[0], AGES[-1]],
        },
        "entries": entries,
    }


def render(data: dict[str, Any]) -> str:
    """Innrykk, men alle faktorene for en øvelse på én linje."""
    text = json.dumps(data, ensure_ascii=False, indent=2)

    def one_line(match: re.Match[str]) -> str:
        body = json.loads("{" + match.group(2) + "}")
        return match.group(1) + json.dumps(body)

    text = re.sub(r'("factors": )\{([^{}]*)\}', one_line, text)
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
