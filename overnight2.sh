#!/usr/bin/env bash
# Study 2, Phase 0 then Phase 1 (DESIGN2.md). Phase 1 runs only if arm S passes.
# Optional first argument: a start time (HH:MM, today) to wait for.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p logs runs/study2
log() { echo "$(date -Iseconds) $*" | tee -a logs/overnight2.log; }

if [ $# -ge 1 ]; then
  wait_s=$(( $(date -j -f "%H:%M" "$1" +%s) - $(date +%s) ))
  [ "$wait_s" -gt 0 ] && { log "waiting ${wait_s}s until $1"; sleep "$wait_s"; }
fi

log "assent survey start"
.venv/bin/python assent2.py runs/assent2 > logs/assent2.log 2>&1
code=$?
echo "EXIT=$code" >> logs/assent2.log
[ "$code" -ne 0 ] && { log "assent survey crashed (exit $code); nothing run"; exit 1; }
if ! .venv/bin/python -I -c "import json,sys; s=json.load(open('runs/assent2/assent_summary.json')); sys.exit(1 if s['S']['dropped'] else 0)"; then
  log "arm S dropped by binding dissent; phase 1 not run"; exit 0
fi

for step in "stories.py runs/study2/stories.jsonl" \
            "extract.py runs/study2/stories.jsonl runs/study2/acts.npz" \
            "analyze.py runs/study2/acts.npz runs/study2/phase1.json"; do
  name=${step%% *}
  log "$name start"
  .venv/bin/python $step > "logs/${name%.py}.log" 2>&1
  code=$?
  echo "EXIT=$code" >> "logs/${name%.py}.log"
  [ "$code" -ne 0 ] && { log "$name failed (exit $code); stopping"; exit 1; }
done
log "done"
