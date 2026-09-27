# AP-021: API-implementasjon (FastAPI) etter kontrakten v1

**Status:** Ferdig 2026-09-27
**Opprettet:** 2026-09-27 (Cowork)
**Eier:** 🤖 Code
**Avhenger av:** AP-020 (ferdig), AP-036 (kontrakten godkjent av Simen 2026-09-27)

## Mål

Et kjørbart HTTP-API som oppfyller `docs/api/openapi.yaml` for alt som ikke er merket `x-status: planned`, med tester
som kjører mot kontrakten. Etter oppgaven kan `uvicorn athletics_api.main:app` startes lokalt, og AP-022 kan deploye
det på Railway uten kodeendringer.

## Hvorfor

Motorene er ferdige og verifisert, og kontrakten er godkjent. API-et er det som gjør dem brukbare for andre:
5KAMP skal kontrollere eller hente poengene sine herfra etter stevnet 2026-10-03, minfriidrett.no skal bruke
`/batch`, og frontenden (AP-023) bygger på `/systems` og `/events`.

## Les dette før du koder

- `docs/api/openapi.yaml` og `docs/api/README.md` — kontrakten. Den er fasit for felt, statuskoder og feilformat.
- `tests/test_api_contract.py` — eksemplene i kontrakten kjørt mot motorene. Gjenbruk eksemplene som HTTP-tester.
- `athletics_scoring/__init__.py` (`default_registry()`), `engine.py`, `models.py`, `errors.py`
- `athletics_scoring/tyrving.py` og `wa_combined_events.py` — der 1000-poengsresultatet ligger internt
  (`h1000`, `_result_for_1000`)
- `docs/BACKLOG.md` → Innboks, de tre punktene merket «(AP-020)». De løses i denne oppgaven (se under).
- `docs/INTEGRASJON-5KAMP.md` og `docs/INTEGRASJON-minfriidrett.md` — hvem som kaller og hvordan

## Verifiserte fakta

- `pyproject.toml` har ingen runtime-avhengigheter, og `athletics_scoring` skal fortsatt ikke ha noen
  (CLAUDE.md regel 7). FastAPI hører hjemme i en egen pakke.
- Loopen tillater `python -m pip …` (`Bash(python:*)`), men ikke `pip` direkte.
- CI (`.github/workflows/`) installerer `.[dev]` og kjører `mypy athletics_scoring`.
- Simen har bekreftet i AP-036: `auto` bruker klassealder (alderen utøveren fyller i konkurranseåret).

## Løsningsretning

1. **Ny pakke `athletics_api/`** i samme repo, med `main.py` (app-fabrikk `create_app(settings)` og `app`),
   `settings.py`, rutere per endepunkt og ett felles feilhåndteringslag. Ingen forretningslogikk: all beregning
   går gjennom `default_registry()`.
2. **Avhengigheter:** ny valgfri gruppe `api = ["fastapi", "uvicorn[standard]"]` i `pyproject.toml`, og `httpx` i
   `dev` for `TestClient`. Pakken `athletics_scoring` får fortsatt ingen avhengigheter. Wheel-oppsettet må ta med
   begge pakkene.
3. **Katalogdata (Innboks-punkt 1):** legg engelske navn og kategori i pakken som data, ikke i API-laget, slik at
   frontenden og API-et bruker samme kilde:
   - `athletics_scoring/data/event_catalog.json`: `event_id` → `name_no`, `name_en`, `category`
     (`sprint`, `middle`, `distance`, `hurdles`, `steeplechase`, `racewalk`, `jump`, `throw`, `other`).
     Norske navn skal være de samme som motorene bruker i dag. En test sjekker at hver `event_id` som noen
     motor tilbyr, finnes i katalogen.
   - `ScoringEngine.points_1000_result(event_id, gender, age_class, implement=None) -> float | None`, med
     standard `None`, og implementert for Tyrving (h1000) og WA Combined Events. Masters og Age Grading kan gi
     `None` i v1.
