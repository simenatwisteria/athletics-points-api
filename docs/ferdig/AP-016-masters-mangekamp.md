# AP-016: Masters mangekamp (WMA Appendix B, NFIF-tabellen som fasit)

**Status:** Ferdig 2026-09-27 (fixture ulåst, venter på Simens stikkprøve)
**Opprettet:** 2026-09-26 (Cowork)
**Eier:** 🤖 Code
**Avhenger av:** AP-012, AP-013, AP-015

## Mål

En motor `("masters_combined_events", "2023")` som gir poeng i masters mangekamp for M/W35–M/W100. Poengene skal
være identiske med NFIFs masters-mangekamptabeller, og hvert steg skal vise aldersfaktoren og avrundingen.

## Hvorfor

Masters mangekamp er et av systemene NFIF publiserer, og ingen åpne kalkulatorer viser hvordan poengene regnes.
Metoden er fullt beskrevet i WMA Appendix B, og NFIF-tabellen gir en komplett fasit. Beslutningen fra
2026-09-25 og B-25 står: NFIF-tabellen er fasit, og motoren regner etter metoden.

## Les dette før du koder

- `athletics_scoring/wa_combined_events.py` (fra AP-012) — formlene og mønsteret. Kall denne motoren for
  poengsteget i stedet for å kopiere formlene.
- `sources/wma/wma-2023-appendix-b-combined-events.pdf` s. 1 (metode, avrunding, håndtid) og s. 4–5
  (aldersfaktorer per 5-årsklasse: kvinner s. 4, menn s. 5)
- `sources/masters/nfif-masters-mangekamp-menn.xlsx` og `-kvinner.xlsm` — alle ark, alle klassekolonner
- `docs/BEREGNINGSVALG.md` BV-024, BV-030 til BV-035
- `docs/KILDEAVVIK.md` — «Manuell tid på 60 m og 60 m hekk»

## Verifiserte fakta

- **Metode** (Appendix B s. 1): (1) håndtid ≤ 400 m korrigeres først (+0,24 s til og med 300 m, +0,14 s på
  400 m), (2) resultat × aldersfaktor med fire desimaler, (3) løp rundes **opp** til 0,01 s, hopp og kast **ned**
  til hel cm, (4) poeng fra Combined Events, avkortet til heltall.
- **Eksempler i Appendix B s. 1:** M50 100 m 13,12 × 0,9031 = 11,848672 → 11,85 → 681 poeng. W35 høyde 1,47 ×
  1,0205 = 1,500135 → 1,50 → 621 poeng.
- **Stikkprøver mot NFIF-arket** (Cowork): M35 200 m 19,44 × 0,9791 = 19,0337 → 19,04 → 1200 (arket: 1200).
  M50 kule 6 kg 18,70 × 1,1551 = 21,6004 → 21,60 → 1200 (arket: 1200).
- **Arkoppsett:** Rad 2 har klassene: kolonne B = «Sr», kolonne C–P = 35, 40, …, 100 (14 klasser). Kastark har
  raden «Vekt:» med redskapsvekt per klasse, for eksempel menn kule: Sr–45 7,26 kg, 50–55 6 kg, 60–65 5 kg, 70–75
  4 kg, 80–100 3 kg. Hekkeark har raden «Hhøyde». Kvinnenes `80-100mHK`-ark starter på W40.
- **Aldersfaktorene tar hensyn til redskap og hekkehøyde** (Appendix B s. 1). Et M65-kulestøt med 5 kg slås opp
  i 7,26 kg-tabellen etter at det er ganget med faktoren.

**Ikke bekreftet, sjekk selv først:**
- Bare stikkprøvene over er kontrollert. Hele tabellen er ikke sjekket mot metoden.
- Hvilken faktorkolonne i Appendix B som hører til hvilket hekkeark («60m Hurdles» og «Short Hurdles»), og hvilken
  referanseøvelse i Combined Events hver hekkeklasse slås opp i (110 m hekk menn, 100 m hekk kvinner, 60 m hekk).
- Om de manuelle arkene for 100, 200 og 400 m følger «korriger først, så faktor».

## Løsningsretning

