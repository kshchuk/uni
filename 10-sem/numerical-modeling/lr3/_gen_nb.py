#!/usr/bin/env python3
"""Generate lr3/navier_stokes_2d.ipynb — full solver code with Ukrainian comments."""
import json
from pathlib import Path

ROOT = Path(__file__).parent


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


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

**Тема:** чисельне моделювання в'язкої ньютонівської нестислої рідини (файл умов ЛР3).

Лінеаризована система на $\\Omega=\\{0\\le x\\le a,\\;0\\le y\\le d\\}$, $t>0$:

$$\\frac{\\partial u}{\\partial t} = -\\frac{1}{\\rho}\\frac{\\partial p}{\\partial x} + \\nu\\Delta u,\\quad
\\frac{\\partial v}{\\partial t} = -\\frac{1}{\\rho}\\frac{\\partial p}{\\partial y} + \\nu\\Delta v,\\quad
\\frac{\\partial u}{\\partial x}+\\frac{\\partial v}{\\partial y}=0.$$

**ГУ:** періодичність по $x$ (5)--(6); на $y=0,d$ — $u,v$ (Діріхле), $\\partial p/\\partial y$ (Нейман), (7)--(8).

**Точний розв'язок (9):**
$$u=-e^{-t}e^{2y/d}\\sin(2x/d),\\quad v=e^{-t}e^{2y/d}\\cos(2x/d),\\quad
p=\\frac{d}{2}\\rho e^{-t}e^{2y/d}\\cos(2x/d).$$

**Параметри:** $\\rho=1$, $d=1$, $a=\\pi$, $Re=1$, $\\nu=1/Re$.
"""),
    md("## Імпорт бібліотек"),
    code("""from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy.sparse import csr_matrix, lil_matrix
from scipy.sparse.linalg import spsolve

%matplotlib inline
plt.rcParams.update({"figure.figsize": (8, 4)})
"""),
    md("""## Параметри задачі та сітка

Клас `Params` збирає фізичні ($\\rho$, $d$, $a$, $Re$) та чисельні ($N_x$, $N_y$, $\\omega$, CFL)
константи. Крок $\\tau$ обирається з умови стійкості ДС-схеми:
$\\tau = \\mathrm{cfl}\\cdot\\min(h_1,h_2)^2\\cdot Re$.
"""),
    code("""@dataclass
class Params:
    \"\"\"Фізичні та чисельні параметри лабораторної роботи.\"\"\"

    rho: float = 1.0          # густина рідини
    d: float = 1.0            # висота області по y
    a: float = np.pi          # довжина періоду по x (sin(2x/d) періодична)
    Re: float = 1.0           # число Рейнольдса Re = 1/nu
    T_final: float = 0.5      # кінець інтервалу моделювання
    Nx: int = 40              # вузлів по x (без дублювання x=a)
    Ny: int = 40              # інтервалів по y (вузлів Ny+1)
    omega: float = 1.7        # параметр релаксації SOR, 1 <= omega <= 2
    sor_tol: float = 1e-6     # критерій збіжності SOR
    sor_max_iter: int = 5000
    cfl: float = 0.2          # множник для tau
    pressure_use_direct: bool = False  # False: SOR (за умовою); True: прямий лише для порівняння

    @property
    def nu(self) -> float:
        \"\"\"Кінематична в'язкість nu = 1/Re.\"\"\"
        return 1.0 / self.Re

    @property
    def h1(self) -> float:
        return self.a / self.Nx

    @property
    def h2(self) -> float:
        return self.d / self.Ny

    @property
    def beta(self) -> float:
        \"\"\"Відношення кроків beta = h1/h2 (для SOR).\"\"\"
        return self.h1 / self.h2

    @property
    def tau(self) -> float:
        h_min = min(self.h1, self.h2)
        return self.cfl * h_min * h_min * self.Re


def build_grid(p: Params) -> Tuple[np.ndarray, np.ndarray]:
    \"\"\"Рівномірна сітка: x in [0,a) періодично, y in [0,d].\"\"\"
    x = np.linspace(0.0, p.a, p.Nx, endpoint=False)
    y = np.linspace(0.0, p.d, p.Ny + 1)
    return np.meshgrid(x, y, indexing="ij")
