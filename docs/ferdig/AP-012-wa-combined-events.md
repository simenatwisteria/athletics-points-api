# AP-012: WA Combined Events (mangekamptabellen)

**Status:** Ferdig 2026-09-26
**Opprettet:** 2026-09-26 (Cowork)
**Eier:** 🤖 Code
**Avhenger av:** AP-001, AP-013, AP-015, AP-027

## Mål

En motor `("wa_combined_events", "2001")` som gir poeng per øvelse etter den internasjonale mangekamptabellen, og
summerer en mangekamp. Den dekker senior og ungdom fra 15 år, inkludert NFIFs fire tilleggsøvelser for UM.

## Hvorfor

All mangekamp fra 15 år regnes med denne tabellen (UM-reglementet §16.5), og masters mangekamp (AP-016) bygger
direkte på den. Resultatsidene Simen har sjekket, bruker den. Motoren er også den første som bruker
kildesporingen fra AP-027, så den blir mønsteret for de neste.

## Les dette før du koder

- `athletics_scoring/tyrving.py` — mønsteret for motor, `calculation_steps`, `list_events`, `calculate_combined`
  og eksakt `Decimal`-regning. Følg det.
- `athletics_scoring/models.py` — `CalculationStep.ref` (fra AP-027), `InputSpec`, `CombinedScoreResult`
- `sources/wma/wma-2023-appendix-b-combined-events.pdf` s. 1–2 — formlene, parametrene og regelen om avkorting
- `sources/nfif/nfif-um-reglement-2026.pdf` s. 9 (§16.4–16.5) — NFIFs tilleggsøvelser og koeffisienter
- `sources/masters/nfif-masters-mangekamp-menn.xlsx` og `-kvinner.xlsm` — kolonnen «Sr» er fasit (se under)
- `docs/BEREGNINGSVALG.md` BV-002, BV-003, BV-004, BV-020 til BV-025
- `docs/KILDEAVVIK.md` — «Manuell tid på 60 m og 60 m hekk»

## Verifiserte fakta

Kontrollert av Cowork 2026-09-26 med formlene fra Appendix B s. 2:

- **Formler:** løp `a·(b−T)^c` (T i sekunder), hopp `a·(M−b)^c` (M i **centimeter**), kast `a·(D−b)^c`
  (D i meter). Poeng avkortes til heltall. Er differansen 0 eller negativ, er poengene 0.
- **Menn (16):** 60, 100, 200, 400, 1000, 1500 m, 60 m hekk, 110 m hekk, høyde, stav, lengde, kule, diskos,
  slegge, spyd, vektkast. **Kvinner (15):** 60, 100, 200, 400, 800 m, 60 m hekk, 100 m hekk, høyde, stav, lengde,
  kule, diskos, slegge, spyd, vektkast. Parametrene står i Appendix B s. 2.
- **Kvinner 1500 m** mangler i Appendix B. Parametrene fra IAAF-boka s. 23 (kvinners tikamp): a = 0,02883,
  b = 535, c = 1,88. NFIF-arket stemmer for alle 1200 rader.
- **NFIFs tilleggsøvelser** (UM-reglementet §16.5):

  | Øvelse | Klasser | a | b | c |
  |---|---|---|---|---|
  | 600 m (inne) | J15, J16 | 0,198890 | 185 | 1,88 |
  | 800 m (inne) | G15, G16 | 0,160027 | 231 | 1,836 |
  | 80 m hekk | J15, J16 | 12,2092 | 22 | 1,835 |
  | 100 m hekk | G15, G16 | 8,73753 | 26 | 1,83 |

- **Fasit:** Seniorkolonnen («Sr», kolonne B) i hvert ark i NFIFs masters-mangekamptabeller er ren Combined
  Events. Null avvik for alle automatiske tider og tekniske øvelser (menn 15 051 rader, kvinner 13 929 rader)
  og for manuell tid på 100, 200, 400 m og korthekk (1 502 rader).
