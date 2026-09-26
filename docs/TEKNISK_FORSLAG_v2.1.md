# Teknisk løsningsforslag v2.1: Athletics Points Calculator API

**Dato:** 17. april 2026
**Versjon:** 2.1 — Utvidet scope etter undersøkelse av NFIFs poengtabeller
**Erstatter:** `TEKNISK_FORSLAG_v2.md` (v2.0 fra 6. april 2026)
**Besluttet grunnlag:** `BESLUTNINGER.md`
**Stack:** Python (scoring-pakke) → FastAPI → React | Deploy: Railway + Vercel

---

## 0. Hva er nytt i v2.1

v2.1 er en tilleggsversjon, ikke en omskriving. All arkitektur, alle formler og all kode fra v2.0 står ved lag. De viktigste endringene er:

1. **Scope utvidet** med tre nye norske poengsystemer som ble identifisert under undersøkelsen av NFIFs offisielle poengtabellsamling (kap. 1.3 og 3.4 nedenfor): Serietabellen/Seriepoeng (Lagserien), Masters Mangekamptabell og Masters Serietabell. World Athletics Scoring og WMA Age Grading står uendret.
2. **Revidert faseinndeling** der Serietabellen prioriteres som første post-MVP-leveranse foran World Athletics Scoring, fordi den er mest brukt av klubbene og ikke finnes i andre åpne kalkulatorer (B-18).
3. **Justeringer i API-kontrakt** fra BESLUTNINGER.md er innarbeidet: eksplisitt `version`-parameter (B-5), `calculation_steps`-array i respons (B-6), deterministisk caching via `Cache-Control` (B-7), `/api/v1/reverse` dokumentert som fase 2 (B-8).
4. **Utvidet event-katalog** med senior-implement og klubbserie-varianter.
5. **Registry-laget** får eksplisitt støtte for kombinasjonen `(scoring_system, version, gender, age_class, event_id)` — tidligere var bare `(scoring_system, event_id, gender, age)`.

Alt annet — scoring-pakke-først-prinsippet, formler for Tyrving, teststrategi, deploy — er uendret fra v2.0.

---

## 1. Prosjektoversikt

### 1.1 Visjon

En åpen, transparent og programmatisk tilgjengelig beregningsmotor for friidrettspoeng relevant for norske utøvere. All logikk, alle parametre og alle formler skal være tilgjengelige og verifiserbare. Dette er en **utility-tjeneste** — ikke en brukerplattform.

### 1.2 Hva dette IKKE er

Dette er ikke minfriidrett.no. Det er en separat tjeneste med en annen type bruker (utviklere, klubber, forbund), en annen forretningsmodell (API-tilgang), og en helt annen livssyklus. Separasjonen er bevisst — tjenesten kan selges, flyttes eller skaleres uavhengig.

### 1.3 Faktisk bruk i norsk friidrett — revidert faseinndeling

Etter undersøkelsen mot NFIFs side *Poengtabeller* er scopet utvidet. Nedenfor er den komplette listen over poengsystemer som brukes i Norge i dag, med kilde og fase:

| Fase | System | Bruksområde | Datakilde | Status |
|------|--------|-------------|-----------|--------|
| **MVP** | Tyrvingtabellen | Ungdom 10–19 (individuelt og mangekamp u/15) | 2014-regneark (NFIF) | Parametre tilgjengelig |
| Fase 2 | Serietabellen / Seriepoeng | Lagserien (klubbserie, senior) | NFIFs serieregler + Excel | Tilgjengelig hos forbundet |
| Fase 3 | World Athletics Scoring | Internasjonalt + seniormangekamp (femkamp/sjukamp/tikamp på UM/NM/Nordisk) | WA 2025 PDF-er | Godt dokumentert |
| Fase 3 | Combined Events (WA) | Mangekampsummering, senior | WA Combined Events tables | Godt dokumentert |
| Fase 4 | Masters Mangekamptabell | Masters (veteran) mangekamp | NFIF Excel-filer (menn/kvinner, basert på WMA 2023) | Tilgjengelig hos forbundet |
| Fase 4 | Masters Serietabell | Masters klubbserie | NFIFs serieregler for masters | Tilgjengelig hos forbundet |
| Fase 4 | WMA Age Grading | Masters individuelt (aldersjustering) | WMA 2023 Age Factors | Godt dokumentert |

