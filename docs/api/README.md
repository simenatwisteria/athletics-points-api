# API-kontrakt v1 — oversikt

Kontrakten er [`openapi.yaml`](openapi.yaml) (OpenAPI 3.1, AP-020). Dette er den lesbare oversikten. Simen godkjenner
kontrakten i AP-036 før API-et bygges (AP-021).

Kontroll: `python scripts/openapi_check.py` sjekker strukturen og at hvert eksempel stemmer med skjemaet.
`tests/test_api_contract.py` kjører eksemplene gjennom motorene og krever samme poeng, steg og klasser.

## Endepunkter (alle under `/api/v1`)

| Endepunkt | Hva | Hvem trenger det |
|---|---|---|
| `GET /health` | Status, pakkeversjon og registrerte systemer | Railway, overvåking |
| `GET /systems` | Tabellene med navn og beskrivelse (no/en), gruppe, *klar*, klassetype, klasser, mangekamp, versjoner og kilder | Frontend (startsiden) |
| `GET /events?system=&version=&gender=&age_class=` | Øvelseskatalog: navn (no/en), kategori, utstyr, `InputSpec`, 1000-poengsresultat | Frontend (menyene) |
| `POST /calculate` | Én beregning med alle steg | Frontend, 5KAMP |
| `POST /combined` | Mangekamp: poeng per øvelse og sum | Frontend, 5KAMP |
| `POST /batch` | 1–2000 rader, eget svar og `status` per rad | minfriidrett.no |
| `POST /interpret` | **Planlagt** (`x-status: planned`, svarer 501 i v1). Tolker tekst fra Liveres/OpenTrack og gir tolkning + poeng (B-27) | minfriidrett.no |

Kontrolltall i eksemplene: menn 200 m 23,79 = 712 (`wa_combined_events`), G15 800 m 2:04,56 = 991 med steg
`BV-011` (`tyrving`), M50 100 m 13,12 = 681 (`masters_combined_events`), og `auto` for mann 16 år gir
`wa_combined_events` G16 = 712.

## Forespørsel og svar

- `result` er et tall: sekunder totalt for tider (2:04,56 sendes som `124.56`) og meter for lengder. Hvilken av
  dem som gjelder, står i `input.measure` for øvelsen. `manual_timing` er valgfri (standard `false`).
- `implement` må sendes når øvelsen har flere utstyrsvarianter i klassen (for eksempel 110 m hekk G17). Den kan
  alltid sendes. Stemmer den ikke med klassens utstyr, er svaret `implement_mismatch`, aldri poeng.
- Svaret (`Calculation`) er `ScoreResult` fra `athletics_scoring`, pluss `result_kind` og, med `auto`,
  `selection`. WMA Age Grading gir `result_kind: age_adjusted_result`: `points` er 0 og det aldersjusterte
  resultatet står i `result_used` (BV-041).
- **Tall, ikke tekst.** API-et formaterer ikke etter språk. Klienten viser komma på norsk og punktum på engelsk.
  Unntaket er de lesbare forklaringene (`calculation_detail`, `formula`), som er norsk tekst.

## Tabellvalg (`system: auto`)

`auto` tar `gender` og `age` (klassealder i hele år) i stedet for `age_class`:

| Alder | System | Klasse |
|---|---|---|
| 10–14 | `tyrving` | `"10"`–`"14"` |
| 15–17 | `wa_combined_events` | G15–G17 / J15–J17 (BV-021, BV-023) |
| 18 og eldre | `wa_combined_events` | `senior` |

Masters (`masters_combined_events`, `wma_age_grading`) brukes bare når klienten ber om det, fordi klubbstevner ofte
bruker senior-tabellen for alle voksne. Svaret har `selection` med alder, system, klasse, regel og `ref`.

## Feilformat

Alle feil har samme form: `{"error": {"code": "...", "message": "... (norsk)", "details": {...} | null}}`.

