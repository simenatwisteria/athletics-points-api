# AP-004: Tyrving — oracle-skript med LibreOffice headless → `tests/fixtures/tyrving_cases.json`

**Status:** Klar
**Opprettet:** 2026-09-25 (PROMPT-001)
**Eier:** 🤖 Code (review: 🧑 Simen i AP-005)
**Avhenger av:** AP-002, AP-003 (LibreOffice installert)

## Problemet

Vi trenger en fasit som er uavhengig av Python-motoren. Regnearket har levende formler og kan rekalkuleres.

## Hvorfor nå

Uten låst fasit kan loopen ikke bevise at `TyrvingCalculator` er riktig (ANALYSE 2026-09-06, kap. 3.1 og 4.1).

## Verifiserte fakta

- Input-celler per rad: `D` (minutter) og `E` (sekunder/resultat). Output: `F` (poeng). Se AP-002.
- `soffice` finnes ikke på maskinen per 2026-09-25 → AP-003.

## Løsningsretning

1. `scripts/oracle_tyrving.py`: kopier `.xlsx` til en temp-mappe (aldri i `sources/`), skriv inn resultater i
   `D`/`E` med `openpyxl`, rekalkuler med `soffice --headless --convert-to xlsx`, les `F` med `data_only=True`.
2. Velg resultater per (kjønn, alder, øvelse): rundt 1000-poengsresultatet, nær 0-poeng, i hvert intervall for
   tre-intervall-øvelser, og grenseverdier for avrunding. ~1600 caser totalt.
3. Skriv `tests/fixtures/tyrving_cases.json` med metadata: kildefil, SHA-256, LibreOffice-versjon, dato.
4. Skriptet er deterministisk: samme input gir byte-identisk fil.

## Fallgruver

- Oracle importerer **ikke** noe fra `athletics_scoring`. Da er den ikke lenger uavhengig.
- `openpyxl` rekalkulerer ikke; verdiene må komme fra LibreOffice.
- Fixtures regnes ikke som låst før Simen har godkjent dem (AP-005). Sett status `Venter på Simen` når fila er
  generert.

## Utenfor scope

Regeltolkning fra DOC/PDF (AP-006), kalkulatoren (AP-008).

## Akseptansekriterier

- [ ] `python scripts/oracle_tyrving.py` genererer fila fra bunnen av
- [ ] To kjøringer gir identisk fil
- [ ] 10 tilfeldige caser listet i sluttrapporten, klare for Simens stikkprøve

## Sluttrapport (fylles av Code)

- **Gjort:** 
- **Avvik fra oppgavefila:** 
- **Funn som bør bli egne oppgaver:** 
