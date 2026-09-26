# Plan: flere poengsystemer etter Tyrving

**Dato:** 26.09.2026  
**Bygger på:** `BESLUTNINGER.md` (B-1 til B-18) og `TEKNISK_FORSLAG_v2.1.md`  
**Kilder:** `sources/README.md` i repoet og `kilder/KILDER.md` i Cowork-mappen (lenker tilbake til NFIF)  
**Oppgaver:** `docs/BACKLOG.md` er eneste sanne oversikt. PS-numrene under er arbeidsnavn: PS-001/002 = AP-027, PS-003 = B-23, PS-010–014 = AP-012, PS-020–024 = AP-016, PS-030–031 = AP-014, PS-040 = AP-026, PS-041–043 = AP-019, PS-044 = AP-028, PS-045 = AP-029, PS-050–052 = AP-011.

Planen oppdaterer faseinndelingen i v2.1 ut fra hva de offisielle dokumentene faktisk inneholder. Den viktigste endringen er rekkefølgen. Mangekamp (WA Combined Events) og masters-mangekamp er fullt dokumentert og kan bygges nå. Serietabellen, som v2.1 satte først, har ingen offisiell kilde og må avklares med NFIF før vi kan implementere den.

---

## 1. Hva kildene viser

### 1.1 Oversikt

| # | System | Brukes til | Offisiell kilde | Beregning | Klar til bygging? |
|---|---|---|---|---|---|
| A | **WA Combined Events** (mangekamptabellen) | Mangekamp fra 15 år, junior, senior, UM/NM/Nordisk | IAAF Scoring Tables for Combined Events (2001, opptrykk 2016) + formler i WMA Appendix B | `P = a·(b−T)^c` / `a·(M−b)^c` / `a·(D−b)^c`, avkortet til heltall | **Ja** |
| B | **Masters mangekamp** | Masters mangekamp, 35+ | WMA Appendix B 2023 + NFIF-regnearkene (menn/kvinner) | Resultat × aldersfaktor (5-årsklasse) → avrund → system A | **Ja** |
| C | **WMA Age Grading** (individuelt) | Sammenligning av masters-resultater | 2023 WMA Age Factors (ettårige faktorer) | Resultat × faktor. Prosentverdi krever standarder (se åpent spørsmål) | Delvis |
| D | **Masters serietabell** | Klubbserie for masters | NFIF-regnearkene (menn/kvinner) | Uavklart, se 1.4 | Nei, må avklares |
| E | **Serietabellen senior** (Lagserien) | Klubbserien | **Ingen offisiell fil.** Bare nettkalkulator på minfriidrettsstatistikk.info | Ukjent formel | **Nei, blokkert** |
| F | **WA Scoring Tables 2025** | Sammenligning på tvers av øvelser (internasjonalt) | WA Scoring Tables of Athletics 2025 (846 s. PDF) | Formel ikke publisert. Må tilpasses fra tabellene | Mulig, men lav prioritet |

### 1.2 A – WA Combined Events

- Alle parametrene (a, b, c) for menn og kvinner står i WMA Appendix B, s. 2, og de gir nøyaktig samme poeng som den offisielle IAAF-tabellen. Kontroll: 200 m menn 19,04 gir 1200 poeng, både etter formelen og i NFIF-regnearket.
- Regler: poengene **avkortes** til heltall (674,999 blir 674). Hopp måles i cm, kast i meter, løp i sekunder.
- Håndtid skal ikke korrigeres i den ordinære mangekamptabellen, for den har egne kolonner for håndtid. Merk at NFIF-regnearkene har egne «-m»-ark for manuell tid.
- WA skriver at mangekamptabellen ikke er endret med 2025-oppdateringen. NFIF-lenken «Poengtabell mangekamp UM, NM og Nordisk» peker på 2025-nyheten, men den nyheten sier selv at mangekamp er et eget system. **Konklusjon:** For mangekamp brukes system A, ikke F.
- Kobling til resultatsiden vi sjekket i går: Den brukte system A, og det var riktig. Avvikene der skyldtes lengdekolonnen og avrundingen, ikke valg av tabell.

**Korrigering av BESLUTNINGER kap. 3:** Der står det at seniormangekamp bruker «World Athletics Scoring Tables (2025-utgave)». Det skal være *IAAF/WA Scoring Tables for Combined Events (2001)*.

