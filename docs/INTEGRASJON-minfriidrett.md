# Integrasjon med minfriidrett.no — funn som styrer API-designet

**Dato:** 2026-09-26. Grunnlag for API-kontrakten (AP-020). Lest fra `CODE/minfriidrett` og `CODE/5KAMP`, uten endringer
der. Ingen persondata er kopiert hit: eksemplene er øvelses-, klasse- og resultatformater.

## Hvordan resultatene kommer inn

- minfriidrett.no (FastAPI/Python på Railway, Firestore) henter resultater fra **Liveres** (én JSON per stevnedag) og
  **OpenTrack** (ett dokument per øvelse, runde og heat), og skraper **minfriidrettsstatistikk.info**.
- Resultatene kommer alltid **samlet per stevnedag eller øvelse**. Store stevner har 1000–1250 resultater. Under
  stevnet blir samme øvelse hentet på nytt ved hver endring (minst hvert 10. sekund).
- Kall til oss vil gå **fra server til server** fra minfriidretts worker-tjeneste, ikke fra nettleseren.
- Historisk etterfylling er planlagt for ca. **1,4 millioner resultater**.
- minfriidrett har i dag en egen Tyrving-kalkulator. Konstantene ligger bare i Firestore, og kalkulatoren brukes ikke
  på innkomne resultater. Den bør erstattes av dette API-et, så det bare finnes én kilde.

## Formatene som må tolkes

| Felt | Liveres | OpenTrack | minfriidrettsstatistikk |
|---|---|---|---|
| Øvelse | `Kule G-15 (4,0kg)`, `60 m hekk G-17 (91,4 9,14m)`, `Spyd KS (600gr)` | `MU20 Kule 6,0kg`, `KU20 100 meter hekk 84,0cm`, eventkode `SP`, `100H` | `Kule 4,0kg`, `200 meter hekk (76,2cm)` |
| Klasse (utøver) | `G-15`, `J-18-19`, `MS`, `U23 Menn`, `Para-T37` | `G15`, `J18/19`, `U23M`, `M60`, i tillegg `gender` og `age_group` | kodetall |
| Resultat | `11,74`, `1,48,98`, av og til `4.47.12` | `13.16`, `2:21.47` | `1.01,14`, `8,62(+2,0)`, `mx` = manuell tid |
| Status i resultatfeltet | `DNS`, `DNF`, `NM`, `DQ:R162.8`, `-`, tomt | samme | samme |
| Vind | eget felt `+0,9` / `+0.8` | eget felt | innbakt i resultat |
| Manuell tid | finnes ikke | finnes ikke | `mx` |
| Inne/ute | finnes ikke | finnes ikke | `arena` |

Viktige detaljer:

- **Utstyr mangler ofte** (`Kule G-18-19`, `KU23 Kule`). Øvelser som `KU20 Spyd 600g` kan ha utøvere i klasse J17, der
  Tyrving bruker 500 g. **Øvelsesklassen og utøverens klasse er ikke det samme.**
- **Blandede klasser i samme øvelse** (`M60-64 Diskos`, `KU20` med J17 og J18/19). Poeng må regnes per utøver.
- Hekk oppgis som høyde og avstand (`91,4 9,14m`), og av og til bare høyde (`84,0cm`).

## Konsekvenser for API-designet

1. **Batch-endepunkt**: 100–1500 rader per kall. Hver rad får eget svar (poeng, eller status og begrunnelse). Én
   ugyldig rad skal aldri stoppe resten.
2. **To lag**:
   - **Kjerne** (`/calculate`, `/batch`) med kanoniske verdier: `event_id`, kjønn, klasse, utstyr og resultat som tall.
     Dette er det skissen og frontenden bruker.
   - **Tolkning** (for eksempel `/interpret` eller rå felt i batch) som tar Liveres/OpenTrack-strenger og returnerer
     *både* tolkningen (kanoniske felt) og poengene. Da ser minfriidrett hva som ble lest, og feil kan spores.
3. **Automatisk tabellvalg per utøverklasse**: G/J 10–19 → Tyrving, senior og U20/U23 → WA (når klar), M/K35+ →
   WMA (når klar). Klassen som brukes, står i svaret.
4. **Utstyr**:
   - Mangler utstyr og klassen bare har én variant, brukes den.
   - Er det flere varianter, er svaret `ambiguous_implement`.
   - Er utstyret oppgitt, men ikke det tabellen bruker for klassen (J17 med 600 g spyd), er svaret
     `implement_mismatch` uten poeng. Det skal aldri gis poeng for feil utstyr.
5. **Status i stedet for feil**: `DNS`, `DNF`, `NM`, `DQ…`, `-` og tomt gir status `no_result`, ikke HTTP-feil.
   Resultater utenfor rimelig område flagges (`within_plausible_range`).
6. **Manuell tid** er et valgfritt flagg (standard: automatisk). **Vind** og **inne/ute** tas imot, men påvirker ikke
   Tyrving-poeng.
7. **Idempotent og deterministisk**: samme input gir alltid samme svar, og svaret har `system` og `version` (B-5),
   så minfriidrett kan lagre hvilken tabell poengene er regnet etter og hoppe over rader som ikke er endret.
8. **Tilgang**: 1400 rader hvert 10. sekund under et stevne og 1,4 millioner ved etterfylling går over en vanlig
   IP-grense. minfriidrett blir den første integrasjonspartneren med **API-nøkkel og høyere grense** (B-4 forutsetter
   nettopp dette).
9. **5KAMP** har ingen backend og kaller eventuelt fra nettleseren. Det krever CORS for sitt domene. Øvelsene der
   (lengde, spyd, diskos, 200 m, 1500 m, 800 m) trenger WA-tabellene.

## Åpent spørsmål

Skal tolkningen av Liveres/OpenTrack-strenger ligge i **dette API-et** (anbefalt: én plass, testbar, gjenbrukbar for
5KAMP og andre) eller i **minfriidrett** (som allerede har parsere, men som i dag kaster utstyrsinformasjonen)?