- **Arkoppsett:** To oppsett. Enten poeng i kolonne A og *laveste resultat for poengtallet* i kolonne B (de fleste
  løp og kast), eller resultat i kolonne A og poeng i kolonne B (høyde, stav, lengde og «-m»-arkene). Radene
  starter på rad 3 eller 4. Kule/diskos/spyd/slegge/vektkast har redskapsvekt i raden «Vekt:», hekk har
  hekkehøyde i raden «Hhøyde».
- **Unntak:** Arkene `80-100mHK` (kvinner) starter på W40, ikke senior, og brukes ikke her. De fire «-m»-arkene
  for 60 m og 60 m hekk bruker +0,20 s og brukes ikke som fasit (BV-024).

**Ikke bekreftet, sjekk selv først:** Hvordan tider over ett minutt står i arkene (f.eks. `2.12.79` for 1000 m)
og at parseren din leser dem riktig. Tell radene per ark og sammenlign med tallene over.

## Løsningsretning

1. `scripts/extract_wa_combined_events_params.py` skriver `athletics_scoring/data/wa_combined_events_2001.json`
   med alle øvelser, parametre, enhet og `source_documents` (AP-027). Parametrene legges inn som konstanter i
   skriptet med sidehenvisning. PDF-en er tekst, men tabellen er liten, og konstanter er lettere å se over enn
   en PDF-parser. Skriptet sjekker SHA-256 på kildefilene.
2. `scripts/oracle_wa_combined_events.py` leser seniorkolonnen i NFIF-arkene med `openpyxl` og skriver
   `tests/fixtures/wa_combined_events_cases.json` (ny, ulåst fil). Importerer ikke `athletics_scoring`.
3. `athletics_scoring/wa_combined_events.py`: `CombinedEventsCalculator(ScoringEngine)`, registrert i
   `default_registry()`. Bruk samme `event_id`-er som Tyrving der øvelsen er den samme (`sprint_100m`,
   `hurdles_110m`, `high_jump`, `shot_put` …). `age_class` er `"senior"` eller `"G15"`–`"G17"`/`"J15"`–`"J17"`,
   fordi tilleggsøvelsene bare gjelder noen klasser. Standardøvelsene gjelder alle klasser.
4. Manuell tid: +0,24 s til og med 300 m, +0,14 s på 400 m, ingen tillegg over 400 m (BV-024). Tider med
   tusendeler rundes opp til hundredeler, lengder ned til hel cm (BV-025).
5. `calculate_combined` summerer poengene, som i Tyrving. Faste øvelsesprogram (tikamp osv.) er ikke med her.
6. `calculation_steps` viser input, justert resultat, formel med tall, rå poeng og avkortet poeng, med `ref` til
   BV-numrene og kildenøkkelen.

## Beregningsvalg

- BV-003 (avkorting), BV-004 (eksakt regning), BV-020, BV-021, BV-022, BV-023, BV-024, BV-025

## Kontrolltall

| Input | Forventet | Kilde |
|---|---|---|
| Menn 100 m 10,40 automatisk | 999 | IAAF-boka s. 23, eksempel |
| Menn 100 m 10,4 manuell | 942 | IAAF-boka s. 23, eksempel |
| Menn 60 m 6,0 manuell | 1170 | IAAF-boka s. 166 (tabell for manuell tid 60 m). BV-024 (NFIF-arket gir 1187) |
| Menn 200 m 23,79 | 712 | Formel, Appendix B s. 2 |
| Menn 1500 m 4:45,8 | 644 | Formel. Uten tillegg, fordi 1500 m er over 400 m |
| Menn lengde 5,17 | 415 | Formel, M = 517 cm |
| Menn diskos 16,33 / spyd 32,80 | 204 / 339 | Formel |
| Kvinner 200 m 26,77 / 800 m 2:54,1 | 731 / 422 | Formel |
| Kvinner 1500 m 4:34,99 | 1000 | IAAF-boka s. 159 |
| J15 600 m 1:40,00 / J15 80 m hekk 12,00 | 843 / 835 | Formel, UM-reglementet §16.5 |
| G15 800 m inne 2:10,00 / G15 100 m hekk 14,00 | 765 / 824 | Formel, UM-reglementet §16.5 |
| Alle rader i seniorkolonnen, unntatt 60 m-manuell og `80-100mHK` | null avvik | `tests/fixtures/wa_combined_events_cases.json` |

