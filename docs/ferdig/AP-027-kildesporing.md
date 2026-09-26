# AP-027: Kildesporing i parametre og beregningssteg

**Status:** Ferdig 2026-09-26
**Opprettet:** 2026-09-26 (Cowork)
**Eier:** 🤖 Code
**Avhenger av:** AP-001

## Mål

Hver poengberegning kan spores til en offisiell kilde og til valgene vi har tatt. En bruker som ser et poengtall,
skal kunne følge `calculation_steps` til NFIF-siden, dokumentet, siden i dokumentet og BV-nummeret i
`docs/BEREGNINGSVALG.md`.

## Hvorfor

Transparens er hovedpoenget med tjenesten (B-10, B-24). minfriidrett.no skal vise poeng til utøvere og trenere,
og når et tall overrasker, må forklaringen stå ved siden av. Dette bygges nå, før flere motorer kommer, så
AP-012, AP-016 og AP-014 kan bruke samme mønster fra start i stedet for å ettermontere det.

## Les dette før du koder

- `athletics_scoring/models.py` — `CalculationStep` (label, value, formula) og `ScoreResult`
- `athletics_scoring/tyrving.py` — hvordan stegene bygges i dag (linje ca. 210–275). Stegene nevner allerede
  regelnumre som «(R3)» i `formula`.
- `athletics_scoring/data/tyrving_parameters_2014.json` — `meta.sources` har i dag bare filsti → SHA-256
- `tests/test_tyrving_params.py` linje 61–64 — leser `meta.sources` som dict
- `scripts/extract_tyrving_params.py` — der `meta` skrives (JSON-en redigeres aldri for hånd)
- `docs/BEREGNINGSVALG.md` — BV-001 til BV-015 gjelder Tyrving
- `sources/README.md` — URL og NFIF-side for hver kildefil

## Verifiserte fakta

- `CalculationStep` har ingen referansefelt i dag. Tyrving-stegene har regelnumre bare som fritekst i `formula`.
- NFIF-siden for Tyrving: https://www.friidrett.no/arrangement/arrangementshjelp/poengtabeller/tyrvingtabellen/
- Dokument-URL-er for Tyrving-filene står i `sources/README.md` (DOC-filene er de offisielle).

## Løsningsretning

1. `CalculationStep` får et valgfritt felt `ref: str | None = None`. Verdien er et BV-nummer (`"BV-011"`) eller
   en kildenøkkel (se punkt 2). Feltet er valgfritt, så eksisterende kode og tester fortsetter å virke.
2. `meta` i parameter-JSON får en ny nøkkel `source_documents`: en liste med objekter
   `{"key", "title", "publisher", "official_page", "document_url", "local_path", "sha256", "retrieved"}`.
   Behold `meta.sources` (filsti → SHA-256) uendret, fordi `tests/test_tyrving_params.py` linje 61–63 leser den.
   `key` er en kort id som steg kan peke til (f.eks. `"nfif-tyrving-2014-gutter"`). Oppdater
   `extract_tyrving_params.py` så den skriver dette, og generer JSON-en på nytt.
3. Motoren eksponerer kildene: en metode `sources()` på `ScoringEngine` som returnerer `source_documents`.
   Den blir grunnlaget for `GET /systems` senere.
4. Tyrving-stegene får `ref` der et BV-valg påvirker resultatet: manuell tid (BV-012), stryking av hundredeler
   (BV-011), nedrunding og 0-gulv (BV-003), og kildesteget peker til riktig kildenøkkel.
5. En test går gjennom alle BV-numre som brukes i koden og sjekker at hvert finnes som overskriftslinje i
   `docs/BEREGNINGSVALG.md` (regex `^\| BV-\d{3} \|`). Da kan ingen referanse peke til et valg som ikke er
   dokumentert.

## Beregningsvalg

- BV-003, BV-011, BV-012 — skal vises som `ref` i Tyrving-stegene

## Kontrolltall

| Input | Forventet | Kilde |
|---|---|---|
| Tyrving G15 800 m, 2:04.56 | poeng uendret (991), og et steg med `ref == "BV-011"` | `tests/fixtures/tyrving_rules.json` R2 |
| Tyrving, alle 2472 fasit-caser | poeng uendret | `tests/fixtures/tyrving_cases.json` |
| `engine.sources()` for Tyrving | minst to kilder, hver med ikke-tom `official_page` og `sha256` lik `sources/SHA256SUMS` | `sources/SHA256SUMS` |

