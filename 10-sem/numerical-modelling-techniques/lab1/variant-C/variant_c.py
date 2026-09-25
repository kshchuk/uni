"""Лаб. №1, варіант «С»: контур — дуга кола у формі літери С. Будує рисунки, метрики та дані для звіту."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "guide"))

import matplotlib.pyplot as plt  # noqa: E402

from make_figures import BLUE, GRID, INK, MUTED, RED, fig_geometry, fig_psi_gammas, four_panels  # noqa: E402
from mdo_lab1 import collocation, grid, psi_transformed, solve_gammas, velocity  # noqa: E402

# ---- Вхідні дані варіанту ----
OPENING_DEG = 80.0          # кутовий розмір «розриву» літери С (відкрита праворуч)
M = 80
GAMMAS0 = (-1.0, 0.0, 1.0)
V_INF = np.array([1.0, 0.0])
DELTA = 0.01

FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)


def c_contour(m, opening_deg=OPENING_DEG):
    """Літера С: дуга кола від кута opening/2 до 360° − opening/2 (проти год. стрілки), розмір 1, центр bbox у (0, 0)."""
    a = np.radians(opening_deg / 2)
    t = np.linspace(a, 2 * np.pi - a, m)
    P = 0.5 * np.column_stack([np.cos(t), np.sin(t)])
    x_min, x_max = -0.5, 0.5 * np.cos(a)
    return P - np.array([0.5 * (x_min + x_max), 0.0])


def metrics():
    P = c_contour(M)
    C, N = collocation(P)
    h = np.hypot(*np.diff(P, axis=0).T)
    out = {"M": M, "opening_deg": OPENING_DEG, "delta": DELTA, "h_min": float(h.min()), "h_max": float(h.max()),
           "size": float(np.max(np.hypot(*(P[:, None] - P[None]).transpose(2, 0, 1)))), "runs": []}
    Xb, Yb = grid(201, 3.0)
    edge = np.maximum(np.abs(Xb), np.abs(Yb)) > 2.95
    for g0 in GAMMAS0:
        G = solve_gammas(P, V_INF, g0)
        U, V = velocity(C[:, 0], C[:, 1], P, G, V_INF, 0.0)
        side = [psi_transformed(*(C + s * 0.01 * N).T, P, G, V_INF, 0.005) for s in (1, -1)]
        Ub, Vb = velocity(Xb, Yb, P, G, V_INF, DELTA)
        out["runs"].append({
            "gamma0": g0,
            "sum_gamma": float(G.sum()),
            "max_vn": float(np.abs(U * N[:, 0] + V * N[:, 1]).max()),
            "psi_ptp_outer": float(np.ptp(side[0])),
            "psi_ptp_inner": float(np.ptp(side[1])),
            "far_speed_dev": float(np.abs(np.hypot(Ub, Vb) - 1)[edge].max()),
            "speed_max_1": float(np.hypot(*velocity(*grid(300), P, G, V_INF, DELTA)).max()),
        })
        np.savetxt(HERE / f"solution_G{g0:+g}.csv", np.column_stack([P, G]), delimiter=",",
                   header="x0j,y0j,Gamma_j", comments="", fmt="%.10f")
    return out


def convergence():
    X, Y = grid(161)
    ref_P = c_contour(1280)
    dist = np.min(np.hypot(X[..., None] - ref_P[:, 0], Y[..., None] - ref_P[:, 1]), axis=-1)
    far = dist > 0.1
    Ms = [20, 40, 80, 160, 320]
    res = {}
    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    for g0, color in [(0.0, BLUE), (1.0, RED)]:
        Ur, Vr = velocity(X, Y, ref_P, solve_gammas(ref_P, V_INF, g0), V_INF, DELTA)
        errs = []
        for m in Ms:
            P = c_contour(m)
            U, V = velocity(X, Y, P, solve_gammas(P, V_INF, g0), V_INF, DELTA)
            errs.append(float(np.max(np.hypot(U - Ur, V - Vr)[far])))
        res[f"{g0:g}"] = dict(zip(map(str, Ms), errs))
        ax.loglog(Ms, errs, "o-", color=color, lw=2, ms=6, label=rf"$\Gamma_0 = {g0:g}$")
    ax.loglog(Ms, 2.0 / np.array(Ms), "--", color=MUTED, lw=1, label=r"$\sim 1/M$")
    ax.set_xlabel("M")
    ax.set_ylabel(r"max $|\vec V_M - \vec V_{1280}|$")
    ax.set_title("Збіжність за M (далі 0.1 від контуру)")
    ax.grid(True, which="both", color=GRID, lw=0.5)
    ax.legend(frameon=False)
    fig.savefig(FIG / "convergence.png")
    plt.close(fig)
    return res


def gamma_distribution():
    P = c_contour(M)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    h = s[1] - s[0]
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    for g0, color in zip(GAMMAS0, [BLUE, INK, RED]):
        ax.plot(s / s[-1], solve_gammas(P, V_INF, g0) / h, color=color, lw=1.8, label=rf"$\Gamma_0 = {g0:g}$")
    ax.set_xlabel(r"параметр дуги $s/L$ (0 — верхній кінець С, 1 — нижній)")
    ax.set_ylabel(r"$\Gamma_j / h \approx \gamma(s)$")
    ax.set_title("Густина вихорів уздовж контуру")
    ax.grid(True, color=GRID, lw=0.5)
    ax.legend(frameon=False)
    fig.savefig(FIG / "gamma_distribution.png")
    plt.close(fig)


if __name__ == "__main__":
    fig_geometry(sample=lambda m: c_contour(m), out=FIG / "geometry.png", lim=0.7)
    for g0 in GAMMAS0:
        four_panels(g0, FIG / f"result_G{g0:+g}.png", sample=c_contour, m=M)
    fig_psi_gammas(out=FIG / "psi_gammas.png", sample=c_contour, m=M)
    gamma_distribution()
    data = metrics()
    data["convergence"] = convergence()
    (HERE / "metrics.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(json.dumps(data, indent=1, ensure_ascii=False))
