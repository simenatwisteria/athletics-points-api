# Backlog — Athletics Points API

Eneste sanne oversikt over utviklerarbeid. Det finnes ingen egen `LOOP.md`: loopen jobber seg gjennom denne fila.
Eies av Cowork sammen med Simen. **Claude Code oppretter ikke nye oppgaver her** — funn skrives under «Innboks»
nederst. Code oppdaterer bare `Status` og notatet på oppgaven den jobber med.

**ID-serie:** `AP-001`, `AP-002`, … Neste ledige: **AP-020**

**Eier:** 🤖 Code (kan tas av agenten/loopen) · 🧑 Simen (legges i Todoist, agenten hopper over)

**Status:** `Ny` → `Klar` (oppgavefil finnes i `docs/active/`) → `Under arbeid` → `Venter på Simen` → `Ferdig`
(oppgavefil flyttes til `docs/ferdig/`). `Blokkert` = agenten mistenker feil fasit eller uklar regel, har skrevet
hvorfor i notatet, og har stoppet.

**Regel for agenten:** ta øverste oppgave med eier 🤖 og status `Klar` eller `Ny` der alle avhengigheter er
`Ferdig`. Står en 🧑-oppgave den avhenger av åpen, hopp videre — ikke gjør Simens oppgave.

---

## Now — grunnmur og Tyrving 2014

| # | ID | Oppgave | Eier | Avhenger av | Status | Fil |
|---|---|---|---|---|---|---|
| 1 | AP-001 | Grunnmur: `models.py`, abstrakt `engine.py`, `registry.py` | 🤖 | — | **Ferdig** | `ferdig/AP-001-grunnmur.md` |
| 2 | AP-002 | Tyrving: parameterekstraksjon Excel → `data/tyrving_parameters_2014.json` (560 kombinasjoner) + test mot Excel-celler | 🤖 | AP-001 | **Blokkert** — kildene er uenige om 2 rader, se Innboks | `active/AP-002-tyrving-parametre.md` |
| 3 | AP-003 | Installer LibreOffice (`brew install --cask libreoffice`) så `soffice` finnes i PATH | 🧑 | — | **Ferdig** (LibreOffice 26.8.0.3, 2026-09-25) | — |
| 4 | AP-004 | Tyrving: oracle-skript `scripts/oracle_tyrving.py` — rekalkulerer regnearket med LibreOffice headless og skriver `tests/fixtures/tyrving_cases.json` (~1600 caser) | 🤖 | AP-002, AP-003 | Klar | `active/AP-004-tyrving-oracle.md` |
| 5 | AP-005 | **Review** Tyrving-fixtures: stikkprøve 10–20 caser mot PDF-tabellen, godkjenn og lås | 🧑 | AP-004 | Ny | — |
| 6 | AP-006 | Tyrving: regeltolkning fra DOC/PDF (80 %-grense, manuell tidtaking, avrunding) som eksplisitte testcaser i `tests/fixtures/tyrving_rules.json` med kildehenvisning per case | 🤖 | AP-001 | Ny | — |
| 7 | AP-007 | **Review** regeltolkningen i AP-006 mot DOC/PDF, godkjenn og lås | 🧑 | AP-006 | Ny | — |
| 8 | AP-008 | Tyrving: `TyrvingCalculator` (simple_quotient, three_interval, edge cases) grønn mot låste fixtures | 🤖 | AP-002, AP-005, AP-007 | Ny | — |
| 9 | AP-009 | Tyrving: mangekamp u/15 (summering av Tyrving-poeng) | 🤖 | AP-008 | Ny | — |

## Next — WA, WMA og masters (WA før masters og mangekamp)

| # | ID | Oppgave | Eier | Avhenger av | Status | Fil |
|---|---|---|---|---|---|---|
| 10 | AP-010 | Last ned WA Scoring Tables 2025 og Combined Events-konstanter til `sources/wa/` (se `sources/wa/README.md`) | 🧑 | — | Ny | — |
| 11 | AP-011 | WA Scoring 2025: ekstraksjon, oracle, kalkulator. Fixtures krever Simens review før kalkulatoren regnes som ferdig | 🤖 | AP-001, AP-010 | Ny | — |
| 12 | AP-012 | WA Combined Events: femkamp, sjukamp, tikamp | 🤖 | AP-011 | Ny | — |
| 13 | AP-013 | Last ned WMA Age Factors 2023 til `sources/wma/` (se `sources/wma/README.md`) | 🧑 | — | Ny | — |
| 14 | AP-014 | WMA Age Grading 2023: ekstraksjon, oracle, kalkulator. Fixtures krever Simens review | 🤖 | AP-001, AP-013 | Ny | — |
| 15 | AP-015 | Last ned NFIF masters mangekamptabell menn + kvinner til `sources/masters/` (se `sources/masters/README.md`) | 🧑 | — | Ny | — |
| 16 | AP-016 | Masters mangekamp (NFIF): tabell-lookup som primær, WA × WMA-faktor som kryssverifisering | 🤖 | AP-012, AP-014, AP-015 | Ny | — |
| 17 | AP-017 | Loop-oppsett: `.claude/commands/loop.md` og `scripts/loop.sh` som jobber seg gjennom denne backlogen, med stoppbetingelser (blokkert, ingen framdrift, alt ferdig, maks runder) | 🤖 | — | Ny | — |

