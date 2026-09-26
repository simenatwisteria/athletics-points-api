# AP-014: WMA Age Grading 2023 (aldersjustert resultat)

**Status:** Klar
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

- [ ] Kontrolltallene over er egne testcaser og er grønne
- [ ] Alle faktorer (30–110 år, begge kjønn, alle kolonner) er med, og ekstraksjon og oracle er enige
- [ ] `calculation_steps` har `ref` til BV-040 og BV-042 og kildenøkkel
- [ ] Fixture-fila er ny og ulåst. Sluttrapporten lister 10 caser spredt over øvelser og skala som Simen kan
      stikkprøve mot kilden før den låses
- [ ] `pytest -q && ruff check . && mypy athletics_scoring` er grønt
- [ ] Ingen endringer i `sources/` eller låste `tests/fixtures/`
- [ ] Midlertidige filer og hjelpeskript fra underveis er fjernet
- [ ] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Sluttrapport (fylles av Code)

- **Gjort:**
- **Bevis:**
- **Valg tatt underveis:**
- **Avvik fra oppgavefila:**
- **Funn som bør bli egne oppgaver:**
