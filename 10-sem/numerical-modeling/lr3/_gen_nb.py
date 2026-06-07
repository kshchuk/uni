#!/usr/bin/env python3
"""Generate lr3/navier_stokes_2d.ipynb."""
import json
import uuid

ROOT = __file__.rsplit("/", 1)[0]


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


cells = [
    md("""# Лабораторна робота №3 — рівняння Нав'є–Стокса (2D)

**Тема:** чисельне моделювання в'язкої ньютонівської нестислої рідини.

Лінеаризована система на $\\Omega=\\{0\\le x\\le a,\\;0\\le y\\le d\\}$, $t>0$:

$$\\frac{\\partial u}{\\partial t} = -\\frac{1}{\\rho}\\frac{\\partial p}{\\partial x} + \\nu\\Delta u,\\quad
\\frac{\\partial v}{\\partial t} = -\\frac{1}{\\rho}\\frac{\\partial p}{\\partial y} + \\nu\\Delta v,\\quad
\\frac{\\partial u}{\\partial x}+\\frac{\\partial v}{\\partial y}=0.$$

**ГУ:** періодичність по $x$; на $y=0,d$ — $u,v$ (Діріхле), $\\partial p/\\partial y$ (Нейман).

**Точний розв'язок (9):**
$$u=-e^{-t}e^{2y/d}\\sin(2x/d),\\quad v=e^{-t}e^{2y/d}\\cos(2x/d),\\quad
p=\\frac{d}{2}\\rho e^{-t}e^{2y/d}\\cos(2x/d).$$

**Параметри:** $\\rho=1$, $d=1$, $a=\\pi$ (періодичність по $x$), $Re=1$, $\\nu=1/Re$.
"""),
    code("""import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

from ns_solver import (
    Params, build_grid, u_exact, v_exact, p_exact,
    divergence, laplacian_h, grad_p, sor_pressure, solve_ns,
    _apply_p_neumann,
)

%matplotlib inline
plt.rcParams.update({"figure.figsize": (8, 4)})
"""),
    md("## SymPy-перевірка точного розв'язку"),
    code("""x, y, t, d, rho = sp.symbols("x y t d rho", positive=True, real=True)
a = sp.pi  # довжина періоду по x

u = -sp.exp(-t) * sp.exp(2 * y / d) * sp.sin(2 * x / d)
v = sp.exp(-t) * sp.exp(2 * y / d) * sp.cos(2 * x / d)
p = sp.Rational(1, 2) * d * rho * sp.exp(-t) * sp.exp(2 * y / d) * sp.cos(2 * x / d)

div = sp.simplify(sp.diff(u, x) + sp.diff(v, y))
u_t = sp.diff(u, t)
v_t = sp.diff(v, t)
mom_u = sp.simplify(u_t + sp.diff(p, x) / rho - sp.diff(u, x, 2) - sp.diff(u, y, 2))
mom_v = sp.simplify(v_t + sp.diff(p, y) / rho - sp.diff(v, x, 2) - sp.diff(v, y, 2))

print("div u =", div)
print("баланс u =", mom_u)
print("баланс v =", mom_v)
"""),
    md("""## Чисельний розв'язок

На кожному кроці $n\\to n+1$:
1. $D=L_x u + L_y v$, $\\;S=D/\\tau + \\Delta_h D/Re$, розв'язати $\\Delta_h P=S$ (SOR / sparse).
2. Оновити $u,v$ за **ДС-алгоритмом** (LR1) з джерелом $-\\nabla p/\\rho$.
"""),
    code("""par = Params(Nx=40, Ny=40, T_final=0.5, cfl=0.25)
X, Y = build_grid(par)
print(f"h1={par.h1:.5f}, h2={par.h2:.5f}, tau={par.tau:.2e}, Re={par.Re}")

times = np.linspace(0, par.T_final, 9)
res = solve_ns(par, record_times=times, verbose=True)
"""),
    md("## Похибка від часу"),
    code("""eh = res["err_hist"]
fig, ax = plt.subplots()
ax.semilogy(eh["t"], eh["u_linf"], "o-", label=r"$\\|e_u\\|_\\infty$")
ax.semilogy(eh["t"], eh["v_linf"], "s-", label=r"$\\|e_v\\|_\\infty$")
ax.semilogy(eh["t"], eh["p_linf"], "^-", label=r"$\\|e_p\\|_\\infty$")
ax.set_xlabel("t")
ax.set_ylabel("norm")
ax.legend()
ax.grid(alpha=0.3)
plt.show()
"""),
    md("## Поля швидкості та тиску"),
    code("""rec = res["records"][-1]
U, V, P = rec["U"], rec["V"], rec["P"]
Ue, Ve, Pe = rec["Ue"], rec["Ve"], rec["Pe"]
t_fin = rec["t"]

fig, ax = plt.subplots(figsize=(7, 4))
step = 2
ax.quiver(X[::step, ::step], Y[::step, ::step], U[::step, ::step], V[::step, ::step],
          np.hypot(U, V)[::step, ::step], cmap="viridis", scale=25)
ax.set_title(f"Поле швидкості, t={t_fin:.2f}")
ax.set_aspect("equal")
plt.show()

fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
for ax, Z, ttl in zip(axes, [P, Pe, P - Pe], ["числ. p", "точний p", "похибка"]):
    im = ax.pcolormesh(X, Y, Z, shading="auto", cmap="RdBu_r")
    ax.set_title(ttl)
    ax.set_aspect("equal")
    plt.colorbar(im, ax=ax)
plt.suptitle(f"Тиск, t={t_fin:.2f}")
plt.tight_layout()
plt.show()
"""),
    md("## Збіжність SOR (рівняння Пуассона для тиску)"),
    code("""par_sor = Params(Nx=40, Ny=40, omega=1.7, pressure_use_direct=False)
X, Y = build_grid(par_sor)
t0 = 0.1
Pe = p_exact(X, Y, t0, par_sor)
_apply_p_neumann(Pe, X, t0, par_sor)
S = laplacian_h(Pe, par_sor.h1, par_sor.h2)

iters, errs = [], []
for mx in [20, 50, 100, 200, 400, 800, 1600]:
    par_sor.sor_max_iter = mx
    Ps, nit, _ = sor_pressure(S, np.zeros_like(Pe), X, t0, par_sor)
    iters.append(nit if nit < mx else mx)
    errs.append(float(np.max(np.abs(Ps - Pe))))

plt.semilogy(iters, errs, "o-")
plt.xlabel("ітерації SOR")
plt.ylabel(r"$\\|P-P_{exact}\\|_\\infty$")
plt.grid(alpha=0.3)
plt.title("Збіжність SOR")
plt.show()
"""),
    md("""## Висновки

- Реалізовано лінеаризовану систему Нав'є–Стокса з рівнянням Пуассона для тиску (10) та ДС-алгоритмом для $u,v$.
- SymPy підтверджує бездивергентність та баланс імпульсу точного розв'язку.
- Чисельний розв'язок порівнюється з аналітичним; спостерігається зростання похибки тиску через дискретну дивергенцію $D\\neq0$ на сітці.
- Для генерації PNG для LaTeX-звіту: `python figures/_make_figures.py`.
"""),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": cells,
}

out = f"{ROOT}/navier_stokes_2d.ipynb"
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print("Wrote", out)
