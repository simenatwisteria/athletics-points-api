# athletics-points-api

Åpen, transparent beregningsmotor for norske friidrettspoeng:

- **Tyrvingtabellen** (2014, 10–19 år), inkludert mangekamp under 15 år
- **World Athletics Scoring Tables** (2025) og **Combined Events** (femkamp, sjukamp, tikamp)
- **WMA Age Grading** (aldersfaktorer 2023)
- **NFIFs mangekamptabell for masters**

**Status: under oppbygging.** Ingen poengberegning er implementert ennå.

Alle parametre ligger som JSON i repoet, og all fasit genereres fra de offisielle kildefilene i
[`sources/`](sources/README.md) — aldri fra motoren selv.

## Dokumentasjon

- [`docs/BACKLOG.md`](docs/BACKLOG.md) — oppgaver og status
- [`docs/KILDEAVVIK.md`](docs/KILDEAVVIK.md) — kjente feil i NFIFs kildefiler og hvordan de håndteres
- [`docs/BESLUTNINGER.md`](docs/BESLUTNINGER.md) — beslutninger og begrunnelser
- [`docs/TEKNISK_FORSLAG_v2.1.md`](docs/TEKNISK_FORSLAG_v2.1.md) — formler, arkitektur, API-design
- [`docs/ANALYSE_2026-09-06.md`](docs/ANALYSE_2026-09-06.md) — verifiseringsstrategi og loop

## Utvikling

```bash
python3 -m venv .venv && source .venv/bin/activate   # Python ≥ 3.12
pip install -e ".[dev,api]"
pytest -q && ruff check . && mypy athletics_scoring athletics_api
```

## API

HTTP-API-et (`athletics_api`) følger kontrakten i [`docs/api/openapi.yaml`](docs/api/openapi.yaml). Start:

```bash
uvicorn athletics_api.main:app --host 0.0.0.0 --port $PORT
```

Miljøvariabler: `CORS_ALLOWED_ORIGINS` (kommaseparert, standard `https://5kamp.minfriidrett.no`),
`RATE_LIMIT_PER_MINUTE` (per klient-IP, standard 600, 0 slår av) og `TRUST_PROXY=1` bak en proxy som setter
`X-Forwarded-For` (Railway).

## Lisens

MIT
