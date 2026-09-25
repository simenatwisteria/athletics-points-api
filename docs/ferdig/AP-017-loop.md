# AP-017: Loop-oppsett

**Status:** Ferdig
**Opprettet:** 2026-09-25 (PROMPT-001, oppgavefil skrevet ved avslutning)
**Eier:** 🤖 Code
**Avhenger av:** —

## Sluttrapport

- **Gjort:** `.claude/commands/loop.md` er prompten for én runde: én oppgave etter backlogregelen, verifisering,
  commit og backlogoppdatering. Den avslutter med `LOOP-STATUS: fremgang | blokkert | ingen-oppgave`.
  `scripts/loop.sh [maks]` starter en fersk `claude -p` per runde (`acceptEdits`, begrenset verktøyliste uten
  push/nettverk, `--max-budget-usd` per runde, standard 5). Logg per runde i `logs/loop/`, som er gitignored.
- **Stoppbetingelser:** rødt eller urent arbeidstre før start, blokkert, ingen oppgave, ingen ny commit i en
  runde, røde tester etter en runde, urent arbeidstre etter en runde, endring i `sources/`, endret eller slettet
  eksisterende fixture (nye fixture-filer er tillatt), ugyldig eller manglende statuslinje, maks runder.
- **Avvik:** loopen pusher aldri. Simen ser gjennom commitene og pusher selv.
- **Merk:** Claude Code har en innebygd `/loop`-kommando. `.claude/commands/loop.md` er navngitt slik
  PROMPT-001 ba om, og `loop.sh` leser fila direkte, så navnelikheten påvirker ikke skriptet. Kjøres runden
  interaktivt, kan `/loop` treffe den innebygde kommandoen.