Tallene fra UM-reglementet har ingen uavhengig fasit. De er regnet ut av Cowork med formelen og skal bare vise at
koeffisientene er lagt inn riktig.

## Utenfor scope

- Masters og aldersfaktorer (AP-016).
- WA Scoring Tables 2025 (AP-011). Det er et annet system.
- Faste øvelsesprogram per klasse (femkamp J15 osv.). Summering av fritt valgte øvelser holder.
- Innendørs 60 m hekk-varianter med andre hekkehøyder enn seniorens. Bare øvelsene over.
- Ikke lag en felles basisklasse for «formelmotorer» ennå. Masters gjenbruker formelen ved å kalle denne motoren.

## Fallgruver

- Hopp regnes i centimeter, kast i meter. Å bruke meter for hopp gir helt feil poeng uten at noe krasjer.
- Flyttall: `1.47 * 1.0205 * 100` kan gi 150,0134…, men `a·x^c` nær et heltall kan havne på feil side. Regn med
  `Decimal` som Tyrving. `Decimal` har ikke desimaleksponent direkte: bruk `exp(c · ln(x))` med høy presisjon
  (`localcontext`, prec ≥ 28), og test at alle fasitradene stemmer.
- Kolonne B i arkene er *laveste resultat som gir poengtallet*. Testen må gå fra resultat til poeng, ikke omvendt.

## Når du skal stoppe

Sett oppgaven til `Blokkert` og avslutt hvis:
- en test bare kan bli grønn ved å endre en test, en låst fixture eller `sources/`
- seniorkolonnen gir avvik mot formelen som ikke er forklart over (Cowork fant null avvik)
- et kontrolltall fra IAAF-boka ikke stemmer med formelen

Alt annet avgjør du selv innenfor løsningsretningen, og skriver valget i sluttrapporten.

## Akseptansekriterier

- [x] Kontrolltallene over er egne testcaser og er grønne
- [x] Oracle-fixturen dekker alle seniorkolonnene som er nevnt, og testen mot den har null avvik
- [x] Manuell tid 60 m gir 1170 (BV-024), ikke 1187
- [x] `calculation_steps` har `ref` til BV-numre og kildenøkkel, og testen fra AP-027 er grønn
- [x] Motoren er registrert, og `list_events` gir tilleggsøvelsene bare for riktige klasser
- [x] Fixture-fila er ny og ulåst. Sluttrapporten lister 10 caser spredt over øvelser og skala som Simen kan
      stikkprøve mot kilden før den låses
- [x] `pytest -q && ruff check . && mypy athletics_scoring` er grønt
- [x] Ingen endringer i `sources/` eller låste `tests/fixtures/`
- [x] Midlertidige filer og hjelpeskript fra underveis er fjernet
- [x] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Sluttrapport (fylles av Code)

- **Gjort:** (commit `599ae97`)
  - `scripts/extract_wa_combined_events_params.py` → `athletics_scoring/data/wa_combined_events_2001.json`
    (36 øvelser: menn 16, kvinner 15 + 1500 m, NFIFs 4 tilleggsøvelser). Konstantene står i skriptet med
    sidehenvisning. Skriptet sjekker SHA-256 mot `sources/SHA256SUMS` og at hver a/b/c står ordrett i teksten på
    Appendix B s. 2 og i tabellen i UM-reglementet §16.5. `--check` som for Tyrving.
  - `scripts/oracle_wa_combined_events.py` → `tests/fixtures/wa_combined_events_cases.json` (ny, ulåst,
    `meta.locked: false`). Leser kolonne B («Sr») med `openpyxl`, finner oppsettet (poeng i A eller resultat i
    A) automatisk, og feiler hvis arbeidsboka får ark som verken er i bruk eller eksplisitt utelatt. Importerer
    ikke `athletics_scoring`.
  - `athletics_scoring/wa_combined_events.py`: `CombinedEventsCalculator` (`wa_combined_events`, `2001`),
    registrert i `default_registry()`. `calculate`, `calculate_combined`, `list_events`, `get_parameters`,
    `sources`, `age_classes`.
  - `tests/test_wa_combined_events.py`: 47 tester (kontrolltall, hele fixturen, reproduserbarhet av fixture og
    parametre, BV-024/BV-025, sporbarhet, klasser, feil, mangekamp).
