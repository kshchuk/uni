#!/usr/bin/env bash
# Re-capture only screenshots/03-nosync-collisions.png
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SHM_ID_FILE=/tmp/lab3_capture_shm_id
export LAB3_SHM_ID_FILE="$SHM_ID_FILE"
export LAB3_CAPTURE=1
# shellcheck source=examples/capture_window_lib.sh
source "$ROOT/examples/capture_window_lib.sh"

pkill -9 -f "$ROOT/bin/supervisor" 2>/dev/null || true
sleep 0.8
while read -r id; do [[ -n "$id" ]] && ipcrm -m "$id" 2>/dev/null || true
done < <(ipcs -m 2>/dev/null | awk -v u="$(whoami)" '$1=="m" && $4==u {print $2}')

make build >/dev/null
go build -tags=nosync -o bin/process_a ./cmd/process_a
go build -tags=nosync -o bin/process_b ./cmd/process_b

rm -f "$SHM_ID_FILE"
"$ROOT/bin/supervisor" >/tmp/lab3_sv.log 2>&1 &
SV=$!
wait_supervisor_ready || true
sleep 1.5
SHM="$(tr -d ' \n' <"$SHM_ID_FILE")"
echo "SHM id=$SHM"

"$ROOT/bin/poke" --id "$SHM" --delay-a 1 --delay-b 1 --auto on
for _ in $(seq 1 80); do
  if "$ROOT/bin/poke" --id "$SHM" --print 2>/dev/null | grep -qE 'Collisions=[1-9]'; then
    break
  fi
  sleep 0.15
done
sleep 2
"$ROOT/bin/poke" --id "$SHM" --print
capture_supervisor_window "$ROOT/screenshots/03-nosync-collisions.png" "$SHM"
kill "$SV" 2>/dev/null || true
wait "$SV" 2>/dev/null || true
make build >/dev/null
echo "done: screenshots/03-nosync-collisions.png"