"""),
    md("""## Точний розв'язок (9) і граничні умови

Функції `u_exact`, `v_exact`, `p_exact` — аналітичний розв'язок з файлу умов.
`p_y_bc` — значення $\\partial p/\\partial y$ на $y=0$ та $y=d$ (Neumann для тиску).
`apply_velocity_bc` — Dirichlet для $u,v$ на горизонтальних границях.
"""),
    code("""def u_exact(X: np.ndarray, Y: np.ndarray, t: float, p: Params) -> np.ndarray:
    d = p.d
    e = np.exp(-t) * np.exp(2.0 * Y / d)
    return -e * np.sin(2.0 * X / d)


def v_exact(X: np.ndarray, Y: np.ndarray, t: float, p: Params) -> np.ndarray:
    d = p.d
    e = np.exp(-t) * np.exp(2.0 * Y / d)
    return e * np.cos(2.0 * X / d)


def p_exact(X: np.ndarray, Y: np.ndarray, t: float, par: Params) -> np.ndarray:
    d, rho = par.d, par.rho
    return 0.5 * d * rho * np.exp(-t) * np.exp(2.0 * Y / d) * np.cos(2.0 * X / d)


def p_y_bc(y_val: float, X: np.ndarray, t: float, par: Params) -> np.ndarray:
    \"\"\"dp/dy на горизонті y = y_val (формули 7--8).\"\"\"
    d, rho = par.d, par.rho
    return rho * np.exp(-t) * np.exp(2.0 * y_val / d) * np.cos(2.0 * X / d)


def apply_velocity_bc(
    U: np.ndarray, V: np.ndarray, X: np.ndarray, Y: np.ndarray, t: float, par: Params,
) -> Tuple[np.ndarray, np.ndarray]:
    \"\"\"Dirichlet: u,v на y=0 та y=d з точного розв'язку.\"\"\"
    U = U.copy()
    V = V.copy()
    U[:, 0] = u_exact(X[:, 0], Y[:, 0], t, par)
    U[:, -1] = u_exact(X[:, -1], Y[:, -1], t, par)
    V[:, 0] = v_exact(X[:, 0], Y[:, 0], t, par)
    V[:, -1] = v_exact(X[:, -1], Y[:, -1], t, par)
    return U, V


def _apply_p_neumann(P: np.ndarray, X: np.ndarray, t: float, par: Params) -> None:
    \"\"\"In-place Neumann для p: SOR на j=2..Ny-1, рядки j=1, Ny-1 з односторонніх різниць.\"\"\"
    h2 = par.h2
    py0 = p_y_bc(0.0, X[:, 0], t, par)
    pyd = p_y_bc(par.d, X[:, 0], t, par)
    P[:, 1] = P[:, 2] - h2 * py0
    P[:, -2] = P[:, -3] + h2 * pyd
    P[:, 0] = P[:, 1] - h2 * py0
    P[:, -1] = P[:, -2] + h2 * pyd
"""),
    md("""## Дискретні оператори

- `L1_x`, `L2_y` — центральні різниці (періодичність по $x$ через `np.roll`).
- `laplacian_h` — п'ятиточковий $\\Delta_h$ (формула (10)).
- `divergence` — $D = L_x u + L_y v$.
- `grad_p` — наближення $\\nabla p$ для джерела $-\\nabla p/\\rho$ у рівняннях (1)--(2).
"""),
    code("""def L1_x(U: np.ndarray, h1: float) -> np.ndarray:
    \"\"\"Центральна різниця dU/dx, np.roll забезпечує періодичність по x.\"\"\"
    return (np.roll(U, -1, axis=0) - np.roll(U, 1, axis=0)) / (2.0 * h1)


def L2_y(U: np.ndarray, h2: float) -> np.ndarray:
    \"\"\"Центральна різниця dU/dy на внутрішніх рядках j=1..Ny-1.\"\"\"
    out = np.zeros_like(U)
    out[:, 1:-1] = (U[:, 2:] - U[:, :-2]) / (2.0 * h2)
    return out


