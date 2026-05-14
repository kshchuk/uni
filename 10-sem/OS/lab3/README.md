# Lab 3 — Автомат розміну монет (варіант 2)

Курс: Операційні системи · ЛП3 (синхронізація процесів).

**Об'єкт моделювання:** Автомат розміну монет.
**Засіб синхронізації:** Алгоритм Деккера.
**Спільна пам'ять:** System V Shared Memory (`shmget`/`shmat`/`shmctl`).
**Модель:** Два реальні ОС-процеси (`process_a`, `process_b`) + супервізор з GUI на Fyne.

## Швидкий старт

```bash
make tidy        # підтягнути модулі (Fyne)
make build       # зібрати supervisor, process_a, process_b, poke у bin/
make run         # запустити супервізор
```

Демонстраційні режими:

```bash
make run-racy     # build tag racy — без atomic, memory reordering
make run-nosync   # build tag nosync — взагалі без Деккера, чистий race
```

## Структура

```
cmd/
  supervisor/   GUI на Fyne, запуск процесів, життєвий цикл SHM
  process_a/    приймає монету, ідентифікує номінал (датчик ВЧ)
  process_b/    виконує розмін, оновлює банк
internal/
  shm/          cgo-обгортка над System V SHM
  dekker/       алгоритм Деккера (atomic + racy-варіант)
  coinbank/     банк монет і логіка розміну
  ipc/          протокол подій між процесами і супервізором
report/         повний звіт
screenshots/    скріни GUI
examples/       # stress.sh, smoketest, poke, capture_report_screenshots.sh
```

## Звіт

Повний звіт лежить у `report/report.md` (Markdown) і `report/report.tex`
(LaTeX). Зібрати PDF з LaTeX:

```bash
make report           # дві проходки xelatex -> report/report.pdf
make report-clean     # видалити .aux / .log / .out / .toc
```

Щоб **перезняти скріншоти** для звіту (повне вікно + поля навколо, без
обрізання заголовка й логу):

```bash
./examples/capture_report_screenshots.sh   # потрібні права Screen Recording
make report
```

## Очищення «осиротілих» SHM-сегментів

```bash
ipcs -m                # перелік сегментів поточного користувача
make clean             # видаляє bin/, проміжні TeX-файли і всі SHM сегменти користувача
```