### 1.3 B – Masters mangekamp

Metoden er beskrevet i sin helhet i WMA Appendix B:

1. Håndtid på distanser til og med 400 m korrigeres først: +0,24 s for 50–300 m og +0,14 s for 400 m. Lengre distanser korrigeres ikke.
2. Resultatet ganges med aldersfaktoren for kjønn, 5-årsklasse og øvelse. Faktoren skal brukes med fire desimaler.
3. Avrunding i utøverens disfavør: **løp rundes opp** til nærmeste hundredel, **hopp og kast rundes ned** til nærmeste centimeter.
4. Det aldersjusterte resultatet slås opp i system A, og poengene avkortes.

Aldersfaktorene tar allerede hensyn til lettere redskaper og lavere hekker. En M65 som støter 5 kg kule, regnes derfor rett mot 7,26 kg-tabellen.

**Kontrollert mot NFIF-regnearket:**
- M35 200 m: 19,44 × 0,9791 = 19,034, rundet opp til 19,04, gir 1200 poeng. Det stemmer med arket.
- M50 kule (6 kg): 18,70 × 1,1551 = 21,60 gir 1200 poeng. Det stemmer med arket.

NFIF-regnearkene er altså ferdig utregnede oppslagstabeller (1–1200 poeng per klasse) laget med denne metoden. Vi implementerer metoden analytisk og bruker regnearkene som fasit i testene.

**Korrigering av v2.1 §3.4.2:** Der står det at «WA Scoring-verdien multipliseres med aldersfaktor». Det er feil. Det er *resultatet* som ganges med faktoren, før poengene slås opp.

Noe gjenstår å sjekke:
- NFIF-arkene har øvelser som ikke er med i WMAs mangekampliste (for eksempel 60/100/400 m og 1000 m for menn, og vektkast). Parametrene for dem må hentes fra Appendix B og verifiseres mot arkene.
- NFIF nevner «nye seniortabeller for slegge (menn) og slegge og vektkast (kvinner)». Vi må kontrollere at Appendix B-parametrene for slegge og vektkast stemmer med arkene.
- Noen klasser har to kolonner (for eksempel ulik kulevekt rundt M50). Hvilke redskaper som gjelder per klasse, må kartlegges fra rad 3 («Vekt:») i hvert ark.

### 1.4 D – Masters serietabell

- NFIF-regnearkene dekker bare øvelser som *ikke* finnes i mangekamptabellen: langhekk, 800 m og lengre, hinder, kappgang, høyde og lengde uten tilløp, og tresteg. **Hypotese:** Masters-serien bruker mangekamptabellen (B) for de øvelsene den dekker, og disse arkene for resten.
- Kolonnen «Sr» i arkene er **ikke** den samme som senior-serietabellen på minfriidrettsstatistikk.info. To eksempler:
  - 800 m 1.39,87 gir 1200 i NFIF-arket, men 1246 i kalkulatoren.
  - Tresteg 17,52 gir 1200 i arket, men 1112 i kalkulatoren.
- Masters-serien har altså sin egen senior-basis, trolig laget med samme formeltype som A. Før vi bygger dette, må vi få NFIFs masterskomité til å bekrefte hypotesen og formelen.

### 1.5 E – Serietabellen senior (Lagserien)

- NFIF har ingen nedlastbar fil. Den eneste inngangen er kalkulatoren på minfriidrettsstatistikk.info, som er en tredjepart. De gamle NFIF-lenkene til `serietabellen.xls` gir 404.
- Tabellen er ikke system A. Et eksempel: 200 m 23,79 gir 668 seriepoeng, mot 712 i mangekamptabellen.
- **Sammenligning 26.09.2026** (`docs/SERIETABELL_SAMMENLIGNING_2026-09-26.md`): Jeg la inn 265 eksempelresultater (27 øvelser, begge kjønn). Bare 2 ga samme poeng som «Sr»-kolonnen i NFIFs masters-tabeller. Medianavviket var 50 poeng og det største 198. WA Scoring 2025 treffer heller ikke, og en enkel potensformel passer ikke. Senior-serietabellen er altså et eget system.
- **Konsekvens:** Uten en offisiell kilde kan vi ikke vise til et NFIF-dokument når vi forklarer beregningen, og det bryter med prinsippet om transparens (B-10). Dette må avklares med NFIF før vi implementerer. Reserveløsningen er å tilpasse parametre fra kalkulatoren, med tillatelse fra dem som drifter den, og merke dem tydelig som «ikke offisiell kilde».

