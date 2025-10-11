Лабораторний звіт (LaTeX)
==========================

Структура
---------
- `report/main.tex` — основний файл звіту з усіма розділами і плейсхолдерами.
- `report/bibliography.bib` — бібліографія (BibLaTeX).
- `report/figures/` — сюди збережіть скриншоти з ноутбука (`.png`/`.pdf`).
- `report/Makefile` — зручна збірка через `latexmk`.

Як скомпілювати
---------------
Варіант 1 (рекомендовано, якщо встановлено `latexmk` і `biber`):

```
cd report
make
```

Варіант 2 (вручну):

```
cd report
pdflatex -interaction=nonstopmode -halt-on-error main.tex
biber main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Вихідний файл: `report/main.pdf`.

Куди класти зображення
----------------------
Експортуйте з `lab_module.ipynb` або `lab.ipynb` потрібні скрини та збережіть у `report/figures/` з такими іменами (або змініть назви в `main.tex`):
- `A_isosurface_path.png`, `A_metrics.png`
- `B_isosurface_path.png`
- `C_isosurface_path.png`
- `surface_slice.png`

Примітки
--------
- У `bibliography.bib` заповніть авторів/рік для «Методи оптимізації. Частина 2», якщо потрібно.
- За потреби змініть шапку титульної сторінки (`\University`, `\Faculty`, тощо) прямо у `main.tex`.