def laplacian_h(U: np.ndarray, h1: float, h2: float) -> np.ndarray:
    \"\"\"П'ятиточковий лапласіан; по x — періодичний, по y — внутрішні вузли.\"\"\"
    out = np.zeros_like(U)
    out[:, 1:-1] = (
        (np.roll(U, -1, axis=0)[:, 1:-1] - 2.0 * U[:, 1:-1] + np.roll(U, 1, axis=0)[:, 1:-1]) / h1 ** 2
        + (U[:, 2:] - 2.0 * U[:, 1:-1] + U[:, :-2]) / h2 ** 2
    )
    return out


def divergence(U: np.ndarray, V: np.ndarray, h1: float, h2: float) -> np.ndarray:
    return L1_x(U, h1) + L2_y(V, h2)


def grad_p(P: np.ndarray, h1: float, h2: float) -> Tuple[np.ndarray, np.ndarray]:
    return L1_x(P, h1), L2_y(P, h2)
"""),
    md("""## Розв'язок рівняння Пуассона для тиску (10)

Права частина: $S = D/\\tau + \\Delta_h D / Re$.

**SOR** — формула з файлу умов (Roache [2]); ітерації на $j=2,\\ldots,M-1$.

**PoissonDirect** — розріджена матриця тієї ж дискретної системи (швидко на часовому циклі).
"""),
    code("""def sor_pressure(
    S: np.ndarray, P_init: np.ndarray, X: np.ndarray, t: float, par: Params,
) -> Tuple[np.ndarray, int, float]:
    \"\"\"SOR для Delta_h P = S (Roache, с.182--183), формула (10) файлу умов.

    Точкова формула з умови:
        P_ij^{r+1} = P_ij^r + omega/(2(1+beta^2)) * [ P_{i+1,j}+P_{i-1,j}
                     + beta^2(P_{i,j+1}+P_{i,j-1}) - h1^2 S_ij - 2(1+beta^2)P_ij ].
    Реалізовано у вигляді red-black (шахового) SOR: це той самий метод, але
    оновлення двох кольорів виконуються векторно (без python-циклів по вузлах),
    що на порядки швидше при збереженні результату при збіжності.
    \"\"\"
    nx, ny = P_init.shape
    h1, beta = par.h1, par.beta
    b2 = beta ** 2
    omega = par.omega
    denom = 2.0 * (1.0 + b2)

    P = P_init.copy()
    _apply_p_neumann(P, X, t, par)

    # робоча область j = 2..M-1 (як в умові); i — періодично по x
    I = np.arange(nx)[:, None]
    J = np.arange(ny)[None, :]
    region = (J >= 2) & (J <= ny - 2)
    red = region & ((I + J) % 2 == 0)
    black = region & ((I + J) % 2 == 1)

    for it in range(par.sor_max_iter):
        P_prev = P.copy()
        for color in (red, black):
            gs = np.zeros_like(P)
            xp = np.roll(P, -1, axis=0)
            xm = np.roll(P, 1, axis=0)
            gs[:, 1:-1] = (
                xp[:, 1:-1] + xm[:, 1:-1]
                + b2 * (P[:, 2:] + P[:, :-2])
                - h1 ** 2 * S[:, 1:-1]
            ) / denom
            P = np.where(color, (1.0 - omega) * P + omega * gs, P)
        _apply_p_neumann(P, X, t, par)
        max_diff = float(np.max(np.abs(P - P_prev)))
        if max_diff < par.sor_tol:
            return P, it + 1, max_diff
    return P, par.sor_max_iter, max_diff