## Utenfor scope

- Ingen API-endepunkter. Det kommer i AP-020/AP-021.
- Ikke flytt eller endre formlene i Tyrving. Oppgaven legger bare til sporing.
- Ikke lag et eget kilderegister-modul med klasser for hver kildetype. En liste med dicts i `meta` holder.

## Fallgruver

- `tyrving_parameters_2014.json` genereres av skriptet. Endre skriptet og kjør det, ikke JSON-en for hånd.
- Å gjøre om `meta.sources` til en liste ville brutt `test_tyrving_params.py`. Legg til en ny nøkkel i stedet.

## Når du skal stoppe

Sett oppgaven til `Blokkert` og avslutt hvis:
- en låst fixture eller en test må endres for å bli grønn
- regenerering av parameter-JSON endrer noe annet enn `meta`

Alt annet avgjør du selv, og skriver valget i sluttrapporten.

## Akseptansekriterier

- [x] Kontrolltallene over er egne testcaser og er grønne
- [x] `CalculationStep.ref` finnes og brukes i Tyrving-stegene for BV-003, BV-011 og BV-012
- [x] Testen som sjekker at alle BV-numre i koden finnes i `docs/BEREGNINGSVALG.md` er grønn
- [x] `git diff athletics_scoring/data/tyrving_parameters_2014.json` viser bare endringer i `meta`
- [x] `pytest -q && ruff check . && mypy athletics_scoring` er grønt
- [x] Ingen endringer i `sources/` eller låste `tests/fixtures/`
- [x] Midlertidige filer og hjelpeskript fra underveis er fjernet
- [x] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Sluttrapport (fylles av Code)

- **Gjort:** `CalculationStep.ref: str | None = None` (`models.py`). `ScoringEngine.sources()` (`engine.py`,
  kaster `NotImplementedError` som standard, som `reverse`). `meta.source_documents` med fem Tyrving-filer (DOC
  gutter/jenter, PDF gutter/jenter, regnearket), skrevet av `scripts/extract_tyrving_params.py` og generert på
  nytt. `TyrvingCalculator.sources()` leser dem fra JSON-en. Tyrving-stegene: `manual_timing_addition` → BV-012,
  nytt steg `hundredths_dropped` → BV-011, `points` → BV-003, `points_raw` → kildenøkkelen for kjønnet
  (`nfif-tyrving-2014-gutter`/`-jenter`, DOC-ene). Ny test `tests/test_kildesporing.py` (6 tester).
- **Bevis:** `pytest -q` 105 passed (inkl. alle 2472 fasit-caser i `test_all_fixture_cases`), `ruff check .` og
  `mypy athletics_scoring` grønne. `extract_tyrving_params.py --check` gir OK. `git diff --stat` på JSON-en:
  52 innsettinger, alle inne i `meta.source_documents`. G15 800 m 2:04,56 gir 991 og et steg med
  `ref == "BV-011"` og verdi 124,5.
- **Valg tatt underveis:**
  - `hundredths_dropped` legges bare til når det faktisk strykes noe i et løp over 500 m. Steget forklarer da
    hvorfor tiden ble endret; uten endring er det ingenting å forklare.
  - `sources()` er ikke abstrakt, så eksisterende motorer (og `Dummy` i `test_registry.py`) fortsatt virker. Den
    kaster i stedet for å returnere tom liste, så en motor uten kilder ikke går stille gjennom `GET /systems`.
  - `document_url` er `null` for alle fem filene. `sources/README.md` har ikke URL-en til DOC-ene, og
    PDF-ene og regnearket har ukjent eller utdatert opphav. Ikke gjettet (Innboks).
  - `retrieved` er datoen filene kom inn i `sources/` (2026-09-25).
- **Avvik fra oppgavefila:** Det er ikke laget et eget «kildesteg». `test_score_result_explains_calculation`
  låser labellista til `["eighty_percent", "points_raw", "points"]`, og testen skal ikke endres. Kildenøkkelen
  ligger i stedet som `ref` på `points_raw`, som er tabellformelen med parametrene fra kilden.
- **Funn som bør bli egne oppgaver:** Direktelenker til DOC-ene i `sources/README.md` (Innboks).
