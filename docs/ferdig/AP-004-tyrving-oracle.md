# AP-004: Tyrving — oracle-skript med LibreOffice headless → `tests/fixtures/tyrving_cases.json`

**Status:** Ferdig
**Opprettet:** 2026-09-25 (PROMPT-001)
**Eier:** 🤖 Code (review: 🧑 Simen i AP-005)
**Avhenger av:** AP-002, AP-003 (LibreOffice installert)

## Problemet

Vi trenger en fasit som er uavhengig av Python-motoren. Regnearket har levende formler og kan rekalkuleres.

## Hvorfor nå

Uten låst fasit kan loopen ikke bevise at `TyrvingCalculator` er riktig (ANALYSE 2026-09-06, kap. 3.1 og 4.1).

## Verifiserte fakta

- Input-celler per rad: `D` (minutter) og `E` (sekunder/resultat). Output: `F` (poeng). Se AP-002.
- `soffice` er installert (`/opt/homebrew/bin/soffice`, LibreOffice 26.8.0.3) — AP-003 ferdig 2026-09-25.

## Løsningsretning

1. `scripts/oracle_tyrving.py`: kopier `.xlsx` til en temp-mappe (aldri i `sources/`), skriv inn resultater i
   `D`/`E` med `openpyxl`, rekalkuler med `soffice --headless --convert-to xlsx`, les `F` med `data_only=True`.
2. Velg resultater per (kjønn, alder, øvelse): rundt 1000-poengsresultatet, nær 0-poeng, i hvert intervall for
   tre-intervall-øvelser, og grenseverdier for avrunding. ~1600 caser totalt.
3. Skriv `tests/fixtures/tyrving_cases.json` med metadata: kildefil, SHA-256, LibreOffice-versjon, dato.
4. Skriptet er deterministisk: samme input gir byte-identisk fil.

## Fallgruver

- **To rader i `.xlsx` er feil ifølge PDF-en** (J17 kule, J15 spyd — se `docs/BACKLOG.md` → Innboks). Ikke
  start før Simen har avgjort hvordan de skal behandles i fixtures.

- Oracle importerer **ikke** noe fra `athletics_scoring`. Da er den ikke lenger uavhengig.
- `openpyxl` rekalkulerer ikke; verdiene må komme fra LibreOffice.
- Fixtures regnes ikke som låst før Simen har godkjent dem (AP-005). Sett status `Venter på Simen` når fila er
  generert.

## Utenfor scope

Regeltolkning fra DOC/PDF (AP-006), kalkulatoren (AP-008).

## Akseptansekriterier

- [x] `python scripts/oracle_tyrving.py` genererer fila fra bunnen av
- [x] To kjøringer gir identisk fil
- [x] 10 tilfeldige caser listet i sluttrapporten, klare for Simens stikkprøve (i `AP-005`)

## Sluttrapport (fylles av Code)

- **Gjort:** `scripts/oracle_tyrving.py` (med `--check`) → `tests/fixtures/tyrving_cases.json`, 2472 caser.
  Enkle rader: 90/100/110 % av 1000p-nivået + ett 0-poengsresultat. Tre-intervall: 5/70/80/90/100/110 %.
  Tider i hundredeler til og med 500 m og tideler over. Én regnearkkopi per variant (6), regnet om av LibreOffice
  med egen profil (`OOXMLRecalcMode=0`), ca. 8 s. De tre PDF-rettingene gjøres i kopien, og skriptet sjekker
  «før»-verdiene mot kilden. `tests/test_tyrving_fixtures.py` (8 tester). Kontroll: alle 560 caser på
  1000p-nivået gir 1000, og 2471/2472 er like med eksakt desimalregning.
- **Avvik fra oppgavefila:** 2472 caser, ikke ~1600. Fasit-fila er generert, men ikke låst før AP-005.
- **Funn som bør bli egne oppgaver:** én flyttallsfeil i regnearket (`float_edge`), og LibreOffice-tester
  hoppes over i CI. Begge står i Innboks.
