# AP-021: API-implementasjon (FastAPI) etter kontrakten v1

**Status:** Klar
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

- [ ] Alle kontrolltallene over er HTTP-tester med `TestClient` og er grønne
- [ ] Hvert endepunkt i kontrakten som ikke er `planned`, har minst én test for suksess og én for feil
- [ ] Hver feiltype i `errors.py` gir kontraktens `code` og HTTP-status
- [ ] `event_catalog.json` dekker alle `event_id` som motorene tilbyr (test)
- [ ] `ImplementMismatchError` finnes, er underklasse av `UnknownEventError`, og alle eksisterende tester er grønne
- [ ] `athletics_scoring` har fortsatt ingen runtime-avhengigheter (`pyproject.toml`)
- [ ] `uvicorn athletics_api.main:app` starter lokalt, og `GET /api/v1/health` svarer 200
- [ ] `pytest -q && ruff check . && mypy athletics_scoring athletics_api` er grønt, og CLAUDE.md og CI er oppdatert
- [ ] Ingen endringer i `sources/` eller låste `tests/fixtures/`
- [ ] Midlertidige filer og hjelpeskript fra underveis er fjernet
- [ ] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Sluttrapport (fylles av Code)

- **Gjort:**
- **Bevis:**
- **Valg tatt underveis:**
- **Avvik fra oppgavefila:**
- **Funn som bør bli egne oppgaver:**
