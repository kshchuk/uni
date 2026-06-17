# OND — курс «Основи нелінійної динаміки»

Матеріали з якісної теорії ОДР на площині: фазові портрети, особливі точки, граничні цикли, біфуркації, фрактали.

## Структура

```
OND/
├── README.md
├── literature/          # підручники та довідники (PDF, DJVU)
├── course/              # білети, програма
├── exam_guide/          # довідники до іспиту
│   ├── teorka_shatyrko/
│   ├── teorka_fractals/
│   ├── practika_fractals/
│   ├── practica_shatyrko/
│   └── _sources/        # сирі скріншоти (screenshots/, clips/, inbox/)
├── lab1/ … lab3/        # лабораторні (code/, figures/, photos/, звіт .tex)
├── notebooks/           # окремі ноутбуки
├── lecs/                # лекції (PDF)
└── referat/             # реферат про стохастичні фрактали
```

## Довідники (`exam_guide/`)

Сирі матеріали для збірки: `_sources/screenshots/`, `_sources/clips/`;
нові файли з кореня проєкту — у `_sources/inbox/`.

| Довідник | Збірка |
|----------|--------|
| `teorka_shatyrko/dovidnyk_teorka_shatyrko.tex` | `make theory` |
| `teorka_fractals/dovidnyk_teorka_fractals.pdf` | лише PDF (без `.tex`) |
| `practika_fractals/dovidnyk_practika_fractals.tex` | `make practika` |
| `practica_shatyrko/dovidnyk_practica_shatyrko.tex` | `make practica-shatyrko` |

Усі `.tex`-довідники: `make all` у `exam_guide/`. Артефакти збірки: `make clean`.

## Лабораторні

| Папка | Зміст |
|-------|--------|
| **lab1** | Фазові портрети 2-го порядку: Maple (`code/lab1.mw`), Python, звіт |
| **lab2** | Нелінійні портрети, розширений фазовий простір: `code/`, `figures/`, `screenshots/` |
| **lab3** | Біфуркація Баутіна, `pi_kan/`, ноутбуки в `code/` |

## Реферат

**referat/** — LaTeX-проєкт про стохастичні фрактали: `referat.tex`, `make` / `build.sh`.