4. **Feil utstyr (Innboks-punkt 2):** ny `ImplementMismatchError(UnknownEventError)` i `errors.py`, kastet der
   motorene i dag kaster `UnknownEventError` fordi utstyret ikke passer klassen. Underklasse, så eksisterende kode og
   tester virker uendret. API-laget mapper den til `implement_mismatch` direkte i stedet for å prøve på nytt uten
   utstyr.
5. **`auto` (Innboks-punkt 3):** som i kontrakten. Svaret har `selection`.
6. **CORS:** tillatte opphav fra miljøvariabelen `CORS_ALLOWED_ORIGINS` (kommaseparert). Standard:
   `https://5kamp.minfriidrett.no`. Ingen jokertegn.
7. **Caching (B-7):** `Cache-Control: public, max-age=31536000, immutable` når `version` er oppgitt, ellers
   `no-cache`.
8. **Rate limiting (B-4):** enkel i minnet per klient-IP (glidende vindu), grense fra `RATE_LIMIT_PER_MINUTE`
   (standard 600). Bruk `X-Forwarded-For` bare når `TRUST_PROXY=1` (Railway står bak en proxy). 429 med
   `Retry-After` og feilformatet fra kontrakten. Ingen ny avhengighet for dette.
9. **`/batch`:** maks 2000 rader, status per rad som i kontrakten, 200 så lenge forespørselen er gyldig.
10. **`/interpret`:** svarer 501 `not_implemented` som kontrakten sier.
11. **Oppstart:** `uvicorn athletics_api.main:app --host 0.0.0.0 --port $PORT`. Skriv kommandoen i README.md.
    Selve Railway-oppsettet (Dockerfile eller Nixpacks, domene) er AP-022.
12. **Ferdig-definisjonen utvides:** `mypy athletics_scoring athletics_api`. Oppdater CLAUDE.md (kommandoer og
    ferdig-definisjon) og CI (installer `.[dev,api]`, kjør mypy på begge).

## Beregningsvalg

Ingen nye. API-et viser `ref` fra motorene uendret.

## Kontrolltall

| Forespørsel | Forventet | Kilde |
|---|---|---|
| `POST /api/v1/calculate` `wa_combined_events`, M, `senior`, `sprint_200m`, 23.79 | 200, `points` 712 | kontrakten |
| Samme med `version: "2001"` | `Cache-Control: public, max-age=31536000, immutable` | B-7 |
| `POST /calculate` `tyrving`, M, `"15"`, `middle_800m`, 124.56 | 991, steg `hundredths_dropped` med `ref` BV-011 | kontrakten |
| `POST /calculate` `auto`, M, alder 16, `sprint_200m`, 23.79 | 712, `selection.system = wa_combined_events`, klasse G16 | kontrakten |
| `POST /combined` femkamp menn fra kontrakten | sum 3190 | kontrakten |
| `POST /batch` med én rad per status | status per rad som i kontraktens eksempel | kontrakten |
| Forespørsel med `Origin: https://5kamp.minfriidrett.no` | `Access-Control-Allow-Origin` satt | CORS |
| Forespørsel fra annet opphav | ingen CORS-header | CORS |
| `RATE_LIMIT_PER_MINUTE=3`, fire kall | fjerde gir 429 med `Retry-After` | B-4 |
| `POST /interpret` | 501 `not_implemented` | kontrakten |
| Feil utstyr, f.eks. J17 spyd `0,6kg` i Tyrving | 422 `implement_mismatch` | Innboks-punkt 2 |

## Utenfor scope

- Deploy, domene og Railway-konfigurasjon (AP-022).
- API-nøkler, kvoter per partner og persistent rate limiting (Redis e.l.).
- `/interpret` (bare 501), `/reverse`, `/parameters/export`.
- Endringer i beregningene. Oppdager du at kontrakten og motoren er uenige om et poengtall, stopp (se under).

## Fallgruver

- Kontraktens eksempler er allerede testet mot motorene i `test_api_contract.py`. HTTP-testene skal sjekke at
  API-et gir *det samme*, ikke regne på nytt.
- `result` er ett tall i kontrakten, men `Result` i pakken har minutter og sekunder hver for seg. Oversettelsen
  skjer i API-laget.
- FastAPI legger på sin egen 422-form ved valideringsfeil. Den må skrives om til kontraktens feilformat.
- Rate limiting i minnet nullstilles ved restart og deles ikke mellom instanser. Det er greit i v1 (én instans).