**Viktig avklaring:** Tyrvingtabellen brukes **ikke** for mangekamp på seniornivå (femkamp/sjukamp/tikamp). Der brukes World Athletics Scoring Tables. Tyrving brukes for ungdomsindividuelle øvelser 10–19 år, samt mangekamp for ungdom under 15. Serietabellen er et helt separat nasjonalt system for klubbserien og er ikke avledet av Tyrving eller WA.

---

## 2. Arkitekturprinsipp: Scoring-pakke først

**Uendret fra v2.0.** Scoring-enginen bygges som en selvstendig Python-pakke med full testdekning før FastAPI og frontend. Dette prinsippet skalerer rett gjennom det utvidede scopet — hvert nytt poengsystem blir en ny `ScoringEngine`-implementasjon i pakken og arver tester, registry og kontrakt.

### Byggerekkefølge (uendret)

```
1. athletics_scoring/        ← Python-pakke med all logikk og tester
2. FastAPI wrapper            ← Tynt API-lag rundt pakken
3. React frontend            ← Kalkulator-UI som kaller API-et
```

---

## 3. Formelanalyse

### 3.1 Tyrvingtabellen (MVP)

Uendret fra v2.0 kap. 3. Formlene (enkel kvotient for løp/hopp, tre-intervall for kast/stav), avrundingsregler og manuell-tidtaking-påslag gjelder som før.

### 3.2 World Athletics Scoring (fase 3)

Uendret fra v2.0. Formelen `poeng = A × |resultat – B|^C` (løpsøvelser har omvendt fortegn), med tabellbaserte A/B/C-konstanter per øvelse og kjønn. Versjon 2025 er gjeldende. Oppdateres hvert 3.–4. år — versjonert i kontrakten (B-5).

### 3.3 WMA Age Grading (fase 4)

Uendret fra v2.0. Formel: `age_graded_result = resultat × aldersfaktor(alder, kjønn, øvelse)` og `age_graded_performance = age_graded_result / åpen_rekord`. Aldersfaktorer fra WMA 2023 er datakilden, og de samme faktorene ligger til grunn for den norske Masters Mangekamptabellen.

### 3.4 Nye systemer i v2.1

#### 3.4.1 Serietabellen / Seriepoeng (fase 2)

Norsk nasjonalt system for klubbserien (Lagserien). Bruker senior-implement: kule 7,26 kg (menn) / 4 kg (kvinner), diskos 2,0 kg / 1,0 kg, slegge 7,26 kg / 4 kg, spyd 800 g / 600 g, hekkehøyder etter seniorstandard. Verdikalibreringen er norsk — tabellen er **ikke** en underliggende World Athletics-tabell.

**Formel (skal verifiseres mot kilde i fase 2, antatt tre-intervall analogt med Tyrving):**
```
R = resultat, H = H1000_serietabell (senior-referanse)
Løp:   poeng = 1000 + (H - R) × kvotient
Hopp:  poeng = 1000 + (R - H) × kvotient
Kast:  tre-intervall (F1/F2/F3), samme logikk som Tyrving
```

Parametersett lastes fra egen JSON-fil: `serietabell_parameters.json`. Implementert som `SerietabellCalculator` som arver `ScoringEngine`.

#### 3.4.2 Masters Mangekamptabell (fase 4)

Egne Excel-filer fra NFIF for menn og kvinner, basert på WMA-aldersfaktorer fra 01.01.2023. Er i praksis en mangekamptabell der WA Scoring-verdien multipliseres med aldersfaktor før summering. Kan reimplementeres analytisk som:

```
poeng_master = wma_age_grading(resultat, alder, kjønn, øvelse) × referanse_1000
```

Alternativt leses som tabell-lookup (kopi av Excel). **Beslutning utsatt til fase 4** — begge varianter lar seg implementere uten arkitekturendring.

#### 3.4.3 Masters Serietabell (fase 4)

Egen NFIF-tabell for klubbserie på masters-nivå. Kombinerer Serietabellens struktur med aldersfaktorer. Implementeres som egen `ScoringEngine` med egen parameter-JSON. Samme patent som 3.4.2: formelen kan være analytisk (serietabell + aldersfaktor) eller tabell-lookup.

---

## 4. Event-ID-system

### 4.1 Designprinsipper (oppdatert)

Event-ID-en identifiserer en øvelse uavhengig av poengsystem. I v2.1 utvides lookup-nøkkelen med en eksplisitt `version`- og `age_class`-dimensjon:

```
(scoring_system, version, event_id, gender, age_or_age_class) → parametersett
```

`age_class` er relevant for systemer der alder ikke er en enkelt verdi (f.eks. Masters: "M40", "M45", ..., "M90") eller der kategorien er "senior" (Serietabellen, WA Scoring for seniormangekamp). For Tyrving er `age_class` lik alder som heltall (10–19).

### 4.2 Utvidet ID-katalog

Base-events fra v2.0 (43 stk) beholdes uendret. I v2.1 tilkommer følgende varianter som trengs for de nye systemene:

**Senior-implement (Serietabellen, WA seniormangekamp):**
- Kast bruker samme event-ID som før (`shot_put`, `discus`, `hammer`, `javelin`), men parametersettet peker på senior-implement (7,26 kg / 4 kg osv.) via `implement`-feltet i parameter-JSON.
- Hekk bruker samme event-ID (`hurdles_100m`, `hurdles_110m`, `hurdles_400m`), parametersettet angir senior-hekkehøyde.

**Masters-klasser:**
- Ingen nye event-ID-er. Aldersklassen (`M35`, `M40`, …, `M90`, `W35`, …) representeres i parameterlookupen, ikke i event-ID-en. Dette er samme prinsipp som for Tyrving-aldre.

**Totalt event-ID-er: fortsatt 43 base-events.** Antall unike parameterkombinasjoner vokser betydelig når alle systemene er inne:

- Tyrving 2014: ~530 (uendret)
- Serietabellen: ~80 (senior, én aldersklasse, begge kjønn, 40 øvelser)
- WA Scoring 2025: ~90 (senior, begge kjønn)
- WA Combined Events: ~20 (femkamp, sjukamp, tikamp)
- WMA Age Grading 2023: ~800 (alle aldersklasser 35–90, begge kjønn)
- Masters Mangekamptabell: ~400
- Masters Serietabell: ~80

Estimat totalvolum i fullt utbygd løsning: ~2000 parameterkombinasjoner, fremdeles trivielt for JSON-fillager.

---

## 5. Parameterlagring

### 5.1 Hvorfor JSON (uendret)

Tyrving 2014 er statisk. WA oppdateres hvert 3.–4. år. Serietabellen oppdateres sjelden. JSON i versjonskontroll gir full transparens. Ingen runtime-avhengighet til database for kjernelogikken.

### 5.2 Format per fil

Hvert poengsystem får én JSON-fil med versjonering i `meta.version`:

```
athletics_scoring/data/
├── event_catalog.json              # Felles event-katalog
├── tyrving_parameters_2014.json    # Tyrving, NFIF 2014
├── serietabell_parameters_2024.json
├── wa_scoring_parameters_2025.json
├── wa_combined_events_2025.json
├── wma_age_factors_2023.json
├── masters_mangekamp_parameters_2024.json
└── masters_serietabell_parameters_2024.json
```

Eksempel (Serietabellen — format analogt med Tyrving):

```json
{
  "meta": {
    "scoring_system": "serietabell",
    "version": "2024",
    "source": "NFIF — Regler og poengtabell for Lagserien",
    "last_extracted": "2026-05-XX"
  },
  "events": {
    "sprint_100m": {
      "name": "100 m",
      "category": "track",
      "formula_type": "simple_quotient",
      "timing_mode": "hundredths",
      "params": {
        "M_senior": { "h1000": 10.45, "quotient": 1.8 },
        "F_senior": { "h1000": 11.60, "quotient": 1.7 }
      }
    },
    "shot_put": {
      "name": "Kule",
      "category": "field_throw",
      "formula_type": "three_interval",
      "params": {
        "M_senior": { "h1000": 18.5, "f1": 0.3, "f2": 0.6, "f3": 1.2, "implement": "7.26kg" },
        "F_senior": { "h1000": 17.0, "f1": 0.3, "f2": 0.6, "f3": 1.2, "implement": "4kg" }
      }
    }
  }
}
```

(Faktiske tall fylles inn ved ekstraksjon i fase 2.)

### 5.3 Forhold mellom versjoner

Én JSON-fil per `(system, version)`. Ingen overskrivning. Eksempel når NFIF publiserer ny Tyrvingtabell:

```
tyrving_parameters_2014.json   ← beholdes
tyrving_parameters_2029.json   ← legges til
```

