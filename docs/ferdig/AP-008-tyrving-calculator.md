# AP-008: TyrvingCalculator

**Status:** Ferdig 2026-09-26
**Eier:** 🤖 Code
**Avhenger av:** AP-002, AP-005 (fasit låst), AP-007 (regeltolkning låst)

## Sluttrapport

- **Gjort:** `athletics_scoring/tyrving.py`, `TyrvingCalculator(ScoringEngine)` for `("tyrving", "2014")`:
  - Enkel kvotient (tid og distanse) og tre-intervall (kast og stav).
  - Eksakt `Decimal`-regning. Poengsummen rundes ned, med 0 som gulv.
  - R1: tillegg for manuell tid etter distanse, også for hekk. Ingen tillegg over 500 m. 40 m avvises.
  - R2: hundredeler til og med 500 m. I lengre løp strykes hundredeler til tideler.
  - Resultat 0, negativt resultat eller feil resultattype avvises.
  - `calculation_detail` og `calculation_steps` (B-6), `list_events`, `get_parameters`.
  - `athletics_scoring.default_registry()` registrerer kalkulatoren.
- **Tester:** `tests/test_tyrving_calculator.py` (39 tester). Dekker alle 2472 fasit-caser (flyttallskanten mot
  `points_if_exact`), alle 29 regelcaser (poeng og effektivt resultat), 3 feilcaser, tvetydig og ukjent utstyr,
  feil resultattype, forklaringstekst, lister og parametre. Mutasjonstest: seks bevisste feil ble alle fanget
  (round i stedet for floor, avrunding i stedet for stryking, feil tillegg for 110 m, feil 80 %-grense, manuell
  tid ignorert, manglende 0-gulv).
- **Avvik fra plan:** `ScoringEngine.calculate` og `get_parameters` fikk en valgfri `implement`-parameter.
  Tyrving har øvelser som bare skilles på utstyr (110 m hekk for G17–19 har to hekkehøyder). Uten `implement`
  gir slike øvelser `AmbiguousEventError` med de gyldige variantene. `EventInfo` og `ScoreResult` har fått
  feltet `implement`. Versjonen er 0.1.0.
- **Funn:** ingen nye.
