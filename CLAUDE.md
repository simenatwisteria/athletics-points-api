# CLAUDE.md — athletics-points-api

Åpen, transparent beregningsmotor for norske friidrettspoeng: Tyrving (10–19 år), World Athletics Scoring og
Combined Events, WMA Age Grading og NFIFs masters-mangekamptabell. Python-pakken `athletics_scoring` bygges og
verifiseres først; FastAPI og React kommer senere.

- Oppgaver og status: `docs/BACKLOG.md` (eneste oppgaveliste), oppgavefiler i `docs/active/`
- Hvorfor: `docs/BESLUTNINGER.md`, `docs/ANALYSE_2026-09-06.md` · Hvordan: `docs/TEKNISK_FORSLAG_v2.1.md`
- Kildefiler og sjekksummer: `sources/README.md` · Kjente feil i kildene (offisiell tabell vinner): `docs/KILDEAVVIK.md`

## Uforanderlige regler

1. `sources/` og `tests/fixtures/` endres **aldri** av agenten. Unntak: et oracle-skript i en oppgave som eksplisitt
   ber om å *generere* en ny, ulåst fixture-fil. Låste fixtures røres aldri.
2. En feilende test fikses i `athletics_scoring/`, aldri i testen eller i fixtures.
3. Fasit genereres fra `sources/` av `scripts/oracle_*.py`. Oracle-skript importerer aldri `athletics_scoring`.
4. Mistenker du feil fasit eller uklar regeltekst: sett oppgaven til `Blokkert` i `docs/BACKLOG.md`, skriv hvorfor
   i notatet, og **stopp**. Ikke gjett.
5. Oppgaver med eier 🧑 er Simens. Hopp over dem, ikke gjør dem.
6. Ikke opprett nye oppgaver i backloggen — skriv funn under «Innboks».
7. Ingen runtime-avhengigheter i `athletics_scoring`.

## Ferdig-definisjon

```bash
pytest -q && ruff check . && mypy athletics_scoring
```

Alle tre grønne, pluss akseptansekriteriene i oppgavefila.

## Arbeidsrytme per økt

1. Les `docs/BACKLOG.md`.
2. Ta øverste 🤖-oppgave med status `Klar`/`Ny` der alle avhengigheter er `Ferdig`. Sett `Under arbeid`.
3. Implementer. Les oppgavefila i `docs/active/` hvis den finnes.
4. Verifiser med ferdig-definisjonen.
5. Commit: `AP-XXX: <kort beskrivelse>`.
6. Oppdater backloggen (status, flytt oppgavefil til `docs/ferdig/`, fyll ut sluttrapporten) og commit.

## Kommandoer

```bash
python3.13 -m venv .venv && source .venv/bin/activate   # Python ≥ 3.12
pip install -e ".[dev]"
pytest -q                                                # tester
ruff check . && mypy athletics_scoring                   # lint + typer
cd sources && shasum -a 256 -c SHA256SUMS                # kildefilene er uendret
scripts/loop.sh 10                                       # autonom loop, maks 10 runder, pusher aldri
```