API-et returnerer nyeste versjon hvis ikke spesifisert (B-5), men klienter kan pinne til 2014 for bakoverkompatibilitet.

---

## 6. Prosjektstruktur

```
athletics-points-api/
├── athletics_scoring/              # ← Selvstendig Python-pakke
│   ├── __init__.py
│   ├── models.py                   # Dataklasser (Event, Result, ScoreResult)
│   ├── engine.py                   # Abstrakt ScoringEngine-interface
│   ├── tyrving.py                  # TyrvingCalculator           (MVP)
│   ├── serietabell.py              # SerietabellCalculator       (fase 2)
│   ├── world_athletics.py          # WorldAthleticsCalculator    (fase 3)
│   ├── combined_events.py          # CombinedEventsCalculator    (fase 3)
│   ├── wma_age_grading.py          # WmaAgeGradingCalculator     (fase 4)
│   ├── masters_mangekamp.py        # MastersMangekampCalculator  (fase 4)
│   ├── masters_serietabell.py      # MastersSerietabellCalculator (fase 4)
│   ├── registry.py                 # Lookup: (system,version,event,gender,age_class) → engine
│   └── data/
│       ├── event_catalog.json
│       ├── tyrving_parameters_2014.json
│       ├── serietabell_parameters_2024.json      (fase 2)
│       ├── wa_scoring_parameters_2025.json       (fase 3)
│       ├── wa_combined_events_2025.json          (fase 3)
│       ├── wma_age_factors_2023.json             (fase 4)
│       ├── masters_mangekamp_parameters_2024.json (fase 4)
│       └── masters_serietabell_parameters_2024.json (fase 4)
│
├── api/                            # ← FastAPI wrapper
│   ├── main.py
│   ├── routers/
│   │   ├── calculate.py            # /calculate, /batch, /reverse (fase 2+)
│   │   ├── parameters.py           # /events, /parameters, /formulas, /export
│   │   └── health.py
│   ├── middleware.py               # Rate limiting (IP-basert)
│   └── cache.py                    # Deterministisk Cache-Control (B-7)
│
├── frontend/                       # ← React app
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Calculator.tsx
│   │   │   ├── BatchCalculator.tsx
│   │   │   ├── SystemSelector.tsx  # Velg Tyrving / Serietabell / WA / WMA / Masters
│   │   │   ├── ReverseCalculator.tsx  (fase 2)
│   │   │   └── ParameterBrowser.tsx
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── types/
│   │       └── index.ts
│   ├── package.json
│   └── vite.config.ts
│
├── tests/
│   ├── test_tyrving_calculator.py
│   ├── test_tyrving_params.py
│   ├── test_serietabell_calculator.py       (fase 2)
│   ├── test_serietabell_params.py           (fase 2)
│   ├── test_wa_scoring_calculator.py        (fase 3)
│   ├── test_combined_events.py              (fase 3)
│   ├── test_wma_age_grading.py              (fase 4)
│   ├── test_masters_mangekamp.py            (fase 4)
│   ├── test_masters_serietabell.py          (fase 4)
│   ├── test_verification.py
│   ├── test_api.py
│   └── fixtures/
│       └── *_test_cases.json
│
├── scripts/
│   ├── extract_tyrving_params.py
│   ├── extract_serietabell_params.py         (fase 2)
│   ├── extract_wa_scoring_params.py          (fase 3)
│   ├── extract_wma_factors.py                (fase 4)
│   ├── extract_masters_mangekamp_params.py   (fase 4)
│   └── generate_test_cases.py
│
├── docs/
│   ├── formulas.md                 # Formelreferanse (lesbar)
│   └── scoring_systems.md          # Oversikt over alle systemer og hva de brukes til
│
├── pyproject.toml
├── Dockerfile
└── README.md
```

---

## 7. Scoring-pakken: `athletics_scoring`

### 7.1 Kjerneklasser (utvidet fra v2.0)

