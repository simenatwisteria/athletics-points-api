# Kildeavvik — kjente feil i de offisielle kildefilene

Register over steder der NFIFs kildefiler er uenige med hverandre eller med seg selv, og hva prosjektet gjør
med det. Kildefilene i `sources/` endres aldri. Rettingene skjer i kode, er synlige i dataene og er låst i tester.

**Regel (Simen, 2026-09-25): Ved konflikt vinner PDF-en.** Forsiden i regnearket sier selv at «den offisielle
utgaven av Tyrvingtabellen er en to siders tabell», altså PDF-en.

**Status overfor NFIF:** ikke meldt ennå. Skal meldes: avvik 1 og 2, merknaden om hundredeler og skrivefeilene i PDF-en. *(Oppdater med dato og svar når avvikene er sendt til forbundet.)*

## Tyrving 2014

Avvikene ble funnet ved å lese alle 560 kombinasjonene i regnearket og sammenligne dem automatisk med begge
PDF-ene (`scripts/tyrving_pdf.py`, `tests/test_tyrving_pdf.py`). PDF-ene er internt konsistente: alle 116
tre-intervall-blokker har 80 %-verdier og poeng som stemmer med 1000p-verdien og multiplikatorene.
DOC-filene er lest på en helt annen måte (tabulatorfelt) og gir **identiske** tabeller
(`scripts/tyrving_doc.py`, `tests/test_tyrving_doc.py`), så DOC og PDF er enige i alle avvikene under.

### Avvik som endrer poeng

**Avvik i NFIFs gjeldende regneark** (`tyrving-2014.xls`, lastet ned fra friidrett.no 2026-09-25, sist endret av
NFIF 2018-02-28): avvik 1 og 2. Låst i `test_current_nfif_xls_against_pdf`. Avvik 3 finnes bare i den eldre
`.xlsx`-kopien og er allerede rettet av NFIF.

| # | Hvor (regnearket) | Regnearket (`.xlsx`) | PDF og DOC | `.xls` |
|---|---|---|---|---|
| 1 | `Gutter 19 år` rad 16 — 2000 m, celle `I16` | multiplikator **0,5** | **0,45** (samme som G14–G18) | som `.xlsx` |
| 2 | `Jenter 17 år` rad 36 — Kule 3kg, cellene `I36`/`P36` | **enkel kvotient** med `I36 = 1.2` hardkodet (`P = 1000-O*I`) | **tre-intervall** 0,3 / 0,6 / 1,2 (som all annen kule) | som `.xlsx` |
| 3 | `Jenter 15 år` rad 36 — Spyd, cellene `C36`/`H36` | **0,4kg**, 1000p = **42,00** | **500 g**, 1000p = **38,00** (400 g gjelder 10–14 år) | som PDF — **rettet av NFIF 2018-02-28** |

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

### Regnearket følger ikke regelen om å stryke hundredeler

Regelteksten: «I lengre løp skal (som før) hundredeler strykes.» Regnearket regner `(D*60+E)*10` rett fram, så
2:04.56 på 800 m gir 989 poeng i regnearket mot 991 etter regelen (2:04.5). Det stemmer bare hvis brukeren selv
legger inn tideler. Motoren følger regelteksten (`tests/fixtures/tyrving_rules.json`, R2-01 – R2-03).

### Skrivefeil i PDF-ene (ingen poengkonsekvens)

| PDF | Hvor | Står | Riktig |
|---|---|---|---|
| gutter | 1500 m hinder, 15 år | `4.48.00` | `4:48.00` |
| gutter | 20000 m kappgang, 18 og 19 år | `1:40.00.0`, `1:38.00.0` | `1:40:00.0`, `1:38:00.0` (jf. jenter-PDF-en) |
| gutter | Slegge 2 kg, 80 %-rad, 12 år | `30,40` | `30.40` |

### Avvik mellom `.xlsx` og `.xls` — `.xlsx` er en eldre kopi

Verifisert 2026-09-25 direkte med `xlrd` (uten LibreOffice-konvertering): eneste forskjell i tekst og parametre
er avvik 3 (spyd J15). Forklaringen står på forsiden av `.xls`: rad 42 har `2014-08-13 | 2018-02-28 | Spyd J15`,
altså en endringslogg der NFIF rettet spyd J15 i februar 2018. Den linjen mangler i `.xlsx`.

Metadata i `.xlsx`: sist lagret av «Simen Armond» 2024-06-28 (opprettet av Ole Petter Sandvig 2003). Den har
også 32 inntastede resultater i kolonne E. `.xlsx` er derfor trolig en lokal kopi laget fra en versjon fra før
2018, ikke filen NFIF publiserer i dag. **Avvik 3 er ikke en feil hos NFIF** og skal ikke meldes.

Konsekvens for data og fasit: ingen. PDF-en vinner uansett, og `.xls`, PDF og DOC er enige om spyd J15.
Parameterekstraksjonen og oracle-en bruker fortsatt `.xlsx` som strukturkilde. Å bytte til `.xls` ville
fjernet én retting, men krever LibreOffice-konvertering i ekstraksjonen. Avgjøres av Simen.

`.xls` deler avvik 1 og 2 og er derfor ikke en uavhengig kontroll for dem.