## Når du skal stoppe

Sett oppgaven til `Blokkert` og avslutt hvis:
- et eksempel i kontrakten gir et annet poengtall gjennom API-et enn i motoren
- kontrakten bare kan oppfylles ved å endre en beregning i `athletics_scoring`
- installasjon av `fastapi` feiler i miljøet

Alt annet avgjør du selv, og skriver valget i sluttrapporten.

## Akseptansekriterier

- [x] Alle kontrolltallene over er HTTP-tester med `TestClient` og er grønne
- [x] Hvert endepunkt i kontrakten som ikke er `planned`, har minst én test for suksess og én for feil
- [x] Hver feiltype i `errors.py` gir kontraktens `code` og HTTP-status
- [x] `event_catalog.json` dekker alle `event_id` som motorene tilbyr (test)
- [x] `ImplementMismatchError` finnes, er underklasse av `UnknownEventError`, og alle eksisterende tester er grønne
- [x] `athletics_scoring` har fortsatt ingen runtime-avhengigheter (`pyproject.toml`)
- [x] `uvicorn athletics_api.main:app` starter lokalt, og `GET /api/v1/health` svarer 200
- [x] `pytest -q && ruff check . && mypy athletics_scoring athletics_api` er grønt, og CLAUDE.md og CI er oppdatert
- [x] Ingen endringer i `sources/` eller låste `tests/fixtures/`
- [x] Midlertidige filer og hjelpeskript fra underveis er fjernet
- [x] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Sluttrapport (fylles av Code)

- **Gjort:** Ny pakke `athletics_api/` (`main.py` med `create_app(settings, service)` og `app`, `settings.py`,
  `schemas.py` (forespørslene, `extra="forbid"`), `service.py` (oversetting til og fra motorene, `auto`,
  batch-status), `routes.py`, `errors.py` (felles feilformat) og `ratelimit.py`). Alle endepunkter i kontrakten:
  `/health`, `/systems`, `/events`, `/calculate`, `/combined`, `/batch`, og `/interpret` som svarer 501.
  I `athletics_scoring`: `ImplementMismatchError(UnknownEventError)` kastes i Tyrving (utstyr finnes ikke for
  klassen), masters (`_check_implement`, begge grener) og WMA Age Grading (`_check_implement`);
  `ScoringEngine.points_1000_result()` med standard `None`, implementert for Tyrving (h1000) og WA Combined Events;
  `catalog.py` + `data/event_catalog.json` (51 øvelser, engelsk navn og kategori). `pyproject.toml`: gruppe
  `api = [fastapi, uvicorn[standard]]`, `httpx` i `dev`, wheel tar med begge pakkene. CI, CLAUDE.md, README,
  `.claude/commands/loop.md` og oppgavemalen bruker `mypy athletics_scoring athletics_api`.
- **Bevis:**
  - `pytest -q`: 301 passed. `ruff check .`: All checks passed. `mypy athletics_scoring athletics_api`: no issues
    in 18 source files. Ingen endringer i `sources/` eller `tests/fixtures/` (`git diff --stat -- sources
    tests/fixtures` er tom).
  - Kontrolltallene er HTTP-tester i `tests/test_api_http.py`: WA 200 m 23,79 = 712 med `no-cache`; med
    `version: "2001"` `public, max-age=31536000, immutable`; Tyrving G15 800 m 124,56 = 991 med
    `hundredths_dropped`/BV-011; `auto` M 16 år = 712, `wa_combined_events`, G16; femkamp = 3190; batch med én rad
    per status lik kontraktens eksempel (uten steg); CORS for `https://5kamp.minfriidrett.no` ja, annet opphav
    nei; `rate_limit_per_minute=3` gir 429 med `Retry-After` på fjerde kall; `/interpret` 501
    `not_implemented`; J17 spyd `0,6kg` gir 422 `implement_mismatch`.
  - Alle `/calculate`-eksemplene i kontrakten gir byte-likt svar gjennom HTTP (inkludert steg og `selection`), og
    `/health`, `/systems` og `/events` stemmer med eksemplene. Svarene valideres mot skjemaene med
    `scripts/openapi_check.validate`.
  - Hver feiltype i `errors.py` er testet mot kode og HTTP-status (`test_error_type_maps_to_contract`), og en
    test feiler hvis en ny feiltype kommer til uten kode.
  - `python -m uvicorn athletics_api.main:app --port 8765` startet, og `GET /api/v1/health` svarte 200 med
    `{"status":"ok","package_version":"0.1.0","systems":{…}}`.
  - Tyrving: `points_1000_result` gir nøyaktig 1000 poeng for alle 560 kombinasjoner. WA: svakeste resultat i hele
    hundredeler/centimeter som gir minst 1000, for alle 136 (øvelse, kjønn, klasse).
