"""Leser Tyrvingtabellen 2014 fra DOC-filene, som kontroll av PDF-leseren (scripts/tyrving_pdf.py).

LibreOffice konverterer DOC til tabulatordelt tekst der tomme celler er bevart, så de ti siste
feltene i hver tabellrad er alltid 10–19 år. Det er en helt annen leseveg enn PDF-ens x-posisjoner.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from tyrving_pdf import (
    NAMED,
    PdfRecord,
    canonical_implement,
    event_id,
    parse_number,
    parse_result,
)

ROOT = Path(__file__).resolve().parent.parent
DOCS = {
    "M": ROOT / "sources" / "tyrving" / "tyrving-2014-gutter.doc",
    "F": ROOT / "sources" / "tyrving" / "tyrving-2014-jenter.doc",
}
AGES = range(10, 20)


def doc_to_text(path: Path) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        subprocess.run(
            ["soffice", f"-env:UserInstallation={(workdir / 'profile').as_uri()}", "--headless",
             "--convert-to", "txt:Text", "--outdir", str(workdir), str(path)],
            check=True,
            capture_output=True,
        )  # fmt: skip
        return (workdir / f"{path.stem}.txt").read_text(encoding="utf-8-sig")


def _values(fields: list[str]) -> dict[int, str]:
    return {age: text for age, text in zip(AGES, fields[-10:], strict=True) if text.strip()}


def parse_doc(text: str, gender: str) -> list[PdfRecord]:
    records: list[PdfRecord] = []
    label: list[str] = []
    block: dict[str, dict[int, str] | list[float]] = {}
    for line in text.splitlines():
        fields = line.split("\t")
        if len(fields) < 11 or fields[0] in {"Gutter", "Jenter"}:
            if len(fields) == 1 and line.strip() and not line.startswith(("Bruk", "Tabellen", "©")):
                label.append(line.strip())
            continue
        marker = next((f for f in fields if f in {"Over 1000p", "1000p-80%", "Under 80%"}), None)
        if marker:
            index = fields.index(marker)
            label += [f for f in fields[:index] if f.strip()]
            factor = parse_number(fields[index + 1])
            if marker == "Over 1000p":
                block = {"f": [factor], "h": _values(fields)}
            elif marker == "1000p-80%":
                block["f"].append(factor)  # type: ignore[union-attr]
                block["80"] = _values(fields)
            else:
                block["f"].append(factor)  # type: ignore[union-attr]
                block["p"] = _values(fields)
                full = " ".join(label)
                name = next(n for n in sorted(NAMED, key=len, reverse=True) if full.startswith(n))
                record = PdfRecord(
                    gender=gender,
                    label=full,
                    event_id=event_id(name),
                    implement=canonical_implement(full[len(name) :]),
                    formula_type="three_interval",
                    multipliers=tuple(block["f"]),  # type: ignore[arg-type]
                )
                for age, value in block["h"].items():  # type: ignore[union-attr]
                    record.h1000[age] = parse_result(value)[0]
                record.checks = {"80": block["80"], "p": block["p"]}  # type: ignore[dict-item]
                records.append(record)
                label, block = [], {}
            continue
        # Enkel rad: etikett og utstyr, multiplikator, deretter ti alderskolonner.
        head = fields[: len(fields) - 10]
        multiplier = next(f for f in reversed(head) if re.fullmatch(r"\d+(,\d+)?", f))
        spec_fields = head[1 : head.index(multiplier)]
        full = " ".join([head[0], *spec_fields])
        record = PdfRecord(
            gender=gender,
            label=full,
            event_id=event_id(full),
            implement=canonical_implement(" ".join(spec_fields)),
            formula_type="simple_quotient",
            multipliers=(parse_number(multiplier),),
        )
        for age, value in _values(fields).items():
            record.h1000[age] = parse_result(value)[0]
        records.append(record)
        label = []
    return records


def parse_all() -> list[PdfRecord]:
    return [r for gender, path in DOCS.items() for r in parse_doc(doc_to_text(path), gender)]
