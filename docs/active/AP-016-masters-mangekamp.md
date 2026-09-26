# AP-016: Masters mangekamp (WMA Appendix B, NFIF-tabellen som fasit)

**Status:** Klar
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

## Sluttrapport (fylles av Code)

- **Gjort:**
- **Bevis:**
- **Valg tatt underveis:**
- **Avvik fra oppgavefila:**
- **Funn som bør bli egne oppgaver:**
