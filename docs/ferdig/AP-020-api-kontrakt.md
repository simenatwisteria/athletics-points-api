# AP-020: API-kontrakt (OpenAPI), v1

**Status:** Ferdig 2026-09-27
**Opprettet:** 2026-09-27 (Cowork)
**Eier:** 🤖 Code
**Avhenger av:** AP-025 (ferdig). Leses sammen med `docs/INTEGRASJON-minfriidrett.md` og `docs/INTEGRASJON-5KAMP.md`

## Mål

En OpenAPI 3.1-spesifikasjon i `docs/api/openapi.yaml` som beskriver v1 av API-et rundt `athletics_scoring`, pluss en
kort lesbar oversikt i `docs/api/README.md`. Ingen serverkode. Simen godkjenner kontrakten i AP-036 før AP-021 starter.

## Hvorfor

Tre klienter venter på API-et: skissen/frontenden (DESIGN.md kap. 7), minfriidrett.no (batch fra server, tolkning av
resultatlister) og 5KAMP (kall fra nettleseren, én og én øvelse, fra 2026-10-04). En skriftlig kontrakt lar Cowork
skrive oppgaven i 5KAMP og lar Simen godkjenne før koden låses fast. Motorene (Tyrving, WA Combined Events, masters,
WMA Age Grading) er ferdige og verifisert, så kontrakten kan beskrive det som faktisk finnes.

## Les dette før du skriver

- `athletics_scoring/models.py`, `engine.py`, `registry.py` — dataklassene og metodene kontrakten eksponerer
- `athletics_scoring/tyrving.py`, `wa_combined_events.py`, `masters_combined_events.py`, `wma_age_grading.py` —
  `system`, `version`, `age_class`-format, `implement`, feiltyper og `sources()` per motor
- `athletics_scoring/errors.py` — feiltypene som må få HTTP-svar
- `docs/DESIGN.md` kap. 7 — kravene fra skissen
- `docs/INTEGRASJON-minfriidrett.md` kap. «Konsekvenser for API-designet» — batch, status i stedet for feil, utstyr
- `docs/INTEGRASJON-5KAMP.md` — CORS, reservevei når API-et er nede, øvelsesmapping, tabellvalg per alder
- `docs/BESLUTNINGER.md` B-4 til B-9, B-24, B-27, og `docs/BEREGNINGSVALG.md`

## Verifiserte fakta

- Fire motorer finnes: `tyrving`/`2014`, `wa_combined_events`/`2001`, `masters_combined_events`/`2023`,
  `wma_age_grading`/`2023`. `default_registry()` registrerer alle.
- `ScoreResult` har `calculation_steps` med `ref` (BV-nummer eller kildenøkkel), og motorene har `sources()`.
- WMA Age Grading returnerer `points = 0` og det aldersjusterte resultatet i `result_used` (AP-014).
- `age_class` har ulikt format per motor: `"15"` (Tyrving), `"senior"`/`"G15"` (Combined Events), `"M50"` (masters),
  `"45"` (Age Grading).

## Løsningsretning

Endepunktene i v1, alle under `/api/v1`:

1. `GET /health`
2. `GET /systems` — motorene med navn og beskrivelse på norsk og engelsk, gruppe, klassetype, klasseliste, om
   mangekamp støttes, versjoner og `sources()`.
3. `GET /events?system=&gender=&age_class=` — øvelseskatalog med `InputSpec`, utstyrsvarianter og kategori.
4. `POST /calculate` — én beregning. Input: `system`, valgfri `version` (B-5), `event_id`, `gender`, `age_class`,
   valgfri `implement`, `result` (tall i sekunder eller meter, `manual_timing`). Svar: hele `ScoreResult` med stegene.
5. `POST /combined` — mangekamp: liste med øvelser, svar med poeng per øvelse og sum.
6. `POST /batch` — 1–2000 rader. Hver rad får eget svar med `status` (`ok`, `no_result`, `ambiguous_implement`,
   `implement_mismatch`, `invalid`) og begrunnelse. Én ugyldig rad stopper aldri resten.
