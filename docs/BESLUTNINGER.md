# Beslutninger og oppsummert løsning

**Prosjekt:** Athletics Points Calculator API
**Dato:** 17. april 2026 (oppdatert 26. september 2026)
**Status:** Løsning besluttet — klar for bygging
**Teknisk referanse:** `TEKNISK_FORSLAG_v2.1.md` (formler, endepunkter, prosjektstruktur)

Dette dokumentet oppsummerer *hva* vi har bestemt og *hvorfor*. Den tekniske beskrivelsen ligger i v2-dokumentet og gjentas ikke her.

---

## 1. Oppsummert løsning

En åpen, transparent beregningsmotor for friidrettspoeng, pakket i tre lag:

1. **`athletics_scoring`** — en selvstendig Python-pakke som inneholder all matematikk, alle parametre og alle tester. Dette er kjerneverdien.
2. **FastAPI-wrapper** — et tynt HTTP-lag rundt pakken, med versjonerte endepunkter og IP-basert rate limiting.
3. **React-frontend** — en brukerflate for enkeltberegning, batch-beregning og parameterutforsking.

Tjenesten er bevisst adskilt fra `minfriidrett.no`. Integrasjonen skjer via HTTP når — og hvis — minfriidrett.no trenger poengberegning. Parametrene lagres som JSON i git for full transparens. Ingen database i MVP.

MVP dekker Tyrvingtabellen (2014, alder 10–19, ~530 parameterkombinasjoner, 43 base-events). World Athletics, Serietabellen (Lagserien), Masters-tabellene og WMA Age Grading kommer i senere faser — se kapittel 3 (faktisk bruk i Norge) og kapittel 4 (roadmap).

---

## 2. Beslutninger

### Arkitektur

**B-1. Scoring-pakken bygges før API og frontend.** Vi bygger `athletics_scoring` som en selvstendig Python-pakke med full testdekning før vi legger til FastAPI eller frontend. Scoring-matematikken er kjerneverdien; alt annet er transportmekanismer. Testbarhet isolert uten HTTP-overhead er kritisk for å få matematikken riktig.

**B-2. To tjenester, ikke én.** Athletics Points API og minfriidrett.no forblir separate tjenester med egne lifecycles. Integrasjonen er rene HTTP-kall. Dette er bevisst og skal ikke endres uten ny beslutning.

**B-3. Ingen database i MVP.** Parametre lagres som JSON-filer i versjonskontroll. Database legges ikke til før det finnes et konkret behov (f.eks. nøkkelhåndtering eller logging med analytiske krav).

**B-4. Åpent API uten nøkler i MVP.** Rate limiting skjer per IP via middleware. API-nøkler innføres først når en konkret integrasjonspartner ønsker høyere rate limit.

### API-design

**B-5. Versjonering av parametersett i kontrakten.** API-et tar imot en eksplisitt `version`-parameter i tillegg til `scoring_system`, f.eks. `{"scoring_system": "tyrving", "version": "2014"}`. Hvis versjon ikke sendes, brukes nyeste. Dette er en justering av v2-forslaget og er tatt inn fordi NFIF kan gi ut nye tabeller, og vi vil unngå bryggende kontraktsbrudd.

**B-6. Strukturert beregningsforklaring i tillegg til streng.** Responsen inkluderer både `calculation_detail` (lesbar streng) og `calculation_steps` (array med `{label, value, formula}`-objekter). Frontend og tredjeparter slipper å parse strenger. Dette er en justering av v2-forslaget.

**B-7. Deterministisk caching.** `/api/v1/calculate` og `/api/v1/batch` returnerer `Cache-Control: public, max-age=31536000, immutable` når `version` er eksplisitt angitt. Samme input gir alltid samme output. Dette er en justering av v2-forslaget.

