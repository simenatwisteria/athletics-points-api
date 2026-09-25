"""Leser Tyrvingtabellen 2014 fra de offisielle PDF-ene (én side per kjønn).

PDF-ene har ingen tabellstruktur som overlever tekstuttrekk: tomme celler forsvinner. Verdiene
knyttes derfor til alder etter x-posisjon, mot kolonneoverskriftene «10 år» … «19 år».

Oppsett:
- Gutter: to tabeller side om side (løp + hopp + kule/diskos til venstre, resten til høyre),
  hver med egen overskriftsrad.
- Jenter: én bred tabell.
- Enkle rader: ``<øvelse> [utstyr] <multiplikator> <1000p-verdier per alder>``.
- Tre-intervall-blokker (kast, stav): tre linjer ``Over 1000p f1 1000p …``, ``1000p-80% f2 80% …``,
  ``Under 80% f3 Poeng …``, med øvelsesnavn og utstyr på egne linjer eller foran nøkkelordene.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
PDFS = {
    "M": ROOT / "sources" / "tyrving" / "tyrving-2014-gutter.pdf",
    "F": ROOT / "sources" / "tyrving" / "tyrving-2014-jenter.pdf",
}
LINE_TOLERANCE = 2.5

NAMED = {
    "Høyde": "high_jump",
    "Høyde u.t.": "high_jump_standing",
    "Stav": "pole_vault",
    "Lengde": "long_jump",
    "Lengde u.t.": "long_jump_standing",
    "Tresteg": "triple_jump",
    "Kule": "shot_put",
    "Diskos": "discus",
    "Slegge": "hammer",
    "Spyd": "javelin",
    "Liten ball": "ball_throw",
    "Slengball": "swing_ball",
}
RUNNING = {40: "sprint", 60: "sprint", 80: "sprint", 100: "sprint", 200: "sprint", 300: "sprint",
           400: "sprint", 600: "middle", 800: "middle", 1000: "middle", 1500: "middle",
           2000: "distance", 3000: "distance", 5000: "distance", 10000: "distance"}  # fmt: skip


@dataclass
class PdfRecord:
    """Én rad (enkel) eller én blokk (tre-intervall) i PDF-en."""

    gender: str
    label: str
    event_id: str
    implement: tuple[tuple[float, str], ...]
    formula_type: str
    multipliers: tuple[float, ...]
    h1000: dict[int, float] = field(default_factory=dict)
    typos: list[str] = field(default_factory=list)
    checks: dict[str, dict[int, str]] = field(default_factory=dict)


def parse_number(text: str) -> float:
    return float(text.replace(",", "."))


def parse_result(text: str) -> tuple[float, str | None]:
    """Resultat i sekunder eller meter, pluss en merknad hvis teksten har en skrivefeil."""
    if re.fullmatch(r"\d+[.,]\d+", text):
        typo = f"«{text}» har komma" if "," in text else None
        return parse_number(text), typo
    if m := re.fullmatch(r"(\d+):(\d{2})\.(\d+)", text):
        return int(m[1]) * 60 + float(f"{m[2]}.{m[3]}"), None
    if m := re.fullmatch(r"(\d+)[:.](\d{2})[:.](\d{2})\.(\d)", text):
        typo = None if text.count(":") == 2 else f"«{text}» skrevet som t:mm.ss.t"
        return int(m[1]) * 3600 + int(m[2]) * 60 + float(f"{m[3]}.{m[4]}"), typo
    if m := re.fullmatch(r"(\d+)\.(\d{2})\.(\d{2})", text):
        return int(m[1]) * 60 + float(f"{m[2]}.{m[3]}"), f"«{text}» har punktum i stedet for kolon"
    raise ValueError(f"Kan ikke tolke resultat: {text!r}")


def canonical_implement(text: str | None) -> tuple[tuple[float, str], ...]:
    """'4kg/119,5cm', '4 kg 119,5 cm' og '4000 g' blir like. Tekst som «Kort reim» ignoreres."""
    if not text:
        return ()
    parts = []
    for number, unit in re.findall(r"(\d+(?:,\d+)?)\s*(kg|g|cm|m)\b", text):
        value = parse_number(number)
        if unit == "kg":
            value, unit = round(value * 1000, 6), "g"
        parts.append((value, unit))
    return tuple(parts)


def event_id(label: str) -> str:
    label = " ".join(label.split())
    for name in sorted(NAMED, key=len, reverse=True):
        if label == name or label.startswith(name + " "):
            return NAMED[name]
    m = re.match(r"(\d+) ?m(H)?\b ?(Kappgang)?", label)
    if not m:
        raise ValueError(f"Ukjent øvelse i PDF: {label!r}")
    distance = int(m[1])
    if m[3]:
        return f"racewalk_{distance}m"
    if m[2]:
        return f"steeplechase_{distance}m" if distance >= 1500 else f"hurdles_{distance}m"
    return f"{RUNNING[distance]}_{distance}m"


def _lines(words: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    lines: list[list[dict[str, Any]]] = []
    for word in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(word["top"] - lines[-1][0]["top"]) <= LINE_TOLERANCE:
            lines[-1].append(word)
        else:
            lines.append([word])
    return [sorted(line, key=lambda w: w["x0"]) for line in lines]


@dataclass
class _Table:
    x_min: float
    x_max: float
    top: float
    multiplier_x1: float
    columns: dict[int, float]  # alder → x-senter

    def age_for(self, word: dict[str, Any]) -> int:
        center = (word["x0"] + word["x1"]) / 2
        return min(self.columns, key=lambda age: abs(self.columns[age] - center))


def _tables(words: list[dict[str, Any]]) -> list[_Table]:
    header_lines = [
        line for line in _lines(words) if any(w["text"] == "Multiplikator" for w in line)
    ]
    tables = []
    for line in header_lines:
        # Overskriftslinjen kan slås sammen med en datarad i nabotabellen; tabellen starter ved
        # «Gutter»/«Jenter» rett foran «Multiplikator».
        index = next(i for i, w in enumerate(line) if w["text"] == "Multiplikator")
        mult, title = line[index], line[index - 1]
        columns = {
            int(w["text"]): (w["x0"] + nxt["x1"]) / 2
            for w, nxt in zip(line[index:], line[index + 1 :], strict=False)
            if re.fullmatch(r"1\d", w["text"]) and nxt["text"] == "år"
        }
        tables.append(_Table(title["x0"] - 5, 10_000, title["top"], mult["x1"], columns))
    # Jenter: overskriften for 17-19 år står i samme linje og hører til samme tabell.
    tables.sort(key=lambda t: t.x_min)
    for table, following in itertools.pairwise(tables):
        table.x_max = following.x_min
    return tables


def _is_value(word: dict[str, Any], table: _Table) -> bool:
    return bool(word["x0"] > table.multiplier_x1 + 1)


def parse_pdf(path: Path, gender: str) -> list[PdfRecord]:
    with pdfplumber.open(path) as pdf:
        if len(pdf.pages) != 1:
            raise ValueError(f"{path.name}: forventet én side, fant {len(pdf.pages)}")
        words = pdf.pages[0].extract_words()

    records: list[PdfRecord] = []
    for table in _tables(words):
        region = [w for w in words if table.x_min <= w["x0"] < table.x_max and w["top"] > table.top]
        footer = min(
            (w["top"] for w in region if w["text"].lower() in {"bruk", "©"}), default=10_000.0
        )
        region = [w for w in region if w["top"] < footer - 1]
        records.extend(_parse_table(_lines(region), table, gender))
    return records


def _parse_table(lines: list[list[dict[str, Any]]], table: _Table, gender: str) -> list[PdfRecord]:
    records: list[PdfRecord] = []
    pending_label: list[str] = []
    block: dict[str, Any] | None = None
    for line in lines:
        texts = [w["text"] for w in line]
        values = [w for w in line if _is_value(w, table)]
        keyword = next(
            (i for i, w in enumerate(line) if w["text"] in {"Over", "1000p-80%", "Under"}), None
        )
        if keyword is not None:
            pending_label += [w["text"] for w in line[:keyword]]
            marker = line[keyword]["text"]
            factor_word = next(w for w in line[keyword:] if re.fullmatch(r"\d+(,\d+)?", w["text"]))
            if marker == "Over":
                block = {"f": [parse_number(factor_word["text"])], "h": values, "80": [], "p": []}
            elif block is None:
                raise ValueError(f"Tre-intervall-linje uten «Over»-linje: {texts}")
            elif marker == "1000p-80%":
                block["f"].append(parse_number(factor_word["text"]))
                block["80"] = values
            else:
                block["f"].append(parse_number(factor_word["text"]))
                block["p"] = values
                label = " ".join(pending_label)
                name = next(n for n in sorted(NAMED, key=len, reverse=True) if n in label)
                records.append(_record(gender, label, name, "three_interval", block, table))
                pending_label, block = [], None
            continue

        multiplier = next(
            (w for w in line if abs(w["x1"] - table.multiplier_x1) < 4 and not _is_value(w, table)),
            None,
        )
        if multiplier is None or not re.fullmatch(r"\d+(,\d+)?", multiplier["text"]):
            pending_label += texts  # rene etikettlinjer (øvelsesnavn, utstyr)
            continue
        label = " ".join(w["text"] for w in line if w["x1"] < multiplier["x0"])
        data = {"f": [parse_number(multiplier["text"])], "h": values}
        records.append(_record(gender, label, label, "simple_quotient", data, table))
        pending_label = []
    return records


def _record(
    gender: str, label: str, name: str, formula_type: str, data: dict[str, Any], table: _Table
) -> PdfRecord:
    ident = event_id(name if formula_type == "three_interval" else label)
    spec = label[len(name) :] if formula_type == "three_interval" else label
    if formula_type == "simple_quotient":
        spec = re.sub(r"^\d+ ?m(H)?\b ?(Kappgang)?", "", spec)
    record = PdfRecord(
        gender=gender,
        label=" ".join(label.split()),
        event_id=ident,
        implement=canonical_implement(spec),
        formula_type=formula_type,
        multipliers=tuple(data["f"]),
    )
    for word in data["h"]:
        value, typo = parse_result(word["text"])
        record.h1000[table.age_for(word)] = value
        if typo:
            record.typos.append(typo)
    for key in ("80", "p"):
        column: dict[int, str] = {table.age_for(w): w["text"] for w in data.get(key, [])}
        if column:
            record.checks[key] = column
            record.typos += [f"«{t}» har komma" for t in column.values() if "," in t]
    return record


def parse_all() -> list[PdfRecord]:
    return [record for gender, path in PDFS.items() for record in parse_pdf(path, gender)]


if __name__ == "__main__":
    for record in parse_all():
        print(record.gender, record.event_id, record.implement, record.multipliers, record.h1000)


@dataclass
class Difference:
    """Et avvik mellom én regnearkrad og PDF-en."""

    sheet: str
    row: int
    field: str
    excel: Any
    pdf: Any


def compare(entries: list[dict[str, Any]], records: list[PdfRecord]) -> list[Difference]:
    """Sammenligner regnearkets oppføringer (som i tyrving_parameters_2014.json) med PDF-en.

    Hver oppføring matches mot PDF-rader med samme kjønn og øvelse som har en verdi for alderen.
    Finnes flere, velges den med samme utstyr. Returnerer også PDF-verdier uten rad i regnearket.
    """
    differences: list[Difference] = []
    used: set[tuple[int, int]] = set()
    for entry in entries:
        sheet, row = entry["source"]["sheet"], entry["source"]["row"]
        candidates = [
            r
            for r in records
            if r.gender == entry["gender"]
            and r.event_id == entry["event_id"]
            and entry["age"] in r.h1000
        ]
        implement = canonical_implement(entry["implement"])
        matching = [r for r in candidates if r.implement == implement] or candidates
        if len(matching) != 1:
            differences.append(Difference(sheet, row, "finnes i PDF", True, len(matching) == 1))
            continue
        record = matching[0]
        used.add((id(record), entry["age"]))
        if record.implement != implement:
            differences.append(Difference(sheet, row, "implement", implement, record.implement))
        if record.formula_type != entry["formula_type"]:
            differences.append(
                Difference(sheet, row, "formula_type", entry["formula_type"], record.formula_type)
            )
        pdf_h1000, excel_h1000 = record.h1000[entry["age"]], entry["params"]["h1000"]
        if abs(pdf_h1000 - excel_h1000) > 1e-9:
            differences.append(Difference(sheet, row, "h1000", excel_h1000, pdf_h1000))
        names = ("f1", "f2", "f3") if record.formula_type == "three_interval" else ("quotient",)
        for name, pdf_value in zip(names, record.multipliers, strict=True):
            excel_value = entry["params"].get(name)
            if excel_value is None or abs(excel_value - pdf_value) > 1e-9:
                differences.append(Difference(sheet, row, name, excel_value, pdf_value))
    for record in records:
        for age in record.h1000:
            if (id(record), age) not in used:
                label = f"{record.gender} {age} år {record.label}"
                differences.append(Difference("PDF", 0, "mangler i regnearket", None, label))
    return differences
