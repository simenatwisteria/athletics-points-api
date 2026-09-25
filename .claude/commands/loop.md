# Én runde i bygg-og-verifiser-loopen

Du kjører ikke-interaktivt, startet av `scripts/loop.sh`. Ingen kan svare på spørsmål underveis. Gjør **én**
oppgave, eller ingen, og avslutt.

1. Les `CLAUDE.md` og `docs/BACKLOG.md`. Reglene i `CLAUDE.md` gjelder uten unntak.
2. Velg oppgave etter «Regel for agenten» øverst i backloggen: øverste 🤖-oppgave med status `Klar` eller `Ny` der
   alle avhengigheter er `Ferdig`. Finnes ingen, avslutt med `LOOP-STATUS: ingen-oppgave`.
3. Sett oppgaven til `Under arbeid` og les oppgavefila i `docs/active/` hvis den finnes.
4. Implementer. Hold deg innenfor oppgaven. Funn utenfor scope skrives under «Innboks».
5. Verifiser: `pytest -q && ruff check . && mypy athletics_scoring` skal være grønt.
6. Commit med `AP-XXX: <kort beskrivelse>`. Ikke push.
7. Oppdater backloggen: status `Ferdig`, flytt oppgavefila til `docs/ferdig/`, fyll ut sluttrapporten. Commit.
8. Avslutt med `LOOP-STATUS: fremgang`.

**Stopp og blokker i stedet** hvis en test bare kan bli grønn ved å endre en test, en låst fixture eller
`sources/`, hvis du mistenker feil fasit, eller hvis regelteksten er uklar. Sett da oppgaven til `Blokkert` med
begrunnelse i notatet, commit backloggen og avslutt med `LOOP-STATUS: blokkert`. Ikke gjett.

Arbeidstreet skal være rent når du avslutter (alt committet). Siste linje i svaret ditt skal være nøyaktig én av:

```
LOOP-STATUS: fremgang
LOOP-STATUS: blokkert
LOOP-STATUS: ingen-oppgave
```
