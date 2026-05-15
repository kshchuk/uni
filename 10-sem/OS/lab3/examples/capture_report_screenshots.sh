#!/usr/bin/env bash
# Re-capture GUI screenshots for the LaTeX report.
# Uses LAB3_SHM_ID_FILE so poke always targets the supervisor segment.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SHM_ID_FILE="${SHM_ID_FILE:-/tmp/lab3_capture_shm_id}"
export LAB3_SHM_ID_FILE="$SHM_ID_FILE"
export LAB3_CAPTURE=1
# shellcheck source=examples/capture_window_lib.sh
source "$ROOT/examples/capture_window_lib.sh"

need_bin() {
  if [[ ! -x "$ROOT/bin/$1" ]]; then
    echo "missing $ROOT/bin/$1 — run: make build" >&2
    exit 1
  fi
}
need_bin supervisor
need_bin process_a
need_bin process_b
need_bin poke

capture_png() {
  capture_supervisor_window "$1" "$SHM_ID"
}

cleanup() {
  if [[ -n "${SV_PID:-}" ]] && kill -0 "$SV_PID" 2>/dev/null; then
    kill "$SV_PID" 2>/dev/null || true
    wait "$SV_PID" 2>/dev/null || true
  fi
  rm -f "$SHM_ID_FILE"
  while read -r id; do
    [[ -n "$id" ]] && ipcrm -m "$id" 2>/dev/null || true
  done < <(ipcs -m 2>/dev/null | awk -v u="$(whoami)" '$1=="m" && $4==u {print $2}')
}
trap cleanup EXIT

kill_supervisors() {
  pkill -9 -f "$ROOT/bin/supervisor" 2>/dev/null || true
  sleep 0.5
}

wait_shm_id() {
  local i id
  for i in $(seq 1 60); do
    if [[ -f "$SHM_ID_FILE" ]]; then
      id="$(tr -d ' \n' <"$SHM_ID_FILE")"
      if [[ "$id" =~ ^[0-9]+$ ]]; then
        echo "$id"
        return 0
      fi
    fi
    sleep 0.25
  done
  echo "[capture] SHM id file not written: $SHM_ID_FILE" >&2
  return 1
}

poke() {
  "$ROOT/bin/poke" --id "$SHM_ID" "$@"
}

poke_print() {
  "$ROOT/bin/poke" --id "$SHM_ID" --print 2>/dev/null
}

enter_b() {
  poke_print | sed -n 's/.*EnterB=\([0-9]*\).*/\1/p'
}

wait_enter_b_gt() {
  local base="$1" desc="$2" timeout="${3:-20}"
  local end=$((SECONDS + timeout))
  while (( SECONDS < end )); do
    local cur
    cur="$(enter_b)"
    if [[ -n "$cur" && "$cur" -gt "$base" ]]; then
      echo "[capture] ready: $desc (EnterB=$cur)"
      return 0
    fi
    sleep 0.25
  done
  echo "[capture] warn: timeout for: $desc" >&2
  return 0
}

wait_poke() {
  local desc="$1" timeout="${2:-20}"
  shift 2
  local end=$((SECONDS + timeout))
  while (( SECONDS < end )); do
    if poke_print | grep -qE "$@"; then
      echo "[capture] ready: $desc"
      return 0
    fi
    sleep 0.25
  done
  echo "[capture] warn: timeout for: $desc (continuing)" >&2
  poke_print || true
  return 0
}

start_supervisor() {
  kill_supervisors
  rm -f "$SHM_ID_FILE"
  "$ROOT/bin/supervisor" >/tmp/lab3_capture_supervisor.log 2>&1 &
  SV_PID=$!
  for i in $(seq 1 40); do
    if osascript -e 'tell application "System Events" to exists window 1 of process "supervisor"' 2>/dev/null | grep -q true; then
      break
    fi
    sleep 0.25
  done
  SHM_ID="$(wait_shm_id)"
  export LAB3_SHM_ID="$SHM_ID"
  echo "[capture] SHM id=$SHM_ID (fullscreen)"
  wait_supervisor_ready "$SHM_ID" || true
  sleep 1.5
}

echo "[capture] starting supervisor…"
start_supervisor

echo "[capture] 01-startup.png"
capture_png "$ROOT/screenshots/01-startup.png"

poke --auto on
wait_poke "auto stress" 25 'EnterA=[1-9][0-9]*' || wait_poke "auto stress (fallback)" 25 'EnterA=[1-9]'
sleep 1
echo "[capture] 02-automode.png"
capture_png "$ROOT/screenshots/02-automode.png"
poke --auto off
sleep 0.8

echo "[capture] preparing manual deal…"
BEFORE_B="$(enter_b)"
for _ in 1 2 3 4 5; do poke --insert; sleep 0.2; done
poke --request 1
wait_enter_b_gt "$BEFORE_B" "manual deal"
sleep 0.8
echo "[capture] 04-manual-deal.png"
capture_png "$ROOT/screenshots/04-manual-deal.png"

echo "[capture] preparing manual refuse (code 4 — недостатньо монет у банку)…"
# Drain 1-kop coins so a large coin cannot be broken into 1-kop pieces.
for _ in $(seq 1 35); do
  poke --insert
  sleep 0.08
  poke --request 1
  sleep 0.12
done
poke --insert
sleep 0.25
poke --request 1
wait_poke "manual refuse" 25 'Last: REFUSE 4'
sleep 0.8
echo "[capture] 05-manual-refuse.png"
capture_png "$ROOT/screenshots/05-manual-refuse.png"

echo "[capture] rebuilding nosync workers for 03-nosync…"
(
  cd "$ROOT"
  go build -tags=nosync -o bin/process_a ./cmd/process_a
  go build -tags=nosync -o bin/process_b ./cmd/process_b
)

kill "$SV_PID" 2>/dev/null || true
wait "$SV_PID" 2>/dev/null || true
SV_PID=
sleep 1
while read -r id; do
  [[ -n "$id" ]] && ipcrm -m "$id" 2>/dev/null || true
done < <(ipcs -m 2>/dev/null | awk -v u="$(whoami)" '$1=="m" && $4==u {print $2}')

echo "[capture] nosync supervisor…"
start_supervisor
# Workers treat delay<=0 as 50ms; use 1ms so A/B overlap inside the CS.
poke --delay-a 1 --delay-b 1
poke --auto on
wait_poke "nosync collisions" 40 'Collisions=[1-9]' \
  || wait_poke "nosync max-in-cs" 40 'MaxInCS=[2-9]' \
  || wait_poke "nosync max-in-cs (fallback)" 10 'MaxInCS=2'
poke --auto off
sleep 0.3
echo "[capture] 03-nosync-collisions.png"
capture_png "$ROOT/screenshots/03-nosync-collisions.png"

echo "[capture] restoring default (atomic) workers…"
(
  cd "$ROOT"
  make build >/dev/null
)

kill "$SV_PID" 2>/dev/null || true
wait "$SV_PID" 2>/dev/null || true
SV_PID=

echo "[capture] checksums:"
md5 -q "$ROOT/screenshots/"*.png | sort | uniq -c
echo "[capture] done."
ls -la "$ROOT/screenshots/"*.png