7. **Automatisk tabellvalg:** `system: "auto"` med `gender` og alder i hele år velger Tyrving under 15 år og
   Combined Events fra 15 år, og svaret sier hvilket system og hvilken klasse som ble brukt. Masters brukes bare når
   klienten ber om det, fordi et klubbstevne ofte bruker senior-tabellen for alle voksne.
8. **Tolkning (B-27)** beskrives som `POST /interpret` i kontrakten, men merkes `x-status: planned`. Den bygges ikke i
   AP-021. Skriv ned hvilke felt den skal ta imot og returnere, basert på tabellen i `INTEGRASJON-minfriidrett.md`.

Tverrgående krav som skal stå i kontrakten:

- **CORS:** `https://5kamp.minfriidrett.no` og frontendens domene. Listen er konfigurerbar.
- **Caching (B-7):** `Cache-Control: public, max-age=31536000, immutable` når `version` er oppgitt.
- **Feil:** ett felles feilformat med `code`, `message` (norsk) og `details`. Mapping fra hver feiltype i
  `errors.py` til HTTP-status.
- **Tall, ikke tekst:** API-et returnerer tall. Formatering etter språk gjøres i klienten (DESIGN.md kap. 7.4).
- **Eksempler:** minst ett request- og responseksempel per endepunkt, med ekte tall fra kontrolltallene
  (for eksempel menn 200 m 23,79 = 712 i `wa_combined_events`).

## Beregningsvalg

Kontrakten endrer ingen beregninger. `ref` i stegene skal forklares i README-en med lenke til
`docs/BEREGNINGSVALG.md`.

## Kontrolltall

| Eksempel i kontrakten | Forventet | Kilde |
|---|---|---|
| `wa_combined_events`, menn 200 m 23,79 | 712 | `tests/test_wa_combined_events.py` |
| `tyrving`, G15 800 m 2:04,56 | 991, med steg `ref = "BV-011"` | `tests/fixtures/tyrving_rules.json` R2-01 |
| `masters_combined_events`, M50 100 m 13,12 | 681 | Appendix B s. 1 |
| `auto`, mann 16 år, 200 m 23,79 | `wa_combined_events`, klasse G16, 712 | BV-021 |

## Utenfor scope

- Serverkode, FastAPI-oppsett og deploy (AP-021, AP-022).
- API-nøkler og kvoter per partner. Skriv bare at de kommer (B-4).
- Serietabellen (venter på NFIF).
- Endringer i `athletics_scoring/`. Oppdager du at kontrakten trenger noe motoren ikke har, skriv det i Innboks.

## Fallgruver

- `age_class` har ulikt format per motor. Kontrakten må si det tydelig per system, eller innføre et felles format
  som API-laget oversetter. Velg én løsning og begrunn den.
- Klassen for Combined Events avhenger av tilleggsøvelsene (G15/G16 800 m inne). Sjekk `age_classes()` i motoren.

## Når du skal stoppe

Sett oppgaven til `Blokkert` og avslutt hvis:
- kravene fra de tre klientene er i direkte strid og ingen av dokumentene avgjør det
- kontrakten bare kan skrives ved å endre `athletics_scoring/`

Alt annet avgjør du selv, og skriver valget i sluttrapporten og i `docs/api/README.md` under «Valg».

## Akseptansekriterier

- [x] `docs/api/openapi.yaml` er gyldig OpenAPI 3.1. Valider med et verktøy som allerede finnes, eller et lite
      skript i `scripts/` som bruker dev-avhengighetene. Ingen nye runtime-avhengigheter
- [x] Alle endepunktene over er med, `/interpret` merket som planlagt
- [x] Eksemplene bruker kontrolltallene over, og en test sjekker at eksemplene i YAML-en gir de samme poengene når
      de kjøres gjennom motorene direkte
- [x] `docs/api/README.md` forklarer endepunktene, tabellvalget, feilformatet, CORS og `ref` på én til to sider
- [x] `pytest -q && ruff check . && mypy athletics_scoring` er grønt
- [x] Ingen endringer i `sources/`, `tests/fixtures/` eller `athletics_scoring/`
- [x] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Sluttrapport (fylles av Code)

