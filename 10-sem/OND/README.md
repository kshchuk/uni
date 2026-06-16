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
│   ├── practika_fractals/
│   └── _sources/        # сирі скріншоти для збірки довідників
├── lab1/ … lab3/        # лабораторні (code/, figures/, photos/, звіт .tex)
├── notebooks/           # окремі ноутбуки
├── lecs/                # лекції (PDF)
└── referat/             # реферат про стохастичні фрактали
```

## Довідники (`exam_guide/`)

| Довідник | Збірка |
|----------|--------|
| `teorka_shatyrko/dovidnyk_teorka_shatyrko.tex` | `make theory` |
| `practika_fractals/dovidnyk_practika_fractals.tex` | `make practika` |

Обидва: `make all` у каталозі `exam_guide/`.

## Лабораторні

| Папка | Зміст |
|-------|--------|
| **lab1** | Фазові портрети 2-го порядку: Maple (`code/lab1.mw`), Python, звіт |
| **lab2** | Нелінійні портрети, розширений фазовий простір: `code/`, `figures/`, `screenshots/` |
| **lab3** | Біфуркація Баутіна, `pi_kan/`, ноутбуки в `code/` |

## Реферат

**referat/** — LaTeX-проєкт про стохастичні фрактали: `referat.tex`, `make` / `build.sh`.