**B-8. Reverse-beregning som uttalt fase 2-feature.** Et `/api/v1/reverse`-endepunkt (gitt ønsket poengsum, beregn nødvendig resultat) dokumenteres som planlagt fase 2-leveranse. Billig å bygge på toppen av eksisterende motor, svært nyttig for trenere. Dette er en justering av v2-forslaget.

**B-9. Ingen JS/TS-mirror-pakke i MVP.** Vi eksponerer parameter-JSON som nedlastbar fil (`/api/v1/parameters/export`), men bygger ikke en parallell JavaScript-beregningsmotor. Duplisering av formellogikk er farligere enn HTTP-latens. Frontend kaller API-et også når det kjører i nettleseren.

### Parametre og data

**B-10. Parameter-JSON ligger i et åpent GitHub-repo.** Formlene er offentlig kjent. Transparens er en feature, ikke en risiko. Dette er åpen beslutning #2 fra v2, avgjort.

**B-11. Tyrving 2014 er gjeldende grunnlag inntil NFIF bekrefter noe annet.** Arkitekturen støtter flere versjoner (jf. B-5), så vi kan legge inn en ny versjon uten å bryte eksisterende klienter. Dette er åpen beslutning #1 fra v2, avgjort.

### Frontend og språk

**B-12. Norsk frontend i MVP.** Målgruppen er norske utøvere, klubber og trenere. Engelsk versjon vurderes hvis det oppstår etterspørsel fra utlandet. Dette er åpen beslutning #3 fra v2, avgjort.

### Deploy og domene

**B-13. Railway (backend) + Vercel (frontend) som deploy-plattformer.** Enkelt oppsett, innebygd rate limiting, auto-deploy fra GitHub.

**B-14. Domenenavn utsettes.** API fungerer uavhengig av domene i utviklingsfasen. Domenenavn bestemmes før soft launch i fase 4. Dette er åpen beslutning #4 fra v2, avgjort som utsatt.

### Integrasjon med minfriidrett.no

**B-15. Integrasjonen venter til det finnes et konkret behov.** minfriidrett.no skal ikke kobles på før en feature der trenger poengberegning. API-et står ferdig og dokumentert til det punktet. Dette er åpen beslutning #5 fra v2, avgjort.

### Verifisering

**B-16. Fire-lags teststrategi som i v2.** Lag 1: enhetstester av formler. Lag 2: parameterverifisering mot Excel. Lag 3: ende-til-ende mot ~1600 genererte testcaser. Lag 4: manuell og kryssverifisering (mot regneark i MVP, mot eksterne kalkulatorer i fase 2+). Ingen avvik aksepteres før soft launch.

---

## 3. Hvilke poengsystemer som faktisk brukes i norsk friidrett

Undersøkelse mot NFIFs offisielle side *Poengtabeller* (friidrett.no/arrangement/arrangementshjelp/poengtabeller/) bekrefter at norsk friidrett bruker *flere* forskjellige poengsystemer avhengig av konteksten. Dette er viktig for scope-prioriteringen videre:

**Femkamp, sjukamp, tikamp for seniorer (inkludert UM, NM, Nordisk):** IAAF/WA Scoring Tables for **Combined Events** (2001-utgaven, opptrykk 2016). Formlene er `a·(b−T)^c` for løp, `a·(M−b)^c` for hopp (cm) og `a·(D−b)^c` for kast (m), og poengene avkortes til heltall. Tyrving brukes *ikke* for mangekamp på seniornivå. *(Rettet 26.09.2026. Det sto tidligere «World Athletics Scoring Tables (2025-utgave)». 2025-tabellene er et eget system som WA selv sier ikke berører mangekamp.)*

**Mangekamp for ungdom under 15:** Tyrvingtabellen. Fra 15 år og oppover brukes de internasjonale tabellene.