1. `scripts/extract_wma_ce_factors.py` leser aldersfaktorene fra Appendix B (tekst med `pdfplumber` eller
   konstanter med sidehenvisning, velg det som gir minst rom for feil) og redskap og hekkehøyde per klasse fra
   raden «Vekt:»/«Hhøyde» i NFIF-arkene. Skriver `athletics_scoring/data/masters_combined_events_2023.json`
   med `source_documents`.
2. `scripts/oracle_masters_combined_events.py` leser *alle* klassekolonnene (C–P) i alle ark og skriver
   `tests/fixtures/masters_combined_events_cases.json` (ny, ulåst). Importerer ikke `athletics_scoring`.
3. `athletics_scoring/masters_combined_events.py`: `MastersCombinedCalculator(ScoringEngine)`. `age_class` er
   f.eks. `"M50"` eller `"W65"` (BV-033). Redskapet er gitt av klassen. Et resultat med annet redskap avvises med
   en feil som sier hvilket redskap klassen bruker (BV-034).
4. Stegene: resultat, håndtidskorreksjon (`ref` BV-024), aldersfaktor (`ref` BV-030 og kildenøkkel), aldersjustert
   resultat før og etter avrunding (`ref` BV-031), poeng fra Combined Events (`ref` BV-003).
5. `calculate_combined` summerer, som i AP-012.

## Beregningsvalg

- BV-024, BV-030, BV-031, BV-032, BV-033, BV-034, BV-035

## Kontrolltall

| Input | Forventet | Kilde |
|---|---|---|
| M50 100 m 13,12 | 681 (aldersjustert 11,85) | Appendix B s. 1 |
| W35 høyde 1,47 | 621 (aldersjustert 1,50) | Appendix B s. 1 |
| M35 200 m 19,44 | 1200 | NFIF-arket `200m`, kolonne C (M35), raden for 1200 poeng |
| M50 kule 6 kg 18,70 | 1200 | NFIF-arket `Kule`, kolonne F (M50), raden for 1200 poeng |
| M50 kule med 7,26 kg | avvises (klassen bruker 6 kg) | BV-034 |
| Alle klassekolonner i alle ark, unntatt 60 m-manuell | null avvik | `tests/fixtures/masters_combined_events_cases.json` |

## Utenfor scope

- WMA Age Grading med ettårige faktorer (AP-014). Her brukes bare 5-årsklassene.
- Masters serietabell (AP-019).
- Beregning av klasse fra fødselsdato. API-et tar imot klassen (BV-033).
- Ikke dupliser formlene fra AP-012. Kall motoren derfra.

## Fallgruver

- «Løp opp, hopp og kast ned» gjelder det aldersjusterte resultatet, ikke bare input. Feil retning gir ofte
  riktig svar, så testen må ha tilfeller nær grensen (som 11,848672 → 11,85).
- `Decimal` og faktor med fire desimaler: `13.12 * 0.9031` som flyttall kan gi 11,848671999…, som rundet opp
  fortsatt blir 11,85, men nær hele hundredeler kan flyttall havne feil. Bruk `Decimal`.
- Kolonne B i poeng-først-arkene er *laveste resultat for poengtallet*. Test fra resultat til poeng.
- Håndtid: korrigeringen skjer før faktoren, og tabellene for manuell tid i IAAF-boka brukes aldri for masters
  (Appendix B s. 1).

## Når du skal stoppe

Sett oppgaven til `Blokkert` og avslutt hvis:
- en test bare kan bli grønn ved å endre en test, en låst fixture eller `sources/`
- et ark eller en klasse gir avvik mot metoden som ikke er 60 m-manuell. Skriv arket, klassen og tre eksempler
  i notatet. Dette er et kildeavvik Simen må ta stilling til (BV-035).
- det er uklart hvilken hekkeøvelse en klasse skal slås opp i, og arket ikke avgjør det

Alt annet avgjør du selv innenfor løsningsretningen, og skriver valget i sluttrapporten.

## Akseptansekriterier