```python
# models.py — utvidet med version og age_class
@dataclass
class Result:
    time_seconds: float | None = None
    time_minutes: int | None = None
    distance_meters: float | None = None
    manual_timing: bool = False


@dataclass
class CalculationStep:
    """Ett steg i beregningen, for strukturert respons (B-6)."""

    label: str  # "hundredths_of_seconds"
    value: float  # 1130
    formula: str  # "time_seconds × 100"


@dataclass
class ScoreResult:
    points: int
    scoring_system: str  # "tyrving" | "serietabell" | ...
    version: str  # "2014" | "2024" | ...
    event_id: str
    event_name: str
    gender: str
    age_class: str  # "19" (Tyrving) | "senior" | "M40" ...
    result_used: float
    parameters: dict
    formula_type: str
    calculation_detail: str  # lesbar streng
    calculation_steps: list[CalculationStep]  # strukturert (B-6)


# engine.py
class ScoringEngine(ABC):
    version: str  # settes av underklasse

    @abstractmethod
    def calculate(
        self, event_id: str, gender: str, age_class: str, result: Result
    ) -> ScoreResult: ...

    @abstractmethod
    def list_events(self, gender: str | None, age_class: str | None) -> list[EventInfo]: ...

    @abstractmethod
    def get_parameters(self, event_id: str, gender: str, age_class: str) -> dict: ...

    # Valgfri: kan implementeres av engines som støtter reverse (B-8)
    def reverse(
        self, event_id: str, gender: str, age_class: str, target_points: int
    ) -> Result | None:
        raise NotImplementedError


# registry.py
class Registry:
    """Mapper (scoring_system, version) → ScoringEngine."""

    def get(self, scoring_system: str, version: str | None = None) -> ScoringEngine:
        # Hvis version=None, returner nyeste registrerte versjon for systemet
        ...
```

### 7.2 TyrvingCalculator (MVP, uendret)

Som i v2.0 kap. 7.2. Eneste endring er at konstruktøren setter `self.version = "2014"` og at `calculate()` fyller inn `scoring_system`, `version`, `age_class` og `calculation_steps` i returverdien.

### 7.3 SerietabellCalculator (fase 2)

Samme struktur som TyrvingCalculator men med:
- `self.version = "2024"` (eller faktisk versjonsnummer)
- `age_class`-verdi alltid `"senior"` i MVP (lagserien har kun senior)
- Laster `serietabell_parameters_2024.json`
- Gjenbruker `_calc_track`, `_calc_jump`, `_calc_throw` — formellogikken er den samme tre-intervall-logikken som Tyrving

**Kritisk verifisering i fase 2:** bekreft at Serietabellens formel faktisk er tre-intervall. Dersom den bruker en annen struktur (f.eks. polynom eller WA-lignende A·|r−b|^c), legges en ny `formula_type` til og testene dekker dette før lansering.

### 7.4 Øvrige kalkulatorer

`WorldAthleticsCalculator`, `CombinedEventsCalculator`, `WmaAgeGradingCalculator`, `MastersMangekampCalculator` og `MastersSerietabellCalculator` følger samme mønster: last JSON, implementer `calculate`, returner `ScoreResult`. Formler er allerede dokumentert i v2.0 (WA, WMA, CE) og i kap. 3.4 her (Masters-tabeller, Serietabellen).

---

## 8. API-design

### 8.1 Autentisering

**Uendret fra v2.0.** MVP: åpent API med IP-basert rate limiting. API-nøkler legges til når konkret integrasjonspartner ønsker høyere rate limit.

### 8.2 Endepunkter (oppdatert)

#### `POST /api/v1/calculate`

**Request (oppdatert med B-5 — eksplisitt `version`):**
```json
{
  "scoring_system": "tyrving",
  "version": "2014",
  "event_id": "sprint_100m",
  "gender": "M",
  "age_class": "19",
  "result": { "time_seconds": 11.30 }
}
```

Hvis `version` utelates, brukes nyeste registrerte versjon for systemet.
Hvis `age_class` er et tall eller en numerisk streng, tolkes det som alder i år (Tyrving-stil). Ellers tolkes det som kategori ("senior", "M40", …).

**Response (oppdatert med B-6 — `calculation_steps`-array):**
```json
{
  "points": 991,
  "scoring_system": "tyrving",
  "version": "2014",
  "event_id": "sprint_100m",
  "event_name": "100 m",
  "gender": "M",
  "age_class": "19",
  "result_used": 11.30,
  "parameters_used": {
    "h1000": 11.25,
    "quotient": 1.7,
    "formula_type": "simple_quotient"
  },
  "calculation_detail": "N=1125, M=1130, diff=-5, poeng=1000+(-5×1.7)=991.5→991",
  "calculation_steps": [
    { "label": "hundredths_of_seconds", "value": 1130, "formula": "time_seconds × 100" },
    { "label": "h1000_hundredths", "value": 1125, "formula": "h1000 × 100" },
    { "label": "difference", "value": -5, "formula": "h1000_hundredths - hundredths_of_seconds" },
    { "label": "points_raw", "value": 991.5, "formula": "1000 + (difference × quotient)" },
    { "label": "points_final", "value": 991, "formula": "floor(points_raw), min 0" }
  ]
}
```

