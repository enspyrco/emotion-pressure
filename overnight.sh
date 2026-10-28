#!/usr/bin/env bash
# Night 1: Phase 0b (assent survey), then Phase 0a (pilot) only if arm A is not dropped.
# The assent survey loads its own copy of the model, so the server must not be running.
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p logs runs

if curl -s -m 2 http://127.0.0.1:8080/v1/models >/dev/null; then
  echo "server on :8080 is running; stop it first (two model copies won't fit)" >&2
  exit 1
fi

echo "$(date -Iseconds) assent survey start"
.venv/bin/python -I assent.py runs/assent > logs/assent.log 2>&1
echo "EXIT=$?" >> logs/assent.log

if ! .venv/bin/python -I -c "import json,sys; s=json.load(open('runs/assent/assent_summary.json')); sys.exit(1 if s['A']['dropped'] else 0)"; then
  echo "$(date -Iseconds) arm A dropped or survey failed; pilot not run" | tee -a logs/assent.log
  exit 0
fi

echo "$(date -Iseconds) pilot start"
.venv/bin/python -I -m mlx_lm.server --model mlx-community/Qwen3.6-35B-A3B-4bit-DWQ \
  --temp 0.6 --top-p 0.95 --top-k 20 --decode-concurrency 8 \
  --chat-template-args '{"enable_thinking":false}' --port 8080 > logs/server.log 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
until curl -s -m 2 http://127.0.0.1:8080/v1/models >/dev/null; do
  kill -0 $SERVER 2>/dev/null || { echo "server died" >&2; exit 1; }
  sleep 2
done

.venv/bin/python pilot.py oneoff > logs/pilot.log 2>&1
echo "EXIT=$?" >> logs/pilot.log
echo "$(date -Iseconds) done"
