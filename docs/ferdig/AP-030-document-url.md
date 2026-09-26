# AP-030 — `document_url` for Tyrving-kildene

Oppgaven hadde ingen egen fil i `docs/active/`. Beskrivelsen står i backloggen: fyll inn `document_url` for
Tyrving-DOC-ene og `.xls` i `meta.source_documents` fra lenkene i `sources/README.md`. PDF-ene og `.xlsx` beholder
`null`. Kjør `extract_tyrving_params.py` på nytt og vis at bare `meta` endres.

## Sluttrapport (fylles av Code)

- **Gjort:** `SOURCE_DOCUMENTS` i `scripts/extract_tyrving_params.py` har nå lenkene fra `sources/README.md` for
  `tyrving-2014-gutter.doc` og `tyrving-2014-jenter.doc`. `.xls` var ikke med i `source_documents` fra før, så den
  er lagt til som sjette dokument (`nfif-tyrving-2014-xls`, «NFIFs gjeldende regneark (kryssjekk)») med lenken
  `…/poengtabell-tyrvingtabellen.xls`. PDF-ene og `.xlsx` har fortsatt `null`. `tyrving_parameters_2014.json` er
  generert på nytt.
- **Bevis:** `git diff` på JSON-en viser bare endringer i `meta.source_documents`: to `null` er byttet mot
  DOC-lenkene, og én ny oppføring for `.xls` (sha256 `d23266b8…`, samme som i `SHA256SUMS`). Parametrene og
  `meta.sources` er uendret. `pytest -q` 105 passed, `ruff check .` og `mypy athletics_scoring` er grønne, og
  `extract_tyrving_params.py --check` gir OK.
- **Valg tatt underveis:** `.xls` ble lagt til som ny oppføring, fordi oppgaven ber om lenken i
  `source_documents` og fila manglet der. Motoren bruker den ikke som `ref`. `meta.sources` (filene
  parametrene faktisk er hentet fra) er ikke endret. `retrieved` er 2026-09-25, datoen for nedlastingen i
  `sources/README.md`.
- **Avvik fra oppgaven:** Ingen.
- **Funn som bør bli egne oppgaver:** Ingen.
