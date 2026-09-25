# Kildeavvik — kjente feil i de offisielle kildefilene

Register over steder der NFIFs kildefiler er uenige med hverandre eller med seg selv, og hva prosjektet gjør
med det. Kildefilene i `sources/` endres aldri. Rettingene skjer i kode, er synlige i dataene og er låst i tester.

**Regel (Simen, 2026-09-25): Ved konflikt vinner PDF-en.** Forsiden i regnearket sier selv at «den offisielle
utgaven av Tyrvingtabellen er en to siders tabell», altså PDF-en.

**Status overfor NFIF:** ikke meldt ennå. *(Oppdater med dato og svar når avvikene er sendt til forbundet.)*

## Tyrving 2014

Avvikene ble funnet ved å lese alle 560 kombinasjonene i regnearket og sammenligne dem automatisk med begge
PDF-ene (`scripts/tyrving_pdf.py`, `tests/test_tyrving_pdf.py`). PDF-ene er internt konsistente: alle 116
tre-intervall-blokker har 80 %-verdier og poeng som stemmer med 1000p-verdien og multiplikatorene.

### Avvik som endrer poeng

| # | Hvor (regnearket) | Regnearket (`.xlsx`) | PDF | `.xls` |
|---|---|---|---|---|
| 1 | `Gutter 19 år` rad 16 — 2000 m, celle `I16` | multiplikator **0,5** | **0,45** (samme som G14–G18) | som `.xlsx` |
| 2 | `Jenter 17 år` rad 36 — Kule 3kg, cellene `I36`/`P36` | **enkel kvotient** med `I36 = 1.2` hardkodet (`P = 1000-O*I`) | **tre-intervall** 0,3 / 0,6 / 1,2 (som all annen kule) | som `.xlsx` |
| 3 | `Jenter 15 år` rad 36 — Spyd, cellene `C36`/`H36` | **0,4kg**, 1000p = **42,00** | **500 g**, 1000p = **38,00** (400 g gjelder 10–14 år) | som PDF |

Poengeksempler. Regnearkets tall er regnet ut av LibreOffice på det urettede regnearket; PDF-tallene følger
PDF-ens parametre og regler.

| # | Resultat | Regnearket | PDF | Differanse |
|---|---|---|---|---|
| 1 | G19 2000 m 6:00.0 | 890 | 901 | +11 |
| 1 | G19 2000 m 5:50.0 | 940 | 946 | +6 |
| 2 | J17 kule 13,50 m | 1108 | 1027 | −81 |
| 2 | J17 kule 11,00 m | 808 | 904 | +96 |
| 2 | J17 kule 9,00 m | 568 | 719 | +151 |
| 3 | J15 spyd 38,00 m | 900 | 1000 | +100 |
| 3 | J15 spyd 35,00 m | 825 | 925 | +100 |
| 3 | J15 spyd 30,00 m | 610 | 790 | +180 |

Avvik 2 gir feil poeng for alle kast unntatt nøyaktig 12,60 m. Avvik 3 regner i tillegg med feil spydvekt.

**Slik håndteres det:**
- Parametre: `athletics_scoring/data/tyrving_parameters_2014.json` bruker PDF-verdiene. Regnearkets verdier
  står i `pdf_override.excel` på de tre oppføringene.
- Fasit: `scripts/oracle_tyrving.py` retter de samme cellene i en temp-kopi før LibreOffice regner om
  (`meta.patches` i `tests/fixtures/tyrving_cases.json`).
- Testene `test_overrides_are_exactly_the_known_ones` og `test_every_entry_equals_pdf` feiler hvis et nytt
  avvik dukker opp eller et kjent forsvinner.

### Flyttallsfeil i regnearkets nedrunding

| Hvor | Resultat | Regnearket | Eksakt (PDF-regelen) |
|---|---|---|---|
| `Jenter 11 år` rad 16 — Høyde uten tilløp | 0,06 m | 11 | 12 |

Mellomresultatet er eksakt 12, men regnearket regner det til 11,9999999999999 og runder ned. PDF-en sier «alle
desimaler beholdes under utregningen» og «poengsummen rundes alltid ned». Resultatet er urealistisk, men
feiltypen kan i prinsippet ramme ekte resultater. Casen er merket `float_edge` i fasiten. **Åpent:** skal
motoren regne eksakt (desimal) og dermed avvike fra regnearket her? Avgjøres i AP-005.

### Skrivefeil i PDF-ene (ingen poengkonsekvens)

| PDF | Hvor | Står | Riktig |
|---|---|---|---|
| gutter | 1500 m hinder, 15 år | `4.48.00` | `4:48.00` |
| gutter | 20000 m kappgang, 18 og 19 år | `1:40.00.0`, `1:38.00.0` | `1:40:00.0`, `1:38:00.0` (jf. jenter-PDF-en) |
| gutter | Slegge 2 kg, 80 %-rad, 12 år | `30,40` | `30.40` |

### Avvik mellom `.xlsx` og `.xls`

Bare avvik 3 (spyd J15). Utover det har de to regnearkene identiske parametre og formler. `.xls` deler feil 1
og 2 og er derfor ikke en uavhengig kontroll.
