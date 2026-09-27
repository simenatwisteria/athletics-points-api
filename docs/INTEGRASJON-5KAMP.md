# Integrasjon med 5KAMP — plan

**Dato:** 2026-09-27 (Cowork). Grunnlag for AP-020 (kontrakten) og for oppgaven 5K-012 i 5KAMP-repoet.
Lest fra `CODE/5KAMP` uten endringer i koden der.

## Hvordan 5KAMP virker i dag

- React/Vite-app på Vercel (`5kamp.minfriidrett.no`) med Supabase som database. **Ingen egen backend.**
- Funksjonærer taster resultater på mobil (`/mobile-input`). Storskjermen (`/display`) oppdateres live.
- **Poengene tastes inn manuelt.** Funksjonæren slår opp i NFIFs tabeller og skriver poengene i et eget felt
  (`src/types/pentathlon.ts`, `usePentathlon.updateEventResult(…, 'points', …)`). Resultatsiden fra 2026-09-25 viste
  hva det koster: poengene i lengde passet ikke med hoppet som ble vist, og avrundingen varierte.
- Øvelser: lengde, spyd, diskos, 200 m, og 1500 m (menn/gutter) eller 800 m (kvinner/jenter). Kategorier
  `men`, `women`, `boys`, `girls`. Deltakeren har fødselsår.
- Neste stevne: **2026-10-03**. 5KAMP har **frys fra og med 2026-10-01**, og ingenting merges før 2026-10-04 uten at
  det retter en feil som ville ødelagt stevnet (`docs/SERIE-robusthet.md` i 5KAMP).

## Endret plan 2026-09-27: automatisk poeng før stevnet, lokalt i 5KAMP

Simen vil ha automatisk poengberegning på stevnet 2026-10-03, og har bekreftet at **senior-tabellen og seniorutstyr
brukes for alle deltakere**. Da er beregningen bare fem øvelser per kjønn med WA Combined Events. Den legges direkte
i 5KAMP som en liten, testet modul (5K-012 i 5KAMP), i stedet for å gå via API-et:

- Ingen avhengighet av nett eller ny tjeneste på stevnedagen.
- Kan merges før frysen 2026-10-01. API-et rekker ikke å bli deployet og koblet på innen da.
- Modulen testes mot 10 685 verdier fra NFIFs tabell og mot de 75 resultatene fra forrige stevne. Fasiten er laget
  herfra (B-28).

**Kontroll av forrige stevne (2026-09-27):** 18 av 75 poengtall var én for høye (poengene var rundet opp i stedet
for ned), og Tobias fikk poeng for 4,50 i lengde i stedet for beste hopp 4,60 (290 mot 308). Rekkefølgen i
resultatlista ble ikke påvirket.

API-koblingen under gjelder fortsatt, men nå **etter** stevnet, og da som kontroll og for flere tabeller.

## Slik blir koblingen (5K-012, etter stevnet)

1. **Kall fra nettleseren.** 5KAMP har ingen backend, så appen kaller API-et direkte. API-et må tillate CORS fra
   `https://5kamp.minfriidrett.no` (og Vercel-previews hvis ønsket). Ingen nøkkel trengs i v1 (B-4), men IP-grensen
   må tåle et stevne (få hundre kall).
2. **Når et resultat lagres,** kaller appen `POST /api/v1/calculate` og fyller inn poengfeltet. Funksjonæren kan
   fortsatt overstyre. Svarer ikke API-et innen noen sekunder, tastes poengene manuelt som i dag, med en tydelig
   melding. Stevnet skal aldri stoppe fordi API-et er nede.
3. **Lagre hvor poengene kom fra:** `points_source` (`api` / `manual`) og `scoring_system` + `version`. Det krever en
   migrasjon i Supabase og er et 🔴-punkt i 5KAMP (Simen godkjenner).
4. **Knapp i admin: «Regn ut alle poeng på nytt»** med liste over avvik før noe skrives. Samme kall, brukt på hele
   stevnet. Det er også kontrollen av gamle stevner.
5. **Tabellvalg per deltaker** (må avgjøres av Simen før 5K-012 skrives):
   - 15 år og eldre: WA Combined Events (BV-021).
   - Under 15 år: Tyrving, med redskapet for alderen. Krever at 5KAMP vet hvilket redskap som ble brukt.
   - 35 år og eldre: senior-tabellen for alle, eller masters-tabellen (aldersjustert)? Vanlig i klubbstevner er
     senior-tabellen for alle.

**Øvelsesmapping** (5KAMP → API): `long_jump` → `long_jump`, `javelin` → `javelin`, `discus` → `discus`,
`200m` → `sprint_200m`, `1500m` → `middle_1500m`, `800m` → `middle_800m`. Kjønn: `men`/`boys` → `M`,
`women`/`girls` → `F`.

**Resultatet:** 5KAMP lagrer resultatet som tekst (for eksempel en hoppserie). v1 av koblingen sender det beste
resultatet som tall. Senere kan tolkningen i API-et (B-27) ta imot teksten direkte.

## Hvem gjør hva

| Steg | Hvor | Hvem | Når |
|---|---|---|---|
| Kontrakten tar med 5KAMPs behov (CORS, enkeltberegning, mangekamp, tabellvalg per alder) | AthleticsPointsCalc, AP-020 | Claude Code | Nå |
| Godkjenne kontrakten | AP-036 | Simen, etter Coworks gjennomgang | Nå |
| Implementere og deploye API-et | AP-021, AP-022 | Claude Code + Simen (Railway) | Før 2026-10-04 |
| Etterkontroll av stevnet 2026-10-03 | Cowork | Cowork | 2026-10-03/04 |
| Oppgavefil 5K-012 i 5KAMP, basert på den godkjente kontrakten | 5KAMP `docs/active/` | Cowork | Etter AP-036 |
| Koblingen i 5KAMP | 5KAMP | Claude Code i 5KAMP-repoet | Fra 2026-10-04 |

Claude Code i 5KAMP trenger ikke tilgang til dette repoet. Den trenger oppgavefila, URL-en til API-et og
OpenAPI-spesifikasjonen (`docs/api/openapi.yaml` herfra, kopiert inn i oppgavefila eller lenket fra GitHub).
