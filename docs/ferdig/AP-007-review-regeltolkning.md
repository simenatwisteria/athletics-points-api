# AP-007: Review av regeltolkningen for Tyrving

**Status:** Ferdig — regeltolkningen er låst 2026-09-26
**Opprettet:** 2026-09-25 (Code, etter AP-006)
**Eier:** 🧑 Simen
**Avhenger av:** AP-006

## Hva som skal godkjennes

`tests/fixtures/tyrving_rules.json`: 29 håndskrevne caser for de fem reglene i «Bruk av 2014-tabellen» (samme
tekst i PDF og DOC), hver med utregning og tolkningsnivå. Code har kontrollregnet alle med desimalaritmetikk.
Når du godkjenner, er fila låst, og motoren (AP-008) må treffe alle casene.

## Casene som er Codes tolkning, ikke ordrett tekst

| Case | Tolkning | Alternativ |
|---|---|---|
| R1-07 – R1-10 | Tilleggene for manuell tid gjelder etter **distanse**, også for hekk: 60/80/300 mH +0,20; 100/110/200 mH +0,24; 400 mH +0,14. Begrunnelse: «110m» i teksten finnes bare som hekk. | Tilleggene gjelder bare flatløp, og hekk med manuell tid avvises |
| R1-11 | 600 m og lengre: **ingen tillegg** for manuell tid (teksten stopper på 400 m, og lange løp regnes i tideler) | Avvise manuell tid over 400 m |
| R3-03 | Negativ poengsum blir **0** (regnearket gjør det; teksten sier ingenting) | Avvise resultater som gir negativ sum |

Resten (`"interpretation": "direkte"`) står ordrett i regelteksten. Se særlig R2-01: 2:04.56 på 800 m regnes som
2:04.5 (hundredeler **strykes**, avrundes ikke).

## Åpne spørsmål — trenger svar

1. **Q-01:** Manuell tid på 40 m har ingen regel. Code foreslår å avvise med feilmelding.
2. **Q-02:** Resultat 0 eller manglende resultat gir 0 i regnearket. Code foreslår å avvise input.
3. **Q-03:** Eksakt desimalregning eller regnearkets flyttall (samme som spørsmål 1 i AP-005). Code foreslår eksakt.

## Akseptansekriterier

- [x] Tolkningene i tabellen over godkjent eller endret (Simen 2026-09-26: alle godkjent)
- [x] Q-01 – Q-03 besvart: 40 m manuelt avvises, resultat 0 avvises, eksakt regning (`decided_questions` og `error_cases`)
- [x] Status i `docs/BACKLOG.md` satt til `Ferdig`, med dato: regeltolkningen er låst
