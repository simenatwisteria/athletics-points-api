# Beregningsvalg

Register over valg vi har tatt selv i beregningene, der kildene er tause, uklare eller uenige. Hvert valg har et
fast nummer (BV-xxx) som koden viser i `calculation_steps` når valget påvirker resultatet, slik at alle kan se
hvorfor et poengtall ble som det ble.

- **Kildeavvik** (kildene sier forskjellige ting) står i `docs/KILDEAVVIK.md`. Her står bare *valget* vi tok.
- **Status:** `Bekreftet` = kilden sier det eksplisitt · `Låst` = godkjent av Simen · `Anbefalt` = foreslått av
  Cowork etter undersøkelse, ikke bekreftet av NFIF · `Antakelse` = ikke kildebelagt, venter på svar.
- Et valg endres ved å legge inn en ny linje i endringsloggen nederst, aldri ved å skrive om historikken.

Kildehenvisninger peker til filer i `sources/`. WA-bøkene ligger ikke i repoet (B-23), bare i Cowork-mappen
`kilder/world-athletics/`, og siteres med sidetall.

---

## Generelt

| BV | Valg | Begrunnelse og kilde | Status |
|---|---|---|---|
| BV-001 | Ved konflikt mellom kildefiler vinner den offisielle tabellen (dokumentet forbundet selv kaller offisielt). Avvikene føres i `KILDEAVVIK.md`. | Simens regel 2026-09-25. | Låst |
| BV-002 | Er kilden taus om avrunding av input, rundes tider **opp** og lengder **ned** til tabellens oppløsning (utøverens disfavør). | Samme prinsipp som WMA Appendix B s. 1 («Run up, Jump and Throw down») og som tidtakingsreglene. Gir aldri kunstig høye poeng. | Anbefalt |
| BV-003 | Poengsummen rundes alltid ned til heltall, og negativ poengsum gir 0. | Tyrving R3, IAAF Combined Events s. 22 («rounded down to a whole number»). | Bekreftet |
| BV-004 | Beregningen gjøres eksakt (desimal), ikke med flyttall. | Tyrving-regelteksten sier at alle desimaler beholdes. Unngår at 674,9999 blir 674 i stedet for 675. | Låst |

## Tyrving 2014

Låst i AP-005 og AP-007. Regelcasene står i `tests/fixtures/tyrving_rules.json`.

| BV | Valg | Begrunnelse og kilde | Status |
|---|---|---|---|
| BV-010 | Word- og PDF-tabellen vinner over regnearket (G19 2000 m, J17 kule 3 kg). | BV-001. Forsiden i regnearket kaller den to siders tabellen offisiell. `KILDEAVVIK.md`. | Låst |
| BV-011 | Hundredeler strykes i løp over 500 m. | Regelteksten (R2). Regnearket gjør det ikke. | Låst |
| BV-012 | Tillegg for manuell tid gis etter distanse, også for hekk. Ingen tillegg fra 600 m. Manuell tid på 40 m avvises. | Regelteksten (R1), tolkning låst i AP-007. | Låst |
| BV-013 | Resultat 0 eller manglende resultat avvises. | AP-007. | Låst |
| BV-014 | «Rimelig område» er brukerhjelp. Poeng beregnes uansett. | Beslutningslogg 2026-09-26. | Låst |
| BV-015 | Mangekamp under 15 år summerer Tyrving-poeng. Fra 15 år avviser Tyrving-motoren mangekamp og viser til BV-021 (implementert i AP-009). | B-17. NFIF-kilde for grensen er ikke funnet, men UM-reglementet (BV-021) bruker internasjonale tabeller fra 15 år. | Anbefalt |

## WA Combined Events (mangekamp)

| BV | Valg | Begrunnelse og kilde | Status |
|---|---|---|---|
| BV-020 | Mangekamp bruker IAAF Scoring Tables for Combined Events (2001, opptrykk 2016), ikke WA Scoring Tables 2025. | WA-nyheten om 2025-tabellene sier at mangekamp er uendret. UM-reglementet §16.5 («internasjonale poengtabeller for mangekamp»). | Bekreftet |
| BV-021 | Fra 15 år bruker mangekamp de internasjonale tabellene, også for ungdom med lettere redskap. | `sources/nfif/nfif-um-reglement-2026.pdf` §16.4–16.5, s. 9. | Bekreftet |
| BV-022 | Parametrene a, b, c hentes fra WMA Appendix B s. 2. Kvinner 1500 m: a = 0,02883, b = 535, c = 1,88. | `sources/wma/wma-2023-appendix-b-combined-events.pdf` s. 2. Kvinner 1500 m fra IAAF-boka s. 23 (kvinners tikamp). Kontrollert 2026-09-26 mot seniorkolonnen («Sr») i NFIFs masters-tabeller: null avvik for alle automatiske tider og tekniske øvelser (menn 16 øvelser, 15 051 rader; kvinner 15 øvelser, 13 929 rader) og for manuell tid på 100, 200, 400 m og korthekk (1 502 rader). | Bekreftet |
| BV-023 | Øvelser som ikke er i de internasjonale tabellene bruker NFIFs koeffisienter: 600 m J15/16 (0,198890 · 185 · 1,88), 800 m inne G15/16 (0,160027 · 231 · 1,836), 80 m hekk J15/16 (12,2092 · 22 · 1,835), 100 m hekk G15/16 (8,73753 · 26 · 1,83). | UM-reglementet §16.5, s. 9. Ingen uavhengig fasit finnes. | Bekreftet |
| BV-024 | Manuell tid: +0,24 s til og med 300 m (også 60 m og 60 m hekk), +0,14 s på 400 m, ingen tillegg over 400 m. | IAAF-boka s. 23 og WMA Appendix B s. 1. IAAF-bokas tabell for manuell tid på 60 m (s. 166: 6,0 = 1170 poeng) bekrefter +0,24. NFIFs masters-ark bruker +0,20 på 60 m, 60 m hekk og 80 m hekk, se `KILDEAVVIK.md`. Vi følger de to primærkildene. | Anbefalt |
| BV-025 | Tider med tusendeler rundes opp til hundredeler, lengder rundes ned til hel centimeter, før poengene regnes. | BV-002. Tabellene har hundredeler og centimeter. | Anbefalt |
| BV-026 | I 5KAMP regnes alle tider som elektroniske. Ingen tillegg for manuell tid. Senior-tabell og seniorutstyr for alle deltakere. | Simen, 2026-09-27. Gjør resultatene sammenlignbare med forrige stevne. Gjelder klubbstevnet, ikke offisielle mesterskap. | Låst |