### 1.6 F – WA Scoring Tables 2025

- Formelen er ikke publisert. PDF-en er tekstbasert (pdftotext fungerer), så parametre kan tilpasses per øvelse. Kjent form: `P = a·(x + b)² + c`.
- PDF-en har et forbehold om kopiering. Å regne ut poeng og lagre tilpassede koeffisienter er vanlig praksis, men vi publiserer ikke tabellene. Dette bør vurderes før lansering.
- Brukes ikke offisielt i norske konkurranser, men er nyttig på minfriidrett.no for å sammenligne øvelser.

---

## 2. Revidert rekkefølge

| Fase | Innhold | Avhenger av | Grovt estimat |
|---|---|---|---|
| **0** | Kildesporing i parameterformatet (gjelder alle systemer, også Tyrving) | – | 1–2 dager |
| **1** | A: WA Combined Events | Fase 0 | 3–4 dager |
| **2** | B: Masters mangekamp | Fase 1 | 4–5 dager |
| **3** | C: WMA Age Grading, individuelt | Fase 2 (samme faktorer) | 3–4 dager |
| **4** | E + D: Serietabell senior og masters | **Svar fra NFIF** | 1–2 uker etter avklaring |
| **5** | F: WA Scoring Tables 2025 | Juridisk avklaring | 1–2 uker |

Begrunnelse: A og B er fullt dokumentert, lette å verifisere og brukes i dag (jf. resultatsiden vi sjekket). E har ingen offisiell kilde. Henvendelsen til NFIF sendes **nå**, slik at svaret kan komme mens fase 1–3 bygges. Dette erstatter B-18 om at serietabellen skal komme først etter MVP.

---

## 3. Backlog

Formatet følger mønsteret fra `/docs` i repoet. ID-ene fortsetter der Tyrving-backloggen slutter, og kan nummereres om ved behov.

### Fase 0 – Kildesporing

**PS-001 Kildeblokk i parameter-JSON**  
Hver parameterfil får en `sources`-liste:
```json
"sources": [{
  "title": "WMA Rulebook Appendix B – Scoring of WMA Combined Events (2023)",
  "publisher": "World Masters Athletics",
  "official_page": "https://www.friidrett.no/aktiviteter/masters/poengberegning/",
  "document_url": "https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-WMA-Appendix-B.pdf",
  "local_copy": "kilder/masters/2023-WMA-Appendix-B.pdf",
  "sha256": "c3d5baa5…",
  "retrieved": "2026-09-26",
  "section": "s. 2, Parameters"
}]
```
*Ferdig når:* Tyrving-JSON også har en kildeblokk, og et skjema-test feiler hvis `official_page` eller `document_url` mangler.

**PS-002 Kilder i API-et**  
`GET /api/v1/systems` og hver `calculation_steps`-oppføring viser til kilden (`source_ref`). Frontend viser «Kilde: NFIF – Poengberegning masters» med lenke.  
*Ferdig når:* Hver beregning i UI-et har en klikkbar lenke til NFIF-siden.

**PS-003 Kildemappe i repoet**  
NFIF- og WMA-filene ligger i `sources/` med SHA-256, slik som Tyrving. WA-PDF-ene sjekkes ikke inn, fordi de har forbehold mot kopiering (B-23). Combined Events trenger dem ikke: parametrene står i WMA Appendix B, og fasiten er NFIF-tabellene. *Ferdig 2026-09-26.*

### Fase 1 – WA Combined Events

**PS-010 Parametre**  
Lag `wa_combined_events_2001.json` med alle øvelsene fra Appendix B s. 2 (16 for menn, 15 for kvinner), pluss enhet (s/cm/m) og formeltype.  
*Ferdig når:* Hver parameter har `source.section`.

**PS-011 `CombinedEventsCalculator`**  
Tre formeltyper og avkorting. Input i s/cm/m. Håndtid tas inn som eget flagg. Ingen korrigering i system A, men flagget brukes i B.  
*Ferdig når:* Enhetstestene dekker både avkorting og 0 poeng når resultatet er dårligere enn b.

