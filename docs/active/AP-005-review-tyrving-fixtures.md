# AP-005: Review av Tyrving-fasiten

**Status:** Klar
**Opprettet:** 2026-09-25 (Code, etter AP-004)
**Eier:** 🧑 Simen
**Avhenger av:** AP-004

## Hva som skal godkjennes

`tests/fixtures/tyrving_cases.json`: 2472 caser, regnet ut av LibreOffice fra NFIFs regneark, med de tre rettede
radene fra `docs/KILDEAVVIK.md`. Når du godkjenner, er fasiten låst: agenten endrer den aldri etterpå, og
`TyrvingCalculator` (AP-008) må treffe den.

## Stikkprøve mot PDF-en

Slå opp i `sources/tyrving/tyrving-2014-gutter.pdf` / `-jenter.pdf`. Regn ut poengene selv, eller bruk PDF-ens
80 %-rad og poengrad for kast og stav.

**Tilfeldig utvalg** (fast frø, én per øvelsesgruppe og kjønn, uten 0 og 1000):

| Klasse | Øvelse | Utstyr | Resultat | Fasit | Rad i regnearket | OK? |
|---|---|---|---|---|---|---|
| G15 | javelin | 0,6kg | 57.20 m | 1052 | Gutter 15 år rad 36 | ✅ |
| G10 | ball_throw | 150g | 43.20 m | 928 | Gutter 10 år rad 22 | ✅ |
| J14 | shot_put | 3kg | 8.64 m | 870 | Jenter 14 år rad 32 | ✅ |
| J17 | sprint_100m | — | 13.86 s | 798 | Jenter 17 år rad 8 | ✅ |
| J15 | long_jump | — | 4.82 m | 886 | Jenter 15 år rad 30 | ✅ |
| J17 | steeplechase_3000m | 76,2cm | 12:50.0 | 860 | Jenter 17 år rad 28 | ✅ (nettside: fasit mangler, håndregnet 860) |
| G13 | discus | 0,75kg | 44.00 m | 1052 | Gutter 13 år rad 26 | ✅ |
| J13 | middle_600m | — | 1:52.2 | 755 | Jenter 13 år rad 11 | ✅ |
| J12 | high_jump | — | 1.58 m | 1105 | Jenter 12 år rad 17 | ✅ |
| G19 | steeplechase_3000m | 91,4cm | 8:46.5 | 1157 | Gutter 19 år rad 32 | ✅ |
| J14 | discus | 0,75kg | 34.20 m | 886 | Jenter 14 år rad 33 | ✅ |
| J18 | racewalk_1000m | — | 4:01.2 | 1187 | Jenter 18 år rad 20 | ✅ |

**De tre rettede radene** (her gjelder PDF-en, ikke regnearket):

| Klasse | Øvelse | Utstyr | Resultat | Fasit | OK? |
|---|---|---|---|---|---|
| G19 | distance_2000m | — | 6:11.8 | 847 | ✅ |
| J17 | shot_put | 3kg | 10.08 m | 848 (PDF: 80 % = 10.08 → 848) | ✅ |
| J17 | shot_put | 3kg | 13.86 m | 1037 | ✅ |
| J15 | javelin | 0,5kg | 30.40 m | 810 (PDF: 80 % = 30.40 → 810) | ✅ |
| J15 | javelin | 0,5kg | 41.80 m | 1049 | ✅ |

## Kvalitetssikring mot Rjukan IL sin Tyrvingkalkulator (Code, 2026-09-26)

https://rjukanfriidrett.no/rilfrioks/tyrvingKalk.php er en uavhengig implementering med egen parametertabell
(868 rader) og egen beregning. Code kjørte sidens beregningsfunksjon `jsCalcTyrvingPoeng` på casene, og kontrollerte
én case gjennom skjemaet (J17 kule 3 kg 13,86 m → 1037), som ga det samme.

**Stikkprøven over:** 16 av 17 identiske. Den siste (J17 3000 m hinder) finnes ikke på nettsiden. Word-dokumentet har
1000p = 11:40.0 og multiplikator 0,2, som gir 1000 + (7000 − 7700) × 0,2 = 860.

**Hele fasiten (2472 caser):**

| | Antall |
|---|---|
| Mangler på nettsiden: G/J12 100 m og 300 m, G/J13 3000 m kappgang, G/J15 10000 m kappgang, G/J17 3000 m hinder | 40 |
| Sammenlignet | 2432 |
| **Identiske** | **2419** |
| Avvik der nettsiden har feil parameter, jf. Word-dokumentet (se under) | 12 |
| Flyttallskanten J11 høyde u.t. 0,06 m: nettsiden gir **12**, regnearket 11 | 1 |

Parameterfeil på nettsiden (Word-dokumentet og fasiten er enige):

| Klasse og øvelse | Nettsiden | Word-dokumentet |
|---|---|---|
| G19 400 m | 1000p = 50,5 | 50.40 |
| J19 1000 m | 1000p = 2:59.50 | 2:59.00 |
| G17 2000 m | 1000p = 4:46.00 | 5:46.00 |
| G15 100 m hekk 84,0 cm | mangler (1000p = 0) | 14.00 |

Nettsiden har de samme verdiene som Word-dokumentet på alle tre radene der NFIFs regneark avviker (G19 2000 m, J17 kule
3 kg, J15 spyd). Den regner også flyttallskanten eksakt (12). Begge deler støtter valgene som er gjort.

## Spørsmål du må svare på

1. **Flyttallskanten** (`docs/KILDEAVVIK.md`): J11 høyde u.t. 0,06 m gir 11 i regnearket og 12 eksakt. Skal
   motoren regne eksakt (desimal, i tråd med PDF-regelen) og ha denne ene casen som dokumentert unntak?
   *Code anbefaler eksakt regning:* det er regelen NFIF har skrevet, og det gjør motoren uavhengig av
   flyttallsdetaljer i regneark.
2. **Resultatoppløsning:** fasiten bruker hundredeler til og med 500 m og tideler over. Hvordan motoren skal
   behandle hundredeler i lange løp, er AP-006/AP-007.

## Akseptansekriterier

- [x] Stikkprøven stemmer med PDF-en (kontrollert mot Rjukan-kalkulatoren 2026-09-26, se over)
- [ ] Spørsmål 1 besvart
- [ ] Status i `docs/BACKLOG.md` satt til `Ferdig`, med dato: fasiten er låst