- [ ] Kontrolltallene over er egne testcaser og er grønne
- [ ] Oracle-fixturen dekker alle klassekolonnene, og testen mot den har null avvik (unntatt de dokumenterte)
- [ ] `calculation_steps` viser faktor, avrunding og `ref` til BV-numrene
- [ ] Feil redskap for klassen gir en forklarende feil
- [ ] Fixture-fila er ny og ulåst. Sluttrapporten lister 10 caser spredt over øvelser og skala som Simen kan
      stikkprøve mot kilden før den låses
- [ ] `pytest -q && ruff check . && mypy athletics_scoring` er grønt
- [ ] Ingen endringer i `sources/` eller låste `tests/fixtures/`
- [ ] Midlertidige filer og hjelpeskript fra underveis er fjernet
- [ ] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Blokkert (Code, 2026-09-26)

Stoppregel: «et ark eller en klasse gir avvik mot metoden som ikke er 60 m-manuell».

**Hva som er gjort:** Et midlertidig skript regnet hele metoden på alle klassekolonnene i alle ark:
faktorer fra Appendix B s. 4–5, håndtid +0,24/+0,14 s før faktoren, «løp opp, hopp og kast ned», og
poeng fra `CombinedEventsCalculator` («senior»). Det ga **null avvik på 431 467 caser**. Unntakene er
de to avvikene under og 60 m-manuell-arkene, som ikke var med. Kontrolltallene i oppgavefila stemmer.
Hekkeoppslaget er avklart av arkene: menn 35–45 110 m (99 cm), 50–65 100 m (91/84 cm), 70–100 80 m
(76/68 cm), alle med «Short Hurdles»-faktoren i 110 m hekk-tabellen. Kvinner 35 100 m (84 cm), 40–100
80 m (76/68 cm), med «Short Hurdles» i 100 m hekk-tabellen. Kvinner 100m-m har ingen W100-kolonne.

Utkastet til `scripts/oracle_masters_combined_events.py` er committet. Det leser alle blokkene,
inkludert hekkearkene med flere tabeller side om side og redskap per klasse. Det stopper med vilje på
de ødelagte cellene. Fixture, parameterfil og motor er ikke laget.

**Avvik 1 — 80 m hekk, manuell tid.** Arkene `80-110m HK-m` (menn, blokk M–T, M70–M100) og
`80-100mHK-m` (kvinner, blokk A–M, W40–W95; W100 har ingen avvik i de radene som finnes) gir flere poeng
enn metoden. Med +0,20 s i stedet for +0,24 s blir det null avvik, akkurat som på 60 m og 60 m hekk
(KA i `KILDEAVVIK.md`). Manuelle 100 og 110 m hekk og 100/200/400 m følger +0,24/+0,14.

| Ark | Klasse | Manuell tid | Arket | Metoden (+0,24) |
|---|---|---|---|---|
| `80-100mHK-m` | W40 | 10,8 | 1199 | 1192 |
| `80-110m HK-m` | M70 | 11,2 | 1206 | 1199 |
| `80-110m HK-m` | M75 | 12,0 | 1200 | 1194 |

**Avvik 2 — menn `200m`, M95 og M100.** Tekstcellene i kolonne N–P fra rad 983 er forskjøvet. Siste
siffer i én kolonne står først i neste kolonne, skilt med to mellomrom:

| Rad | Poeng | N (M90) | O (M95) | P (M100) | Riktig lesning |
|---|---|---|---|---|---|
| 983 | 200 | 51.60 | `1.00.0` | `2  1.14.72` | M95 1.00.02, M100 1.14.72 |
| 984 | 199 | 51.63 | `1.00.0` | `6  1.14.77` | M95 1.00.06, M100 1.14.77 |
| 1163 | 20 | `1.00.0` | `5  1.09.8` | `6  1.26.96` | M90 1.00.05, M95 1.09.86, M100 1.26.96 |

200 celler i P og 20 i O kan ikke leses som tid. 82 celler i O (M95) er avkortede tider som gir
feil poeng (rad 984: «1.00.0» gir 200, arket sier 199; reparert 1.00.06 gir 199). Reparert lesning gir
riktige poeng i alle kontrollerte eksempler.

**Forslag til Simen:**
1. 80 m hekk manuell: legg inn en KA som utvider «Manuell tid på 60 m og 60 m hekk» til 80 m hekk. Da
   hoppes blokkene over i fasiten, og motoren følger +0,24 s (BV-024). Alternativet er at NFIF bruker
   +0,20 s under 100 m med vilje. Det bør i så fall inn i e-posten til NFIF (AP-026).