**PS-012 Verifisering mot IAAF-PDF**  
Hent ut utvalgte rader fra `IAAF-Scoring-Tables-for-Combined-Events.pdf` med pdftotext (minst 20 per øvelse, spredt over skalaen) og bruk dem som fasit.  
*Ferdig når:* Null avvik.

**PS-013 Verifisering mot NFIF-regnearkene («Sr»-kolonnen)**  
Seniorkolonnen i NFIFs masters-mangekamptabell er system A. Bruk hele kolonnen (1–1200) som fasit.  
*Ferdig når:* Null avvik for alle øvelser som finnes i begge kildene.

**PS-014 Mangekamp-summering**  
`POST /api/v1/combined` tar en liste med øvelser og resultater og returnerer poeng per øvelse og sum. Definer standardøvelser for femkamp, sjukamp og tikamp.  
*Ferdig når:* Resultatsiden fra 25.09 kan regnes ut på nytt, og avrundingsfeilene der blir synlige.

### Fase 2 – Masters mangekamp

**PS-020 Aldersfaktorer**  
Lag `wma_ce_age_factors_2023.json` fra Appendix B (5-årsklasser 35–110, begge kjønn, alle øvelser).  
*Ferdig når:* Faktorene er lest ut maskinelt og kontrollert manuelt mot PDF-en for tre klasser.

**PS-021 Redskapskatalog per klasse**  
Kartlegg rad «Vekt:» og hekkehøyder fra NFIF-arkene. Lag `masters_implements.json` som viser hvilket redskap som gjelder for hver klasse og hvilken kolonne i arket det tilsvarer.

**PS-022 `MastersCombinedCalculator`**  
Rekkefølge: håndtidskorreksjon → × faktor → avrunding (løp opp, hopp og kast ned) → system A → avkorting. Alle trinnene vises i `calculation_steps`.  
*Ferdig når:* Eksemplene i Appendix B stemmer: M50 100 m 13,12 gir 681 poeng, og W35 høyde 1,47 gir 621 poeng.

**PS-023 Verifisering mot NFIF-regnearkene**  
Bruk hele oppslagstabellen (alle ark, alle klasser, 1–1200 poeng) som fasit. Merk at arket viser *laveste resultat for hvert poengtall*, så testen må kjøres som «resultat → poeng».  
*Ferdig når:* Null avvik. Eventuelle avvik i slegge og vektkast dokumenteres og tas opp med NFIF.

**PS-024 Øvelser utenfor WMA-listen**  
Sjekk 60/100/400/1000 m og vektkast mot arkene. Hvis NFIF bruker egne parametre, legges de inn med NFIF-regnearket som kilde.

### Fase 3 – WMA Age Grading, individuelt

**PS-030 Ettårige faktorer**  
Hent ut de ettårige aldersfaktorene fra `2023-Age-Factors-WMA.pdf` (16 s.) til JSON.

**PS-031 Aldersjustert resultat**  
Beregn resultat × faktor. Sjekk først om PDF-en inneholder standarder («open standards») slik at vi kan regne ut prosent. Hvis den ikke gjør det, leverer fase 3 bare det aldersjusterte resultatet, og prosent utsettes.

### Fase 4 – Serietabeller (blokkert)

**PS-040 Henvendelse til NFIF** *(start nå. Samlet med Tyrving-avvikene i `docs/henvendelser/2026-09-26-nfif-tyrving-avvik.md`, og lagt i Gmail som utkast)*  
Be om: (1) den offisielle serietabellen for senior, som fil eller formel med parametre og gjeldende utgave, (2) bekreftelse på hvordan masters-serien er bygget opp (hypotesen i 1.4), og (3) tillatelse til å vise til dokumentene i et åpent API.  
Mottaker: NFIF (friidrett@friidrett.no) og masterskomiteen.

**PS-041 Reserveløsning**  
Hvis NFIF ikke har noen fil: be om tillatelse fra dem som drifter minfriidrettsstatistikk.info, hent ut stikkprøver og tilpass parametre. Merk tydelig: «Kilde: minfriidrettsstatistikk.info (ikke offisielt NFIF-dokument)».

**PS-042 / PS-043** `SerietabellCalculator` og `MastersSerietabellCalculator`, med de fasitene som finnes.

