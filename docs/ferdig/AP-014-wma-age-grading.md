# AP-014: WMA Age Grading 2023 (aldersjustert resultat)

**Status:** Ferdig 2026-09-27 (fixture ulåst, venter på Simens stikkprøve)
**Opprettet:** 2026-09-26 (Cowork)
**Eier:** 🤖 Code
**Avhenger av:** AP-001, AP-013, AP-027

## Mål

En motor `("wma_age_grading", "2023")` som gir det aldersjusterte resultatet for en masters-utøver: resultat ×
ettårig aldersfaktor, avrundet som i Appendix B. Motoren gir **ikke** prosent eller poeng (BV-041).

## Hvorfor

Aldersjustering lar masters-utøvere sammenligne resultater på tvers av alder, og minfriidrett.no skal kunne vise
det. Faktorene er offisielle og ligger allerede i `sources/wma/`. Prosent krever en standardtabell vi ikke har, så
oppgaven avgrenses til det kilden faktisk dekker.

## Les dette før du koder

- `athletics_scoring/masters_combined_events.py` (AP-016) hvis den finnes — samme avrunding. Ellers
  `athletics_scoring/tyrving.py` for motormønsteret.
- `sources/wma/wma-2023-age-factors.pdf` — s. 5–10 kvinner, s. 11–16 menn, ett år per rad fra 30 år
- `docs/BEREGNINGSVALG.md` BV-040, BV-041, BV-042

## Verifiserte fakta

- PDF-en har 16 sider. S. 2–3 er de samme 5-årsfaktorene for mangekamp som i Appendix B. S. 5–16 er ettårige
  faktorer per kjønn i tre blokker: (1) 60 m–10 000 m inkludert mile, (2) 60 m hekk, kort og lang hekk, hinder,
  hopp og kast, (3) spyd, vektkast og gateløp/kappgang (3000 m, 5000 m, 10 km, 20 km, halvmaraton, maraton).
- Faktorene starter på 1,0000 ved 30 år. Eksempler: kvinner 45 år 100 m 0,9441 (s. 5). Menn 71 år 100 m 0,7803
  (s. 12).
- PDF-en har **ingen** standarder (rekorder) å regne prosent mot (BV-041).

**Ikke bekreftet, sjekk selv først:** Nøyaktig kolonneoppsett i blokk 2 og 3 (overskriftene går over flere linjer
i teksten). Hvilken hekkeøvelse «Short» og «Long» betyr for hver alder.

## Løsningsretning

1. `scripts/extract_wma_age_factors.py` leser alle ettårige faktorer (30–110 år, begge kjønn, alle kolonner)
   til `athletics_scoring/data/wma_age_factors_2023.json` med `source_documents`. Skriptet teller rader og
   kolonner og feiler hvis en side har et annet antall enn forventet.
2. `scripts/oracle_wma_age_factors.py` leser PDF-en på en annen måte enn ekstraksjonsskriptet (f.eks. ord med
   koordinater i `pdfplumber` mot tekstlinjer) og skriver `tests/fixtures/wma_age_factors_cases.json` (ny,
   ulåst). To uavhengige lesinger som er enige, er fasiten, slik som for Tyrving.
3. `athletics_scoring/wma_age_grading.py`: motor med `age_class` som alder i hele år (`"45"`). Resultatet er
   `ScoreResult` med `points = 0` og det aldersjusterte resultatet i `result_used`, eller en egen resultattype
   hvis `ScoreResult` passer dårlig. Velg selv og begrunn i sluttrapporten.
4. Stegene: resultat, faktor (`ref` BV-040 og kildenøkkel), produkt, avrundet produkt (`ref` BV-042).

## Beregningsvalg

- BV-040, BV-041, BV-042

## Kontrolltall

| Input | Forventet | Kilde |
|---|---|---|
| Kvinne 45 år, 100 m 13,50 | 13,50 × 0,9441 = 12,74535 → **12,75** | s. 5, BV-042 (løp rundes opp) |
| Mann 71 år, 100 m 15,00 | 15,00 × 0,7803 = 11,7045 → **11,71** | s. 12 |
| Kvinne 45 år, 60 m | faktor 0,9613, lik 5-årsfaktoren for W45 | s. 5 og s. 2 |
| Alder 29 | avvises | Faktorene starter på 30 år |

## Utenfor scope

- Prosent og poeng. De krever en standardtabell som ikke er i `sources/` (BV-041).
- Gateløp på tid over maraton, og terreng.
- Beregning av alder fra fødselsdato.

## Fallgruver

- PDF-tekst med kolonneoverskrifter over flere linjer er lett å lese forskjøvet. Derfor to uavhengige lesinger.
- Faktoren kan være over eller under 1 uavhengig av om øvelsen er løp eller kast, fordi den også tar hensyn til
  lettere redskap og lavere hekker. Eksempel menn 60 år (s. 13): lang hekk 1,1628, hinder 1,2613, diskos 0,9653.
  Bruk faktoren slik den står, og ikke legg inn kontroller som antar en retning.

## Når du skal stoppe

Sett oppgaven til `Blokkert` og avslutt hvis:
- de to lesingene av PDF-en er uenige og du ikke kan avgjøre hvilken som er riktig ved å se på siden
- en test bare kan bli grønn ved å endre en test, en låst fixture eller `sources/`

Alt annet avgjør du selv innenfor løsningsretningen, og skriver valget i sluttrapporten.

## Akseptansekriterier

- [x] Kontrolltallene over er egne testcaser og er grønne
- [x] Alle faktorer (30–110 år, begge kjønn, alle kolonner) er med, og ekstraksjon og oracle er enige
- [x] `calculation_steps` har `ref` til BV-040 og BV-042 og kildenøkkel
- [x] Fixture-fila er ny og ulåst. Sluttrapporten lister 10 caser spredt over øvelser og skala som Simen kan
      stikkprøve mot kilden før den låses
