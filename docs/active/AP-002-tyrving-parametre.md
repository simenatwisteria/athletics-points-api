# AP-002: Tyrving — parameterekstraksjon Excel → JSON, testet mot Excel-celler

**Status:** Klar
**Opprettet:** 2026-09-25 (PROMPT-001)
**Eier:** 🤖 Code
**Avhenger av:** AP-001

## Problemet

Parametrene (1000-poengsresultat, kvotient, faktorer) finnes bare inne i regnearket. Motoren trenger dem som
versjonert JSON (B-3, B-10), og vi må vite at JSON-en er en tro kopi.

## Hvorfor nå

Både oracle (AP-004) og kalkulatoren (AP-008) trenger parametrene.

## Verifiserte fakta

- `sources/tyrving/tyrving-2014-redigerbar.xlsx` — ark `Forside` + 20 ark `Gutter NN år` / `Jenter NN år` (10–19).
- Ark `Gutter 15 år`: rad 4 er overskrift. Kolonne `B` = øvelse, `D` = minutter, `E` = sekunder/resultat
  (input), `F` = poeng (formel), `H` = «1000 poeng», `I` = «Kvotient», `J`/`K`/`L` = «Faktor 1–3».
  Hjelpekolonner `M`–`P` inneholder mellomregning.
- Eksempel `F6` (60 m): `=IF(P6<0,0,IF(E6=0,0,ROUNDDOWN(P6,0)))`, `P6 = 1000 + (H6*100 − E6*100) * I6`.
- 600 m og lengre: `M = (D*60+E)*10`, `N = H*10` — tideler, ikke hundredeler.

**Verifiser før du koder:** hvilke rader som bruker `J`–`L` (tre-intervall, kast/stav), og om alle 20 ark har
samme kolonneoppsett. Les formlene, ikke bare verdiene (`openpyxl` med `data_only=False`).

## Løsningsretning

1. `scripts/extract_tyrving_params.py` (bruker `openpyxl`, dev-avhengighet) skriver
   `athletics_scoring/data/tyrving_parameters_2014.json`, med kildefil og SHA-256 i metadata.
2. Formeltype per rad utledes fra formelen i `F`/`P` (`simple_quotient` / `three_interval`) og enheten
   (hundredeler/tideler/meter), ikke fra øvelsesnavnet.
3. `tests/test_tyrving_params.py`: for hver kombinasjon, JSON-verdi == Excel-celle (leser Excel direkte).

## Fallgruver

- Ikke skriv noe til `sources/`. Ikke åpne filen i skrivemodus.
- Flyttall: sammenlign eksakt mot cellenes verdier; ikke rund av i JSON.

## Utenfor scope

Poengberegning (AP-008), oracle (AP-004), regeltekst fra DOC/PDF (AP-006).

## Akseptansekriterier

- [ ] ~530 kombinasjoner i JSON, antallet rapportert i sluttrapporten
- [ ] `test_tyrving_params` grønn for alle kombinasjoner
- [ ] `pytest -q && ruff check . && mypy athletics_scoring` grønt

## Sluttrapport (fylles av Code)

- **Gjort:** 
- **Avvik fra oppgavefila:** 
- **Funn som bør bli egne oppgaver:** 
