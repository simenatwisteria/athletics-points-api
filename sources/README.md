# Kildefiler

Offisielle kildefiler som all fasit (`tests/fixtures/`) genereres fra. **Agenten endrer aldri noe her.**
Nye filer legges inn av Simen, og sjekksummen føres i tabellen i samme commit.

Verifiser sjekksummene:

```bash
cd sources && shasum -a 256 -c SHA256SUMS
```

## Tyrving 2014 (`tyrving/`)

Opprinnelse: Norges Friidrettsforbund (NFIF), friidrett.no → Poengtabeller. Kopiert fra Cowork-mappen
`Projects/AthleticsPointsCalc/` 2026-09-25. `tyrving-2014.xls` ble samme dag byttet ut med en fersk nedlasting
fra https://www.friidrett.no/siteassets/arrangement/poengtabell-tyrvingtabellen.xls (lagret som
`poengtabell-tyrvingtabellen 25.09.2026.xls` i Cowork-mappen). Innholdet er identisk med den gamle kopien; bare
brukernavnet i Excel-posten `WRITEACCESS` var ulikt («Simen Armond» mot «Bruker»).

DOC-filene er verifisert byte-identiske med Word-dokumentene på friidrett.no, lastet ned 2026-09-25
(`NFIF 2026.09.25/` i Cowork-mappen). De er **NFIFs offisielle tabell**. PDF-ene er ikke fra den siden og har
ukjent opphav, men har identisk innhold (`tests/test_tyrving_doc.py`).

**NB:** `tyrving-2014-redigerbar.xlsx` er **ikke** NFIFs gjeldende fil. Den er en kopi av 2014-versjonen fra før
NFIF rettet spyd J15 (2018-02-28, se endringsloggen på forsiden i `.xls`), sist lagret lokalt 2024-06-28, med
inntastede resultater. Formlene er ellers identiske med `.xls`. Den brukes fortsatt som strukturkilde for
ekstraksjon og oracle; avvikene er dokumentert i `docs/KILDEAVVIK.md`.

