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
| 2 | AP-002 | Tyrving: parameterekstraksjon Excel → `data/tyrving_parameters_2014.json` (560 kombinasjoner) + test mot Excel-celler | 🤖 | AP-001 | **Ferdig** (PDF vinner, 3 rader rettet — `KILDEAVVIK.md`) | `ferdig/AP-002-tyrving-parametre.md` |
| 3 | AP-003 | Installer LibreOffice (`brew install --cask libreoffice`) så `soffice` finnes i PATH | 🧑 | — | **Ferdig** (LibreOffice 26.8.0.3, 2026-09-25) | — |
| 4 | AP-004 | Tyrving: oracle-skript `scripts/oracle_tyrving.py` — rekalkulerer regnearket med LibreOffice headless og skriver `tests/fixtures/tyrving_cases.json` (2472 caser) | 🤖 | AP-002, AP-003 | **Ferdig** | `ferdig/AP-004-tyrving-oracle.md` |
| 5 | AP-005 | **Review** Tyrving-fixtures: stikkprøve 10–20 caser mot PDF-tabellen, godkjenn og lås | 🧑 | AP-004 | **Ferdig** 2026-09-26 — fasiten er låst | `ferdig/AP-005-review-tyrving-fixtures.md` |
| 6 | AP-006 | Tyrving: regeltolkning fra DOC/PDF (80 %-grense, manuell tidtaking, avrunding) som eksplisitte testcaser i `tests/fixtures/tyrving_rules.json` med kildehenvisning per case | 🤖 | AP-001 | **Ferdig** (29 caser, 3 åpne spørsmål) | `ferdig/AP-006-tyrving-regeltolkning.md` |
| 7 | AP-007 | **Review** regeltolkningen i AP-006 mot DOC/PDF, godkjenn og lås | 🧑 | AP-006 | **Ferdig** 2026-09-26 — regeltolkningen er låst | `ferdig/AP-007-review-regeltolkning.md` |
| 8 | AP-008 | Tyrving: `TyrvingCalculator` (simple_quotient, three_interval, edge cases) grønn mot låste fixtures | 🤖 | AP-002, AP-005, AP-007 | **Ferdig** 2026-09-26 | `ferdig/AP-008-tyrving-calculator.md` |
| 9 | AP-009 | Tyrving: mangekamp u/15 (summering av Tyrving-poeng) | 🤖 | AP-008 | **Ferdig** 2026-09-26 (generell summering) | `ferdig/AP-009-tyrving-mangekamp.md` |

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
| 17 | AP-017 | Loop-oppsett: `.claude/commands/loop.md` og `scripts/loop.sh` som jobber seg gjennom denne backlogen, med stoppbetingelser (blokkert, ingen framdrift, alt ferdig, maks runder) | 🤖 | — | **Ferdig** | `ferdig/AP-017-loop.md` |

AP-017 ble tatt tidlig (2026-09-25) fordi den ikke har avhengigheter og alle andre 🤖-oppgaver ventet på Simen.

## Later — ikke i loop

| ID | Oppgave | Status | Notat |
|---|---|---|---|
| AP-018 | FastAPI-wrapper, deploy på Railway, frontend på Vercel | Ny | Først når pakken er verifisert (B-1). Railway/Vercel kobles på når `/health` finnes. |
| AP-019 | Serietabellen / Seriepoeng (Lagserien) | Ny | B-17. Flyttet bak WA fordi masters og mangekamp avhenger av WA (ANALYSE 2026-09-06, B-21-forslag). |

---

## Innboks — funn fra Claude Code, ikke prioritert

Code skriver hit. Cowork tømmer lista og prioriterer inn i Now/Next/Later.

- **Meld avvikene i Tyrving-filene til NFIF** *(AP-002, forslag til 🧑-oppgave)*
  To feil i regnearket (G19 2000 m, J17 kule) og tre skrivefeil i PDF-en, dokumentert i `docs/KILDEAVVIK.md`.
  Spyd J15 skal ikke meldes: NFIF rettet den i `.xls` 2018-02-28, og `.xlsx` i `sources/` er en eldre kopi. Utkast til e-post er gitt
  Simen i chat 2026-09-25. Oppdater «Status overfor NFIF» i `KILDEAVVIK.md` når svaret kommer. Sier NFIF at
  regnearket er riktig, må regelen «PDF vinner» revurderes for den raden, og data og fasit må genereres på nytt.

- **`sources/tyrving/tyrving-2014-redigerbar.xlsx` er ikke NFIFs gjeldende fil** *(verifisert 2026-09-25)*
  Sist lagret av Simen 2024-06-28, har inntastede resultater og mangler NFIFs retting fra 2018. Simen bør laste ned
  gjeldende regneark fra friidrett.no og erstatte den, eller rette opprinnelsen i `sources/README.md` (agenten
  endrer ikke `sources/`). Parametrene og fasiten påvirkes ikke, fordi PDF-en vinner.

- **Faste mangekamper per klasse mangler** *(AP-009, forslag til 🧑-oppgave)*
  Motoren summerer fritt valgte øvelser. For at frontenden skal kunne tilby «Femkamp J13» osv., trengs NFIFs
  oversikt over hvilke mangekamper (og øvelser) som gjelder for hvilke klasser under 15 år. Legges inn som data.

