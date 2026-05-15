# shellcheck shell=bash
# Shared helpers for supervisor GUI screenshots (source from capture scripts).
# With LAB3_CAPTURE=1 the supervisor opens in fullscreen; we capture its bounds.

window_bounds_points() {
  local shm="${1:-$SHM_ID}"
  osascript <<APPLESCRIPT
set targetShm to "$shm"
tell application "System Events"
  tell process "supervisor"
    set frontmost to true
    repeat with i from 1 to (count of windows)
      tell window i
        if name contains ("SHM=" & targetShm) then
          set p to position
          set s to size
          return (item 1 of p as string) & " " & (item 2 of p as string) & " " & (item 1 of s as string) & " " & (item 2 of s as string)
        end if
      end tell
    end repeat
    error "supervisor window with SHM=" & targetShm & " not found"
  end tell
end tell
APPLESCRIPT
}

wait_supervisor_ready() {
  local shm="${1:-$SHM_ID}"
  local i
  for i in $(seq 1 40); do
    if window_bounds_points "$shm" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

capture_supervisor_window() {
  local out="$1"
  local shm="${2:-$SHM_ID}"
  local gx gy gw gh attempt

  for attempt in 1 2 3 4 5; do
    if ! osascript -e 'tell application "System Events" to exists process "supervisor"' 2>/dev/null | grep -q true; then
      sleep 0.4
      continue
    fi
    osascript -e 'tell application "System Events" to tell process "supervisor" to set frontmost to true' >/dev/null 2>&1 || true
    sleep 0.35
    read -r gx gy gw gh <<<"$(window_bounds_points "$shm")"
    screencapture -o -x -R "${gx},${gy},${gw},${gh}" "$out"
    if python3 -c "from PIL import Image; w,h=Image.open('${out}').size; exit(0 if w>=400 and h>=400 else 1)" 2>/dev/null; then
      echo "[capture] $(basename "$out"): $(python3 -c "from PIL import Image; im=Image.open('${out}'); print(im.size[0], 'x', im.size[1], sep='')")"
      return 0
    fi
    sleep 0.4
  done
  echo "[capture] failed to capture supervisor window (SHM=${shm})" >&2
  return 1
}
