# Utkast: e-post til NFIF om avvik i Tyrvingtabellen 2014

**Status:** utkast, ikke sendt
**Til:** friidrett@friidrett.no (Statistikk- og rekordutvalget, jf. forsiden i regnearket)
**Grunnlag:** `docs/KILDEAVVIK.md`. Poengtallene for regnearket er regnet ut i LibreOffice på NFIFs egen fil.

---

**Emne:** Avvik i Tyrvingtabellen 2014 — regnearket, Word-dokumentene og Tyrvingkalkulatoren

Hei,

Jeg holder på å lage en åpen poengkalkulator for norsk friidrett. I den forbindelse har jeg sammenlignet alle 560
kombinasjoner av øvelse, kjønn og alder i Tyrvingtabellen (2014-utgaven), slik den ligger på friidrett.no per
25.09.2026:

- regnearket poengtabell-tyrvingtabellen.xls (sist oppdatert 28.02.2018)
- Word-dokumentene tyrvingtabellen-gutter-2014.doc og tyrvingtabellen-jenter-2014.doc

Alle 1000-poengsnivåer og multiplikatorer stemmer mellom filene, bortsett fra to steder der regnearket gir andre
poeng enn Word-dokumentene:

1. **Gutter 19 år, 2000 m** (arket «Gutter 19 år», celle I16): Regnearket bruker multiplikator 0,5.
   Word-dokumentet har 0,45, som er det samme som for 14–18 år. Eksempel: 6:00.0 gir 890 poeng i regnearket, men
   901 etter Word-dokumentet.
2. **Jenter 17 år, kule 3 kg** (arket «Jenter 17 år», rad 36): Regnearket regner med én fast multiplikator på 1,2
   (cellene I36 og P36). Word-dokumentet, og all annen kule i regnearket, bruker tre intervaller med
   0,3 / 0,6 / 1,2. Eksempel: 11,00 m gir 808 poeng i regnearket, men 904 etter Word-dokumentet, og 13,50 m gir
   1108 mot 1027.

I tillegg har jeg funnet to mindre ting:

**Hundredeler i lange løp.** Bruksteksten sier at hundredeler skal strykes i løp over 500 m. Et resultat på
2:04.56 på 800 m skal altså regnes som 2:04.5. Regnearket bruker tiden slik den er tastet inn, med hundredeler.
For gutter 15 år gir 2:04.56 dermed 989 poeng i regnearket, mens riktig etter bruksteksten er 991.

**Skrivefeil i Word-dokumentet for gutter.** Disse har ingen betydning for poengene, men gjør tabellen vanskeligere
å lese riktig:

| Hvor | Står | Skal stå | Feil |
|---|---|---|---|
| 1500 m hinder, 15 år | 4.48.00 | 4:48.00 | Punktum i stedet for kolon mellom minutter og sekunder |
| 20 km kappgang, 18 år | 1:40.00.0 | 1:40:00.0 | Punktum i stedet for kolon mellom minutter og sekunder (tiden er 1 t 40 min, jf. jenter-dokumentets 1:53:30.0) |
| 20 km kappgang, 19 år | 1:38.00.0 | 1:38:00.0 | Samme som over |
| Slegge 2 kg, 80 %-raden, 12 år | 30,40 | 30.40 | Komma i stedet for punktum som desimaltegn (verdien er riktig) |

**Tyrvingkalkulatoren på rjukanfriidrett.no**

Siden dere lenker til Rjukan IL sin Tyrvingkalkulator (https://rjukanfriidrett.no/rilfrioks/tyrvingKalk.php), har jeg
også sammenlignet den med Word-dokumentene. Den har egne parametre og regner riktig i de aller fleste tilfeller. Av
2432 testresultater gir den nøyaktig samme poeng som Word-dokumentene i 2419. På de to stedene der regnearket avviker,
følger kalkulatoren Word-dokumentene. Men den har også noen feil:

Feil 1000-poengsnivå:

| Klasse og øvelse | Kalkulatoren | Word-dokumentet | Eksempel |
|---|---|---|---|
| Gutter 19 år, 400 m | 50,50 | 50,40 | 50,40 gir 1004 poeng i kalkulatoren |
| Jenter 19 år, 1000 m | 2:59.50 | 2:59.00 | 2:59.0 gir 1005 poeng i kalkulatoren |
| Gutter 17 år, 2000 m | 4:46.00 | 5:46.00 | 5:46.0 gir 730 poeng i kalkulatoren |
| Gutter 15 år, 100 m hekk 84,0 cm | mangler (gir 0 poeng) | 14,00 | 14,00 gir 0 poeng |

Øvelser som står i Word-dokumentene, men mangler i kalkulatoren:

- 100 m og 300 m for gutter og jenter 12 år
- 3000 m kappgang for gutter og jenter 13 år
- 10000 m kappgang for gutter og jenter 15 år
- 3000 m hinder for gutter og jenter 17 år

Kalkulatoren har også noen varianter som ikke står i Word-dokumentene, de fleste i tillegg til Word-dokumentets
egne. Noen kan være bevisste tillegg etter nyere utstyrsregler, men da mangler de i Word-dokumentene:

| Klasse | Øvelse i kalkulatoren | Word-dokumentet |
|---|---|---|
| G10, J10 | 200 m (1000p 30,8 / 31,0) | 200 m fra 11 år |
| J10–J13 | Slegge 2 kg / 100 cm | Slegge 2 kg / 110 cm |
| G12 | Slegge 3 kg / 110 cm | Slegge 2 kg / 110 cm |
| G13, J14, J15 | Slegge 3 kg / 110 cm (i tillegg til 119,5 cm) | Slegge 3 kg / 119,5 cm |
| J16, J17 | Slegge 4 kg / 119,5 cm | Slegge 3 kg / 119,5 cm |
| J17 | Kule 4 kg | Kule 3 kg |
| J12, J13 | 60 m hekk 68,0 cm | 60 m hekk 76,2 cm |
| G15 | 100 m hekk 91,4 cm | 100 m hekk 84,0 cm (91,4 cm fra 16 år) |
| G17 | 110 m hekk 91,4 cm / 8,8 m | 110 m hekk 91,4 cm / 9,14 m |
| G18, G19 | 400 m hekk 84,0 cm (1000p mangler) | 400 m hekk 91,4 cm |

Jeg har ikke kontaktet Rjukan IL, men sender gjerne oversikten til dem også hvis dere ønsker det.

**Spørsmål til dere**

Kan dere bekrefte at det er Word-dokumentene som er riktige, og i så fall rette regnearket? Er det regnearket som er
riktig, må Word-dokumentene rettes, og da justerer jeg beregningen min etter det. Inntil jeg hører fra dere, bruker
jeg Word-dokumentene som fasit.

Jeg sender gjerne en detaljert oversikt med cellereferanser. Hvis noen av variantene i kalkulatoren gjelder i dag,
setter jeg pris på å få vite hvilke utstyrsregler som er gjeldende.

Vennlig hilsen
Simen Armond