**Klubbrangering i Lagserien:** En egen norsk **Serietabell / Seriepoeng**. Dette er et nasjonalt eget system, uavhengig av Tyrving og WA, implementert på `minfriidrettsstatistikk.info`. Bruker senior-implement (kule 7,26 kg, diskos 2,0 kg, slegge 7,26 kg, spyd 800 g m.m.). Gjelder for senior. *(26.09.2026: NFIF har ingen nedlastbar fil eller formel. Stikkprøver i kalkulatoren viser at tabellen ikke er lik mangekamptabellen, masters-tabellenes seniorkolonne eller WA Scoring 2025. Se `docs/SERIETABELL_SAMMENLIGNING_2026-09-26.md`.)*

**Masters mangekamp:** En norsk **Mangekamptabell for masters** (egne Excel-filer for menn og kvinner på friidrett.no), basert på WMAs nye aldersfaktorer fra 01.01.2023. Metoden står i WMA Rulebook Appendix B: *resultatet* ganges med aldersfaktoren, avrundes (løp opp, hopp og kast ned), og slås så opp i Combined Events-tabellen. NFIF-regnearkene er oppslagstabeller laget med denne metoden.

**Masters klubbserien:** En egen **Serietabell for masters**. NFIF-regnearkene dekker bare øvelser som ikke finnes i mangekamptabellen, og seniorkolonnen deres er ikke lik senior-serietabellen. Oppbyggingen må bekreftes av NFIF.

**Masters individuelt:** WMA Age Grading med 2023-aldersfaktorer.

**Ungdomsindividuelt (10–19):** Tyrvingtabellen.

### B-17. Scope utvides for å dekke alle norske poengsystemer

Opprinnelig plan dekket Tyrving (MVP) + WA Scoring + WMA (senere). Dette er nå utvidet med:

- **Serietabellen/Seriepoeng** for Lagserien — høyt prioritert fordi den brukes aktivt av alle klubber og mangler i dagens åpne tilbud.
- **Masters Mangekamptabell** og **Masters Serietabell** — mindre i volum, men helt separate datakilder fra WMA Age Grading.

Begrunnelse: om målet er "én åpen, norsk poengtjeneste" er det ikke forsvarlig å stoppe ved Tyrving + WA + WMA. Klubbene trenger Serietabellen, og masters-miljøet har tre parallelle tabeller, ikke én.

### B-18. Tyrving beholdes som MVP — ingen omprioritering *(prioriteringen av Serietabellen er erstattet av B-22)*

Selv om Serietabellen er bredere brukt, er Tyrvingtabellen det som har rensket datagrunnlag (Excel med formler + DOC-utdrag) og er klart avgrenset. Derfor fortsetter MVP som før. Serietabellen prioriteres som første fase etter MVP, foran WA Scoring.


*B-19 til B-21 er forslag i `docs/ANALYSE_2026-09-06.md`, vedtatt i beslutningsloggen i `docs/BACKLOG.md` (én klone, fasit fra kildefiler, WA foran Serietabellen). B-24 erstatter B-21 for rekkefølgen.*

### B-22. Ny rekkefølge etter MVP (26.09.2026)

Etter at de offisielle kildene er gått gjennom (`kilder/KILDER.md`), er rekkefølgen etter Tyrving: **(0) kildesporing → (1) WA Combined Events → (2) masters mangekamp → (3) WMA Age Grading → (4) serietabell senior og masters → (5) WA Scoring Tables 2025.** Begrunnelse: 1–3 er fullt dokumentert i offisielle kilder og kan verifiseres uten avvik. Serietabellen har ingen offisiell kilde og venter på svar fra NFIF. Erstatter prioriteringen i B-18 og B-21.

### B-23. Kildefiler: NFIF og WMA i `sources/`, WA utenfor repoet

NFIF- og WMA-filene legges i `sources/` med SHA-256 i `sources/SHA256SUMS`, slik som Tyrving. WA-PDF-ene sjekkes ikke inn, fordi de har forbehold mot kopiering og repoet er offentlig. De ligger i Cowork-mappen `kilder/world-athletics/` og brukes lokalt til verifisering. Parametrene for Combined Events hentes fra WMA Appendix B, og fasiten fra seniorkolonnen i NFIF-tabellene. Cowork-mappen `kilder/KILDER.md` har full kildeliste med NFIF-sidene filene er lenket fra.