AP-017 har ingen avhengigheter og kan trekkes fram foran Tyrving-kalkulatoren hvis loopen skal brukes allerede der.
Rekkefølgen over er slik Simen ba om den i PROMPT-001 — flytting avgjøres i Cowork.

## Later — ikke i loop

| ID | Oppgave | Status | Notat |
|---|---|---|---|
| AP-018 | FastAPI-wrapper, deploy på Railway, frontend på Vercel | Ny | Først når pakken er verifisert (B-1). Railway/Vercel kobles på når `/health` finnes. |
| AP-019 | Serietabellen / Seriepoeng (Lagserien) | Ny | B-17. Flyttet bak WA fordi masters og mangekamp avhenger av WA (ANALYSE 2026-09-06, B-21-forslag). |

---

## Innboks — funn fra Claude Code, ikke prioritert

Code skriver hit. Cowork tømmer lista og prioriterer inn i Now/Next/Later.

- **Kildene er uenige om to Tyrving-rader — Simen må avgjøre hvilken kilde som vinner** *(AP-002, blokkerer AP-004/AP-005/AP-008)*
  `tyrving_parameters_2014.json` gjengir `.xlsx` uendret. Radene er merket med `conflict` og et alternativ, og
  ingenting er avgjort.
  1. `Jenter 17 år` rad 36, Kule 3kg: `.xlsx` og `.xls` regner enkel kvotient med `I36 = 1.2` hardkodet
     (`P = 1000-O*I`). All annen kule, og PDF-en, bruker tre-intervall 0,3 / 0,6 / 1,2. Over 80 % av 12,60 m
     (10,08 m) gir regnearket for få poeng.
  2. `Jenter 15 år` rad 36, Spyd: `.xlsx` har **0,4kg / 1000p = 42**. Både `.xls` og PDF-en har **500 g / 1000p = 38**
     (400 g gjelder 10–14 år, 500 g gjelder 15–17 år).
  Forslag: la PDF-en (den offisielle utgaven, jf. Forside-arket) vinne ved konflikt, og behandle begge radene likt.
  Konsekvens for AP-004: en oracle som rekalkulerer `.xlsx` gir feil fasit for begge radene. De må enten holdes
  utenfor fixtures eller rettes i en kopi, og det må Simen bestemme.

- **Ingen fullstendig kryssjekk mot PDF-ene ennå** *(AP-002)*
  Parametrene er sjekket celle for celle mot `.xlsx`, og `.xls` er sammenlignet automatisk (bare J15 spyd skiller).
  `.xls` deler formelfeilen for J17 kule, så den er ikke en uavhengig kilde. PDF-ene ble bare lest for de to
  konfliktradene. En automatisk sammenligning av alle 560 parametre mot PDF-tabellene vil sannsynligvis finne
  flere avvik hvis de finnes. `pypdf` gir tekst, men kolonnene for alder må tolkes varsomt (tomme celler forsvinner).

- **xls-kryssjekken hoppes over i CI** *(AP-002)*
  `test_xls_has_same_parameters` krever `soffice` og er `skip` i GitHub Actions. Den kjører lokalt. Vurder
  `apt-get install libreoffice-calc` i CI når oracle (AP-004) uansett trenger LibreOffice.

- **Formlene for lange løp stryker ikke hundredeler** *(til AP-006)*
  For 600 m og lengre regner regnearket `(D*60+E)*10` uten å runde av tideler. PDF-teksten sier «I lengre løp skal
  hundredeler strykes». Regnearket forutsetter altså at brukeren legger inn tid med tideler. Motoren må ta stilling
  til hva den gjør med input som 2:04.56.

---

## Beslutningslogg

Datert, kort. Hvorfor noe ble valgt — ikke hva som ble gjort (det står i git).

- **2026-09-25** — Repo `simenatwisteria/athletics-points-api` (public, MIT) klonet til `CODE/AthleticsPointsCalc`. Navnene er bevisst forskjellige. Én klone, ett repo (B-19-forslag i ANALYSE).
- **2026-09-25** — Backloggen følger formatet fra `5KAMP/docs/BACKLOG.md`. `godkjennutlegg` har backloggen sin i Google Drive, ikke i repoet, så 5KAMP var nærmeste mal i `CODE/`. Ingen egen `LOOP.md`.
- **2026-09-25** — Fasit genereres alltid fra `sources/` av separate oracle-skript, aldri fra motoren, og er skrivebeskyttet for agenten (B-20-forslag). Review av fixtures og regeltolkning er Simens oppgave, fordi loopen bare kan bevise «koden matcher fasiten», ikke «fasiten er riktig».
- **2026-09-25** — Kildefiler med SHA-256 i `sources/SHA256SUMS`, så endringer i fasit-grunnlaget er synlige i diff og kan sjekkes med én kommando.
- **2026-09-25** — Masters mangekamp: NFIF-tabellen er fasit (lookup), WA × WMA brukes bare til kryssverifisering. Det er NFIF som publiserer tabellen som faktisk brukes.