- **Klikkbar skisse, versjon 2** *(2026-09-26, til AP-018)*
  Skissen har en startside med alle tabellene (Tyrving, WA, WA mangekamp, Serietabellen, WMA, masters
  mangekamp), valg mellom norsk og engelsk, og et kompakt iOS-skjema med nedtrekksmenyer for klasse, øvelse og
  utstyr. Det gir tre krav til API-et:
  1. `GET /systems` må gi navn og beskrivelse på norsk og engelsk, gruppe (ungdom/senior/masters), om tabellen
     er klar, klassetype (alder/klasse/masters), klasseliste og om mangekamp støttes.
  2. Øvelsesnavn må finnes på norsk og engelsk (en felles øvelseskatalog), og kategorien (løp, hekk, kappgang,
     hopp, kast) brukes til å gruppere menyene.
  3. Tall formateres etter språk (komma på norsk, punktum på engelsk). Poengberegningen påvirkes ikke.

- **LibreOffice-tester hoppes over i CI** *(AP-002, AP-004)*
  `test_xls_has_same_parameters` og `test_fixture_is_reproducible` krever `soffice` og er `skip` i GitHub
  Actions. Lokalt kjører de. Vurder `apt-get install libreoffice-calc` i CI (koster ca. 1–2 min per kjøring).

- **Regnearket stryker ikke hundredeler i lange løp** *(AP-006)*
  Regelteksten sier at hundredeler skal strykes (R2), men regnearket regner `(D*60+E)*10` rett fram. Motoren skal
  følge regelteksten (case R2-01 – R2-03). Fasiten fra oracle bruker bare tideler i lange løp, så den er ikke
  berørt. Bør med i meldingen til NFIF som en merknad.

---

## Beslutningslogg

Datert, kort. Hvorfor noe ble valgt — ikke hva som ble gjort (det står i git).

- **2026-09-25** — Repo `simenatwisteria/athletics-points-api` (public, MIT) klonet til `CODE/AthleticsPointsCalc`. Navnene er bevisst forskjellige. Én klone, ett repo (B-19-forslag i ANALYSE).
- **2026-09-25** — Backloggen følger formatet fra `5KAMP/docs/BACKLOG.md`. `godkjennutlegg` har backloggen sin i Google Drive, ikke i repoet, så 5KAMP var nærmeste mal i `CODE/`. Ingen egen `LOOP.md`.
- **2026-09-25** — Fasit genereres alltid fra `sources/` av separate oracle-skript, aldri fra motoren, og er skrivebeskyttet for agenten (B-20-forslag). Review av fixtures og regeltolkning er Simens oppgave, fordi loopen bare kan bevise «koden matcher fasiten», ikke «fasiten er riktig».
- **2026-09-25** — Kildefiler med SHA-256 i `sources/SHA256SUMS`, så endringer i fasit-grunnlaget er synlige i diff og kan sjekkes med én kommando.
- **2026-09-25** — **PDF vinner ved konflikt mellom Tyrving-kildene** (Simen). Forsiden i regnearket kaller
  PDF-en den offisielle utgaven. Kryssjekk av alle 560 kombinasjoner fant tre regnearkfeil; de er rettet i data
  og fasit, men aldri i `sources/`. Register: `docs/KILDEAVVIK.md`.
- **2026-09-25** — **Grunnlaget er NFIFs offisielle tabell, publisert som DOC på friidrett.no.** DOC-filene i
  `sources/` er byte-identiske med Simens nedlasting samme dag. PDF-ene har ukjent opphav, men identisk innhold, og
  brukes videre av koden fordi de kan leses uten LibreOffice. Ingen tall endres. NFIFs gjeldende `.xls` avviker
  fra tabellen på to rader (G19 2000 m, J17 kule).
- **2026-09-26** — **Rimelig område per øvelse** (`InputSpec.plausible_min/max`, `ScoreResult.within_plausible_range`):
  0,6–3,0 × 1000p-nivået for tid og 0,2–1,6 × for distanse. Det er brukerhjelp, ikke regel: frontenden viser ikke
  poeng utenfor området, fordi resultatet trolig er halvveis tastet inn. Motoren beregner poeng uansett. Kom fra
  tastatur-skissen, der sifre fylles inn fra høyre (1-0-9 = 1,09 s gir 2711 poeng underveis).
- **2026-09-26** — **Regeltolkningen er låst (AP-007).** Tillegg for manuell tid gjelder etter distanse, også for hekk.
  Løp fra 600 m og oppover får ingen tillegg. Manuell tid på 40 m avvises. Resultat 0 eller et manglende resultat
  avvises, mens negativ poengsum for et gyldig resultat gir 0.
- **2026-09-26** — **Tyrving-fasiten er låst (AP-005).** Kvalitetssikret mot Rjukan IL sin Tyrvingkalkulator: 2419 av
  2432 sammenlignbare caser er identiske, og resten er forklart av feil på nettsiden. **Motoren regner eksakt**
  (desimal), fordi regelteksten sier at alle desimaler beholdes. Flyttallskanten testes mot `points_if_exact`.
  **Hundredeler strykes i løp over 500 m**, slik regelteksten sier.
- **2026-09-25** — Masters mangekamp: NFIF-tabellen er fasit (lookup), WA × WMA brukes bare til kryssverifisering. Det er NFIF som publiserer tabellen som faktisk brukes.
