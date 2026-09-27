# Backlog — Athletics Points API

Eneste sanne oversikt over utviklerarbeid. Det finnes ingen egen `LOOP.md`: loopen jobber seg gjennom denne fila.
Eies av Cowork sammen med Simen. **Claude Code oppretter ikke nye oppgaver her** — funn skrives under «Innboks»
nederst. Code oppdaterer bare `Status` og notatet på oppgaven den jobber med.

**ID-serie:** `AP-001`, `AP-002`, … Neste ledige: **AP-032**

**Eier:** 🤖 Code (kan tas av agenten/loopen) · 🧑 Simen (legges i Todoist, agenten hopper over)

**Status:** `Ny` → `Klar` (oppgavefil finnes i `docs/active/`) → `Under arbeid` → `Venter på Simen` → `Ferdig`
(oppgavefil flyttes til `docs/ferdig/`). `Blokkert` = agenten mistenker feil fasit eller uklar regel, har skrevet
hvorfor i notatet, og har stoppet.

**Regel for agenten:** ta øverste oppgave med eier 🤖 og status `Klar` eller `Ny` der alle avhengigheter er
`Ferdig`. Står en 🧑-oppgave den avhenger av åpen, hopp videre — ikke gjør Simens oppgave.

---

## Now — grunnmur og Tyrving 2014

| # | ID | Oppgave | Eier | Avhenger av | Status | Fil |
|---|---|---|---|---|---|---|
| 1 | AP-001 | Grunnmur: `models.py`, abstrakt `engine.py`, `registry.py` | 🤖 | — | **Ferdig** | `ferdig/AP-001-grunnmur.md` |
| 2 | AP-002 | Tyrving: parameterekstraksjon Excel → `data/tyrving_parameters_2014.json` (560 kombinasjoner) + test mot Excel-celler | 🤖 | AP-001 | **Ferdig** (PDF vinner, 3 rader rettet — `KILDEAVVIK.md`) | `ferdig/AP-002-tyrving-parametre.md` |
| 3 | AP-003 | Installer LibreOffice (`brew install --cask libreoffice`) så `soffice` finnes i PATH | 🧑 | — | **Ferdig** (LibreOffice 26.8.0.3, 2026-09-25) | — |
| 4 | AP-004 | Tyrving: oracle-skript `scripts/oracle_tyrving.py` — rekalkulerer regnearket med LibreOffice headless og skriver `tests/fixtures/tyrving_cases.json` (2472 caser) | 🤖 | AP-002, AP-003 | **Ferdig** | `ferdig/AP-004-tyrving-oracle.md` |
| 5 | AP-005 | **Review** Tyrving-fixtures: stikkprøve 10–20 caser mot PDF-tabellen, godkjenn og lås | 🧑 | AP-004 | **Ferdig** 2026-09-26 — fasiten er låst | `ferdig/AP-005-review-tyrving-fixtures.md` |
| 6 | AP-006 | Tyrving: regeltolkning fra DOC/PDF (80 %-grense, manuell tidtaking, avrunding) som eksplisitte testcaser i `tests/fixtures/tyrving_rules.json` med kildehenvisning per case | 🤖 | AP-001 | **Ferdig** (29 caser, 3 åpne spørsmål) | `ferdig/AP-006-tyrving-regeltolkning.md` |
| 7 | AP-007 | **Review** regeltolkningen i AP-006 mot DOC/PDF, godkjenn og lås | 🧑 | AP-006 | **Ferdig** 2026-09-26 — regeltolkningen er låst | `ferdig/AP-007-review-regeltolkning.md` |
| 8 | AP-008 | Tyrving: `TyrvingCalculator` (simple_quotient, three_interval, edge cases) grønn mot låste fixtures | 🤖 | AP-002, AP-005, AP-007 | **Ferdig** 2026-09-26 | `ferdig/AP-008-tyrving-calculator.md` |
| 9 | AP-009 | Tyrving: mangekamp u/15 (summering av Tyrving-poeng) | 🤖 | AP-008 | **Ferdig** 2026-09-26 (generell summering) | `ferdig/AP-009-tyrving-mangekamp.md` |

## Next — kildesporing, mangekamp og masters (rekkefølge besluttet 2026-09-26, B-22)

Combined Events avhenger ikke av WA Scoring 2025. Parametrene står i WMA Appendix B, og fasiten er seniorkolonnen
i NFIFs masters-tabeller. Bakgrunn: `docs/PLAN_FLERE_POENGSYSTEMER.md`.