**Response headers (B-7):**
```
Cache-Control: public, max-age=31536000, immutable
```
Settes kun når `version` er eksplisitt angitt i requesten. Uten eksplisitt versjon returneres `Cache-Control: public, max-age=3600` — korte cacher, fordi "nyeste versjon" kan endre seg.

#### `POST /api/v1/batch`

Som v2.0, men med `scoring_system` og `version` i topnivå og per-calculation (per-calculation overrider topnivå). Respons inkluderer `calculation_steps` for hver beregning.

#### `POST /api/v1/reverse` (fase 2, B-8)

**Request:**
```json
{
  "scoring_system": "tyrving",
  "version": "2014",
  "event_id": "sprint_100m",
  "gender": "M",
  "age_class": "19",
  "target_points": 1000
}
```

**Response:**
```json
{
  "required_result": { "time_seconds": 11.25 },
  "points_at_required_result": 1000,
  "explanation": "For 1000 poeng på 100m (Gutter 19, Tyrving 2014) trengs 11.25 sekunder."
}
```

Implementeres ved å invertere formelen analytisk (enkel kvotient er triviell; tre-intervall har to mulige løsninger som begge returneres).

#### `GET /api/v1/events`

Query params: `?scoring_system=tyrving&version=2014&gender=M&age_class=15`.
`age_class` er valgfritt. Returnerer alle øvelser i systemet som er definert for angitt filter.

#### `GET /api/v1/events/{event_id}/parameters`

Query params: `?scoring_system=tyrving&version=2014&gender=M&age_class=19`.
Returnerer kun parametersettet for gitt kombinasjon.

#### `GET /api/v1/systems`

**Ny i v2.1.** Lister alle registrerte scoring-systemer med versjoner og en kort beskrivelse:

```json
{
  "systems": [
    { "id": "tyrving", "name": "Tyrvingtabellen", "versions": ["2014"], "use_case": "Ungdom 10–19 individuelt, mangekamp u/15", "default_version": "2014" },
    { "id": "serietabell", "name": "Serietabellen (Lagserien)", "versions": ["2024"], "use_case": "Klubbserie senior", "default_version": "2024" }
  ]
}
```

Dette gjør det mulig for frontend og tredjeparter å bygge riktig UI uten hardkoding.

#### `GET /api/v1/formulas` og `/api/v1/parameters/export`

Uendret fra v2.0. Begge støtter `?scoring_system=...&version=...`.

#### `GET /api/v1/health`

Uendret.

### 8.3 Feilhåndtering (utvidet)

```json
{
  "error": "VERSION_NOT_AVAILABLE",
  "message": "Tyrvingtabellen versjon 2029 er ikke registrert",
  "available_versions": ["2014"],
  "suggestion": "Bruk version=2014, eller utelat version for nyeste (= 2014)"
}
```

Ny feilkode i v2.1 sammen med `EVENT_NOT_AVAILABLE`, `AGE_CLASS_NOT_AVAILABLE`, `GENDER_NOT_AVAILABLE`, `SYSTEM_NOT_AVAILABLE`.

---

## 9. Frontend

### 9.1 Sider (utvidet)

1. **Kalkulator** — Systemvelger øverst (Tyrving / Serietabell / WA / Masters …). Dropdowns for versjon, kjønn, aldersklasse, øvelse. Live-beregning. Viser `calculation_steps` i en utvidbar panel.

2. **Batch** — Som v2.0. Systemvelger påvirker hele batchen, med mulighet for å overstyre per-rad.

3. **Reverse-kalkulator** (fase 2, B-8) — Oppgi poeng, få ut resultat. Nyttig for trenere.

4. **Parametervisning** — Browse alle parametre. Filtrer på system, versjon, kjønn, aldersklasse. Lenke til kildemateriale.

5. **API-docs** — Autogenerert OpenAPI/Swagger fra FastAPI. Eksempler med curl, Python, JavaScript.