- **Bevis:**
  - Radtelling: menn 15 051, kvinner 13 929 automatisk/teknisk, 1 502 manuell — nøyaktig som i oppgavefila.
    Totalt 30 482 caser, **null avvik**.
  - Alle 15 kontrolltall stemmer, også 60 m manuell 6,0 = 1170 og kvinner 1500 m 4:34,99 = 1000. I tillegg
    Appendix B-eksemplene høyde K 1,50 = 621, 400 m M 66,09 = 230, kule K 12,34 = 684.
  - Tider over ett minutt står som `2.12.79` (min.sek.hundredeler) i arkene; parseren leser `m.ss.cc` og
    `ss.cc`, og feiler på alt annet.
  - `pytest -q` 152 passed, `ruff check .` og `mypy athletics_scoring` grønne. `git diff` viser ingen endringer
    i `sources/` eller i de låste Tyrving-fixturene.
- **Stikkprøve for Simen** (fil, ark, rad → forventet poeng i kolonne A/B):

  | Kjønn | Ark | Rad | Resultat i arket | Poeng |
  |---|---|---|---|---|
  | M | Diskos | 947 | 19.23 | 258 |
  | M | Lengde | 575 | 2.83 | 47 |
  | M | 200m | 7 | 19.07 | 1197 |
  | M | 400m | 905 | 1.03.61 | 299 |
  | M | 100m-m (manuell) | 4 | 9.3 | 1213 |
  | F | Vektkast | 471 | 16.01 | 734 |
  | F | 800m | 301 | 2.14.31 | 903 |
  | F | 100m | 380 | 14.54 | 522 |
  | F | Høyde | 24 | 1.78 | 953 |
  | F | 60mHK | 220 | 9.85 | 740 |

- **Valg tatt underveis:**
  - `age_class` er `"senior"`, `"G15"`–`"G17"` eller `"J15"`–`"J17"`; klassen må passe kjønnet. Andre klasser
    avvises med `UnknownEventError`. Standardøvelsene gjelder alle klasser, tilleggsøvelsene bare sine.
  - `implement` ignoreres: tabellen er lik uansett redskap (BV-021). `EventInfo.implement` er `None`.
  - Nye `event_id`-er: `weight_throw` (vektkast). NFIFs 800 m inne for G15/16 bruker `middle_800m`, og 100 m
    hekk G15/16 bruker `hurdles_100m`, samme id som kvinnenes øvelser (skilt på kjønn).
  - Manuell tid over 400 m godtas, men gir tillegg 0 og et steg med `ref="BV-024"`. `manual_timing_allowed` i
    `InputSpec` er likevel `False` for disse, fordi feltet betyr «regelverket har tillegg».
  - Rimelig område: samme andeler som Tyrving (0,6–3,0 × og 0,2–1,6 × resultatet for 1000 poeng), regnet
    fra formelen. Brukerhjelp, påvirker ikke poeng.
  - Rå poeng vises avkortet til fire desimaler i `calculation_detail`, så visningen aldri runder opp til et
    heltall motoren ikke gir.
  - `source` per øvelse i parameter-JSON har `ref` (kildenøkkel eller BV-nummer) og `location` (side/paragraf).
    Kvinner 1500 m har `ref="BV-022"`, fordi IAAF-boka ikke ligger i repoet (B-23).
  - Fixture-fila er gruppert per ark med én case per linje (`[rad, resultat i arket, result, poeng]`), 1,75 MB
    i stedet for 10 MB med én dict per case.
- **Avvik fra oppgavefila:** Ingen.
- **Funn som bør bli egne oppgaver:** Skrevet i Innboks: låsing av fixturen (🧑), og at kvinner 100 m hekk
  senior mangler fasit i NFIF-arkene.