| Feiltype i `athletics_scoring` | HTTP | `code` |
|---|---|---|
| `UnknownSystemError` | 422 | `unknown_system` |
| `UnknownVersionError` | 422 | `unknown_version` |
| `UnknownEventError` | 422 | `unknown_event` |
| `ImplementMismatchError` (underklasse av `UnknownEventError`): utstyret er ikke klassens | 422 | `implement_mismatch` |
| `AmbiguousEventError` | 422 | `ambiguous_implement` |
| `InvalidResultError` | 422 | `invalid_result` |
| `UnsupportedManualTimingError` | 422 | `unsupported_manual_timing` |
| `InvalidCombinedEventError` | 422 | `invalid_combined_event` |
| Ugyldig forespørsel (skjema) | 422 | `validation_error` |
| For mange forespørsler | 429 | `rate_limited` (med `Retry-After`) |
| `/interpret` i v1 | 501 | `not_implemented` |
| `DuplicateEngineError` og alt uventet | 500 | `internal_error` |

I `/batch` gir disse feilene ikke HTTP-feil. Raden får `status` (`ok`, `no_result`, `ambiguous_implement`,
`implement_mismatch`, `invalid`) og `message`, og `invalid` har `error` med koden over. `result: null` (DNS, DNF,
NM, DQ) gir `no_result`. Svaret er 200 så lenge selve forespørselen er gyldig.

## CORS, caching og tilgang

- **CORS:** tillatte opphav er en konfigurerbar liste. Standard er `https://5kamp.minfriidrett.no` og frontendens
  domene (settes ved deploy). 5KAMP kaller fra nettleseren og har ingen backend.
- **Caching (B-7):** med `version` i forespørselen svarer `/calculate`, `/combined` og `/batch` med
  `Cache-Control: public, max-age=31536000, immutable`. Uten `version` brukes nyeste versjon og `no-cache`.
- **Tilgang (B-4):** åpent uten nøkkel, rate limiting per IP. API-nøkler med høyere grense for partnere (først
  minfriidrett.no) kommer senere og er ikke en del av v1.

## `ref` i beregningsstegene

Hvert steg i `calculation_steps` har `label`, `value`, `formula` og `ref`. `ref` er enten et beregningsvalg
(`BV-011`, se [`docs/BEREGNINGSVALG.md`](../BEREGNINGSVALG.md)) eller `key` til et kildedokument i `sources` fra
`GET /systems` (for eksempel `nfif-tyrving-2014-gutter` eller `wma-2023-appendix-b`). `null` betyr at steget er ren
regning uten eget valg. Kildene har `official_page`, `document_url`, lokal sti og SHA-256 (B-24).

## Valg

1. **`age_class` i motorens eget format**, ikke et felles format som API-laget oversetter. `GET /systems` gir
   klasselisten per system og `class_type` sier hvordan den leses. Et felles format ville vært en ekstra
   oversettelse som kan gå galt, og hvert system har allerede sitt naturlige format (alder, klasse, masters-klasse).
   Klienter som bare vet alderen, bruker `system: auto`.
2. **`result` er ett tall** (sekunder totalt eller meter) i stedet for `Result` med minutter og sekunder. Det er
   enklere for alle tre klientene, og API-laget velger felt etter `input.measure`. Motoren gir samme poeng for
   `124.56` s som for 2 min 4,56 s.
3. **`auto` bruker klassealder** (alderen utøveren fyller i konkurranseåret), som ungdomsklassene. WMA Age Grading,
   som bruker alder på konkurransedagen (BV-040), er ikke med i `auto`.
4. **Feil utstyr er `implement_mismatch`, ikke `unknown_event`.** Motorene kaster `UnknownEventError` i begge
   tilfeller. API-laget skiller dem ved å se om øvelsen finnes for klassen uten `implement`.
5. **Alle 4xx fra beregningen er 422**, også ukjent system. Forespørselen er syntaktisk riktig, men kan ikke
   beregnes. 404 er reservert for ukjente stier.
6. **`/systems` viser også tabeller som ikke er klare** (`ready: false`, for eksempel Serietabellen), fordi
   startsiden viser dem med status *Kommer*.
7. **Vind og inne/ute** er bare med i `/interpret`. De påvirker ingen poeng i dag, så `/calculate` tar dem ikke imot.
8. **Kontrollen av YAML-en** gjøres av et lite skript (`scripts/openapi_check.py`) uten nye avhengigheter. Det leser
   et utsnitt av YAML som kontrakten holder seg innenfor, og sjekker OpenAPI-strukturen og eksemplene mot skjemaene.
   Det er ikke en full OpenAPI-validator.

## Ikke i v1

`/reverse` (B-8), `/parameters/export` (B-9), API-nøkler (B-4), Serietabellen (B-26) og WA Scoring Tables 2025
(AP-011).
