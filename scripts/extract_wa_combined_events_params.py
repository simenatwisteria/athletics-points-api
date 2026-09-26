"""WA Combined Events: kildefiler → athletics_scoring/data/wa_combined_events_2001.json.

Parametrene står som konstanter her, med sidehenvisning (AP-012). Skriptet kontrollerer dem mot
teksten i kilde-PDF-ene og sjekker SHA-256 mot ``sources/SHA256SUMS`` før det skriver noe.

- Standardøvelsene: WMA Appendix B s. 2 (``sources/wma/wma-2023-appendix-b-combined-events.pdf``).
- Kvinner 1500 m: IAAF Scoring Tables for Combined Events s. 23 (ikke i repoet, B-23), BV-022.
- NFIFs tilleggsøvelser for UM: UM-reglementet §16.5 s. 9
  (``sources/nfif/nfif-um-reglement-2026.pdf``), BV-023.

    python scripts/extract_wa_combined_events_params.py [--check]

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

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "athletics_scoring" / "data" / "wa_combined_events_2001.json"
APPENDIX_B = ROOT / "sources" / "wma" / "wma-2023-appendix-b-combined-events.pdf"
UM_RULES = ROOT / "sources" / "nfif" / "nfif-um-reglement-2026.pdf"

APPENDIX_B_KEY = "wma-2023-appendix-b"
UM_RULES_KEY = "nfif-um-reglement-2026"
SOURCE_DOCUMENTS: list[dict[str, Any]] = [
    {
        "key": APPENDIX_B_KEY,
        "title": "WMA Rulebook 2023, Appendix B: Scoring of WMA Combined Events (parametre s. 2)",
        "publisher": "World Masters Athletics (WMA)",
        "official_page": "https://world-masters-athletics.org/",
        "document_url": (
            "https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-WMA-Appendix-B.pdf"
        ),
        "path": APPENDIX_B,
        "retrieved": "2026-09-26",
    },
    {
        "key": UM_RULES_KEY,
        "title": "Reglement og retningslinjer ved Ungdomsmesterskapene 2026 (§16.4–16.5, s. 9)",
        "publisher": "Norges Friidrettsforbund (NFIF)",
        "official_page": "https://www.friidrett.no/",
        "document_url": (
            "https://www.friidrett.no/siteassets/arrangement/um-2026/um-reglement-2026.2.pdf"
        ),
        "path": UM_RULES,
        "retrieved": "2026-09-26",
    },
]

YOUTH_CLASSES = {"M": ["G15", "G16", "G17"], "F": ["J15", "J16", "J17"]}

# (event_id, navn, enhet, a, b, c, etikett i Appendix B s. 2). Enhet: s = tid, cm = hopp, m = kast.
APPENDIX_B_MEN: list[tuple[str, str, str, str, str, str, str]] = [
    ("sprint_60m", "60 m", "s", "58.015", "11.5", "1.81", "60 m"),
    ("sprint_100m", "100 m", "s", "25.4347", "18", "1.81", "100m"),
    ("sprint_200m", "200 m", "s", "5.8425", "38", "1.81", "200m"),
    ("sprint_400m", "400 m", "s", "1.53775", "82", "1.81", "400m"),
    ("middle_1000m", "1000 m", "s", "0.08713", "305.5", "1.85", "1000m"),
    ("middle_1500m", "1500 m", "s", "0.03768", "480", "1.85", "1500m"),
    ("hurdles_60m", "60 m hekk", "s", "20.5173", "15.5", "1.92", "60m Hurdles"),
    ("hurdles_110m", "110 m hekk", "s", "5.74352", "28.5", "1.92", "110m Hurdles"),
    ("high_jump", "Høyde", "cm", "0.8465", "75", "1.42", "High Jump"),
    ("pole_vault", "Stav", "cm", "0.2797", "100", "1.35", "Pole Vault"),
    ("long_jump", "Lengde", "cm", "0.14354", "220", "1.40", "Long Jump"),
    ("shot_put", "Kule", "m", "51.39", "1.5", "1.05", "Shot Put"),
    ("discus", "Diskos", "m", "12.91", "4", "1.10", "Discus"),
    ("hammer", "Slegge", "m", "13.0941", "5.5", "1.05", "Hammer"),
    ("javelin", "Spyd", "m", "10.14", "7", "1.08", "Javelin"),
    ("weight_throw", "Vektkast", "m", "47.8338", "1.5", "1.05", "Weight"),
]
APPENDIX_B_WOMEN: list[tuple[str, str, str, str, str, str, str]] = [
    ("sprint_60m", "60 m", "s", "46.0849", "13", "1.81", "60 m"),
    ("sprint_100m", "100 m", "s", "17.857", "21", "1.81", "100m"),
    ("sprint_200m", "200 m", "s", "4.99087", "42.5", "1.81", "200m"),
    ("sprint_400m", "400 m", "s", "1.34285", "91.7", "1.81", "400m"),
    ("middle_800m", "800 m", "s", "0.11193", "254", "1.88", "800m"),
    ("hurdles_60m", "60 m hekk", "s", "20.0479", "17", "1.835", "60m Hurdles"),
    ("hurdles_100m", "100 m hekk", "s", "9.23076", "26.7", "1.835", "100m Hurdles"),
    ("high_jump", "Høyde", "cm", "1.84523", "75", "1.348", "High Jump"),
    ("pole_vault", "Stav", "cm", "0.44125", "100", "1.35", "Pole Vault"),
    ("long_jump", "Lengde", "cm", "0.188807", "210", "1.41", "Long Jump"),
    ("shot_put", "Kule", "m", "56.0211", "1.5", "1.05", "Shot Put"),
    ("discus", "Diskos", "m", "12.3311", "3", "1.10", "Discus"),
    ("hammer", "Slegge", "m", "13.3174", "5", "1.05", "Hammer"),
    ("javelin", "Spyd", "m", "15.9803", "3.8", "1.04", "Javelin"),
    ("weight_throw", "Vektkast", "m", "44.2593", "1.5", "1.05", "Weight"),
]
# Kvinner 1500 m mangler i Appendix B. IAAF-boka s. 23 (kvinners tikamp), BV-022.
WOMEN_1500M = ("middle_1500m", "1500 m", "s", "0.02883", "535", "1.88")
# UM-reglementet §16.5 s. 9, BV-023: (kjønn, event_id, navn, a, b, c, klasser, etikett i PDF).
UM_EVENTS: list[tuple[str, str, str, str, str, str, list[str], str]] = [
    ("F", "middle_600m", "600 m (inne)", "0.198890", "185", "1.88", ["J15", "J16"],
     "600m (innendørs) J15+J16"),
    ("M", "middle_800m", "800 m (inne)", "0.160027", "231", "1.836", ["G15", "G16"],
     "800m (innendørs) G15+G16"),
    ("F", "hurdles_80m", "80 m hekk", "12.2092", "22", "1.835", ["J15", "J16"],
     "80m hk (utendørs) J15+J16"),
    ("M", "hurdles_100m", "100 m hekk", "8.73753", "26", "1.83", ["G15", "G16"],
     "100m hk (utendørs) G15+G16"),
]  # fmt: skip


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


def _page_text(path: Path, page: int) -> str:
    with pdfplumber.open(path) as pdf:
        return pdf.pages[page].extract_text() or ""


def _number(text: str) -> str:
    """'.08713' → '0.08713', '1,88' → '1.88'."""
    text = text.replace(",", ".")
    return f"0{text}" if text.startswith(".") else text


def _check_appendix_b() -> None:
    """Konstantene over står ordrett på s. 2 i Appendix B (sidetall 2 er PDF-side 3)."""
    text = _page_text(APPENDIX_B, 2)
    men, women = text.split("\nWOMEN\n")
    men = men.split("\nMEN\n")[1]
    pattern = re.compile(r"^(.+?) a=([\d.]+) b=([\d.]+)(?:s|cm|m)? c=([\d.]+)$", re.MULTILINE)
    for block, constants in ((men, APPENDIX_B_MEN), (women, APPENDIX_B_WOMEN)):
        found = {m[1]: tuple(_number(v) for v in m.groups()[1:]) for m in pattern.finditer(block)}
        expected = {label: (a, b, c) for *_, a, b, c, label in constants}
        if found != expected:
            raise ValueError(f"Appendix B s. 2 avviker fra konstantene: {found} ≠ {expected}")


def _check_um_rules() -> None:
    """Konstantene over står i tabellen i §16.5 (PDF-side 9)."""
    text = _page_text(UM_RULES, 8)
    for _, _, _, a, b, c, _, label in UM_EVENTS:
        match = re.search(re.escape(label) + r" ([\d.,]+) ([\d.,]+) ([\d.,]+)$", text, re.MULTILINE)
        if match is None or tuple(_number(v) for v in match.groups()) != (a, b, c):
            raise ValueError(f"UM-reglementet §16.5 avviker for {label!r}")


def _entry(
    gender: str,
    constant: tuple[str, str, str, str, str, str],
    classes: list[str] | None,
    source: dict[str, str],
) -> dict[str, Any]:
    """``source["ref"]`` er en nøkkel i ``source_documents`` eller et BV-nummer."""
    event_id, name, unit, a, b, c = constant
    return {
        "event_id": event_id,
        "name": name,
        "gender": gender,
        "classes": classes,
        "measure": "time" if unit == "s" else "distance",
        "unit": unit,
        "formula_type": "track" if unit == "s" else "field",
        "params": {"a": float(a), "b": float(b), "c": float(c)},
        "source": source,
    }


def extract() -> dict[str, Any]:
    _check_sha256sums()
    _check_appendix_b()
    _check_um_rules()

    appendix = {"ref": APPENDIX_B_KEY, "location": "s. 2"}
    entries = [_entry("M", row[:6], None, appendix) for row in APPENDIX_B_MEN]
    entries += [_entry("F", row[:6], None, appendix) for row in APPENDIX_B_WOMEN]
    iaaf = {"ref": "BV-022", "location": "IAAF Scoring Tables for Combined Events s. 23"}
    entries.append(_entry("F", WOMEN_1500M, None, iaaf))
    um = {"ref": UM_RULES_KEY, "location": "§16.5 s. 9"}
    for gender, event_id, name, a, b, c, classes, _ in UM_EVENTS:
        entries.append(_entry(gender, (event_id, name, "s", a, b, c), classes, um))

    keys = [(e["event_id"], e["gender"]) for e in entries]
    if len(set(keys)) != len(keys):
        raise ValueError("Samme øvelse to ganger for samme kjønn")
    return {
        "meta": {
            "scoring_system": "wa_combined_events",
            "version": "2001",
            "source": "IAAF Scoring Tables for Combined Events (2001, opptrykk 2016), BV-020",
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
            "generated_by": "scripts/extract_wa_combined_events_params.py",
            "entry_count": len(entries),
            "youth_classes": YOUTH_CLASSES,
            "formula_types": {
                "track": "a * (b - T)^c, T i sekunder",
                "field": "a * (X - b)^c, X i centimeter (hopp) eller meter (kast)",
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
    print(f"Skrev {target} ({json.loads(output)['meta']['entry_count']} øvelser)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
