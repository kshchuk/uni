# Лабораторна №2 — рівняння Бюргерса

## Файли

| Файл | Опис |
|------|------|
| `lab2_burgers.ipynb` | Основний ноутбук |
| `burgers_fdm.py` | Точний розв'язок, ДС, неявна σ=1/2 + Ньютон |
| `burgers_pinn.py` | PINN (TensorFlow + PhiFlow, [туторіал](https://physicsbaseddeeplearning.org/physicalloss-code.html)) |
| `figures/_make_figures.py` | Генерація PNG для звіту |
| `report.tex` | Звіт українською |

## Запуск

```bash
cd lr2
python3 figures/_make_figures.py   # FDM + (опційно) PINN

# PINN потребує Python з tensorflow та phiflow, напр.:
PINN_ITERS=10000 PYTHON_PINN=~/miniconda3/bin/python python3 figures/_make_figures.py

pdflatex report.tex && pdflatex report.tex
```

## Параметри

$\beta=\gamma=1$, $T=50$, $\ell=100$, $h=1$, $\tau=1/3$ (як у `burgers.pdf`).