class PoissonDirect:
    \"\"\"Прямий sparse-розв'язувач для (10) — та сама дискретизація, що й SOR.\"\"\"

    def __init__(self, nx: int, ny: int, h1: float, beta: float):
        self.nx, self.ny = nx, ny
        self.h1 = h1
        self.b2 = beta ** 2
        self.j_vals = list(range(2, ny - 1))
        self.nunk = nx * len(self.j_vals)
        self.index = {(i, j): k * nx + i for k, j in enumerate(self.j_vals) for i in range(nx)}

        A = lil_matrix((self.nunk, self.nunk))
        diag = -2.0 * (1.0 + self.b2) / h1 ** 2
        off_x = 1.0 / h1 ** 2
        off_y = self.b2 / h1 ** 2
        for j in self.j_vals:
            for i in range(nx):
                row = self.index[(i, j)]
                A[row, row] = diag
                A[row, self.index[((i + 1) % nx, j)]] += off_x
                A[row, self.index[((i - 1) % nx, j)]] += off_x
                if j - 1 in self.j_vals:
                    A[row, self.index[(i, j - 1)]] += off_y
                else:
                    A[row, row] += off_y  # Neumann: P[i,j-1] = P[i,j] - h2*g
                if j + 1 in self.j_vals:
                    A[row, self.index[(i, j + 1)]] += off_y
                else:
                    A[row, row] += off_y
        self.A = csr_matrix(A)

    def solve(self, S, X, t, par, P_init):
        b = np.zeros(self.nunk)
        h2 = par.h2
        py0 = p_y_bc(0.0, X[:, 0], t, par)
        pyd = p_y_bc(par.d, X[:, 0], t, par)
        off_y = self.b2 / self.h1 ** 2
        for j in self.j_vals:
            for i in range(self.nx):
                row = self.index[(i, j)]
                b[row] = S[i, j]
                if j == self.j_vals[0]:
                    b[row] += off_y * h2 * py0[i]
                if j == self.j_vals[-1]:
                    b[row] -= off_y * h2 * pyd[i]
        sol = spsolve(self.A, b)
        P = P_init.copy()
        for j in self.j_vals:
            for i in range(self.nx):
                P[i, j] = sol[self.index[(i, j)]]
        _apply_p_neumann(P, X, t, par)
        return P


def solve_pressure(S, P_init, X, t, par, direct=None):
    \"\"\"Тиск: основний метод — SOR (за умовою). Прямий sparse — лише для порівняння.\"\"\"
    if par.pressure_use_direct and direct is not None:
        return direct.solve(S, X, t, par, P_init), 1, 0.0
    return sor_pressure(S, P_init, X, t, par)
"""),
    md("""## ДС-алгоритм для рівнянь (1)--(2)

Рівняння для $u$ (аналогічно $v$): $u_t = \\nu\\Delta u - p_x/\\rho$.

ДС-схема з файлу умов: два півкроки $\\tau/2$, шахівниця $(i+j)\\bmod 2$,
чергування явного та CN-неявного кроків (як у LR1 для теплопровідності).
"""),
    code("""def neighbor_sum_4_periodic(U: np.ndarray) -> np.ndarray:
    \"\"\"Сума чотирьох сусідів на внутрішніх вузлах (x — періодично).\"\"\"
    S = np.zeros_like(U)
    S[:, 1:-1] = (
        np.roll(U, -1, axis=0)[:, 1:-1]
        + np.roll(U, 1, axis=0)[:, 1:-1]
        + U[:, :-2] + U[:, 2:]
    )
    return S


def ds_diffusion_step(
    U: np.ndarray,
    tau: float,
    t_n: float,
    source_fn: Callable[[float], np.ndarray],
    par: Params,
    apply_bc: Callable[[np.ndarray, float], np.ndarray],
) -> np.ndarray:
    \"\"\"Один крок ДС для u_t = nu*Lap(u) + f (рівняння 1 або 2).\"\"\"
    h1, h2, nu = par.h1, par.h2, par.nu
    dt2 = tau / 2.0
    t_mid, t_np1 = t_n + dt2, t_n + tau
    h_ref2 = min(h1, h2) ** 2
    coef_imp = 1.0 + nu * tau / h_ref2
    coef_exp = 1.0 - nu * tau / h_ref2

    U0 = apply_bc(U.copy(), t_n)
    F_n, F_mid, F_np1 = source_fn(t_n), source_fn(t_mid), source_fn(t_np1)

    nx, ny = U0.shape
    I = np.arange(nx)[:, None]
    J = np.arange(ny)[None, :]
    interior = (J > 0) & (J < ny - 1)
    white = interior & ((I + J) % 2 == 0)
    black = interior & ((I + J) % 2 == 1)

    # --- перший півкрок tau/2
    W = U0.copy()
    Lap0 = laplacian_h(U0, h1, h2)
    W[white] = U0[white] + dt2 * (nu * Lap0[white] + F_n[white])
    W = apply_bc(W, t_mid)

    Sc, So = neighbor_sum_4_periodic(W), neighbor_sum_4_periodic(U0)
    rhs_b = coef_exp * U0 + (nu * tau / 4.0) * (Sc + So) / h_ref2 + (tau / 2.0) * F_mid
    W[black] = rhs_b[black] / coef_imp
    W = apply_bc(W, t_mid)

    # --- другий півкрок tau/2
    U2 = W.copy()
    LapW = laplacian_h(W, h1, h2)
    U2[black] = W[black] + dt2 * (nu * LapW[black] + F_mid[black])
    U2 = apply_bc(U2, t_mid)

    Sc2, So2 = neighbor_sum_4_periodic(U2), neighbor_sum_4_periodic(W)
    rhs_w = coef_exp * W + (nu * tau / 4.0) * (Sc2 + So2) / h_ref2 + (tau / 2.0) * F_np1
    U2[white] = rhs_w[white] / coef_imp
    return apply_bc(U2, t_np1)
