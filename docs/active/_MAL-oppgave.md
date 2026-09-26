# AP-XXX: [kort tittel]

**Status:** Klar
**Opprettet:** ÅÅÅÅ-MM-DD (Cowork)
**Eier:** 🤖 Code | 🧑 Simen
**Avhenger av:** AP-XXX

<!--
Skriveregler for Cowork. Slett denne blokken når en oppgavefil lages fra malen.
- Oppgaven kjøres av Claude Opus 5.5 i en ikke-interaktiv loop. Ingen kan svare på spørsmål, så alt Code trenger
  skal stå her eller i filene det pekes til.
- Skriv hvorfor bak hver regel. En begrunnelse gjør at Code kan handle riktig i tilfeller vi ikke forutså.
- Skriv hva Code skal gjøre, ikke bare hva det skal la være. Navngi konkrete mønstre i stedet for generelle
  formaninger. Unngå STORE BOKSTAVER og «MÅ».
- Hold fila kort. Pek til filer og celler i stedet for å lime inn utdrag.
- Hver oppgave skal ha en sjekk Code kan kjøre selv, med konkrete tall.
-->

## Mål

Hva som skal virke når oppgaven er ferdig, sett fra brukeren eller verifiseringskjeden. Én til tre setninger.

## Hvorfor

Hvilket mål dette flytter, og hvorfor denne oppgaven kommer nå. Ta med bakgrunn Code ellers ville måttet gjette,
for eksempel hvem som bruker resultatet og hva en feil vil koste.

## Les dette før du koder

Filene Code skal åpne og forstå før det skriver noe. Åpne dem i stedet for å anta hva de inneholder.

- `athletics_scoring/...` — [mønsteret som skal følges, f.eks. «følg `tyrving.py`»]
- `sources/...` — [ark, side eller celle, og hva som står der]
- `docs/BEREGNINGSVALG.md` — [BV-numrene som gjelder]

## Verifiserte fakta

Det Cowork har kontrollert mot kildene, med eksakte filstier, sider, ark og celler. Skill mellom det som er
bekreftet og det som bare er antatt.

- [bekreftet fakta]

**Ikke bekreftet, sjekk selv først:** [antakelser]

## Løsningsretning

Det som er bestemt, og så konkret som mulig. Følg eksisterende mønstre i koden. Er noe ikke bestemt, skriv hva
Code kan velge selv og hva som krever blokkering (se «Når du skal stoppe»).

## Beregningsvalg

Valgene fra `docs/BEREGNINGSVALG.md` som denne oppgaven implementerer. Hvert valg skal kunne spores fra koden:
`calculation_steps` viser BV-nummeret når valget påvirker resultatet.

- BV-XXX — [kort]

Trenger du et valg som ikke står der, skriv det under «Innboks» i backloggen og velg det alternativet som er
strengest mot utøveren (lavest poeng), eller blokker hvis valget endrer poeng i vanlige tilfeller.

## Kontrolltall

Konkrete input og forventet output fra kilden, slik at Code kan teste før det bygger mer. Oppgi kilden for hvert tall.

| Input | Forventet | Kilde |
|---|---|---|
| ... | ... | `sources/...` side/ark/celle |

## Utenfor scope

Det som ikke skal gjøres i denne oppgaven, og hvorfor. Nevn fristelser konkret (f.eks. «ikke lag et felles
rammeverk for alle tabeller ennå, det kommer i AP-XXX»). Hold endringene til det oppgaven krever: ingen nye
abstraksjoner for engangsbruk og ingen feilhåndtering for tilfeller som ikke kan oppstå.

## Fallgruver

- [kjente feller, med hvorfor]

## Når du skal stoppe

Sett oppgaven til `Blokkert` med begrunnelse, og avslutt, når:
- en test bare kan bli grønn ved å endre en test, en låst fixture eller `sources/`
- kildene er uenige med hverandre, eller med kontrolltallene her, og `docs/KILDEAVVIK.md` ikke dekker det
- [oppgavespesifikke stopp]

Alt annet avgjør du selv innenfor løsningsretningen, og skriver valget i sluttrapporten.

## Akseptansekriterier

Verifiserbare. Løsningen skal virke for alle gyldige input, ikke bare for kontrolltallene. Ikke hardkod
forventede verdier eller lag spesialtilfeller for testene.

- [ ] Kontrolltallene over er egne testcaser og er grønne
- [ ] [oppgavespesifikt, med kommando Code kan kjøre]
- [ ] `pytest -q && ruff check . && mypy athletics_scoring` er grønt
- [ ] Ingen endringer i `sources/` eller låste `tests/fixtures/`
- [ ] Midlertidige filer og hjelpeskript fra underveis er fjernet
- [ ] Før commit: gått gjennom kriteriene ett for ett mot `git diff`, og rettet det som mangler

## Sluttrapport (fylles av Code)

- **Gjort:**
- **Bevis:** kommandoene som ble kjørt og resultatet (antall tester, eventuelle avvik mot fasit)
- **Valg tatt underveis:** med begrunnelse
- **Avvik fra oppgavefila:**
- **Funn som bør bli egne oppgaver:** (skriv også til `docs/BACKLOG.md` → Innboks)