Nedlastingslenker (NFIF-siden: https://www.friidrett.no/arrangement/arrangementshjelp/poengtabeller/tyrvingtabellen/):

- `tyrving-2014-gutter.doc`: https://www.friidrett.no/siteassets/arrangement/tyrvingtabellen-gutter-2014.doc
- `tyrving-2014-jenter.doc`: https://www.friidrett.no/siteassets/arrangement/tyrvingtabellen-jenter-2014.doc
- `tyrving-2014.xls`: https://www.friidrett.no/siteassets/arrangement/poengtabell-tyrvingtabellen.xls
- PDF-ene og `tyrving-2014-redigerbar.xlsx` har ingen offisiell nedlastingslenke (se over).

| Fil | Originalt filnavn | SHA-256 | Brukes til |
|---|---|---|---|
| `tyrving-2014-redigerbar.xlsx` | `poengtabell-tyrvingtabellen - redigerbar.xlsx` | `713ef97f36f3194d235e4d5d85e136278f92aeb98365d5cfb593ff75ec8550df` | Strukturkilde (eldre kopi, se NB): 20 ark (G/J 10–19) med levende formler. Parameterekstraksjon og LibreOffice-oracle. |
| `tyrving-2014.xls` | `poengtabell-tyrvingtabellen.xls` (nedlastet 2026-09-25) | `d23266b89b3bc5adbf21e0a1bc3d690dd1430fbc5471f02f8e7c3d20e3ef6058` | **NFIFs gjeldende regneark** (sist endret 2018-02-28). Kryssjekk mot `.xlsx` og PDF. |
| `tyrving-2014-gutter.doc` | `tyrvingtabellen-gutter-2014.doc` | `9cda1bfee1f31fe0b9d3c232ee04bdf73a34f00d7219eb1c1c949d262d1b9c2f` | **Offisiell tabell, gutter** (identisk med nedlasting fra friidrett.no 2026-09-25). Tabell og regeltekst. |
| `tyrving-2014-gutter.pdf` | `tyrvingtabellen-gutter-2014.pdf` | `5112f82affc2fb6844caa30dcca51a87419c91c09dcbbcff804ee9fbd24da4ff` | PDF av samme tabell, ukjent opphav, identisk innhold. Leses av `scripts/tyrving_pdf.py`. |
| `tyrving-2014-jenter.doc` | `tyrvingtabellen-jenter-2014.doc` | `5e57056180f069a6f22bfe20e9690789d61920c006d5b52682c43a78fdf7c776` | **Offisiell tabell, jenter** (identisk med nedlasting fra friidrett.no 2026-09-25). Tabell og regeltekst. |
| `tyrving-2014-jenter.pdf` | `tyrvingtabellen-jenter-2014.pdf` | `85ed54697ca614ebb63cbbf863691022145d4ce19f77f7d81a8e3b87dda12d49` | PDF av samme tabell, ukjent opphav, identisk innhold. Leses av `scripts/tyrving_pdf.py`. |

## Masters (`masters/`) og WMA (`wma/`)

Lastet ned 2026-09-26 fra de offisielle nedlastingslenkene og lagt inn av Cowork på vegne av Simen. Kopier med
samme SHA-256 ligger i Cowork-mappen `kilder/`, der `kilder/KILDER.md` har full kildeliste. NFIF-siden alle filene
er lenket fra: https://www.friidrett.no/aktiviteter/masters/poengberegning/

| Fil | Originalt filnavn og URL | SHA-256 | Brukes til |
|---|---|---|---|
| `masters/nfif-masters-mangekamp-menn.xlsx` | `mangekamptabellen-for-menn.xlsx` — https://www.friidrett.no/contentassets/d8222e75a783431481bdf30d9fa02720/mangekamptabellen-for-menn.xlsx | `1cf6af34f3334c5a0600a1ee9d98992cb5ee1a2d9d093458b4fe1833f2f2d0e1` | **Fasit** for masters mangekamp, menn. Seniorkolonnen («Sr») er også fasit for WA Combined Events. |
| `masters/nfif-masters-mangekamp-kvinner.xlsm` | `mangekamptabellen-for-kvinner.xlsm` — https://www.friidrett.no/contentassets/d8222e75a783431481bdf30d9fa02720/mangekamptabellen-for-kvinner.xlsm | `d2c2ce52f8aeeb265dff88740c204a24105265c26e79904643687827a49d75ca` | Samme, kvinner |
| `masters/nfif-masters-serietabell-menn.xlsx` | `serietabellen-for-menn.xlsx` — https://www.friidrett.no/contentassets/d8222e75a783431481bdf30d9fa02720/serietabellen-for-menn.xlsx | `96d9db959cd5e11fb61837d0ec2c97512e764324e804ea6d431c16b5cde17c12` | Masters serietabell (øvelser utenfor mangekamptabellen). Oppbyggingen er uavklart, se `docs/henvendelser/`. |
| `masters/nfif-masters-serietabell-kvinner.xlsx` | `serietabellen-for-kvinner.xlsx` — https://www.friidrett.no/contentassets/d8222e75a783431481bdf30d9fa02720/serietabellen-for-kvinner.xlsx | `b17ca2eeadd152ffc3b9d31d33a70f48f4c35afa33bfb22ad7c7f360d3ef4035` | Samme, kvinner |
| `wma/wma-2023-appendix-b-combined-events.pdf` | `2023-WMA-Appendix-B.pdf` — https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-WMA-Appendix-B.pdf | `c3d5baa5fff954c6e7a7686c203a1146111342c351cd6e83e0a3a49c52b20858` | **Metoden** for masters mangekamp (aldersfaktorer per 5-årsklasse, avrunding, håndtid) og **parametrene a, b, c for WA Combined Events** (s. 2). NFIF kaller lenken «Poengberegningsprogram». |
| `wma/wma-2023-age-factors.pdf` | `2023-Age-Factors-WMA.pdf` — https://world-masters-athletics.org/wp-content/uploads/2023/02/2023-Age-Factors-WMA.pdf | `466e28d9edb848ebe8d03251d8ac41405498f368a44a7199894f61e3983cda94` | Ettårige aldersfaktorer for WMA Age Grading. NFIF kaller lenken «Masterstabell». WMA bekrefter at 2023-utgaven gjelder (sjekket 2026-09-26). |

## NFIF-regler (`nfif/`)

| Fil | Originalt filnavn og URL | SHA-256 | Brukes til |
|---|---|---|---|
| `nfif/nfif-um-reglement-2026.pdf` | `um-reglement-2026.2.pdf` — https://www.friidrett.no/siteassets/arrangement/um-2026/um-reglement-2026.2.pdf (sist endret 12.11.2025, lastet ned 2026-09-26) | `adce7baf2943e43d1616045069514b28b570daa7cad68b32bcca225a6599144e` | §16.4–16.5: mangekamp fra 15 år bruker de internasjonale tabellene, og NFIFs egne koeffisienter for 600 m (J15/16), 800 m inne (G15/16), 80 m hekk (J15/16) og 100 m hekk (G15/16). |

## World Athletics (`wa/`) — ikke i repoet

WA-PDF-ene (Combined Events 2001/2016 og Scoring Tables 2025) er lastet ned 2026-09-26, men **sjekkes ikke inn**
fordi de har forbehold mot kopiering og repoet er offentlig (B-23). De ligger i Cowork-mappen
`kilder/world-athletics/`, se [`wa/README.md`](wa/README.md). Parametrene for Combined Events hentes fra
`wma/wma-2023-appendix-b-combined-events.pdf`, og fasiten fra seniorkolonnen i NFIF-tabellene.

## Mangler

| Mappe | System | Status |
|---|---|---|
| — | Serietabellen senior (Lagserien) | Ingen offisiell fil hos NFIF. Spurt i `docs/henvendelser/2026-09-26-nfif-tyrving-avvik.md` |
