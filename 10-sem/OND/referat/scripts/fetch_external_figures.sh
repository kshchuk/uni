#!/usr/bin/env bash
# Ілюстрації з тих самих джерел, що й у referat.bib (Paul Bourke, JEM Engineering,
# Fractal Foundation, NASA Photojournal, NASA Earth Observatory). Пауза між запитами.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/figures/external"
mkdir -p "$OUT"
if [[ "${FORCE_SOURCE_IMAGES:-}" == 1 ]]; then
  rm -f "$OUT/ext_mandelbrot.jpg" "$OUT/ext_sierpinski.png" "$OUT/ext_koch.png" \
    "$OUT/ext_lungs.jpg" "$OUT/ext_romanesco.jpg" "$OUT/ext_hurricane.jpg" "$OUT/ext_earthlights.jpg" \
    "$OUT/ext_antennas_aircraft.jpg"
fi
fetch() {
  local url="$1" dest="$2"
  if [[ -s "$dest" ]]; then
    echo "skip exists: $dest"
    return 0
  fi
  sleep 4
  curl -fsSL -o "$dest" "$url"
  echo "ok: $dest"
}
# c47 — Paul Bourke, The Mandelbrot Set
fetch "https://paulbourke.net/fractals/mandelbrot/mandel1s.jpg" "$OUT/ext_mandelbrot.jpg"
# c09 — JEM Engineering, Fractal Antennas Explained
fetch "https://jemengineering.com/wp-content/uploads/2021/04/Sierpinski-Triangle-Fractal-980x309.png" "$OUT/ext_sierpinski.png"
fetch "https://jemengineering.com/wp-content/uploads/2021/04/Koch-Snowflake-Fractal-980x309.png" "$OUT/ext_koch.png"
# c25 — Fractal Foundation OFC (легенева схема)
fetch "https://fractalfoundation.org/OFCA/lungs.jpg" "$OUT/ext_lungs.jpg"
# c38 — Paul Bourke, DLA (2D point attractor; аналогія з блискавкою / дендритами)
fetch "https://paulbourke.net/fractals/dla/dla1s.jpg" "$OUT/ext_hurricane.jpg"
# c52 — NASA Earth Observatory (композит нічних вогнів)
fetch "https://eoimages.gsfc.nasa.gov/images/imagerecords/55000/55167/earth_lights_lrg.jpg" "$OUT/ext_earthlights.jpg"
