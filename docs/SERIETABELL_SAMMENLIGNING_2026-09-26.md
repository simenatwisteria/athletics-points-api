# Serietabellen – sammenligning med kjente tabeller

**Dato:** 26.09.2026  
**Formål:** Finne ut om kalkulatoren for seriepoeng på minfriidrettsstatistikk.info (senior, uten alder) gir de samme poengene som en tabell vi allerede har.

## Metode

- **Kalkulator:** https://www.minfriidrettsstatistikk.info/php/SeriePoengBeregning.php (NFIF lenker til den fra https://www.friidrett.no/arrangement/arrangementshjelp/poengtabeller/). Menn og kvinner senior, alle 27 øvelser.
- **Eksempelresultater:** For hver øvelse valgte jeg fem resultater fra «Sr»-kolonnen (senior) i NFIFs masters-tabeller, ved omtrent 1100, 900, 700, 500 og 300 poeng. Alle resultatene ble lagt inn i kalkulatoren, og seriepoengene lest av.
- **Sammenlignet med:**
  1. **NFIF masters, «Sr»-kolonne.** For sprint, hekk, hopp og kast ligger den i *mangekamptabellen*, og der er den identisk med **WA Combined Events** (kontrollert med formelen, for eksempel 200 m 19,04 = 1200). For 800 m og lengre, langhekk, hinder, kappgang, øvelser uten tilløp og tresteg ligger den i *masters-serietabellen*.
  2. **WA Scoring Tables 2025.** Oppslag i PDF-en for løpsøvelser. For tekniske øvelser er oppslaget for grovt til å gjengis.

## Resultat

**Hypotesen holder ikke.** Kalkulatoren gir andre poeng enn alle tabellene vi har:

- Bare **2 av 265** sammenligninger med «Sr»-kolonnen er like. Medianavviket er **50 poeng**, og det største avviket er **198 poeng**.
- Avviket følger et mønster. Rundt 900 poeng ligger menns tall nær hverandre, men de sprer seg mot begge ender av skalaen. Kvinnenes seriepoeng ligger 60–150 poeng *under* mangekamptabellen i sprint, hekk og høyde, men *over* den i stav og kast i nedre del av skalaen (stav 2,26 m gir 500 mot 302).
- WA Scoring 2025 treffer heller ikke. Eksempel: 200 m menn 23,92 gir 655 i kalkulatoren, 681 i WA 2025 og 700 i mangekamptabellen.
- En enkel potensformel av typen `a·(b−x)^c` passer ikke. Tilpasset til fem punkter gir den avvik på 3–10 poeng. Tabellen er derfor trolig laget på en annen måte, for eksempel stykkevis eller med en egen skala.

**Konklusjon:** Senior-serietabellen er et eget system. Vi kan ikke regne den ut med motorene vi planlegger, så den trenger egen kilde eller egne parametre (B-23).

**Oppfølging:**
1. Spør NFIF om den offisielle tabellen eller formelen (`docs/henvendelser/2026-09-26-nfif-tyrving-avvik.md`).
2. Når motorene for Combined Events og masters er bygget, kjøres en større sammenligning: flere punkter per øvelse, og testing av om «Sr»-kolonnen i masters-serietabellen kan være en annen utgave av serietabellen.
3. Reserveløsning: tilpasse parametre fra kalkulatoren, med tillatelse fra dem som drifter den.

## Data

Kolonnen «NFIF masters, Sr» viser hvilket poengtall resultatet har i NFIF-arket. Kalkulatoren ble brukt med resultatene i punktumformat (for eksempel `1.51.41`). Til sammen ble det sendt noen få skjemainnsendinger per kjønn med alle øvelser samlet.

### Menn senior

