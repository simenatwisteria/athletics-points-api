# AP-006: Tyrving — regeltolkning fra DOC/PDF som eksplisitte testcaser

**Status:** Ferdig
**Opprettet:** 2026-09-25 (PROMPT-001, oppgavefil skrevet ved avslutning)
**Eier:** 🤖 Code
**Avhenger av:** AP-001

## Sluttrapport

- **Gjort:** `tests/fixtures/tyrving_rules.json` har de fem reglene ordrett (R1 manuell tid, R2 hundredeler/tideler,
  R3 avrunding, R4 tre-intervall, R5 automatisk tidtaking). 29 caser med input, effektivt resultat, utregning,
  poeng og tolkningsnivå (`direkte` / `tolkning` / `regneark`), og 3 åpne spørsmål. Parametrene er PDF-ens.
  Alle casene er kontrollregnet med `Decimal` mot `tyrving_parameters_2014.json`. `tests/test_tyrving_rules.py`
  sjekker strukturen og at hver case peker på en ekte kombinasjon.
- **Kilder:** DOC-filene er konvertert med LibreOffice. Regelteksten er identisk med PDF-ens og har ingen
  regler utover dem.
- **Avvik fra backlog-teksten:** «80 %-grensen» er dekket som R4 (tre-intervall), ikke som egen regel. Teksten
  har ingen annen 80 %-regel.
- **Funn:** manuell tid på 40 m og resultat 0 er ikke regulert. Begge står som spørsmål i AP-007.
