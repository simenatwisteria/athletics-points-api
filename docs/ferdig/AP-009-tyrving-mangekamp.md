# AP-009: Tyrving mangekamp under 15 år

**Status:** Ferdig 2026-09-26 (generell summering). Faste mangekamper per klasse venter på oversikt fra NFIF.
**Eier:** 🤖 Code
**Avhenger av:** AP-008

## Sluttrapport

- **Gjort:** `TyrvingCalculator.calculate_combined(gender, age_class, events)` summerer Tyrving-poengene for
  øvelser brukeren velger fritt, og returnerer `CombinedScoreResult` med poeng og forklaring per øvelse. Den
  avviser tom liste, samme øvelse to ganger og klasser fra 15 år (der gjelder WA-tabellene, jf. BESLUTNINGER kap. 3).
- **For frontend (etter avtale med Simen 2026-09-26):** `EventInfo.input` (`InputSpec`) sier hvordan resultatet
  skal tastes inn: tid eller distanse, oppløsning (0,01 / 0,1), om minutter brukes, og om manuell tid er lov.
  En test sjekker at `manual_timing_allowed` stemmer med hva kalkulatoren faktisk godtar for alle øvelser.
- **Ikke gjort:** Hvilke faste mangekamper som finnes per klasse og kjønn (f.eks. femkamp J13). Det legges inn som
  data når Simen har en oversikt fra NFIF. Står i Innboks.
- **Tester:** 4 nye (93 totalt).
