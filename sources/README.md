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

| Fil | Originalt filnavn | SHA-256 | Brukes til |
|---|---|---|---|
| `tyrving-2014-redigerbar.xlsx` | `poengtabell-tyrvingtabellen - redigerbar.xlsx` | `713ef97f36f3194d235e4d5d85e136278f92aeb98365d5cfb593ff75ec8550df` | Strukturkilde (eldre kopi, se NB): 20 ark (G/J 10–19) med levende formler. Parameterekstraksjon og LibreOffice-oracle. |
| `tyrving-2014.xls` | `poengtabell-tyrvingtabellen.xls` (nedlastet 2026-09-25) | `d23266b89b3bc5adbf21e0a1bc3d690dd1430fbc5471f02f8e7c3d20e3ef6058` | **NFIFs gjeldende regneark** (sist endret 2018-02-28). Kryssjekk mot `.xlsx` og PDF. |
| `tyrving-2014-gutter.doc` | `tyrvingtabellen-gutter-2014.doc` | `9cda1bfee1f31fe0b9d3c232ee04bdf73a34f00d7219eb1c1c949d262d1b9c2f` | **Offisiell tabell, gutter** (identisk med nedlasting fra friidrett.no 2026-09-25). Tabell og regeltekst. |
| `tyrving-2014-gutter.pdf` | `tyrvingtabellen-gutter-2014.pdf` | `5112f82affc2fb6844caa30dcca51a87419c91c09dcbbcff804ee9fbd24da4ff` | PDF av samme tabell, ukjent opphav, identisk innhold. Leses av `scripts/tyrving_pdf.py`. |
| `tyrving-2014-jenter.doc` | `tyrvingtabellen-jenter-2014.doc` | `5e57056180f069a6f22bfe20e9690789d61920c006d5b52682c43a78fdf7c776` | **Offisiell tabell, jenter** (identisk med nedlasting fra friidrett.no 2026-09-25). Tabell og regeltekst. |
| `tyrving-2014-jenter.pdf` | `tyrvingtabellen-jenter-2014.pdf` | `85ed54697ca614ebb63cbbf863691022145d4ce19f77f7d81a8e3b87dda12d49` | PDF av samme tabell, ukjent opphav, identisk innhold. Leses av `scripts/tyrving_pdf.py`. |

## Mangler

| Mappe | System | Status |
|---|---|---|
| [`wa/`](wa/README.md) | WA Scoring Tables 2025 + Combined Events | Mangler — Simen laster ned |
| [`wma/`](wma/README.md) | WMA Age Factors 2023 | Mangler — Simen laster ned |
| [`masters/`](masters/README.md) | NFIF masters mangekamptabell | Mangler — Simen laster ned |
