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
- [`docs/BESLUTNINGER.md`](docs/BESLUTNINGER.md) — beslutninger og begrunnelser
- [`docs/TEKNISK_FORSLAG_v2.1.md`](docs/TEKNISK_FORSLAG_v2.1.md) — formler, arkitektur, API-design
- [`docs/ANALYSE_2026-09-06.md`](docs/ANALYSE_2026-09-06.md) — verifiseringsstrategi og loop

## Utvikling

```bash
python3 -m venv .venv && source .venv/bin/activate   # Python ≥ 3.12
pip install -e ".[dev]"
pytest -q && ruff check . && mypy athletics_scoring
```

## Lisens

MIT