| # | ID | Oppgave | Eier | Avhenger av | Status | Fil |
|---|---|---|---|---|---|---|
| 10 | AP-026 | Send e-posten til NFIF (Tyrving-avvik, serietabellen og masters-serien): `docs/henvendelser/2026-09-26-nfif-tyrving-avvik.md`. Oppdater «Status overfor NFIF» i `KILDEAVVIK.md` | 🧑 | — | Ny — utkast ligger i Gmail | — |
| 11 | AP-010 | Last ned WA Combined Events og Scoring Tables 2025 | 🧑 | — | **Ferdig** 2026-09-26 — lastet ned, men ikke sjekket inn (B-23), se `sources/wa/README.md` | — |
| 12 | AP-013 | Last ned WMA Appendix B og Age Factors 2023 til `sources/wma/` | 🧑 | — | **Ferdig** 2026-09-26 | `sources/README.md` |
| 13 | AP-015 | Last ned NFIF masters mangekamp- og serietabeller til `sources/masters/` | 🧑 | — | **Ferdig** 2026-09-26 | `sources/README.md` |
| 14 | AP-027 | Kildesporing: `source_documents` i parameter-JSON og `ref` (BV-nummer eller kilde) i beregningsstegene, også Tyrving. Test at alle BV-numre i koden finnes i `docs/BEREGNINGSVALG.md` (B-24) | 🤖 | AP-001 | **Ferdig** 2026-09-26 | `ferdig/AP-027-kildesporing.md` |
| 14b | AP-030 | Fyll inn `document_url` for Tyrving-DOC-ene og `.xls` i `meta.source_documents` fra lenkene i `sources/README.md` (lagt inn 2026-09-26). PDF-ene og `.xlsx` beholder `null`. Kjør `extract_tyrving_params.py` på nytt og vis at bare `meta` endres | 🤖 | AP-027 | **Ferdig** 2026-09-26 (`.xls` lagt til som sjette dokument) | `ferdig/AP-030-document-url.md` |
| 15 | AP-012 | WA Combined Events: parametre fra Appendix B s. 2 (menn 16, kvinner 15 øvelser + kvinner 1500 m), NFIFs UM-tillegg (600 m, 800 m inne, 80/100 m hekk), fasit fra «Sr»-kolonnen i `sources/masters/` (null avvik), summering | 🤖 | AP-001, AP-013, AP-015, AP-027 | **Ferdig** 2026-09-26 (null avvik mot 30 482 rader; fixture ulåst, venter på Simens stikkprøve) | `ferdig/AP-012-wa-combined-events.md` |
| 16 | AP-016 | Masters mangekamp: håndtidskorreksjon → resultat × aldersfaktor (5-årsklasse) → avrunding (løp opp, hopp/kast ned) → Combined Events. Fasit er hele NFIF-tabellen, null avvik (B-25). Eksemplene i Appendix B som enhetstester. Kartlegg redskap per klasse fra raden «Vekt:» | 🤖 | AP-012, AP-013, AP-015 | **Ferdig** 2026-09-27 (null avvik mot 427 750 rader; fixture ulåst, venter på Simens stikkprøve) | `ferdig/AP-016-masters-mangekamp.md` |
| 16b | AP-031 | **Review** WA Combined Events-fasit: stikkprøve de 10 casene i sluttrapporten til AP-012 (`ferdig/AP-012-wa-combined-events.md`) mot NFIF-arket, godkjenn og lås `tests/fixtures/wa_combined_events_cases.json` | 🧑 | AP-012 | Ny | — |
| 17 | AP-014 | WMA Age Grading 2023: ettårige faktorer fra `wma-2023-age-factors.pdf`. Aldersjustert resultat, ikke prosent (BV-041). Fixtures krever Simens review | 🤖 | AP-001, AP-013, AP-027 | Klar | `active/AP-014-wma-age-grading.md` |
| 18 | AP-028 | Serietabellen: utvidet sammenligning mellom kalkulatoren på minfriidrettsstatistikk.info og våre motorer (flere punkter per øvelse, få innsendinger). Grunnlag: `docs/SERIETABELL_SAMMENLIGNING_2026-09-26.md` | 🧑 (Cowork) | AP-012, AP-016 | Klar | `active/AP-028-serietabell-sammenligning.md` |

## API og frontend — rekkefølge besluttet 2026-09-26