6. **Om systemene** — Ny i v2.1. Kort forklaring av hvilke systemer som brukes til hva, basert på NFIFs offisielle veiledning. Reduserer tvil for brukere som ikke vet hvilket system de skal velge.

### 9.2 Teknologi

Uendret fra v2.0: React + TypeScript, Vite, Tailwind CSS, Tanstack Query, React Router. Norsk UI (B-12).

---

## 10. Teststrategi

### 10.1 Lagvis testing (uendret struktur, utvidet scope)

```
Lag 1: Enhetstest av formler         ← athletics_scoring-pakken, per system
Lag 2: Parameterverifisering         ← JSON mot Excel-kilden, per system
Lag 3: Ende-til-ende verifisering    ← API-respons mot kjente verdier
Lag 4: Kryssverifisering             ← Mot eksterne kalkulatorer der tilgjengelig
```

### 10.2 Per-system testkrav

| System | Lag 1 (håndregnet) | Lag 2 (Excel-match) | Lag 3 (autogen) | Lag 4 (ekstern) |
|--------|--------------------|---------------------|-----------------|-----------------|
| Tyrving 2014 | ✓ | ✓ (~530) | ✓ (~1600) | manuell mot regneark |
| Serietabell 2024 | ✓ | ✓ (~80) | ✓ (~250) | mot minfriidrettsstatistikk.info hvis tilgjengelig |
| WA Scoring 2025 | ✓ | ✓ (~90) | ✓ (~300) | worldathleticsscores.com |
| WA Combined Events | ✓ | ✓ | ✓ | multieventcalculator.com |
| WMA 2023 | ✓ | ✓ (~800) | ✓ | howardgrubb.co.uk/athletics/wmatnf23.html |
| Masters Mangekamp | ✓ | ✓ | ✓ | manuell mot NFIFs Excel |
| Masters Serietabell | ✓ | ✓ | ✓ | manuell mot NFIFs Excel |

Ingen systemer går i produksjon før lag 1–3 er grønne. Lag 4 gjøres i sluttfasen per system.

### 10.3 Konkrete testeksempler

Se v2.0 kap. 10.2 for Tyrving (uendret). Serietabell, WA, WMA og Masters får tilsvarende håndregnede eksempler i respektive testfiler når systemene implementeres.

---

## 11. Deploy

### 11.1 Plattform (uendret)

- **Backend:** Railway, Docker, auto-deploy fra GitHub `main`
- **Frontend:** Vercel, auto-deploy fra GitHub `main`
- **Ingen database** i MVP eller fase 2. Legges til først når API-nøkkelhåndtering eller analytisk logging krever det.
- **Domene:** Bestemmes før soft launch (B-14)

### 11.2 CI/CD (uendret)

GitHub Actions:
- Ved PR: kjør alle tester (pytest) for alle implementerte systemer
- Ved push til `main`: auto-deploy backend (Railway) + frontend (Vercel)

### 11.3 Integrasjon med minfriidrett.no

Uendret fra v2.0. Ren HTTP-integrasjon. minfriidrett.no kaller API-et når en feature trenger poengberegning — ingen før det (B-15).

---

## 12. Revidert roadmap v2.1

Totalestimat for utvidet scope: **~10 uker** fordelt på 5 faser. MVP (fase 1) er fortsatt **4–5 uker** som i v2.0.

### Fase 1: MVP — Tyrving-scoring-pakke, API og frontend (uke 1–5)

Uke 1–2: `athletics_scoring`-pakken med TyrvingCalculator, parameterekstraksjon, enhetstester, ~1600 autogenererte testcaser.
Uke 3: FastAPI-wrapper med alle endepunkter (inkl. `/systems`), rate limiting, versjonering (B-5), strukturerte steg (B-6), deterministisk caching (B-7), OpenAPI-docs.
Uke 3–4: React-frontend med kalkulator, batch, parameterutforsker. Responsivt design.
Uke 4–5: Railway + Vercel deploy, CI/CD, domenenavn, README, soft launch.

**Utgangspunkt etter fase 1:** Tyrving fungerer 100 %. Arkitekturen er klar for nye systemer uten refaktorering.

### Fase 2: Serietabellen / Seriepoeng (uke 6–7)