| Øvelse | Resultat | Kalkulator (seriepoeng) | NFIF masters, «Sr»-kolonne | Kilde for «Sr» | WA 2025 (løp) |
|---|---|---:|---:|---|---:|
| 60m | 6.42 | 1164 | 1099 | mangekamptabell (= Combined Events) | 1256 |
| 60m | 6.95 | 886 | 900 | mangekamptabell (= Combined Events) | 964 |
| 60m | 7.54 | 646 | 700 | mangekamptabell (= Combined Events) | 685 |
| 60m | 8.21 | 433 | 500 | mangekamptabell (= Combined Events) | 398 |
| 60m | 9.02 | 221 | 300 | mangekamptabell (= Combined Events) | 193 |
| 100m | 9.98 | 1135 | 1101 | mangekamptabell (= Combined Events) | 1199 |
| 100m | 10.82 | 888 | 901 | mangekamptabell (= Combined Events) | 898 |
| 100m | 11.75 | 664 | 701 | mangekamptabell (= Combined Events) | 678 |
| 100m | 12.81 | 454 | 501 | mangekamptabell (= Combined Events) | 400 |
| 100m | 14.09 | 248 | 300 | mangekamptabell (= Combined Events) | 200 |
| 200m | 19.93 | 1137 | 1100 | mangekamptabell (= Combined Events) | 1200 |
| 200m | 21.83 | 881 | 900 | mangekamptabell (= Combined Events) | 899 |
| 200m | 23.92 | 655 | 700 | mangekamptabell (= Combined Events) | 681 |
| 200m | 26.31 | 452 | 500 | mangekamptabell (= Combined Events) | 400 |
| 200m | 29.18 | 265 | 300 | mangekamptabell (= Combined Events) | 200 |
| 400m | 44.23 | 1130 | 1100 | mangekamptabell (= Combined Events) | 1200 |
| 400m | 48.19 | 881 | 900 | mangekamptabell (= Combined Events) | 969 |
| 400m | 52.58 | 662 | 700 | mangekamptabell (= Combined Events) | 700 |
| 400m | 57.57 | 481 | 500 | mangekamptabell (= Combined Events) | 468 |
| 400m | 1.03.57 | 318 | 300 | mangekamptabell (= Combined Events) | 200 |
| 800m | 1.43.55 | 1114 | 1100 | masters-serieark | 1200 |
| 800m | 1.51.41 | 880 | 900 | masters-serieark | 986 |
| 800m | 2.00.12 | 685 | 700 | masters-serieark | 758 |
| 800m | 2.10.08 | 523 | 500 | masters-serieark | 500 |
| 800m | 2.22.12 | 377 | 300 | masters-serieark | 300 |
| 1500m | 3.32.81 | 1090 | 1100 | masters-serieark | – |
| 1500m | 3.48.97 | 876 | 900 | masters-serieark | – |
| 1500m | 4.06.88 | 697 | 700 | masters-serieark | – |
| 1500m | 4.27.36 | 543 | 500 | masters-serieark | – |
| 1500m | 4.52.12 | 393 | 300 | masters-serieark | – |
| 3000m | 7.37.11 | 1081 | 1100 | masters-serieark | 1194 |
| 3000m | 8.15.44 | 881 | 900 | masters-serieark | 967 |
| 3000m | 8.57.94 | 696 | 700 | masters-serieark | 700 |
| 3000m | 9.46.50 | 530 | 500 | masters-serieark | 500 |
| 3000m | 10.45.25 | 369 | 300 | masters-serieark | 300 |
| 5000m | 13.09.73 | 1080 | 1100 | masters-serieark | 1174 |
| 5000m | 14.12.46 | 887 | 900 | masters-serieark | 958 |
| 5000m | 15.22.01 | 724 | 700 | masters-serieark | 700 |
| 5000m | 16.41.50 | 567 | 500 | masters-serieark | 500 |
| 5000m | 18.17.65 | 411 | 300 | masters-serieark | 300 |
| 10000m | 27.33.06 | 1066 | 1100 | masters-serieark | 1174 |
| 10000m | 29.51.52 | 876 | 900 | masters-serieark | 967 |
| 10000m | 32.25.02 | 714 | 700 | masters-serieark | 760 |
| 10000m | 35.20.46 | 560 | 500 | masters-serieark | 555 |
| 10000m | 38.52.67 | 406 | 300 | masters-serieark | 300 |
| 60mhekk106,7cm | 7.54 | 1088 | 1101 | mangekamptabell (= Combined Events) | 1191 |
| 60mhekk106,7cm | 8.33 | 858 | 900 | mangekamptabell (= Combined Events) | 898 |
| 60mhekk106,7cm | 9.21 | 671 | 700 | mangekamptabell (= Combined Events) | 694 |
| 60mhekk106,7cm | 10.22 | 497 | 500 | mangekamptabell (= Combined Events) | 458 |
| 60mhekk106,7cm | 11.45 | 319 | 300 | mangekamptabell (= Combined Events) | 200 |
| 110mhekk106,7cm | 13.05 | 1151 | 1101 | mangekamptabell (= Combined Events) | 1200 |
| 110mhekk106,7cm | 14.59 | 875 | 900 | mangekamptabell (= Combined Events) | 962 |
| 110mhekk106,7cm | 16.29 | 672 | 700 | mangekamptabell (= Combined Events) | 692 |
| 110mhekk106,7cm | 18.25 | 512 | 500 | mangekamptabell (= Combined Events) | 400 |
| 110mhekk106,7cm | 20.65 | 368 | 300 | mangekamptabell (= Combined Events) | 200 |
| 400mhekk91,4cm | 47.58 | 1143 | 1100 | masters-serieark | 1253 |
| 400mhekk91,4cm | 52.24 | 889 | 900 | masters-serieark | 1000 |
| 400mhekk91,4cm | 57.40 | 695 | 700 | masters-serieark | 792 |
| 400mhekk91,4cm | 1.03.27 | 546 | 500 | masters-serieark | 567 |
| 400mhekk91,4cm | 1.10.33 | 416 | 300 | masters-serieark | 300 |
| 3000mhinder91,4cm | 8.20.96 | 1029 | 1100 | masters-serieark | – |
| 3000mhinder91,4cm | 9.14.32 | 811 | 900 | masters-serieark | – |
| 3000mhinder91,4cm | 10.13.47 | 620 | 700 | masters-serieark | – |
| 3000mhinder91,4cm | 11.21.07 | 452 | 500 | masters-serieark | – |
| 3000mhinder91,4cm | 12.42.85 | 296 | 300 | masters-serieark | – |
| Kappgang3000m | 11.31.74 | 907 | 1100 | masters-serieark | 1099 |
| Kappgang3000m | 12.39.41 | 722 | 900 | masters-serieark | 900 |
| Kappgang3000m | 13.54.43 | 555 | 700 | masters-serieark | 782 |
| Kappgang3000m | 15.20.16 | 401 | 500 | masters-serieark | 600 |
| Kappgang3000m | 17.03.87 | 255 | 300 | masters-serieark | 400 |
| Kappgang5000m | 19.26.41 | 908 | 1100 | masters-serieark | 1098 |
| Kappgang5000m | 21.20.88 | 723 | 900 | masters-serieark | 900 |
| Kappgang5000m | 23.27.79 | 556 | 700 | masters-serieark | 779 |
| Kappgang5000m | 25.52.83 | 401 | 500 | masters-serieark | 600 |
| Kappgang5000m | 28.48.28 | 255 | 300 | masters-serieark | 400 |
| Kappgang10000m | 40.57.05 | 909 | 1100 | masters-serieark | 1087 |
| Kappgang10000m | 44.57.89 | 724 | 900 | masters-serieark | 900 |
| Kappgang10000m | 49.24.91 | 556 | 700 | masters-serieark | 759 |
| Kappgang10000m | 54.30.07 | 401 | 500 | masters-serieark | 591 |
| Kappgang10000m | 1:00.39.21 | 255 | 300 | masters-serieark | 400 |
| Kappgang20000m | 1:25.00.70 | 910 | 1100 | masters-serieark | 1085 |
| Kappgang20000m | 1:33.14.04 | 726 | 900 | masters-serieark | 900 |
| Kappgang20000m | 1:42.21.00 | 560 | 700 | masters-serieark | 756 |
| Kappgang20000m | 1:52.46.10 | 406 | 500 | masters-serieark | 587 |
| Kappgang20000m | 2:05.22.25 | 261 | 300 | masters-serieark | 400 |
| Høyde | 2.31 | 1075 | 1101 | mangekamptabell (= Combined Events) | – |
| Høyde | 2.10 | 903 | 896 | mangekamptabell (= Combined Events) | – |
| Høyde | 1.88 | 722 | 696 | mangekamptabell (= Combined Events) | – |
| Høyde | 1.65 | 511 | 504 | mangekamptabell (= Combined Events) | – |
| Høyde | 1.38 | 207 | 303 | mangekamptabell (= Combined Events) | – |
| Høydeu/t | 1.88 | 1078 | 1106 | masters-serieark | – |
| Høydeu/t | 1.72 | 913 | 898 | masters-serieark | – |
| Høydeu/t | 1.56 | 738 | 704 | masters-serieark | – |
| Høydeu/t | 1.38 | 538 | 505 | masters-serieark | – |
| Høydeu/t | 1.17 | 220 | 301 | masters-serieark | – |
| Stav | 5.60 | 1038 | 1100 | mangekamptabell (= Combined Events) | – |
| Stav | 4.97 | 902 | 901 | mangekamptabell (= Combined Events) | – |
| Stav | 4.29 | 775 | 699 | mangekamptabell (= Combined Events) | – |
| Stav | 3.57 | 630 | 501 | mangekamptabell (= Combined Events) | – |
| Stav | 2.76 | 436 | 300 | mangekamptabell (= Combined Events) | – |
| Lengde | 8.15 | 1058 | 1099 | mangekamptabell (= Combined Events) | – |
| Lengde | 7.36 | 903 | 900 | mangekamptabell (= Combined Events) | – |
| Lengde | 6.51 | 720 | 700 | mangekamptabell (= Combined Events) | – |
| Lengde | 5.59 | 512 | 500 | mangekamptabell (= Combined Events) | – |
| Lengde | 4.56 | 263 | 301 | mangekamptabell (= Combined Events) | – |
| Lengdeu/t | 3.75 | 1074 | 1098 | masters-serieark | – |
| Lengdeu/t | 3.44 | 913 | 898 | masters-serieark | – |
| Lengdeu/t | 3.11 | 733 | 699 | masters-serieark | – |
| Lengdeu/t | 2.75 | 532 | 500 | masters-serieark | – |
| Lengdeu/t | 2.34 | 220 | 299 | masters-serieark | – |
| Tresteg | 16.75 | 1046 | 1101 | masters-serieark | – |
| Tresteg | 15.12 | 891 | 900 | masters-serieark | – |
| Tresteg | 13.40 | 712 | 701 | masters-serieark | – |
| Tresteg | 11.52 | 506 | 500 | masters-serieark | – |
| Tresteg | 9.40 | 258 | 300 | masters-serieark | – |
| Kule7,26kg | 20.00 | 1063 | 1100 | mangekamptabell (= Combined Events) | – |
| Kule7,26kg | 16.79 | 901 | 900 | mangekamptabell (= Combined Events) | – |
| Kule7,26kg | 13.53 | 703 | 700 | mangekamptabell (= Combined Events) | – |
| Kule7,26kg | 10.24 | 467 | 500 | mangekamptabell (= Combined Events) | – |
| Kule7,26kg | 6.87 | 197 | 300 | mangekamptabell (= Combined Events) | – |
| Diskos2,0kg | 60.89 | 1023 | 1100 | mangekamptabell (= Combined Events) | – |
| Diskos2,0kg | 51.40 | 880 | 900 | mangekamptabell (= Combined Events) | – |
| Diskos2,0kg | 41.72 | 716 | 700 | mangekamptabell (= Combined Events) | – |
| Diskos2,0kg | 31.78 | 519 | 500 | mangekamptabell (= Combined Events) | – |
| Diskos2,0kg | 21.46 | 256 | 300 | mangekamptabell (= Combined Events) | – |
| Slegge7,26kg/121,5cm | 73.53 | 1042 | 1100 | mangekamptabell (= Combined Events) | – |
| Slegge7,26kg/121,5cm | 61.70 | 900 | 900 | mangekamptabell (= Combined Events) | – |
| Slegge7,26kg/121,5cm | 49.74 | 749 | 700 | mangekamptabell (= Combined Events) | – |
| Slegge7,26kg/121,5cm | 37.61 | 580 | 500 | mangekamptabell (= Combined Events) | – |
| Slegge7,26kg/121,5cm | 25.24 | 376 | 300 | mangekamptabell (= Combined Events) | – |
| Spyd800gr | 83.67 | 1078 | 1100 | mangekamptabell (= Combined Events) | – |
| Spyd800gr | 70.67 | 911 | 900 | mangekamptabell (= Combined Events) | – |
| Spyd800gr | 57.45 | 725 | 700 | mangekamptabell (= Combined Events) | – |
| Spyd800gr | 43.95 | 543 | 500 | mangekamptabell (= Combined Events) | – |
| Spyd800gr | 30.03 | 331 | 300 | mangekamptabell (= Combined Events) | – |