### B-24. Alle beregninger viser til en offisiell kilde

Hver parameterfil får en `sources`-blokk (`official_page`, `document_url`, `local_copy`, `sha256`, `retrieved`, `section`). API-et returnerer `source_ref` i `calculation_steps`, og frontend viser en lenke til NFIF-siden. Dette gjelder også Tyrving. Utvider B-6 og B-10.

### B-25. Masters mangekamp: NFIF-tabellen er fasit, motoren regner etter WMA Appendix B

Beslutningen fra 2026-09-25 står: NFIF-tabellen er fasit. Motoren regner analytisk etter WMA Appendix B (resultat × aldersfaktor → avrunding → Combined Events), og testen krever null avvik mot hele NFIF-tabellen. Hvis noe avviker, vinner NFIF-tabellen for den øvelsen, og avviket føres i `docs/KILDEAVVIK.md`. Stikkprøver 26.09.2026 stemmer eksakt (M35 200 m og M50 kule).

### B-26. Serietabellen avventer NFIF, og blir en egen funksjon

Vi implementerer ikke Serietabellen før vi har en offisiell kilde (henvendelse til NFIF, se `docs/henvendelser/2026-09-26-nfif-tyrving-avvik.md`). Reserveløsningen er å tilpasse parametre fra kalkulatoren på minfriidrettsstatistikk.info, med tillatelse fra dem som drifter den, og merke kilden som «ikke offisiell». Når motorene for Combined Events og masters er bygget, kjøres en utvidet sammenligning mot kalkulatoren. Serietabell-beregning skal senere vises som en egen funksjon på siden vår.

### B-27. Tolkning av resultatlister ligger i dette API-et (27.09.2026)

Tekst fra Liveres, OpenTrack og minfriidrettsstatistikk.info («Kule G-18-19», «91,4 9,14m», «1,48,98») tolkes i dette
API-et, ikke i hver klient. Svaret viser både tolkningen og poengene, så feil kan spores. Begrunnelse: én plass som kan
testes, samme tolkning for minfriidrett.no, 5KAMP og andre, og utstyrsinformasjonen som trengs for å velge riktig
tabell går ikke tapt. Besluttet av Simen etter anbefaling i `docs/INTEGRASJON-minfriidrett.md`.

### B-28. 5KAMP får en lokal kopi av Combined Events-formelen (27.09.2026)

Unntak fra B-9 for én klient. 5KAMP regner femkamp-poeng lokalt i nettleseren (fem øvelser per kjønn, senior-tabellen),
fordi stevnet 2026-10-03 ikke skal være avhengig av nett eller en ny tjeneste. Kopien er gjort trygg ved at den testes
mot fasit laget her: 10 685 verdier fra NFIFs tabell og resultatlista fra forrige stevne. Dette repoet er fortsatt
kilden. Når API-et er på nett, skal 5KAMP enten bytte til API-et eller kontrollere mot det.

---

## 4. Roadmap

Totalt MVP-estimat: **4–5 uker**, inkludert verifisering.

### Fase 1: Scoring-pakke og verifisering (uke 1–2)

Uke 1 leverer `extract_tyrving_params.py` som ekstraherer alle ~530 parameterkombinasjoner fra Excel til JSON, parameterverifisering mot Excel som kjører grønt, implementert `TyrvingCalculator` med begge formeltyper (enkel kvotient og tre-intervall), og enhetstester med håndregnede eksempler.

Uke 2 leverer ~1600 automatisk genererte testcaser som kjører grønt, fiksing av edge cases (80%-grense, avrunding, manuell tidtaking), og manuell verifisering av et utvalg mot regnearket. Pakken har 100 % korrekte beregninger ved slutten av fase 1.

### Fase 2: API (uke 3)