Uke 6: Ekstraher Serietabellens parametre fra NFIF-kilden til JSON. Verifiser formeltypen (sannsynligvis tre-intervall, må bekreftes). Implementer `SerietabellCalculator` i samme mønster som Tyrving. Enhetstester.
Uke 7: Autogenererte testcaser, kryssverifisering mot `minfriidrettsstatistikk.info` hvis mulig, registrer system i `/systems`, eksponer i frontend-systemvelger.

**Samtidig:** Implementer `/api/v1/reverse` (B-8) og bygg reverse-kalkulator i frontend.

### Fase 3: World Athletics Scoring + Combined Events (uke 8–9)

Uke 8: Ekstraher WA 2025-parametre (A, B, C per øvelse), implementer `WorldAthleticsCalculator`, enhetstester og kryssverifisering mot worldathleticsscores.com.
Uke 9: Implementer `CombinedEventsCalculator` for femkamp/sjukamp/tikamp, verifiser mot multieventcalculator.com.

### Fase 4: Masters (uke 10+)

Uke 10: Ekstraher WMA 2023-aldersfaktorer, implementer `WmaAgeGradingCalculator`, kryssverifiser mot howardgrubb.co.uk.
Uke 11: Masters Mangekamptabell fra NFIF Excel — enten analytisk (via WMA) eller tabell-lookup, basert på hvilken som gir eksakt match mot kilden.
Uke 12: Masters Serietabell fra NFIF Excel.

### Fase 5: Infrastrukturpåbygging (ved behov)

API-nøkkelhåndtering når første integrasjonspartner ønsker høyere rate limit. Historisk logging når et analytisk behov defineres. Eventuell migrering til database hvis nøkkelbestanden vokser forbi det som er praktisk i JSON/env-variables.

---

## 13. Besluttet utenfor scope (uendret)

Fra v2.0 og bekreftet i BESLUTNINGER.md:
- Database (SQLite/PostgreSQL) i MVP
- API-nøkkelhåndtering og signup-flyt i MVP
- Engelsk frontend i MVP
- JS/TS-speilpakke av scoring-logikken
- Historisk logging av beregninger
- Sammenslåing med minfriidrett.no

Hver av disse kan legges til senere uten å rive opp kjernen. Hele poenget med å holde scoring-pakken som et selvstendig lag er akkurat dette.

---

## 14. Endringer fra v2.0 til v2.1 (oppsummert)

| Område | v2.0 | v2.1 |
|--------|------|------|
| Scope | Tyrving → WA → WMA | Tyrving → Serietabell → WA → Masters-tabeller → WMA |
| Antall systemer | 4 (Tyrving, WA, CE, WMA) | 7 (+ Serietabell, Masters Mangekamp, Masters Serietabell) |
| Antall parameterkombinasjoner | ~1500 | ~2000 |
| API: eksplisitt `version` | implisitt | eksplisitt parameter (B-5) |
| API: respons-steg | streng | streng + strukturert array (B-6) |
| API: caching | ikke spesifisert | deterministisk Cache-Control (B-7) |
| API: `/reverse` | ikke nevnt | dokumentert som fase 2 (B-8) |
| API: `/systems` | ingen | nytt endepunkt |
| Lookup-nøkkel | `(system, event, gender, age)` | `(system, version, event, gender, age_class)` |
| Registry | implisitt | eksplisitt `Registry`-klasse |
| Total tidsestimat | 4–5 uker MVP + udefinert fase 5+ | 4–5 uker MVP + ~7 uker for full scope |

---

## Vedlegg A: Komplett øvelseskatalog

Uendret fra v2.0 Vedlegg A. Senior-implement og masters-aldersklasser uttrykkes gjennom parameter-JSON, ikke gjennom nye event-ID-er.

---

## Vedlegg B: Kildereferanser

- NFIF — Poengtabeller: `friidrett.no/arrangement/arrangementshjelp/poengtabeller/`
- NFIF — Tyrvingtabellen 2014 (regneark)
- NFIF — Regler for Lagserien med Serietabellen
- NFIF — Masters Mangekamptabell (separate Excel-filer for menn og kvinner, WMA 2023-basert)
- NFIF — Serietabell for masters
- World Athletics — Scoring Tables of Athletics 2025
- WMA — Age Factors 2023 (`wma-athletics.com`)
- Ekstern verifisering: `worldathleticsscores.com`, `multieventcalculator.com`, `howardgrubb.co.uk/athletics/wmatnf23.html`, `minfriidrettsstatistikk.info`
