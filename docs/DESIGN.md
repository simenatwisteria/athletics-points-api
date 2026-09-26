# Designspesifikasjon — Poengtabeller (web/mobil)

Fasit for frontenden (AP-023). Bygget på den klikkbare skissen, versjon 2, godkjent av Simen 2026-09-26.

- Skissen (privat Artifact): https://claude.ai/artifact/X2gLMXyPqEA67KSNTNd25C
- Kildefiler i repoet: [`docs/design/skisse-v2/`](design/skisse-v2/) (gjeldende) og [`docs/design/skisse-v1/`](design/skisse-v1/)
  (første runde, bare til sammenligning). Filene er i Design-formatet (`.dc.html`) og kjører i skisseverktøyet, ikke
  alene i en nettleser.
- Skjermbilder: mangler. Skissen er privat og krever innlogging, så Simen legger dem i `docs/design/skjermbilder/`.

Skissen regner selv med en kopi av reglene (`tyrving-sketch.js`) for å være klikkbar. **Den ferdige frontenden regner
aldri selv**: alle tall, øvelser, klasser, grenser og forklaringer kommer fra API-et (B-9).

## 1. Informasjonsarkitektur

To nivåer, én app:

1. **Poengtabeller** (startside): alle tabeller gruppert i *Ungdom*, *Senior* og *Masters*. Hver rad har navn,
   kort beskrivelse og status (*Klar* / *Kommer*). Språkvalg NO/EN øverst til høyre.
2. **Kalkulator** for valgt tabell: samme skjermoppsett for alle tabeller, men klasser, øvelser og om mangekamp
   finnes, styres av tabellen (data fra `GET /systems` og `GET /events`).

| Tabell | Gruppe | Klasser | Mangekamp |
|---|---|---|---|
| Tyrvingtabellen 2014 | Ungdom | Gutter/Jenter, alder 10–19 | Ja, til og med 14 år |
| World Athletics 2025 | Senior | Kvinner/Menn, Senior | Nei (egen tabell) |
| WA mangekamp | Senior | Tikamp, sjukamp, femkamp inne | Kun mangekamp |
| Serietabellen | Senior | Kvinner/Menn, Senior | Nei |
| WMA aldersgradering 2023 | Masters | K35–K90 / M35–M90 | Nei |
| Masters mangekamp (NFIF) | Masters | K35–K90 / M35–M90 | Kun mangekamp |

En tabell som ikke er klar kan åpnes og vise klasser og øvelser, men viser en melding i stedet for resultatfelt.

## 2. Kalkulator — enkeltøvelse

Kompakt, uten scrolling på en telefon (390 × 844). iOS-mønstre:

- **Segmentert kontroll** øverst: *Enkeltøvelse | Mangekamp* (bare når tabellen har mangekamp).
- **Skjema med rader** (inset grouped). Hver rad viser valgt verdi:
  - *Kjønn*: segmentert kontroll i raden.
  - *Alder* / *Klasse*: nedtrekksmeny med hake.
  - *Øvelse*: nedtrekksmeny gruppert i *Løp*, *Hekk og hinder*, *Kappgang*, *Hopp*, *Kast*.
  - *Utstyr*: nedtrekksmeny bare når øvelsen har flere varianter (f.eks. 110 m hekk G17–19). Én variant: vises som
    tekst. Ingen variant: raden vises ikke.
  - *Manuell tidtaking*: iOS-bryter, bare der regelverket har tillegg. Tillegget står i teksten (+0,24 s).
- **Resultatfelt** (stort): tomt felt viser 1000-poengsresultatet i grått som referanse.
- **Poengkort**: poengsum stort, *1000 poeng: …* til høyre, én linje med «regnet som …» og tillegg, og
  *Slik er det regnet* som utvidbar forklaring (`calculation_detail`).

## 3. Resultatinntasting — talltastatur

Samme mønster som beløp i Apple Cash og vekt i Helse-appen:

- Egne tastatur (1–9, 0, *Tøm*, ⌫) som glir opp nederst når resultatfeltet trykkes, og lukkes med *Ferdig*.
  Det vises ikke hele tiden.
- **Sifre fylles inn fra høyre.** Brukeren taster aldri komma eller kolon.
  - Sprint og distanse: to desimaler. 7-4-0 blir 7,40 s, og 5-2-0 blir 5,20 m.
  - Lange løp (over 500 m): minutter, sekunder og tideler. 2-0-4-5 blir 2:04,5. Hundredeler kan ikke tastes, så
    regelen om at de strykes kan ikke misforstås.
- Tastaturets tittellinje viser øvelse, enhet og poeng underveis.
- **Rimelig område** (`InputSpec.plausible_min/max`): utenfor området vises ikke poeng, bare «Utenfor rimelig område
  (4,53–22,65 s)». Det skjuler meningsløse tall mens sifrene tastes (1-0-9 = 1,09 s).
- Sekunder over 59 i lange løp gir melding i stedet for poeng.

## 4. Mangekamp

- Klasse som for enkeltøvelse. Tyrving: fra 15 år vises en melding om at WA-tabellene gjelder.
- Én rad per øvelse: navn og utstyr, *1000 poeng: …*, resultatfelt, poeng og fjern-knapp.
- *+ Legg til øvelse* åpner øvelsesmenyen (samme gruppering). Den nye øvelsen blir aktiv med én gang.
- Tastaturet har *Neste ›* for å gå til neste øvelse uten å lukke tastaturet.
- Sumlinje nederst: sum og hvor mange øvelser som mangler gyldig resultat. Øvelser utenfor rimelig område telles ikke.
- Faste mangekamper per klasse (f.eks. femkamp J13) vises som valg når NFIFs oversikt er lagt inn.

## 5. Språk

- Norsk og engelsk for all tekst, øvelsesnavn («110 m hurdles», «Shot put») og klassenavn («Age 15», «W35»).
- Tallformat følger språket: komma på norsk, punktum på engelsk. Poengene er de samme.
- Øvelses- og tabellnavn skal komme fra API-et på begge språk, ikke være hardkodet i frontenden.

## 6. Visuell stil

| Rolle | Verdi |
|---|---|
| Bakgrunn | `#F5F2EC` |
| Flater (kort, skjema) | `#FFFFFF`, skillelinjer `#EEE9E0` |
| Tekst / dempet tekst | `#1C1B19` / `#5F5A52` (kontrast ≥ 4.5:1 på bakgrunn) |
| Aksent (tartanrød) | `#B8391F` — valgt, poeng, handlinger |
| Topplinje | `#1C1B19` |
| Tastatur | `#E8E3D9`, funksjonstaster `#D6CFC2` |
| Overskrifter / tall | Barlow Condensed 600/700 |
| Brødtekst | Source Sans 3 400/600/700 |

Trykkflater minst 44 px. Ekte `<button>`-elementer med `aria-pressed`, `aria-expanded`, `role="switch"` og
`role="menu"` der det gjelder.

## 7. Krav til API-et (fra skissen)

1. `GET /systems`: navn og beskrivelse (no/en), gruppe, *klar*, klassetype (alder/klasse/masters), klasseliste og om
   mangekamp støttes.
2. `GET /events`: felles øvelseskatalog med navn på norsk og engelsk, kategori (løp/hekk/kappgang/hopp/kast),
   utstyrsvarianter, `InputSpec` (måletype, oppløsning, minutter, manuell tid tillatt, rimelig område) og
   1000-poengsnivå.
3. `POST /calculate` og mangekamp-beregning: poeng, effektivt resultat, `within_plausible_range`,
   `calculation_detail` / `calculation_steps`.
4. Tallformatering etter språk gjøres i frontenden. API-et returnerer tall, ikke formaterte strenger.