- **Gjort:** `docs/api/openapi.yaml` (OpenAPI 3.1, v1 under `/api/v1`): `/health`, `/systems`, `/events`,
  `/calculate`, `/combined`, `/batch` og `/interpret` (`x-status: planned`, 501 i v1). Felles feilformat med
  mapping fra alle feiltypene i `errors.py`, CORS-liste (`x-cors-allowed-origins`), `Cache-Control` etter B-7,
  429 ved rate limiting, `system: auto` med `selection` i svaret. `docs/api/README.md` er oversikten.
  `scripts/openapi_check.py` leser YAML-en og kontrollerer OpenAPI-strukturen (påkrevde felt, operasjoner, svar,
  alle `$ref`) og at hvert eksempel stemmer med skjemaet sitt. `tests/test_api_contract.py` (18 tester) kjører
  alle eksemplene gjennom motorene.
- **Bevis:**
  - `python scripts/openapi_check.py` → `docs/api/openapi.yaml: gyldig`. Negativ test: et eksempel uten `points`,
    med et ukjent felt og en `$ref` som ikke finnes, gir tre feil.
  - Kontrolltallene gir de samme tallene i motorene: `wa_combined_events` menn 200 m 23,79 = 712;
    `tyrving` G15 800 m 124,56 = 991 med steg `hundredths_dropped` `ref = "BV-011"`;
    `masters_combined_events` M50 100 m 13,12 = 681; `auto` mann 16 år 200 m 23,79 → `wa_combined_events` G16 = 712.
    `/calculate`-eksemplene sammenlignes felt for felt med motoren, også alle stegene.
  - `/combined` femkamp menn (6,12 / 48,30 / 23,79 / 36,40 / 4:35,4) = 613 + 563 + 712 + 592 + 710 = 3190.
    `/batch` har én rad per status, og status og melding er de motoren gir. `/events`: `points_1000_result`
    (124,0 og 20,86) gir 1000 poeng. `/systems` og `/health` stemmer med `default_registry()`.
  - `pytest -q`: 220 passed. `ruff check .` og `mypy athletics_scoring`: grønt.
  - `git diff` mot forrige commit: ingen endringer i `sources/`, `tests/fixtures/` eller `athletics_scoring/`.
- **Valg tatt underveis:** (står også under «Valg» i `docs/api/README.md`)
  1. `age_class` i motorens eget format. `class_type` og `classes` i `/systems` sier hvordan det leses. Klienter
     som bare kjenner alderen, bruker `auto`.
  2. `result` er ett tall: sekunder totalt eller meter, valgt etter `input.measure`.
  3. `auto`: 10–14 → Tyrving; 15–17 → mangekamp G/J15–17; 18+ → senior. Alderen er klassealder. Masters bare når
     klienten ber om det.
  4. Feil utstyr gir `implement_mismatch`. API-laget skiller det fra `unknown_event` ved å prøve uten `implement`.
  5. Alle beregningsfeil er 422, også ukjent system og versjon.
  6. `/systems` viser tabeller som ikke er klare (`series_table`, `ready: false`).
  7. Vind og inne/ute er bare med i `/interpret`.
- **Avvik fra oppgavefila:** Det finnes ingen YAML-pakke i dev-avhengighetene. Derfor leser `openapi_check.py` et
  avgrenset utsnitt av YAML og avviser alt utenfor det, i stedet for å legge til PyYAML eller en OpenAPI-validator.
  Kontrollen er ikke en full OpenAPI 3.1-validator. Den dekker struktur, `$ref` og eksempler mot skjema. I
  `/combined`, `/batch` og `/interpret` står stegene som tomme lister i eksemplene, og det er sagt i `summary`.
  Poeng, felt og sum kontrolleres likevel.
- **Funn som bør bli egne oppgaver:** skrevet under «Innboks» i backloggen: (1) motoren har ikke engelske
  øvelsesnavn, kategori eller 1000-poengsresultat som offentlig metode, og `/systems` trenger navn og beskrivelse
  på to språk. Det må komme fra API-laget eller pakken i AP-021. (2) Feil utstyr gir `UnknownEventError`. En egen
  underklasse, for eksempel `ImplementMismatchError`, ville gjort det enklere for API-et. (3) `auto` bruker
  klassealder, og det bør bekreftes før 5K-012.