## Masters mangekamp

| BV | Valg | Begrunnelse og kilde | Status |
|---|---|---|---|
| BV-030 | Metoden følger WMA Appendix B: (1) håndtidskorreksjon, (2) resultat × aldersfaktor med fire desimaler, (3) avrunding, (4) Combined Events-tabellen, (5) avkorting. | `sources/wma/wma-2023-appendix-b-combined-events.pdf` s. 1. | Bekreftet |
| BV-031 | Det aldersjusterte resultatet rundes **opp** til 0,01 s for løp og **ned** til hel cm for hopp og kast. | Appendix B s. 1. | Bekreftet |
| BV-032 | Aldersfaktorene er per 5-årsklasse (M/W35, 40, …). | Appendix B s. 4 (kvinner) og s. 5 (menn). NFIF-arkene har samme klasser. | Bekreftet |
| BV-033 | Klassen bestemmes av alder på konkurransedagen. API-et tar imot klasse direkte (f.eks. «M50»), ikke fødselsdato. | WMA-praksis. Holder beregningen fri for persondata. Klassen er ikke fastsatt i kildene vi har lagret. | Anbefalt |
| BV-034 | Redskap og hekkehøyde er gitt av klassen (raden «Vekt:»/«Hhøyde» i NFIF-arkene). Et resultat med annet redskap enn klassens avvises med en forklarende feil. | Aldersfaktoren forutsetter klassens redskap (Appendix B s. 1). En annen vekt ville gitt feil poeng uten at noen merket det. | Anbefalt |
| BV-035 | NFIF-tabellen er fasit. Motoren skal gi null avvik mot den, unntatt der `KILDEAVVIK.md` sier noe annet: manuell tid under 100 m (BV-024) og de forskjøvne cellene i menn 200 m M90–M100 (hoppes over, ikke reparert). | B-25. Kontrollert av Code i AP-016: null avvik på 431 467 caser utenom disse. | Låst |

## WMA Age Grading (individuelt)

| BV | Valg | Begrunnelse og kilde | Status |
|---|---|---|---|
| BV-040 | Ettårige aldersfaktorer fra 2023-utgaven. Alder i hele år på konkurransedagen. | `sources/wma/wma-2023-age-factors.pdf`. | Bekreftet |
| BV-041 | Vi leverer det aldersjusterte resultatet, men **ikke prosent**. PDF-en har ingen standarder («open standards») å dele på. | Kontrollert 2026-09-26: PDF-en inneholder bare faktorer. Prosent kommer når en offisiell standardtabell er funnet. | Anbefalt |
| BV-042 | Det aldersjusterte resultatet avrundes som BV-031. | Samme regel som masters mangekamp gir sammenlignbare tall. | Anbefalt |

## Serietabellen

| BV | Valg | Begrunnelse og kilde | Status |
|---|---|---|---|
| BV-050 | Serietabellen implementeres ikke før vi har en offisiell kilde. | B-26. Ingen NFIF-fil finnes, og kalkulatoren på minfriidrettsstatistikk.info avviker fra alle kjente tabeller (`docs/SERIETABELL_SAMMENLIGNING_2026-09-26.md`). | Antakelse |
| BV-051 | Hypotese: masters-serien bruker masters-mangekamptabellen for øvelsene den dekker, og masters-seriearkene for resten. | Arkene dekker nøyaktig øvelsene som mangler i mangekamptabellen. Spurt NFIF. | Antakelse |

---

## Endringslogg

| Dato | Endring |
|---|---|
| 2026-09-26 | Registeret opprettet (Cowork). Tyrving-valgene samlet fra AP-005/AP-007 og beslutningsloggen. Nye valg for Combined Events, masters, Age Grading og serietabellen etter gjennomgang av kildene. |
| 2026-09-26 | BV-024 utvidet til 80 m hekk. BV-035 utvidet med de forskjøvne 200 m-cellene. Begge etter blokkeringen av AP-016, anbefalt av Cowork og gjeldende til Simen sier noe annet. |
| 2026-09-27 | BV-026: 5KAMP regner tider som elektroniske og bruker senior-tabellen for alle (Simen). |
