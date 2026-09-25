#!/usr/bin/env bash
# Bygg-og-verifiser-loop: kjører én fersk Claude Code-økt per runde mot docs/BACKLOG.md.
#
#   scripts/loop.sh [maks_runder]        (standard 10)
#
# Miljøvariabler: LOOP_MODEL (valgfri modell), LOOP_BUDGET_USD (maks kostnad per runde, standard 5).
# Loopen pusher aldri. Se gjennom commitene og push selv.
#
# Stopper når: en oppgave er blokkert, ingen oppgave er tilgjengelig, en runde ikke gir ny commit,
# testene er røde, arbeidstreet ikke er rent, sources/ eller en eksisterende fixture er endret,
# eller maks antall runder er nådd.
set -euo pipefail

cd "$(dirname "$0")/.."
MAX_ROUNDS="${1:-10}"
BUDGET="${LOOP_BUDGET_USD:-5}"
LOG_DIR="logs/loop"
PROMPT_FILE=".claude/commands/loop.md"
ALLOWED_TOOLS="Read,Edit,Write,Glob,Grep,Bash(pytest:*),Bash(ruff:*),Bash(mypy:*),Bash(python:*),Bash(python3:*),Bash(soffice:*),Bash(git status:*),Bash(git diff:*),Bash(git log:*),Bash(git show:*),Bash(git add:*),Bash(git commit:*),Bash(git mv:*),Bash(ls:*),Bash(cat:*),Bash(grep:*)"

mkdir -p "$LOG_DIR"
if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

stop() { echo "⏹  $1"; exit "${2:-0}"; }

verify() { pytest -q >/dev/null && ruff check . >/dev/null && mypy athletics_scoring >/dev/null; }

[[ -z "$(git status --porcelain)" ]] || stop "Arbeidstreet er ikke rent før start — commit eller rydd først." 1
verify || stop "Testene er røde før start — loopen starter ikke på rødt." 1

START="$(git rev-parse HEAD)"
for round in $(seq 1 "$MAX_ROUNDS"); do
  before="$(git rev-parse HEAD)"
  log="$LOG_DIR/$(date +%Y%m%d-%H%M%S)-runde-$round.log"
  echo "▶  Runde $round/$MAX_ROUNDS (logg: $log)"

  model_args=()
  [[ -n "${LOOP_MODEL:-}" ]] && model_args=(--model "$LOOP_MODEL")
  claude -p "$(cat "$PROMPT_FILE")" \
    --permission-mode acceptEdits \
    --allowedTools "$ALLOWED_TOOLS" \
    --max-budget-usd "$BUDGET" \
    ${model_args[@]+"${model_args[@]}"} >"$log" 2>&1 || stop "claude avsluttet med feil i runde $round — se $log" 1

  status="$(grep -Eo 'LOOP-STATUS: [a-z-]+' "$log" | tail -1 | cut -d' ' -f2 || true)"
  echo "   status: ${status:-mangler}"

  [[ -z "$(git status --porcelain)" ]] || stop "Arbeidstreet er ikke rent etter runde $round — se $log" 1
  if ! git diff --quiet "$START" HEAD -- sources/; then
    stop "sources/ er endret i loopen — det er forbudt. Se git log $START..HEAD" 1
  fi
  if git diff --name-status "$START" HEAD -- tests/fixtures/ | grep -qE '^[MDR]'; then
    stop "En eksisterende fixture er endret i loopen — det er forbudt. Se git log $START..HEAD" 1
  fi
  verify || stop "Testene er røde etter runde $round — se $log" 1

  case "$status" in
    blokkert) stop "Blokkert — se docs/BACKLOG.md" ;;
    ingen-oppgave) stop "Ingen oppgave agenten kan ta nå — resten venter på Simen eller er ferdig" ;;
    fremgang) ;;
    *) stop "Runde $round endte uten gyldig LOOP-STATUS — se $log" 1 ;;
  esac
  [[ "$(git rev-parse HEAD)" != "$before" ]] || stop "Ingen ny commit i runde $round — ingen framdrift" 1
done
stop "Nådde maks $MAX_ROUNDS runder"
