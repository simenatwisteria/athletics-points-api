"""DOC-filene og PDF-ene gir identiske Tyrving-tabeller.

To uavhengige leseveier (tabulatorfelt i DOC, x-posisjoner i PDF) som må gi samme svar. Det
bekrefter PDF-leseren, og at DOC og PDF sier det samme i alle avvikene fra regnearket
(docs/KILDEAVVIK.md).
"""

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import tyrving_doc  # noqa: E402
import tyrving_pdf  # noqa: E402


def _key(record: tyrving_pdf.PdfRecord) -> tuple[object, ...]:
    return (
        record.gender,
        record.event_id,
        record.implement,
        record.formula_type,
        record.multipliers,
        tuple(sorted(record.h1000.items())),
        tuple(sorted((k, tuple(sorted(v.items()))) for k, v in record.checks.items())),
    )


@pytest.mark.skipif(shutil.which("soffice") is None, reason="krever LibreOffice (soffice)")
def test_doc_equals_pdf() -> None:
    doc = sorted(map(_key, tyrving_doc.parse_all()), key=repr)
    pdf = sorted(map(_key, tyrving_pdf.parse_all()), key=repr)
    assert len(doc) == 121
    assert doc == pdf