"""),
    md("""## Часовий цикл `solve_ns`

На кожному кроці $n\\to n+1$ (файл умов):
1. $D^n$, $S^n$; знайти $P^{n+1}$ з (10).
2. ДС-крок для $u$, $v$ з $-\\nabla P^{n+1}/\\rho$.
3. Застосувати граничні умови для $u,v$.
"""),
    code("""def solve_ns(par: Params, record_times=None, verbose=False) -> dict:
    X, Y = build_grid(par)
    U = u_exact(X, Y, 0.0, par)
    V = v_exact(X, Y, 0.0, par)
    P = p_exact(X, Y, 0.0, par)
    _apply_p_neumann(P, X, 0.0, par)

    poisson = (
        PoissonDirect(X.shape[0], X.shape[1], par.h1, par.beta)
        if par.pressure_use_direct else None
    )

    t = 0.0
    n_steps = int(np.ceil(par.T_final / par.tau))
    tau = par.T_final / n_steps  # рівномірно покриваємо [0, T_final]

    if record_times is None:
        record_times = np.linspace(0.0, par.T_final, 11)
    record_times = sorted(set(float(tt) for tt in record_times) | {par.T_final})

    records, sor_iters = [], []
    err_hist = {k: [] for k in ("t", "u_linf", "v_linf", "p_linf", "u_l2", "v_l2", "p_l2")}

    def record_state(t_now: float):
        ue = u_exact(X, Y, t_now, par)
        ve = v_exact(X, Y, t_now, par)
        pe = p_exact(X, Y, t_now, par)
        mask = np.zeros_like(U, dtype=bool)
        mask[:, 1:-1] = True
        eu, ev, ep = U - ue, V - ve, P - pe
        err_hist["t"].append(t_now)
        err_hist["u_linf"].append(np.max(np.abs(eu[mask])))
        err_hist["v_linf"].append(np.max(np.abs(ev[mask])))
        err_hist["p_linf"].append(np.max(np.abs(ep[mask])))
        err_hist["u_l2"].append(np.sqrt(np.mean(eu[mask] ** 2)))
        err_hist["v_l2"].append(np.sqrt(np.mean(ev[mask] ** 2)))
        err_hist["p_l2"].append(np.sqrt(np.mean(ep[mask] ** 2)))
        records.append({"t": t_now, "U": U.copy(), "V": V.copy(), "P": P.copy(),
                        "Ue": ue, "Ve": ve, "Pe": pe})

    next_rec = 0
    if record_times[0] <= 1e-12:
        record_state(0.0)
        next_rec = 1

    def bc_u(field, t_bc):
        out = field.copy()
        out[:, 0] = u_exact(X[:, 0], Y[:, 0], t_bc, par)
        out[:, -1] = u_exact(X[:, -1], Y[:, -1], t_bc, par)
        return out

    def bc_v(field, t_bc):
        out = field.copy()
        out[:, 0] = v_exact(X[:, 0], Y[:, 0], t_bc, par)
        out[:, -1] = v_exact(X[:, -1], Y[:, -1], t_bc, par)
        return out

    for step in range(n_steps):
        t_n, t_np1 = t, t + tau
        D = divergence(U, V, par.h1, par.h2)
        S = D / tau + laplacian_h(D, par.h1, par.h2) / par.Re
        P, nit, _ = solve_pressure(S, P, X, t_np1, par, poisson)
        sor_iters.append(nit)

        px, py = grad_p(P, par.h1, par.h2)
        src_u = lambda tt, px=px, par=par: -px / par.rho
        src_v = lambda tt, py=py, par=par: -py / par.rho

        U = ds_diffusion_step(U, tau, t_n, src_u, par, bc_u)
        V = ds_diffusion_step(V, tau, t_n, src_v, par, bc_v)
        U, V = apply_velocity_bc(U, V, X, Y, t_np1, par)
        t = t_np1

        while next_rec < len(record_times) and t >= record_times[next_rec] - 1e-9:
            record_state(t)
            next_rec += 1
        if verbose and (step + 1) % max(1, n_steps // 10) == 0:
            print(f"  крок {step+1}/{n_steps}, t={t:.4f}")

    if not records or records[-1]["t"] < par.T_final - 1e-9:
        record_state(t)

    return {"X": X, "Y": Y, "par": par, "records": records, "err_hist": err_hist,
            "sor_iters": sor_iters, "U": U, "V": V, "P": P}
"""),
    md("## SymPy-перевірка точного розв'язку"),
    code("""x, y, t, d, rho, Re = sp.symbols("x y t d rho Re", positive=True)
nu = 1 / Re

u_s = -sp.exp(-t) * sp.exp(2 * y / d) * sp.sin(2 * x / d)
v_s = sp.exp(-t) * sp.exp(2 * y / d) * sp.cos(2 * x / d)
p_s = sp.Rational(1, 2) * d * rho * sp.exp(-t) * sp.exp(2 * y / d) * sp.cos(2 * x / d)

print("div =", sp.simplify(sp.diff(u_s, x) + sp.diff(v_s, y)))
print("res_u =", sp.simplify(
    sp.diff(u_s, t) + sp.diff(p_s, x) / rho - nu * (sp.diff(u_s, x, 2) + sp.diff(u_s, y, 2))
))
print("res_v =", sp.simplify(
    sp.diff(v_s, t) + sp.diff(p_s, y) / rho - nu * (sp.diff(v_s, x, 2) + sp.diff(v_s, y, 2))
))
"""),
    md("""## Запуск чисельного експерименту

Тиск на кожному кроці знаходиться методом **SOR** (за умовою, Roache).
Прямий sparse-розв'язувач лишено лише для порівняння (`pressure_use_direct=True`).
"""),
    code("""par = Params(Nx=40, Ny=40, T_final=0.5, cfl=0.25)  # pressure_use_direct=False => SOR
X, Y = build_grid(par)
print(f"h1={par.h1:.5f}, h2={par.h2:.5f}, tau~{par.tau:.2e}, Re={par.Re}")
print(f"Метод тиску: {'прямий (порівняння)' if par.pressure_use_direct else 'SOR (за умовою)'}")

times = np.linspace(0, par.T_final, 25)  # кадри для анімації
res = solve_ns(par, record_times=times, verbose=True)
print(f"SOR ітерацій: середньо {np.mean(res['sor_iters']):.1f}, макс {np.max(res['sor_iters'])}")
"""),
    md("## Візуалізація: похибка від часу"),
    code("""eh = res["err_hist"]
fig, ax = plt.subplots()
ax.semilogy(eh["t"], eh["u_linf"], "o-", label=r"$\\|e_u\\|_\\infty$")
ax.semilogy(eh["t"], eh["v_linf"], "s-", label=r"$\\|e_v\\|_\\infty$")
ax.semilogy(eh["t"], eh["p_linf"], "^-", label=r"$\\|e_p\\|_\\infty$")
ax.set_xlabel("$t$")
ax.set_ylabel("норма похибки")
ax.legend()
ax.grid(alpha=0.3)
plt.show()
"""),
    md("## Візуалізація: поля швидкості та тиску"),
    code("""rec = res["records"][-1]
U, V, P = rec["U"], rec["V"], rec["P"]
Ue, Ve, Pe = rec["Ue"], rec["Ve"], rec["Pe"]
t_fin = rec["t"]

fig, ax = plt.subplots(figsize=(7, 4))
step = 2
ax.quiver(
    X[::step, ::step], Y[::step, ::step],
    U[::step, ::step], V[::step, ::step],
    np.hypot(U, V)[::step, ::step], cmap="viridis", scale=25,
)
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
    md("""## Анімація динаміки полів

Інтерактивна анімація еволюції векторного поля швидкості та поля тиску
у часі (відтворюється у ноутбуці; також збережено `figures/ns_dynamics.mp4`).
"""),
    code("""from matplotlib import animation
from IPython.display import HTML

recs = res["records"]
step = 2
figA, (axv, axp) = plt.subplots(1, 2, figsize=(12, 4))
pmax = max(np.max(np.abs(r["P"])) for r in recs)


def _update(k):
    axv.clear()
    axp.clear()
    r = recs[k]
    U, V, P = r["U"], r["V"], r["P"]
    axv.quiver(X[::step, ::step], Y[::step, ::step], U[::step, ::step], V[::step, ::step],
               np.hypot(U, V)[::step, ::step], cmap="viridis", scale=25)
    axv.set_title(f"Швидкість, t={r['t']:.3f}")
    axv.set_aspect("equal")
    axp.pcolormesh(X, Y, P, shading="auto", cmap="RdBu_r", vmin=-pmax, vmax=pmax)
    axp.set_title(f"Тиск, t={r['t']:.3f}")
    axp.set_aspect("equal")
    return []


ani = animation.FuncAnimation(figA, _update, frames=len(recs), interval=150)
plt.close(figA)
HTML(ani.to_jshtml())
"""),
    md("## Збіжність SOR (демонстрація методу з файлу умов)"),
    code("""par_sor = Params(Nx=40, Ny=40, omega=1.7, pressure_use_direct=False)
Xs, Ys = build_grid(par_sor)
t0 = 0.1
Pe = p_exact(Xs, Ys, t0, par_sor)
_apply_p_neumann(Pe, Xs, t0, par_sor)
S = laplacian_h(Pe, par_sor.h1, par_sor.h2)

iters, errs = [], []
for mx in [20, 50, 100, 200, 400, 800, 1600]:
    par_sor.sor_max_iter = mx
    Ps, nit, _ = sor_pressure(S, np.zeros_like(Pe), Xs, t0, par_sor)
    iters.append(nit if nit < mx else mx)
    errs.append(float(np.max(np.abs(Ps - Pe))))

plt.semilogy(iters, errs, "o-")
plt.xlabel("ітерації SOR")
plt.ylabel(r"$\\|P-P_{exact}\\|_\\infty$")
plt.grid(alpha=0.3)
plt.title("Збіжність SOR для рівняння (10)")
plt.show()
"""),
    md("""## Порівняння SOR і прямого розв'язувача

SOR (основний метод за умовою) та прямий sparse-розв'язувач розв'язують
**ту саму** дискретну систему (10), тому при збіжності SOR дають однаковий тиск.
"""),
    code("""par_c = Params(Nx=30, Ny=30, omega=1.7, sor_tol=1e-10, sor_max_iter=20000)
Xc, Yc = build_grid(par_c)
tc = 0.1
# права частина від точного поля швидкості
Uc, Vc = u_exact(Xc, Yc, tc, par_c), v_exact(Xc, Yc, tc, par_c)
Dc = divergence(Uc, Vc, par_c.h1, par_c.h2)
Sc = Dc / par_c.tau + laplacian_h(Dc, par_c.h1, par_c.h2) / par_c.Re

P_sor, nit, res_sor = sor_pressure(Sc, np.zeros_like(Dc), Xc, tc, par_c)
direct = PoissonDirect(Xc.shape[0], Xc.shape[1], par_c.h1, par_c.beta)
P_dir = direct.solve(Sc, Xc, tc, par_c, np.zeros_like(Dc))

m = np.zeros_like(Dc, bool); m[:, 1:-1] = True
print(f"SOR збігся за {nit} ітерацій (нев'язка {res_sor:.1e})")
print(f"||P_SOR - P_direct||inf = {np.max(np.abs((P_sor - P_dir)[m])):.2e}  <- та сама система")
"""),
    md("""## Висновки

- Усі функції розв'язувача зібрані в цьому ноутбуці.
- Швидкості збігаються з точним розв'язком; тиск має правильну форму, але роздуту амплітуду через $D/\\tau$ на колокованій сітці.
- PNG для LaTeX-звіту: `python figures/_make_figures.py`.
"""),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": cells,
}

out = ROOT / "navier_stokes_2d.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("Wrote", out)
