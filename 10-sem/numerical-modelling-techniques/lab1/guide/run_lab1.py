"""Шаблон виконання лаб. №1: задайте свій контур, M, Γ0, V∞ — отримаєте 4 графіки завдання."""
import matplotlib.pyplot as plt
import numpy as np

from mdo_lab1 import (collocation, grid, normalize, phi_transformed, psi_transformed, resample, solve_gammas,
                      velocity)

# ---- Вхідні дані (п. 7.1.3) ----
CONTOUR = [(0.35, 0.45), (-0.3, 0.45), (-0.3, -0.45), (0.2, -0.45), (0.2, -0.1)]  # свій «ієрогліф»
M = 60                                   # кількість дискретних особливостей
GAMMA0 = 1.0                             # циркуляція: запустіть для -1, 0, 1
ALPHA = 0.0                              # кут набігаючого потоку, рад
V_INF = np.array([np.cos(ALPHA), np.sin(ALPHA)])
DELTA = 0.01                             # параметр регуляризації r_j
N_PIX = 400                              # роздільність «екрана» N_PIX x N_PIX

P = resample(normalize(CONTOUR), M)
G = solve_gammas(P, V_INF, GAMMA0)

C, N = collocation(P)
U, V = velocity(C[:, 0], C[:, 1], P, G, V_INF, 0.0)
print(f"sum Γ = {G.sum():.6f} (має бути {GAMMA0}),  max|V·n| у колокаціях = {np.abs(U * N[:, 0] + V * N[:, 1]).max():.1e}")

X, Y = grid(N_PIX)
U, V = velocity(X, Y, P, G, V_INF, DELTA)
fields = {
    "speed": np.hypot(U, V),
    "phi": phi_transformed(X, Y, P, G, V_INF, DELTA),
    "psi": psi_transformed(X, Y, P, G, V_INF, DELTA),
}

fig, ax = plt.subplots(2, 2, figsize=(10, 10))
Xs, Ys = grid(25)
Us, Vs = velocity(Xs, Ys, P, G, V_INF, DELTA)
ax[0, 0].quiver(Xs, Ys, Us, Vs)
ax[0, 0].set_title("1) векторне поле V")
for a, (key, title) in zip(ax.flat[1:], [("speed", "2) |V| = const"), ("phi", "3) φ = const"), ("psi", "4) ψ = const")]):
    F = fields[key]
    lv = np.linspace(*np.percentile(F, [1, 99]), 30)
    a.contour(X, Y, F, levels=lv, cmap="Blues" if key == "speed" else "RdBu_r")
    a.set_title(title)
for a in ax.flat:
    a.plot(P[:, 0], P[:, 1], "k-", lw=2)
    a.set_aspect("equal")
fig.savefig(f"lab1_G{GAMMA0:g}.png", dpi=150)
