# AP-028: Serietabellen — utvidet sammenligning mot våre motorer

**Status:** Klar (kjøres av Cowork, ikke av loopen)
**Opprettet:** 2026-09-26 (Cowork)
**Eier:** 🧑 Simen (utføres av Cowork)
**Avhenger av:** AP-012, AP-016

## Mål

Avgjøre om noen del av senior-serietabellen på minfriidrettsstatistikk.info kan regnes ut med motorene vi har,
og samle nok datapunkter til å tilpasse parametre hvis NFIF ikke har en offisiell kilde (BV-050).

## Hvorfor

Stikkprøven 2026-09-26 (`docs/SERIETABELL_SAMMENLIGNING_2026-09-26.md`, 265 resultater) viste at kalkulatoren
avviker fra alle tabellene vi har. Når motorene for Combined Events og masters finnes, kan sammenligningen gjøres
med våre egne beregninger og med flere punkter.

## Hvorfor ikke loopen

Oppgaven sender skjema til et eksternt nettsted. Loopen har ikke nettverkstilgang i `scripts/loop.sh`, og
hvor mye vi belaster en tredjeparts side bør styres av et menneske.

## Løsningsretning

1. Gjenbruk metoden fra 26.09: samle alle øvelser i hver innsending og hold antallet innsendinger lavt (under 30
   totalt). Vent minst noen sekunder mellom innsendingene.
2. For hver øvelse: 15–20 resultater spredt over skalaen, pluss punkter rundt 1000 og 1200 poeng.
3. Sammenlign med `CombinedEventsCalculator` og med seniorkolonnen i `sources/masters/nfif-masters-serietabell-*`.
4. Undersøk om seriepoengene følger en kjent formelform per øvelse (potens, stykkevis lineær, andregrad) og
   hvor godt den passer.
5. Resultatet skrives i en ny analyse i `docs/`, og konklusjonen i BV-050.

## Akseptansekriterier

- [ ] Analyse i `docs/` med data, metode og konklusjon
- [ ] BV-050 i `docs/BEREGNINGSVALG.md` er oppdatert med konklusjonen
- [ ] Ingen endringer i `athletics_scoring/`, `sources/` eller `tests/fixtures/`
