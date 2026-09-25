# AP-001: Grunnmur — `models.py`, abstrakt `engine.py`, `registry.py`

**Status:** Ferdig
**Opprettet:** 2026-09-25 (PROMPT-001)
**Eier:** 🤖 Code
**Avhenger av:** —

## Problemet

Pakken `athletics_scoring` er tom. Alle kalkulatorer (Tyrving, WA, WMA, masters) trenger felles datamodell,
et felles grensesnitt og et oppslag fra (system, versjon) til motor.

## Hvorfor nå

Første byggestein. AP-002 og alle senere kalkulatorer bygger på typene herfra.

## Verifiserte fakta

- `docs/TEKNISK_FORSLAG_v2.1.md` kap. 7.1 — utkast til `Result`, `CalculationStep`, `ScoreResult`,
  `ScoringEngine` (ABC med `calculate`, `list_events`, `get_parameters`, valgfri `reverse`) og `Registry`.
- `docs/BESLUTNINGER.md` B-5 (versjon i kontrakten, nyeste som standard), B-6 (`calculation_steps`), B-8 (`reverse`).
- Ingen runtime-avhengigheter tillatt (`pyproject.toml`): bruk `dataclasses`, `abc`, `enum`.

## Løsningsretning

1. `models.py`: frosne dataklasser (`frozen=True`) for `Result`, `CalculationStep`, `ScoreResult`, `EventInfo`.
   `Gender` som `enum.StrEnum` (`"M"`, `"F"`).
2. `engine.py`: `ScoringEngine(ABC)` med `system: str` og `version: str` som klasseattributter.
3. `registry.py`: `Registry` med `register(engine)` og `get(system, version=None)`; `None` gir nyeste versjon.
   Tydelige unntak (`UnknownSystemError`, `UnknownVersionError`) i egen `errors.py`.
4. Enhetstester med en dummy-motor i `tests/test_registry.py`.

## Fallgruver

- `mypy --strict`: `parameters: dict` må typesettes (`dict[str, float]` eller en `TypedDict`).
- Versjonssortering: `"2014" < "2025"` fungerer som streng, men dokumenter antakelsen.

## Utenfor scope

Ingen poengberegning, ingen Tyrving-spesifikk logikk, ingen FastAPI.

## Akseptansekriterier

- [x] `Registry.get("x")` returnerer nyeste versjon; ukjent system/versjon gir eget unntak
- [x] `pytest -q && ruff check . && mypy athletics_scoring` grønt

## Sluttrapport (fylles av Code)

- **Gjort:** `models.py` (`Gender`, `Result`, `CalculationStep`, `EventInfo`, `ScoreResult`, typealias
  `Parameters = Mapping[str, float]`), `engine.py` (`ScoringEngine` med `system`/`version` som `ClassVar`),
  `registry.py` (`register`, `get`, `systems`), `errors.py`. 13 tester.
- **Avvik fra oppgavefila:** `Result` validerer negative verdier og `time_minutes` uten `time_seconds`, og har
  `total_seconds`. `calculation_steps` er `tuple` (frossen). Egen `DuplicateEngineError` ved dobbel registrering.
- **Funn som bør bli egne oppgaver:** ingen.