2. 200 m M90–M100: bestem om oracle-skriptet skal (a) hoppe over de ødelagte cellene og registrere dem
   i `meta`, eller (b) reparere den forskjøvne teksten. (b) er en tolkning av kilden. (a) gir ingen
   gjetting.

## Avgjørelse (Cowork, 2026-09-26, gjelder til Simen sier noe annet)

1. **80 m hekk manuell:** Forslag 1 er valgt. Blokkene med +0,20 s hoppes over i fasiten, og motoren bruker
   +0,24 s (BV-024, `KILDEAVVIK.md`). Utelatelsen skal stå i fixturens `meta` med ark, blokk og klasser.
2. **200 m M90–M100:** Alternativ (a). Oracle-skriptet hopper over cellene som ikke kan leses som tid, og de 82
   avkortede M95-cellene. Alle skal listes i `meta` med rad, kolonne og råtekst. Ingen reparasjon (BV-035).
   Avgjør selv hvordan du kjenner igjen de avkortede cellene (f.eks. `m.ss.c` med bare ett siffer etter siste
   punktum der kolonnen ellers har hundredeler), og skriv regelen i sluttrapporten.
3. **Hekkeoppslaget** er avklart av Code og kan brukes som beskrevet under «Blokkert».

4. **Kvinner 100 m hekk senior** (Innboks fra AP-012): NFIF-arkene har ingen seniorkolonne for øvelsen. Legg til
   tre kontrolltall fra IAAF-boka s. 104 i `tests/test_wa_combined_events.py`: 12,00 = 1280, 12,50 = 1201,
   13,50 = 1050 (Cowork har sjekket at formelen gir det samme). Tabellen dekkes også indirekte av W35-kolonnen.

Fortsett fra utkastet til `scripts/oracle_masters_combined_events.py`. Resten av oppgaven er uendret.

## Sluttrapport (fylles av Code)

*(Code, 2026-09-27, commit `7d9b54e`)*

- **Gjort:**
  - `scripts/extract_masters_combined_events_params.py` leser faktorene fra Appendix B PDF-side 4–5 med
    `pdfplumber`. Kolonnerekkefølgen står som konstanter, og fire kjente verdier kontrolleres. Klasser og
    redskap/hekkehøyde leses fra raden «Vekt:»/«Hhøyde». Skriptet skriver
    `athletics_scoring/data/masters_combined_events_2023.json` (35 øvelser, 3 kildedokumenter).
  - `scripts/oracle_masters_combined_events.py` er ferdig fra utkastet og skriver
    `tests/fixtures/masters_combined_events_cases.json` (ny, ulåst, 538 blokker, 427 750 caser). Utelatelsene
    står i `meta.skipped_sheets`, `meta.skipped_blocks` og `meta.skipped_cells` (rad, kolonne, råtekst, grunn).
  - `athletics_scoring/masters_combined_events.py`: `MastersCombinedCalculator` (`masters_combined_events`
    2023), registrert i `default_registry()`. Den kaller `CombinedEventsCalculator` for poengsteget.
    `_effective_result` i `wa_combined_events.py` er gjort om til modulfunksjonen `effective_result`, så begge
    motorene deler kontroll, BV-025-avrunding og BV-024-tillegg. Oppførselen er uendret.
  - `tests/test_masters_combined_events.py` (27 tester). Tre kontrolltall for kvinner 100 m hekk senior er lagt
    til i `tests/test_wa_combined_events.py` (avgjørelse 4).
- **Bevis:**
  - `pytest -q`: 182 passed (56 s). `ruff check .` og `mypy athletics_scoring` er grønne.
  - `test_all_fixture_cases`: **null avvik** på 427 750 caser (alle klassekolonner i alle ark, automatisk og
    manuell tid, unntatt utelatelsene under).
  - Kontrolltallene: M50 100 m 13,12 → 11,85 → 681 · W35 høyde 1,47 → 1,50 → 621 · M35 200 m 19,44 → 1200 ·
    M50 kule 18,70 → 1200 · M50 kule med `7,26kg` avvises («M50 bruker 6kg i kule …, BV-034»).
  - `test_fixture_covers_every_class_column`: hver (kjønn, øvelse, klasse) motoren tilbyr, har en blokk med
    automatisk tid eller distanse, og redskapet i motoren er det samme som i arket.
  - Begge skriptene er reproduserbare (`--check` i testene). Ingen endringer i `sources/` eller låste fixtures.