Kontrakten først, så API, så frontend (B-1, B-9). Kontrakten bygger på skissen (`docs/DESIGN.md` kap. 7) og på
bruken fra minfriidrett.no, som sjekkes før kontrakten låses.

| # | ID | Oppgave | Eier | Avhenger av | Status | Fil |
|---|---|---|---|---|---|---|
| 19 | AP-025 | Lagre skissen i repoet (`docs/design/`) og skriv `docs/DESIGN.md` | 🤖 | — | **Ferdig** 2026-09-26 | `docs/DESIGN.md` |
| 20 | AP-020 | API-kontrakt: OpenAPI-spesifikasjon (`/systems`, `/events`, `/calculate`, mangekamp, batch og tolkning for minfriidrett.no, `/health`). Simen godkjenner før implementasjon | 🤖 | AP-025, `docs/INTEGRASJON-minfriidrett.md` | Ny — venter på svar om hvor tolkningen skal ligge | — |
| 21 | AP-021 | API-implementasjon: FastAPI rundt pakken, tester mot kontrakten, rate limiting (B-4), cache (B-7) | 🤖 | AP-020 | Ny | — |
| 22 | AP-022 | Deploy API på Railway (`/health` først) | 🤖 + 🧑 | AP-021 | Ny | — |
| 23 | AP-023 | Frontend: React/Vite etter `docs/DESIGN.md`, kaller API-et, norsk og engelsk. Styrte økter, ikke loop | 🤖 + 🧑 | AP-020 | Ny | — |
| 24 | AP-024 | Deploy frontend på Vercel | 🤖 + 🧑 | AP-022, AP-023 | Ny | — |

## Later — ikke i loop

| ID | Oppgave | Status | Notat |
|---|---|---|---|
| AP-018 | FastAPI-wrapper, deploy på Railway, frontend på Vercel | **Erstattet** 2026-09-26 | Delt opp i AP-020–AP-025 (se «API og frontend» over). |
| AP-019 | Serietabellen / Seriepoeng (Lagserien), senior og masters | Venter på NFIF (AP-026) | B-26. Ingen offisiell fil. Kalkulatoren på minfriidrettsstatistikk.info avviker fra alle kjente tabeller (`docs/SERIETABELL_SAMMENLIGNING_2026-09-26.md`). Reserveløsning: tilpasse parametre med tillatelse. |
| AP-029 | Seriepoeng som egen funksjon i frontenden (senior, uten alder), med lenke til kilden | Ny | B-26. Avhenger av AP-019. |
| AP-011 | WA Scoring Tables 2025: parametre tilpasses fra PDF-tabellen (`a·(x+b)²+c`), verifisering mot alle rader | Ny — flyttet hit 2026-09-26 | Eget system, ikke mangekamp. Krever vurdering av WA sitt forbehold mot kopiering før publisering (B-23). |

---

## Innboks — funn fra Claude Code, ikke prioritert

Code skriver hit. Cowork tømmer lista og prioriterer inn i Now/Next/Later.

- **`sources/tyrving/tyrving-2014-redigerbar.xlsx` er ikke NFIFs gjeldende fil** *(verifisert 2026-09-25)*
  Sist lagret av Simen 2024-06-28, har inntastede resultater og mangler NFIFs retting fra 2018. Simen bør laste ned
  gjeldende regneark fra friidrett.no og erstatte den, eller rette opprinnelsen i `sources/README.md` (agenten
  endrer ikke `sources/`). Parametrene og fasiten påvirkes ikke, fordi PDF-en vinner.

- **Faste mangekamper per klasse mangler** *(AP-009, forslag til 🧑-oppgave)*
  Motoren summerer fritt valgte øvelser. For at frontenden skal kunne tilby «Femkamp J13» osv., trengs NFIFs
  oversikt over hvilke mangekamper (og øvelser) som gjelder for hvilke klasser under 15 år. Legges inn som data.

- **Klikkbar skisse, versjon 2** *(2026-09-26, til AP-018)*
  Skissen har en startside med alle tabellene (Tyrving, WA, WA mangekamp, Serietabellen, WMA, masters
  mangekamp), valg mellom norsk og engelsk, og et kompakt iOS-skjema med nedtrekksmenyer for klasse, øvelse og
  utstyr. Det gir tre krav til API-et:
  1. `GET /systems` må gi navn og beskrivelse på norsk og engelsk, gruppe (ungdom/senior/masters), om tabellen
     er klar, klassetype (alder/klasse/masters), klasseliste og om mangekamp støttes.
  2. Øvelsesnavn må finnes på norsk og engelsk (en felles øvelseskatalog), og kategorien (løp, hekk, kappgang,
     hopp, kast) brukes til å gruppere menyene.
  3. Tall formateres etter språk (komma på norsk, punktum på engelsk). Poengberegningen påvirkes ikke.

