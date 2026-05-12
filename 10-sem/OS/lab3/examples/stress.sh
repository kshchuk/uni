#!/usr/bin/env bash
# stress.sh — запускає трьохрежимну демонстрацію (atomic / racy / nosync)
# і друкує метрики кожного запуску, щоб у звіті було видно, як веде себе
# взаємовиключення для кожної реалізації Деккера.
set -euo pipefail

cd "$(dirname "$0")/.."

DURATION="${DURATION:-3s}"
GO=${GO:-go}

run_one () {
    local tag="$1"
    echo
    echo "================================================================"
    echo "== Build & run mode: ${tag:-default-atomic}"
    echo "================================================================"
    if [[ -n "$tag" ]]; then
        $GO build -tags="$tag" -o bin/process_a ./cmd/process_a
        $GO build -tags="$tag" -o bin/process_b ./cmd/process_b
    else
        $GO build -o bin/process_a ./cmd/process_a
        $GO build -o bin/process_b ./cmd/process_b
    fi
    $GO run ./examples/smoketest --duration "$DURATION"
}

run_one ""
run_one "racy"
run_one "nosync"

echo
echo "Готово. Якщо у режимах racy/nosync 'CS collisions' > 0 —"
echo "це експериментальне підтвердження, що Деккер без atomic"
echo "ламається на сучасних CPU."
