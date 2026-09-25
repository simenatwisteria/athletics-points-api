# Kildefiler

Offisielle kildefiler som all fasit (`tests/fixtures/`) genereres fra. **Agenten endrer aldri noe her.**
Nye filer legges inn av Simen, og sjekksummen føres i tabellen i samme commit.

Verifiser sjekksummene:

```bash
cd sources && shasum -a 256 -c SHA256SUMS
```

## Tyrving 2014 (`tyrving/`)

Opprinnelse: Norges Friidrettsforbund (NFIF), friidrett.no → Poengtabeller. Kopiert fra Cowork-mappen
`Projects/AthleticsPointsCalc/` 2026-09-25.

| Fil | Originalt filnavn | SHA-256 | Brukes til |
|---|---|---|---|
| `tyrving-2014-redigerbar.xlsx` | `poengtabell-tyrvingtabellen - redigerbar.xlsx` | `713ef97f36f3194d235e4d5d85e136278f92aeb98365d5cfb593ff75ec8550df` | Primærkilde: 20 ark (G/J 10–19) med levende formler. Parameterekstraksjon og LibreOffice-oracle. |
| `tyrving-2014.xls` | `poengtabell-tyrvingtabellen.xls` | `8e8831f3a69b4207430a1653d3f8c11ca25e9866929032658063d7596a105639` | Eldre formatvariant. Kryssjekk av parametre mot `.xlsx`. |
| `tyrving-2014-gutter.doc` | `tyrvingtabellen-gutter-2014.doc` | `9cda1bfee1f31fe0b9d3c232ee04bdf73a34f00d7219eb1c1c949d262d1b9c2f` | Regeltekst gutter (80 %-grense, manuell tidtaking, avrunding). |
| `tyrving-2014-gutter.pdf` | `tyrvingtabellen-gutter-2014.pdf` | `5112f82affc2fb6844caa30dcca51a87419c91c09dcbbcff804ee9fbd24da4ff` | Samme som `.doc`, i PDF. Manuell stikkprøve av tabellverdier. |
| `tyrving-2014-jenter.doc` | `tyrvingtabellen-jenter-2014.doc` | `5e57056180f069a6f22bfe20e9690789d61920c006d5b52682c43a78fdf7c776` | Regeltekst jenter. |
| `tyrving-2014-jenter.pdf` | `tyrvingtabellen-jenter-2014.pdf` | `85ed54697ca614ebb63cbbf863691022145d4ce19f77f7d81a8e3b87dda12d49` | Samme som `.doc`, i PDF. Manuell stikkprøve av tabellverdier. |

## Mangler

| Mappe | System | Status |
|---|---|---|
| [`wa/`](wa/README.md) | WA Scoring Tables 2025 + Combined Events | Mangler — Simen laster ned |
| [`wma/`](wma/README.md) | WMA Age Factors 2023 | Mangler — Simen laster ned |
| [`masters/`](masters/README.md) | NFIF masters mangekamptabell | Mangler — Simen laster ned |