- **LibreOffice-tester hoppes over i CI** *(AP-002, AP-004)*
  `test_xls_has_same_parameters` og `test_fixture_is_reproducible` krever `soffice` og er `skip` i GitHub
  Actions. Lokalt kjører de. Vurder `apt-get install libreoffice-calc` i CI (koster ca. 1–2 min per kjøring).

- **Kvinner `100m-m` i masters-mangekamparket mangler klassen i kolonne P** *(AP-016, 2026-09-27)*
  Kolonne P har poeng i rad 138–359 (222 celler), men rad 2 er tom. Lest som W100 gir motoren samme poeng i
  alle 222 radene, så det ser ut som en manglende overskrift. Kolonnen er utelatt fra fasiten og listet i
  fixturens `meta`. Forslag: før det i `KILDEAVVIK.md` og ta det med i e-posten til NFIF (AP-026).

- **Masters-fixturen er 25 MB** *(AP-016)*
  `tests/fixtures/masters_combined_events_cases.json` har 427 750 caser, én per linje. Git og GitHub tåler det,
  men klonen blir større. Vurder før låsing (AP-016-review) om fasiten heller skal genereres i CI, eller om
  `result`-objektet kan utledes fra teksten i arket.

- **Lås masters-fixturen** *(AP-016, forslag til 🧑-oppgave)*
  Stikkprøv de 10 casene i `ferdig/AP-016-masters-mangekamp.md` mot NFIF-arkene, godkjenn og lås
  `tests/fixtures/masters_combined_events_cases.json`, slik AP-031 gjør for WA Combined Events.

---

## Beslutningslogg

Datert, kort. Hvorfor noe ble valgt — ikke hva som ble gjort (det står i git).

- **2026-09-25** — Repo `simenatwisteria/athletics-points-api` (public, MIT) klonet til `CODE/AthleticsPointsCalc`. Navnene er bevisst forskjellige. Én klone, ett repo (B-19-forslag i ANALYSE).
- **2026-09-25** — Backloggen følger formatet fra `5KAMP/docs/BACKLOG.md`. `godkjennutlegg` har backloggen sin i Google Drive, ikke i repoet, så 5KAMP var nærmeste mal i `CODE/`. Ingen egen `LOOP.md`.
- **2026-09-25** — Fasit genereres alltid fra `sources/` av separate oracle-skript, aldri fra motoren, og er skrivebeskyttet for agenten (B-20-forslag). Review av fixtures og regeltolkning er Simens oppgave, fordi loopen bare kan bevise «koden matcher fasiten», ikke «fasiten er riktig».
- **2026-09-25** — Kildefiler med SHA-256 i `sources/SHA256SUMS`, så endringer i fasit-grunnlaget er synlige i diff og kan sjekkes med én kommando.
- **2026-09-25** — **PDF vinner ved konflikt mellom Tyrving-kildene** (Simen). Forsiden i regnearket kaller
  PDF-en den offisielle utgaven. Kryssjekk av alle 560 kombinasjoner fant tre regnearkfeil; de er rettet i data
  og fasit, men aldri i `sources/`. Register: `docs/KILDEAVVIK.md`.
- **2026-09-25** — **Grunnlaget er NFIFs offisielle tabell, publisert som DOC på friidrett.no.** DOC-filene i
  `sources/` er byte-identiske med Simens nedlasting samme dag. PDF-ene har ukjent opphav, men identisk innhold, og
  brukes videre av koden fordi de kan leses uten LibreOffice. Ingen tall endres. NFIFs gjeldende `.xls` avviker
  fra tabellen på to rader (G19 2000 m, J17 kule).
- **2026-09-26** — **Rimelig område per øvelse** (`InputSpec.plausible_min/max`, `ScoreResult.within_plausible_range`):
  0,6–3,0 × 1000p-nivået for tid og 0,2–1,6 × for distanse. Det er brukerhjelp, ikke regel: frontenden viser ikke
  poeng utenfor området, fordi resultatet trolig er halvveis tastet inn. Motoren beregner poeng uansett. Kom fra
  tastatur-skissen, der sifre fylles inn fra høyre (1-0-9 = 1,09 s gir 2711 poeng underveis).
