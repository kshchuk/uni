"""Генерує всі рисунки для guide.typ у каталог figures/."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import numpy as np

from mdo_lab1 import (collocation, grid, normalize, phi_direct, phi_transformed, plate_exact_velocity,
                      psi_transformed, resample, solve_gammas, velocity)

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

INK, MUTED, GRID = "#1a1a19", "#6b6a66", "#d9d8d4"
BLUE, RED = "#256abf", "#e34948"
SEQ = LinearSegmentedColormap.from_list("seq", ["#fcfcfb", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
DIV = LinearSegmentedColormap.from_list(
    "div", ["#104281", "#3987e5", "#9ec5f4", "#f0efec", "#f2aaa3", "#e34948", "#8f2020"])

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 10, "axes.titlecolor": INK,
    "savefig.dpi": 200, "savefig.bbox": "tight",
})

V_INF = np.array([1.0, 0.0])
DELTA = 0.01
HOOK = normalize([(0.35, 0.45), (-0.3, 0.45), (-0.3, -0.45), (0.2, -0.45), (0.2, -0.1)])
M = 60


def hook(m):
    return resample(HOOK, m)


def style(ax, lim=1.0):
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ticks = np.linspace(-lim, lim, 5)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xlabel("x")
    ax.set_ylabel("y")


def draw_contour(ax, P, lw=2.2):
    ax.plot(P[:, 0], P[:, 1], color=INK, lw=lw, solid_capstyle="round", zorder=5)


def fig_geometry(sample=hook, out=OUT / "geometry.png", lim=0.6, colloc=collocation):
    P = sample(16)
    C, N = colloc(P)
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    Pd = sample(400)
    ax.plot(Pd[:, 0], Pd[:, 1], color=GRID, lw=6, solid_capstyle="round", zorder=1, label="вихідний контур")
    ax.plot(Pd[:, 0], Pd[:, 1], color=INK, lw=1, zorder=2)
    ax.quiver(C[:, 0], C[:, 1], N[:, 0], N[:, 1], color=MUTED, scale=9, width=0.006, zorder=3)
    ax.scatter(P[:, 0], P[:, 1], s=42, facecolor="white", edgecolor=BLUE, lw=1.8, zorder=4,
               label=r"особливості $\omega_{0j}$ (M = 16)")
    ax.scatter(C[:, 0], C[:, 1], s=36, marker="x", color=RED, lw=1.6, zorder=4, label=r"колокації $\omega_k$ (M − 1 = 15)")
    for j in (0, len(P) - 1):
        ax.annotate(rf"$\omega_{{0{1 if j == 0 else 'M'}}}$", P[j], xytext=(6, 4), textcoords="offset points", color=INK)
    style(ax, lim)
    ax.legend(loc="lower left", fontsize=7.5, frameon=False, bbox_to_anchor=(0, -0.02))
    ax.set_title("Дискретизація контуру: нормалі дивляться ліворуч від обходу")
    fig.savefig(out)
    plt.close(fig)


def fig_phi_cuts():
    P = resample(HOOK, M)
    G = solve_gammas(P, V_INF, 1.0)
    X, Y = grid(500)
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4.2))
    for ax, F, title in [
        (axes[0], phi_direct(X, Y, P, G, V_INF), "Пряма (7.1.13′): розрізи від кожної ω₀ⱼ"),
        (axes[1], phi_transformed(X, Y, P, G, V_INF, DELTA), "Перетворена (7.1.22′): один розріз від ω₀M"),
    ]:
        lv = np.linspace(np.percentile(F, 1), np.percentile(F, 99), 31)
        ax.contourf(X, Y, F, levels=lv, cmap=DIV, extend="both")
        ax.contour(X, Y, F, levels=lv, colors=INK, linewidths=0.35, alpha=0.6)
        draw_contour(ax, P)
        style(ax)
        ax.set_title(title, fontsize=9)
    fig.suptitle(r"Потенціал $\varphi(x,y)$, $\Gamma_0 = 1$", color=INK)
    fig.savefig(OUT / "phi_cuts.png")
    plt.close(fig)


def four_panels(gamma0, out, sample=hook, m=M, colloc=collocation):
    P = sample(m)
    G = solve_gammas(P, V_INF, gamma0, colloc)
    X, Y = grid(500)
    U, V = velocity(X, Y, P, G, V_INF, DELTA)
    speed = np.hypot(U, V)
    phi = phi_transformed(X, Y, P, G, V_INF, DELTA)
    psi = psi_transformed(X, Y, P, G, V_INF, DELTA)

    fig, axes = plt.subplots(2, 2, figsize=(8.4, 8.6))
    top = np.percentile(speed, 99)

    ax = axes[0, 0]
    im = ax.imshow(np.clip(speed, 0, top), extent=(-1, 1, -1, 1), origin="lower", cmap=SEQ, vmin=0, vmax=top)
    Xs, Ys = grid(27)
    Us, Vs = velocity(Xs, Ys, P, G, V_INF, DELTA)
    mag = np.maximum(np.hypot(Us, Vs), 1e-12)
    ax.quiver(Xs, Ys, Us / mag, Vs / mag, color=INK, scale=38, width=0.0028, headwidth=3.5)
    draw_contour(ax, P)
    style(ax)
    ax.set_title(r"1) Векторне поле $\vec V$ на тлі $|\vec V|$")
    fig.colorbar(im, ax=ax, shrink=0.8)

    ax = axes[0, 1]
    lv = np.linspace(0, top, 21)
    cs = ax.contourf(X, Y, np.clip(speed, 0, top), levels=lv, cmap=SEQ)
    ax.contour(X, Y, speed, levels=lv[1::2], colors=INK, linewidths=0.35, alpha=0.7)
    draw_contour(ax, P)
    style(ax)
    ax.set_title(r"2) Ізолінії $|\vec V| = \mathrm{const}$")
    fig.colorbar(cs, ax=ax, shrink=0.8)

    for ax, F, title in [(axes[1, 0], phi, r"3) Ізолінії $\varphi = \mathrm{const}$"),
                         (axes[1, 1], psi, r"4) Ізолінії $\psi = \mathrm{const}$ (лінії течії)")]:
        lo, hi = np.percentile(F, [1, 99])
        lv = np.linspace(lo, hi, 31)
        norm = TwoSlopeNorm(0.0, min(lo, -1e-9), max(hi, 1e-9))
        cs = ax.contourf(X, Y, F, levels=lv, cmap=DIV, norm=norm, extend="both")
        ax.contour(X, Y, F, levels=lv, colors=INK, linewidths=0.4, alpha=0.7)
        draw_contour(ax, P)
        style(ax)
        ax.set_title(title)
        fig.colorbar(cs, ax=ax, shrink=0.8)

    fig.suptitle(rf"Результат лаб. №1: M = {m}, $\Gamma_0 = {gamma0:g}$, $\vec V_\infty = (1, 0)$, $r_j = {DELTA}$",
                 color=INK)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def fig_psi_gammas(out=OUT / "psi_gammas.png", sample=hook, m=M, colloc=collocation):
    P = sample(m)
    X, Y = grid(500)
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.6))
    for ax, g0 in zip(axes, (-1.0, 0.0, 1.0)):
        G = solve_gammas(P, V_INF, g0, colloc)
        psi = psi_transformed(X, Y, P, G, V_INF, DELTA)
        lv = np.linspace(-1.1, 1.1, 34)
        ax.contour(X, Y, psi, levels=lv, colors=BLUE, linewidths=0.7)
        draw_contour(ax, P)
        style(ax)
        ax.set_title(rf"$\Gamma_0 = {g0:g}$")
    fig.suptitle(r"Лінії течії $\psi = \mathrm{const}$ при різних циркуляціях", color=INK)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def fig_plate():
    plate = [(0.0, -0.5), (0.0, 0.5)]
    X, Y = grid(201)
    far = np.hypot(X, np.maximum(np.abs(Y) - 0.5, 0)) > 0.15
    Ms = np.array([10, 20, 40, 80, 160, 320])

    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.9))
    ax = axes[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        for g0, color, label in [(0.0, BLUE, r"$\Gamma_0 = 0$"), (1.0, RED, r"$\Gamma_0 = 1$")]:
            errs = []
            for m in Ms:
                P = resample(plate, m)
                G = solve_gammas(P, V_INF, g0)
                U, V = velocity(X, Y, P, G, V_INF, DELTA)
                Ue, Ve = plate_exact_velocity(X, Y, 0.5, g0)
                errs.append(np.max(np.hypot(U - Ue, V - Ve)[far]))
            ax.loglog(Ms, errs, "o-", color=color, lw=2, ms=6, label=label)
    ax.loglog(Ms, 1.3 / Ms, "--", color=MUTED, lw=1, label=r"$\sim 1/M$")
    ax.set_xlabel("M")
    ax.set_ylabel(r"max $|\vec V_{МДО} - \vec V_{точн}|$ (далі 0.15 від пластини)")
    ax.set_title("Збіжність до точного розв'язку")
    ax.legend(frameon=False)
    ax.grid(True, which="both", color=GRID, lw=0.5)

    ax = axes[1]
    Xf, Yf = grid(400)
    P = resample(plate, 80)
    G = solve_gammas(P, V_INF, 1.0)
    psi = psi_transformed(Xf, Yf, P, G, V_INF, DELTA)
    lv = np.linspace(-1.1, 1.1, 30)
    ax.contour(Xf, Yf, psi, levels=lv, colors=BLUE, linewidths=0.8)
    draw_contour(ax, P)
    style(ax)
    ax.set_title(r"Пластина, M = 80, $\Gamma_0 = 1$: лінії течії")
    fig.tight_layout()
    fig.savefig(OUT / "plate.png")
    plt.close(fig)


def fig_regularization():
    x0 = 0.0
    y = np.linspace(-0.08, 0.08, 1601)
    fig, ax = plt.subplots(figsize=(5.2, 2.8))
    for d, color, label in [(0.0, MUTED, "без регуляризації"), (0.01, BLUE, r"$r_j = 0.01$"), (0.03, RED, r"$r_j = 0.03$")]:
        R2 = np.maximum(y ** 2, d * d)
        with np.errstate(divide="ignore", invalid="ignore"):
            ax.plot(y, np.abs(y) / (2 * np.pi * R2), color=color, lw=2 if d else 1.2, label=label)
    ax.set_ylim(0, 25)
    ax.set_xlabel(r"відстань до особливості ($x = x_{0j}$, змінюємо $y$)")
    ax.set_ylabel(r"$|\vec V_j|$ при $\Gamma_j = 1$")
    ax.set_title("Регуляризація (7.1.18): обмежуємо швидкість біля вихору")
    ax.legend(frameon=False)
    ax.grid(True, color=GRID, lw=0.5)
    fig.savefig(OUT / "regularization.png")
    plt.close(fig)


if __name__ == "__main__":
    fig_geometry()
    fig_regularization()
    fig_phi_cuts()
    four_panels(1.0, OUT / "result_G1.png")
    four_panels(0.0, OUT / "result_G0.png")
    fig_psi_gammas()
    fig_plate()
    print("figures:", sorted(p.name for p in OUT.glob("*.png")))