**PS-044 Utvidet sammenligning mot kalkulatoren** *(når fase 1–2 er ferdige)*  
Kjør skriptet fra 26.09 på nytt med flere punkter per øvelse, og sammenlign med *våre* motorer (Combined Events og masters) i stedet for regnearkene. Sjekk også om «Sr»-kolonnen i masters-serietabellen er en eldre utgave av senior-serietabellen. Begrens antall innsendinger og samle alle øvelser i hver.

**PS-045 Serietabell som egen funksjon på siden**  
Når vi har en kilde: en egen «Seriepoeng»-kalkulator for senior (uten alder), med lenke til NFIF-kilden. Kan senere kobles til lagserie-summering.

### Fase 5 – WA Scoring Tables 2025

**PS-050** Juridisk vurdering: kan vi publisere koeffisienter tilpasset en PDF med forbehold om kopiering?  
**PS-051** Hent ut tabellene med pdftotext og tilpass `a·(x+b)²+c` per øvelse.  
**PS-052** Verifiser mot alle rader. *Ferdig når:* Null avvik.

---

## 4. Tverrgående tiltak

- **Enhetlig avrundingsmodul.** Tyrving, WA CE og masters har ulike regler: avkorting, «løp opp / hopp og kast ned» og håndtidskorreksjon. Samle dem i én modul med navngitte regler, slik at `calculation_steps` kan vise hvilken regel som ble brukt.
- **Resultatparser.** Resultatsiden viste at formater som «2:45:9» og lengdeserier («5.17 (…») skaper feil. Lag en felles parser som godtar norske formater (1.45,8 / 1:45.8 / 105.8) og avviser tvetydige verdier med en tydelig feilmelding.
- **`version` per system (B-5):** `wa_combined_events@2001`, `wma_ce_factors@2023`, `wma_age_factors@2023`, `tyrving@2014`.
- **Oppdateringsrutine.** Et skript kjører `kilder/.dl.tsv` på nytt hver måned og varsler når SHA-256 endrer seg.

---

## 5. Beslutninger (tatt 26.09.2026)

1. **Ny rekkefølge:** WA CE → masters mangekamp → age grading → serietabeller → WA 2025. *Besluttet (B-22).*
2. **Kildefiler:** NFIF og WMA i `sources/`, WA utenfor repoet. *Besluttet (B-23).*
3. **Henvendelse til NFIF:** Slått sammen med Tyrving-avvikene til én e-post (`docs/henvendelser/`). Simen sender den (AP-026).
4. **Rettelser:** `BESLUTNINGER.md` (kap. 3, B-18 og B-22 til B-26) og `TEKNISK_FORSLAG_v2.1.md` (kap. 0.1, 1.3, 3.2 og 3.4) er oppdatert på stedet, både i Cowork-mappen og i `docs/` i repoet. Det er ikke laget en ny v2.2.

---

## 6. Åpne spørsmål — undersøkt 26.09.2026

Svarene og valgene står i `docs/BEREGNINGSVALG.md`. Kort oppsummert:

| Spørsmål | Svar | Status |
|---|---|---|
| Hvordan er senior-serietabellen bygget opp? | Ukjent. Avviker fra alle kjente tabeller og passer ikke en enkel potensformel. Spurt NFIF (AP-026). Reserve: tilpasse parametre (AP-028). | BV-050, antakelse |
| Er masters-serien «mangekamptabell + serieark»? | Sannsynlig: arkene dekker nøyaktig øvelsene som mangler i mangekamptabellen. Spurt NFIF. | BV-051, antakelse |
| Hvilke slegge- og vektkastparametre ligger bak «nye seniortabeller»? | Parametrene i WMA Appendix B. Seniorkolonnen stemmer for alle 1200 rader, begge kjønn. Kontrollen fant i stedet et avvik for manuell tid på 60 m (+0,20 s mot +0,24 s). | BV-022, BV-024 |
| Har 2023 Age Factors-PDF-en standarder for prosent? | Nei, bare faktorer. AP-014 leverer aldersjustert resultat uten prosent. | BV-041 |
| Skal ungdom 15–19 bruke mangekamptabellen? | Ja. UM-reglementet 2026 §16.5 sier internasjonale tabeller, og gir NFIFs egne koeffisienter for 600 m, 800 m inne, 80 m og 100 m hekk. Tyrving-motoren avviser allerede mangekamp fra 15 år. | BV-015, BV-021, BV-023 |