- **Valg tatt underveis:**
  - **Avkortede celler:** i ark med automatisk tid regnes en tekstcelle med bare ett siffer etter siste punktum
    (`^[\d.]*\.\d$`, f.eks. «1.00.0») som avkortet og hoppes over. Celler som ikke passer tidsformatet, er
    «kan ikke leses som tid». Regelen treffer bare menn `200m`: N (M90) 20 avkortede, O (M95) 180 avkortede
    og 20 uleselige, P (M100) 200 uleselige, til sammen 420. Det er flere enn de 82 i avgjørelsen, fordi regelen
    også tar avkortede celler som tilfeldigvis gir riktige poeng og de 20 i M90 (rad 1163–1182). Regelen er
    strukturell og bruker ikke motoren.
  - **Kvinner `100m-m`, kolonne P:** kolonnen har data i rad 138–359 (222 celler), men ingen klasse i rad 2.
    Den er utelatt og listet i `meta` (samme prinsipp som BV-035 (a)). Kontroll utenfor fixturen: lest som
    W100 gir motoren samme poeng i alle 222 radene. Se Innboks.
  - Stegene: `input` → (`rounded` BV-025) → (`manual_timing_addition` BV-024) → `age_factor` (ref
    `wma-2023-appendix-b`, teksten nevner BV-030/BV-032) → `age_adjusted` (BV-030) → `age_adjusted_rounded`
    (BV-031, vises alltid) → `difference` → `points_raw` → `points` (BV-003).
  - Feil redskap gir `UnknownEventError`, samme type som Tyrving bruker for ukjent utstyr. `implement` kan
    utelates, og redskapsteksten tolkes tallmessig («6 kg», «6.0kg», «700g» godtas).
  - `result_used` er det aldersjusterte, avrundede resultatet (det tabellen slår opp). Det rimelige området er
    seniortabellens område delt på faktoren.
  - Bare klassene 35–100 er med (NFIF-arkene). Faktorene for 105 og 110 i Appendix B er ikke tatt med.
- **Avvik fra oppgavefila:** Flere celler er utelatt enn de 82 som er nevnt (se over). I tillegg er kolonne P i
  kvinner `100m-m` utelatt, som ikke var kjent da oppgaven ble avgjort.
- **Funn som bør bli egne oppgaver:** se Innboks (kolonne P uten klasse, størrelsen på fixturen).
- **10 caser til stikkprøve** (resultat → poeng, fra fixturen):

  | Ark | Celle | Klasse | Redskap | Resultat i arket | Poeng |
  |---|---|---|---|---|---|
  | menn `100m` | N484 | M90 | — | 22.49 | 259 |
  | kvinner `400m-m` | D609 | W40 | — | 1.06.3 (manuell) | 594 |
  | menn `1500m` | I468 | M65 | — | 5.47.31 | 736 |
  | kvinner `80-100mHK` | I16 | W75 | 68 cm | 15.29 | 1182 |
  | menn `80-110m HK-m` | J74 | M60 | 84 cm (100 m hekk) | 19.4 (manuell) | 470 |
  | kvinner `Høyde` | F115 | W50 | — | 0.87 | 156 |
  | menn `Stav` | F110 | M50 | — | 4.85 | 1181 |
  | kvinner `Kule` | G689 | W55 | 3 kg | 7.93 | 516 |
  | menn `Spyd` | P691 | M100 | 0,4 kg | 9.39 | 514 |
  | menn `200m-m` | J94 | M70 | — | 27.8 (manuell) | 905 |

  I poeng-først-arkene er cellen resultatet og poengene står i kolonne A i samme rad. I resultat-først-arkene
  (hopp og de fleste «-m»-arkene) er cellen poengene og resultatet står i kolonne A.