- **Valg tatt underveis:**
  - **Kategori:** kontrakten (`Category`: `run`, `hurdles`, `racewalk`, `jump`, `throw`) vant over oppgavefilas
    liste (`sprint`, `middle`, …), fordi kontrakten er fasit for feltene. Hinder er `hurdles`, uten tilløp er `jump`.
  - **Norske navn:** motorene bruker ulike navn på samme `event_id` (for eksempel `racewalk_3000m` «3000 m» i
    Tyrving og «3000 m kappgang» i WMA, `middle_800m` «800 m (inne)» i WA). `/events` viser motorens eget navn
    (som kontrakten sier), og katalogens `name_no` er ett av motornavnene (test).
  - **1000-poengsresultat i WA:** tabellen har ofte ikke et resultat som gir nøyaktig 1000 (38 av 136
    kombinasjoner, for eksempel 60 m menn 6,67 = 1003). Vi gir svakeste resultat som gir minst 1000: tider rundet
    ned, lengder rundet opp. 200 m menn gir 20,86 som i kontrakten. Påvirker ikke poeng, bare referansen.
  - **`auto`:** `age_class` sammen med `auto`, eller `age` uten `auto`, gir `validation_error` (kontrakten sier
    «bare med `system: auto`»). Regeltekst for under 15 år: «Under 15 år gjelder Tyrvingtabellen, med
    klassealderen som klasse (10–14).» Ref BV-021 for alle valg.
  - **Batch:** skjemafeil i selve forespørselen gir 422; feil som bare gjelder én rad (for eksempel `auto` uten
    `age`) gir `invalid` med `validation_error`. `Cache-Control: immutable` bare når alle rader har `version`.
  - **Negativt resultat** gir `invalid_result` (`Result` avviser negative tall med `ValueError`, det fanges før).
    `result` er `strict` tall: tekst som `"23,79"` gir `validation_error`.
  - **Rate limiting:** gjelder alle endepunkter unntatt `/health` (Railways helsesjekk) og CORS-preflight.
    `RATE_LIMIT_PER_MINUTE=0` slår av. Med `TRUST_PROXY=1` brukes *siste* ledd i `X-Forwarded-For`, fordi det er
    det proxyen selv la til; første ledd kan klienten forfalske. CORS ligger ytterst, så også 429 får CORS-headere.
  - **CORS:** `*` i `CORS_ALLOWED_ORIGINS` ignoreres (ingen jokertegn). Metodene er GET og POST, header
    `Content-Type`.
  - **Klasser i `/systems`:** motorens rekkefølge, men aldre sortert stigende (Tyrving-dataene står 19→10).
  - **Kontrakten oppdatert i teksten:** feiltabellen i `openapi.yaml` og `docs/api/README.md` nevner nå
    `ImplementMismatchError` ved navn. `test_error_codes_cover_every_scoring_error` krever at hver feiltype står
    der. Ingen felt, koder eller eksempler er endret.
- **Avvik fra oppgavefila:**
  - Rutene ligger i én fil (`routes.py`) i stedet for én ruter per endepunkt. Hver rute er 3–5 linjer.
  - `scripts/loop.sh` er ikke endret (se Innboks): den kjørte denne runden, og å endre et bash-skript mens det
    kjører er utrygt.
- **Funn som bør bli egne oppgaver:** se Innboks i backloggen (verify i `loop.sh`, `httpx`-advarsel fra
  Starlette).