- [x] `pytest -q && ruff check . && mypy athletics_scoring` er grønt
- [x] Ingen endringer i `sources/` eller låste `tests/fixtures/`
- [x] Midlertidige filer og hjelpeskript fra underveis er fjernet
- [x] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Sluttrapport (fylles av Code)

- **Gjort:** (2026-09-27, commit `3d09a3a`)
  - `scripts/extract_wma_age_factors.py` leser PDF-side 5–16 som tekstlinjer →
    `athletics_scoring/data/wma_age_factors_2023.json` (60 øvelser = 30 kolonner × 2 kjønn, 81 aldre hver, 4860
    faktorer, `source_documents` med SHA-256). Kontrollerer tittel, overskriftslinjer, aldersrader (30–70 og
    71–110) og antall tall per rad på hver side, pluss seks kjente faktorer fra oppgavefila.
  - `scripts/oracle_wma_age_factors.py` leser de samme sidene som ord med koordinater: kolonnen bestemmes av
    overskriftsordene rett over tallet, kjønnet av sidetittelen. Skriver `tests/fixtures/wma_age_factors_cases.json`
    (ny, ulåst, 4860 caser) med faktor, et eksempelresultat per øvelse og forventet aldersjustert resultat regnet
    med `Decimal`.
  - `athletics_scoring/wma_age_grading.py`: `WmaAgeGradingCalculator` (`"wma_age_grading"`, `"2023"`),
    registrert i `default_registry()`. `age_class` er alder i hele år (`"30"`–`"110"`).
  - `tests/test_wma_age_grading.py`: 20 tester.
- **Bevis:**
  - Ekstraksjon og oracle er enige om alle 4860 faktorene (`test_all_fixture_cases`, null avvik), og begge
    skriptene er reproduserbare (`--check`).
  - Kontrolltallene: W45 100 m 13,50 → 12,75 (0,9441); M71 100 m 15,00 → 11,71 (0,7803); W45 60 m 0,9613, lik
    `masters_combined_events` W45; alder 29, 111, «45.5», «W45» og tom avvises.
  - `pytest -q` (202 passerte), `ruff check .` og `mypy athletics_scoring` er grønne. Ingen endringer i `sources/`
    eller i eksisterende fixtures.
  - 10 caser for stikkprøve (kjønn, øvelse, alder, faktor, resultat → aldersjustert; sidene i PDF-en):

    | Kjønn | Øvelse | Alder | Faktor | Resultat | Justert | PDF-side |
    |---|---|---|---|---|---|---|
    | K | 60 m | 45 | 0,9613 | 8,47 | 8,15 | 5 |
    | M | 100 m | 71 | 0,7803 | 13,50 | 10,54 | 12 |
    | K | Mile | 58 | 0,8162 | 336,52 | 274,67 | 5 |
    | M | 10 000 m | 83 | 0,6383 | 2391,58 | 1526,55 | 12 |
    | K | Long Hurdles | 70 | 1,5178 | 68,25 | 103,59 | 7 |
    | M | Steeple Chase | 60 | 1,2613 | 421,66 | 531,84 | 13 |
    | K | Pole Vault | 64 | 1,4509 | 3,15 | 4,57 | 7 |
    | M | Hammer | 92 | 2,2215 | 41,93 | 93,14 | 14 |
    | K | 20k RaceWalk | 77 | 0,6520 | 7012,55 | 4572,19 | 10 |
    | M | Marathon | 110 | 0,0100 | 11874,61 | 118,75 | 16 |
- **Valg tatt underveis:**
  - **`ScoreResult` med `points = 0`**, aldersjustert resultat i `result_used`, `parameters = {"age_factor": …}` og
    `formula_type = "age_factor"`. Da virker registeret, `list_events` og API-et videre uten en ny resultattype.
    Ulempen er at `points` ikke betyr noe for dette systemet, og det står i docstringen.
  - **Stegene:** `input`, `age` (BV-040), `age_factor` (kildenøkkel `wma-2023-age-factors`, med side og kolonne),
    `age_adjusted` (BV-041), `age_adjusted_rounded` (BV-042).
  - **Input rundes ikke før multiplikasjonen.** Bare produktet rundes (BV-042). Resultatet brukes som oppgitt.
  - **Manuell tid avvises** (`UnsupportedManualTimingError`). Kilden har ingen regel for det, og BV-024 gjelder
    mangekamp.
  - **Redskap avvises** hvis det oppgis. Faktorene gjelder redskapet og hekkehøyden for alderen.
  - **«Short Hurdles» og «Long Hurdles» heter `hurdles_short` («Kort hekk») og `hurdles_long` («Lang hekk»)**,
    og hinder heter `steeplechase`, uten distanse. PDF-en sier ikke hvilken distanse som gjelder for hver alder.
    Hoppet i kvinner lang hekk fra 69 år (0,9881) til 70 år (1,5178) tyder på at distansen skifter der.
  - **Øvrige event_id-er:** `middle_mile`, `racewalk_3000m`/`5000m`/`10000m`/`20000m`, `half_marathon`,
    `marathon`, ellers som Tyrving og masters mangekamp.
  - **Rimelig område** (`PLAUSIBLE_RANGE` i modulen) er grove grenser per øvelse som jeg har satt selv. Det er ren
    brukerhjelp, kommer ikke fra kilden og påvirker ikke beregningen.
- **Avvik fra oppgavefila:** Ingen.
- **Funn som bør bli egne oppgaver:** Se Innboks: distanse per alder for kort og lang hekk og hinder, og det
  rimelige området.
