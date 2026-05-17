# Lab 4 — Клієнт–серверне сортування масиву

Курс: Операційні системи · ЛП4.

TCP-клієнт надсилає масив із 10 000 `int32` на сервер; сервер сортує (QuickSort) і повертає результат. Клієнт виконує 100 вимірювань round-trip і обчислює середню швидкість порту.

## Швидкий старт

```bash
make build
# термінал 1
make run-server
# термінал 2
make run-client
```

Або один скрипт (сервер у фоні + клієнт):

```bash
make experiment
```

## Прапорці

**Сервер:** `-addr :9504`

**Клієнт:** `-addr 127.0.0.1:9504` `-n 10000` `-runs 100` `-seed 42`

## Структура

```
cmd/server/     TCP-сервер, QuickSort
cmd/client/     генерація масиву, 100 runs, метрики
internal/
  protocol/     бінарний протокол uint32 N + N×int32
  sort/         QuickSort
examples/       run_experiment.sh
report/         звіт LaTeX / Markdown
screenshots/
```

## Звіт

```bash
make report    # -> report/report.pdf
```