### Kvinner senior

| Øvelse | Resultat | Kalkulator (seriepoeng) | NFIF masters, «Sr»-kolonne | Kilde for «Sr» | WA 2025 (løp) |
|---|---|---:|---:|---|---:|
| 60m | 7.23 | 997 | 1099 | mangekamptabell (= Combined Events) | 1097 |
| 60m | 7.83 | 788 | 901 | mangekamptabell (= Combined Events) | 899 |
| 60m | 8.50 | 593 | 701 | mangekamptabell (= Combined Events) | 753 |
| 60m | 9.26 | 416 | 501 | mangekamptabell (= Combined Events) | 559 |
| 60m | 10.18 | 238 | 300 | mangekamptabell (= Combined Events) | 363 |
| 100m | 11.25 | 1011 | 1101 | mangekamptabell (= Combined Events) | 1099 |
| 100m | 12.27 | 802 | 901 | mangekamptabell (= Combined Events) | 900 |
| 100m | 13.40 | 604 | 701 | mangekamptabell (= Combined Events) | 699 |
| 100m | 14.69 | 412 | 501 | mangekamptabell (= Combined Events) | 500 |
| 100m | 16.24 | 223 | 300 | mangekamptabell (= Combined Events) | 300 |
| 200m | 22.79 | 1011 | 1100 | mangekamptabell (= Combined Events) | 1156 |
| 200m | 24.86 | 819 | 900 | mangekamptabell (= Combined Events) | 955 |
| 200m | 27.14 | 640 | 700 | mangekamptabell (= Combined Events) | 755 |
| 200m | 29.75 | 466 | 500 | mangekamptabell (= Combined Events) | 556 |
| 200m | 32.88 | 297 | 300 | mangekamptabell (= Combined Events) | 357 |
| 400m | 51.00 | 1018 | 1100 | mangekamptabell (= Combined Events) | 1166 |
| 400m | 55.27 | 845 | 900 | mangekamptabell (= Combined Events) | 1000 |
| 400m | 59.99 | 680 | 700 | mangekamptabell (= Combined Events) | 800 |
| 400m | 1.05.37 | 529 | 500 | mangekamptabell (= Combined Events) | 667 |
| 400m | 1.11.84 | 390 | 300 | mangekamptabell (= Combined Events) | 487 |
| 800m | 1.59.15 | 1007 | 1100 | masters-serieark | 1177 |
| 800m | 2.08.85 | 819 | 900 | masters-serieark | 1000 |
| 800m | 2.19.63 | 672 | 700 | masters-serieark | 800 |
| 800m | 2.31.98 | 538 | 500 | masters-serieark | 661 |
| 800m | 2.46.98 | 405 | 300 | masters-serieark | 474 |
| 1500m | 4.05.41 | 994 | 1100 | masters-serieark | – |
| 1500m | 4.24.10 | 832 | 900 | masters-serieark | – |
| 1500m | 4.44.86 | 695 | 700 | masters-serieark | – |
| 1500m | 5.08.64 | 568 | 500 | masters-serieark | – |
| 1500m | 5.37.52 | 436 | 300 | masters-serieark | – |
| 3000m | 8.49.70 | 984 | 1100 | masters-serieark | 1100 |
| 3000m | 9.30.22 | 832 | 900 | masters-serieark | 1000 |
| 3000m | 10.15.24 | 700 | 700 | masters-serieark | 868 |
| 3000m | 11.06.82 | 575 | 500 | masters-serieark | 700 |
| 3000m | 12.09.44 | 445 | 300 | masters-serieark | 562 |
| 5000m | 15.28.68 | 959 | 1100 | masters-serieark | 1100 |
| 5000m | 16.39.69 | 818 | 900 | masters-serieark | 978 |
| 5000m | 17.58.56 | 692 | 700 | masters-serieark | 800 |
| 5000m | 19.28.92 | 570 | 500 | masters-serieark | 700 |
| 5000m | 21.18.62 | 441 | 300 | masters-serieark | 500 |
| 10000m | 32.33.32 | 955 | 1100 | masters-serieark | 1100 |
| 10000m | 35.09.91 | 815 | 900 | masters-serieark | 977 |
| 10000m | 38.03.85 | 689 | 700 | masters-serieark | 800 |
| 10000m | 41.23.14 | 566 | 500 | masters-serieark | 696 |
| 10000m | 45.25.08 | 438 | 300 | masters-serieark | 500 |
| 60mhekk84,0cm | 8.13 | 974 | 1100 | mangekamptabell (= Combined Events) | 1100 |
| 60mhekk84,0cm | 9.05 | 769 | 900 | mangekamptabell (= Combined Events) | 899 |
| 60mhekk84,0cm | 10.06 | 592 | 701 | mangekamptabell (= Combined Events) | 700 |
| 60mhekk84,0cm | 11.22 | 426 | 501 | mangekamptabell (= Combined Events) | 500 |
| 60mhekk84,0cm | 12.63 | 252 | 300 | mangekamptabell (= Combined Events) | 300 |
| 400mhekk76,2cm | 55.01 | 1019 | 1100 | masters-serieark | 1172 |
| 400mhekk76,2cm | 1.00.05 | 841 | 900 | masters-serieark | 1000 |
| 400mhekk76,2cm | 1.05.61 | 684 | 700 | masters-serieark | 864 |
| 400mhekk76,2cm | 1.11.95 | 556 | 500 | masters-serieark | 700 |
| 400mhekk76,2cm | 1.19.59 | 455 | 300 | masters-serieark | 500 |
| 3000mhinder76,2cm | 9.20.57 | 1044 | 1100 | masters-serieark | – |
| 3000mhinder76,2cm | 10.19.23 | 852 | 900 | masters-serieark | – |
| 3000mhinder76,2cm | 11.24.39 | 698 | 700 | masters-serieark | – |
| 3000mhinder76,2cm | 12.39.05 | 557 | 500 | masters-serieark | – |
| 3000mhinder76,2cm | 14.09.69 | 413 | 300 | masters-serieark | – |
| Kappgang3000m | 12.23.93 | 961 | 1100 | masters-serieark | 1100 |
| Kappgang3000m | 13.37.44 | 789 | 900 | masters-serieark | 968 |
| Kappgang3000m | 14.59.09 | 642 | 700 | masters-serieark | 800 |
| Kappgang3000m | 16.32.65 | 501 | 500 | masters-serieark | 665 |
| Kappgang3000m | 18.26.22 | 355 | 300 | masters-serieark | 499 |
| Kappgang5000m | 21.31.02 | 961 | 1100 | masters-serieark | 1100 |
| Kappgang5000m | 23.38.48 | 790 | 900 | masters-serieark | 961 |
| Kappgang5000m | 26.00.06 | 642 | 700 | masters-serieark | 800 |
| Kappgang5000m | 28.42.28 | 502 | 500 | masters-serieark | 652 |
| Kappgang5000m | 31.59.22 | 356 | 300 | masters-serieark | 483 |
| Kappgang10000m | 42.40.51 | 1048 | 1100 | masters-serieark | 1169 |
| Kappgang10000m | 47.15.83 | 845 | 900 | masters-serieark | 1000 |
| Kappgang10000m | 52.21.66 | 681 | 700 | masters-serieark | 800 |
| Kappgang10000m | 58.12.08 | 528 | 500 | masters-serieark | 672 |
| Kappgang10000m | 1:05.17.48 | 372 | 300 | masters-serieark | 491 |
| Kappgang20000m | 1:31.49.06 | 961 | 1100 | masters-serieark | 1100 |
| Kappgang20000m | 1:40.56.86 | 789 | 900 | masters-serieark | 954 |
| Kappgang20000m | 1:51.05.38 | 641 | 700 | masters-serieark | 798 |
| Kappgang20000m | 2:02.42.60 | 499 | 500 | masters-serieark | 600 |
| Kappgang20000m | 2:16.49.00 | 353 | 300 | masters-serieark | 465 |
| Høyde | 1.90 | 960 | 1106 | mangekamptabell (= Combined Events) | – |
| Høyde | 1.74 | 808 | 903 | mangekamptabell (= Combined Events) | – |
| Høyde | 1.57 | 667 | 701 | mangekamptabell (= Combined Events) | – |
| Høyde | 1.39 | 509 | 502 | mangekamptabell (= Combined Events) | – |
| Høyde | 1.19 | 291 | 302 | mangekamptabell (= Combined Events) | – |
| Høydeu/t | 1.56 | 953 | 1095 | masters-serieark | – |
| Høydeu/t | 1.44 | 810 | 904 | masters-serieark | – |
| Høydeu/t | 1.31 | 672 | 707 | masters-serieark | – |
| Høydeu/t | 1.16 | 504 | 496 | masters-serieark | – |
| Høydeu/t | 1.01 | 296 | 305 | masters-serieark | – |
| Stav | 4.28 | 966 | 1099 | mangekamptabell (= Combined Events) | – |
| Stav | 3.83 | 859 | 900 | mangekamptabell (= Combined Events) | – |
| Stav | 3.35 | 750 | 700 | mangekamptabell (= Combined Events) | – |
| Stav | 2.83 | 636 | 500 | mangekamptabell (= Combined Events) | – |
| Stav | 2.26 | 500 | 302 | mangekamptabell (= Combined Events) | – |
| Lengde | 6.78 | 1011 | 1099 | mangekamptabell (= Combined Events) | – |
| Lengde | 6.16 | 878 | 899 | mangekamptabell (= Combined Events) | – |
| Lengde | 5.50 | 728 | 700 | mangekamptabell (= Combined Events) | – |
| Lengde | 4.78 | 570 | 500 | mangekamptabell (= Combined Events) | – |
| Lengde | 3.97 | 379 | 301 | mangekamptabell (= Combined Events) | – |
| Lengdeu/t | 3.00 | 959 | 1104 | masters-serieark | – |
| Lengdeu/t | 2.78 | 805 | 896 | masters-serieark | – |
| Lengdeu/t | 2.56 | 666 | 700 | masters-serieark | – |
| Lengdeu/t | 2.32 | 511 | 504 | masters-serieark | – |
| Lengdeu/t | 2.04 | 283 | 301 | masters-serieark | – |
| Tresteg | 14.10 | 986 | 1100 | masters-serieark | – |
| Tresteg | 12.79 | 851 | 900 | masters-serieark | – |
| Tresteg | 11.39 | 701 | 700 | masters-serieark | – |
| Tresteg | 9.86 | 544 | 500 | masters-serieark | – |
| Tresteg | 8.14 | 348 | 300 | masters-serieark | – |
| Kule4,0kg | 18.54 | 1016 | 1100 | mangekamptabell (= Combined Events) | – |
| Kule4,0kg | 15.58 | 883 | 900 | mangekamptabell (= Combined Events) | – |
| Kule4,0kg | 12.58 | 742 | 700 | mangekamptabell (= Combined Events) | – |
| Kule4,0kg | 9.55 | 557 | 500 | mangekamptabell (= Combined Events) | – |
| Kule4,0kg | 6.45 | 290 | 300 | mangekamptabell (= Combined Events) | – |
| Diskos1,0kg | 62.31 | 1030 | 1100 | mangekamptabell (= Combined Events) | – |
| Diskos1,0kg | 52.42 | 895 | 900 | mangekamptabell (= Combined Events) | – |
| Diskos1,0kg | 42.33 | 757 | 700 | mangekamptabell (= Combined Events) | – |
| Diskos1,0kg | 31.96 | 611 | 500 | mangekamptabell (= Combined Events) | – |
| Diskos1,0kg | 21.21 | 415 | 300 | mangekamptabell (= Combined Events) | – |
| Slegge4,0kg/119,5cm | 71.95 | 1059 | 1100 | mangekamptabell (= Combined Events) | – |
| Slegge4,0kg/119,5cm | 60.30 | 929 | 900 | mangekamptabell (= Combined Events) | – |
| Slegge4,0kg/119,5cm | 48.53 | 792 | 700 | mangekamptabell (= Combined Events) | – |
| Slegge4,0kg/119,5cm | 36.60 | 637 | 500 | mangekamptabell (= Combined Events) | – |
| Slegge4,0kg/119,5cm | 24.43 | 445 | 300 | mangekamptabell (= Combined Events) | – |
| Spyd600gr | 62.30 | 1040 | 1100 | mangekamptabell (= Combined Events) | – |
| Spyd600gr | 52.04 | 886 | 900 | mangekamptabell (= Combined Events) | – |
| Spyd600gr | 41.68 | 727 | 700 | mangekamptabell (= Combined Events) | – |
| Spyd600gr | 31.21 | 566 | 500 | mangekamptabell (= Combined Events) | – |
| Spyd600gr | 20.58 | 368 | 300 | mangekamptabell (= Combined Events) | – |