FastAPI-wrapper rundt pakken med alle endepunkter (`calculate`, `batch`, `events`, `parameters`, `formulas`, `export`, `health`). IP-basert rate limiting, versjonering i kontrakten (B-5), strukturerte beregningssteg (B-6), deterministisk caching (B-7). Integrasjonstester og autogenerert OpenAPI-dokumentasjon.

### Fase 3: Frontend (uke 3–4)

React-app med kalkulator (live-beregning, viser calculation steps), batch-view (tabell-input og CSV-paste), og parameterutforsker. Responsivt design som fungerer på mobil. Kobles til API-et via `VITE_API_URL`.

### Fase 4: Deploy og polish (uke 4–5)

Railway + Vercel satt opp, GitHub Actions CI/CD med automatiske tester ved PR og auto-deploy til produksjon ved push til `main`. README, brukerdokumentasjon, domenenavn valgt. Siste runde manuell testing. Soft launch.

### Fase 5+: Utvidelser (utenfor MVP)

Rekkefølgen er erstattet av B-22. Oppgavene står i `docs/BACKLOG.md`, og bakgrunnen i `docs/PLAN_FLERE_POENGSYSTEMER.md`: kildesporing (fase 0) → WA Combined Events → masters mangekamp → WMA Age Grading → serietabeller (når NFIF har svart) → WA Scoring 2025. Reverse-beregning (`/api/v1/reverse`, B-8) kommer etter Combined Events. API-nøkler og historisk logging legges til når konkret behov oppstår.

---

## 5. Hva vi *ikke* gjør (bevisste utelatelser)

Disse er aktivt fjernet fra scope for å holde MVP ren:

- Database (SQLite/PostgreSQL) — vurderes først ved konkret behov.
- API-nøkkelhåndtering, hashing, signup-flyt — venter til første integrasjonspartner.
- Engelsk frontend — venter til etterspørsel.
- JS/TS-speilpakke — venter på at problemet faktisk oppstår.
- Historisk logging av beregninger — venter til et analytisk behov defineres.
- Sammenslåing med minfriidrett.no — eksplisitt adskilt.

Hver av disse kan legges til senere uten å rive opp kjernen. Det er hele poenget med å holde scoring-pakken som et selvstendig lag.

---

## 6. Endringslogg

| Dato | Endring |
|------|---------|
| 2026-04-17 | Initial beslutningslogg. v2 lagt til grunn, med fire justeringer (B-5, B-6, B-7, B-8). Alle åpne punkter fra v2 kap. 13 avgjort. |
| 2026-04-17 | Scope utvidet etter undersøkelse av NFIFs offisielle poengtabeller (kap. 3): Serietabellen/Seriepoeng, Masters Mangekamptabell og Masters Serietabell lagt til som egne poengsystemer (B-17). Tyrving beholdes som MVP, Serietabellen blir første post-MVP-leveranse foran WA Scoring (B-18). Teknisk forslag oppdatert til v2.1 med utvidet arkitektur, nye scoring-systemer og revidert roadmap. |
| 2026-09-26 | Offisielle kilder lastet ned (NFIF og WMA i `sources/`, WA bare i Cowork-mappen `kilder/`). Kap. 3 rettet: seniormangekamp bruker Combined Events-tabellen (2001), ikke WA Scoring 2025. Masters-metoden beskrevet (WMA Appendix B). Serietabellen har ingen offisiell kilde og avviker fra alle kjente tabeller. Nye beslutninger B-22 til B-26: ny rekkefølge, kildefiler (WA utenfor repoet), kildesporing i API-et, masters-mangekamp regnes etter Appendix B med NFIF-tabellen som fasit, serietabellen avventer NFIF. |
| 2026-09-27 | B-27: tolkning av resultatlister ligger i dette API-et. |
| 2026-09-27 | B-28: 5KAMP får en lokal, testet kopi av Combined Events-formelen før stevnet 2026-10-03. |
