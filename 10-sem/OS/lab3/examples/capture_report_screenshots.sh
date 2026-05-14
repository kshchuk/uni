#!/usr/bin/env bash
# Re-capture GUI screenshots for the LaTeX report without clipping the
# Fyne window.  AppleScript's window "size" sometimes under-reports the
# visible chrome; a fixed screencapture -R from an old session therefore
# crops the title bar and the event log.  This script reads fresh
# {position,size} every time and adds generous padding in *points* (same
# coordinate system as screencapture -R on macOS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PAD_X="${PAD_X:-80}"
PAD_Y="${PAD_Y:-40}"

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

geom() {
  osascript <<'APPLESCRIPT'
tell application "System Events"
  tell process "supervisor"
    set frontmost to true
    set p to position of window 1
    set s to size of window 1
    return (item 1 of p as string) & " " & (item 2 of p as string) & " " & (item 1 of s as string) & " " & (item 2 of s as string)
  end tell
end tell
APPLESCRIPT
}

capture_png() {
  local out="$1"
  read -r gx gy gw gh <<<"$(geom)"
  local x=$((gx - PAD_X))
  local y=$((gy - PAD_Y))
  local w=$((gw + 2 * PAD_X))
  local h=$((gh + 2 * PAD_Y))
  if ((x < 0)); then x=0; fi
  if ((y < 0)); then y=0; fi
  screencapture -o -x -R "${x},${y},${w},${h}" "$out"
}

cleanup() {
  if [[ -n "${SV_PID:-}" ]] && kill -0 "$SV_PID" 2>/dev/null; then
    kill "$SV_PID" 2>/dev/null || true
    wait "$SV_PID" 2>/dev/null || true
  fi
  while read -r id; do
    [[ -n "$id" ]] && ipcrm -m "$id" 2>/dev/null || true
  done < <(ipcs -m 2>/dev/null | awk -v u="$(whoami)" '$1=="m" && $4==u {print $2}')
}
trap cleanup EXIT

echo "[capture] starting supervisor…"
"$ROOT/bin/supervisor" >/tmp/lab3_capture_supervisor.log 2>&1 &
SV_PID=$!

for i in $(seq 1 40); do
  if osascript -e 'tell application "System Events" to exists window 1 of process "supervisor"' 2>/dev/null | grep -q true; then
    break
  fi
  sleep 0.25
done
sleep 1

echo "[capture] 01-startup.png"
capture_png "$ROOT/screenshots/01-startup.png"

"$ROOT/bin/poke" --auto on
sleep 5
echo "[capture] 02-automode.png"
capture_png "$ROOT/screenshots/02-automode.png"
"$ROOT/bin/poke" --auto off
sleep 0.5

for _ in 1 2 3 4 5; do "$ROOT/bin/poke" --insert; sleep 0.15; done
"$ROOT/bin/poke" --request 1
sleep 0.4
"$ROOT/bin/poke" --insert
sleep 0.2
"$ROOT/bin/poke" --request 2
sleep 0.8
echo "[capture] 04-manual-deal.png"
capture_png "$ROOT/screenshots/04-manual-deal.png"

for _ in 1 2 3 4 5 6; do "$ROOT/bin/poke" --insert; sleep 0.12; done
for _ in 1 2 3; do "$ROOT/bin/poke" --request 50; sleep 0.25; done
sleep 0.6
echo "[capture] 05-manual-refuse.png"
capture_png "$ROOT/screenshots/05-manual-refuse.png"

echo "[capture] rebuilding nosync workers for 03-nosync…"
(
  cd "$ROOT"
  go build -tags=nosync -o bin/process_a ./cmd/process_a
  go build -tags=nosync -o bin/process_b ./cmd/process_b
)

# Restart supervisor so it respawns workers with new binaries
kill "$SV_PID" 2>/dev/null || true
wait "$SV_PID" 2>/dev/null || true
SV_PID=
sleep 1
while read -r id; do
  [[ -n "$id" ]] && ipcrm -m "$id" 2>/dev/null || true
done < <(ipcs -m 2>/dev/null | awk -v u="$(whoami)" '$1=="m" && $4==u {print $2}')

"$ROOT/bin/supervisor" >/tmp/lab3_capture_supervisor.log 2>&1 &
SV_PID=$!
for i in $(seq 1 40); do
  if osascript -e 'tell application "System Events" to exists window 1 of process "supervisor"' 2>/dev/null | grep -q true; then
    break
  fi
  sleep 0.25
done
sleep 1
"$ROOT/bin/poke" --auto on
sleep 5
echo "[capture] 03-nosync-collisions.png"
capture_png "$ROOT/screenshots/03-nosync-collisions.png"
"$ROOT/bin/poke" --auto off

echo "[capture] restoring default (atomic) workers…"
(
  cd "$ROOT"
  make build >/dev/null
)

kill "$SV_PID" 2>/dev/null || true
wait "$SV_PID" 2>/dev/null || true
SV_PID=

echo "[capture] done."
ls -la "$ROOT/screenshots/"*.png