- **2026-09-26** — **Regeltolkningen er låst (AP-007).** Tillegg for manuell tid gjelder etter distanse, også for hekk.
  Løp fra 600 m og oppover får ingen tillegg. Manuell tid på 40 m avvises. Resultat 0 eller et manglende resultat
  avvises, mens negativ poengsum for et gyldig resultat gir 0.
- **2026-09-26** — **Tyrving-fasiten er låst (AP-005).** Kvalitetssikret mot Rjukan IL sin Tyrvingkalkulator: 2419 av
  2432 sammenlignbare caser er identiske, og resten er forklart av feil på nettsiden. **Motoren regner eksakt**
  (desimal), fordi regelteksten sier at alle desimaler beholdes. Flyttallskanten testes mot `points_if_exact`.
  **Hundredeler strykes i løp over 500 m**, slik regelteksten sier.
- **2026-09-25** — Masters mangekamp: NFIF-tabellen er fasit (lookup), WA × WMA brukes bare til kryssverifisering. Det er NFIF som publiserer tabellen som faktisk brukes.
- **2026-09-26** — **Ny rekkefølge etter Tyrving (B-22):** kildesporing → WA Combined Events → masters mangekamp →
  WMA Age Grading → serietabeller → WA Scoring 2025. Combined Events trenger ikke WA 2025: parametrene står i WMA
  Appendix B, og seniorkolonnen i NFIFs masters-tabeller er fasit. Erstatter B-21-forslaget. AP-011 flyttet til Later.
- **2026-09-26** — **Kildefiler (B-23):** NFIF- og WMA-filer lagt i `sources/` (Cowork på vegne av Simen, AP-013 og
  AP-015). WA-PDF-ene sjekkes ikke inn fordi de har forbehold mot kopiering.
- **2026-09-26** — **Masters mangekamp (B-25):** Beslutningen fra 2026-09-25 står, NFIF-tabellen er fasit. Motoren
  regner etter WMA Appendix B og skal gi null avvik. Stikkprøver stemmer eksakt.
- **2026-09-26** — **Serietabellen (B-26):** Ingen offisiell kilde. Stikkprøver (265 resultater) viser at
  kalkulatoren avviker fra mangekamptabellen, masters-tabellene og WA 2025. Venter på NFIF (AP-026).
- **2026-09-26** — Innboks tømt for «Meld avvikene til NFIF» og «hundredeler i lange løp». Begge er med i den samlede
  e-posten (AP-026).
- **2026-09-26** — **Beregningsvalg samlet i `docs/BEREGNINGSVALG.md`** (BV-numre vises i `calculation_steps`).
  Åpne spørsmål undersøkt av Cowork: slegge og vektkast stemmer med Appendix B; NFIFs masters-ark bruker +0,20 s
  på 60 m manuell mot +0,24 s i IAAF og WMA (vi følger +0,24, BV-024, `KILDEAVVIK.md`); Age Factors-PDF-en har
  ingen standarder, så AP-014 leverer aldersjustert resultat uten prosent (BV-041); UM-reglementet §16.5
  bekrefter internasjonale tabeller fra 15 år og gir NFIFs egne koeffisienter (BV-021, BV-023).
- **2026-09-26** — Oppgavemalen oppdatert etter Anthropics råd for Opus 5.5 og Claude Code (les først, kontrolltall,
  stoppregler, bevis i sluttrapporten). Oppgavefiler skrevet for AP-027, AP-012, AP-016, AP-014 og AP-028.
- **2026-09-26** — AP-027 gjennomgått av Cowork: godkjent. Innboks-funnet om manglende lenker løst ved at lenkene er ført inn i `sources/README.md`; utfyllingen i JSON er AP-030.
- **2026-09-26** — **AP-016 avblokkert.** 80 m hekk manuell følger +0,24 s som 60 m (BV-024, anbefalt av Cowork). Forskjøvne celler i menn 200 m M90–M100 hoppes over i fasiten, ikke reparert (BV-035). Begge ført i `KILDEAVVIK.md` og tatt med i e-posten til NFIF.
- **2026-09-26** — AP-012 gjennomgått av Cowork: godkjent (30 482 caser, null avvik). Innboks tømt: låsing av fixturen er AP-031 (🧑), og kontrolltall for kvinner 100 m hekk senior fra IAAF-boka er lagt til AP-016.
