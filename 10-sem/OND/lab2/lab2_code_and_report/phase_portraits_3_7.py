"""
Lab 2 — nonlinear system (task 3.7):
    dx/dt = (2x - y)(x - 2),   dy/dt = xy - 2

Singular points: M1(2,1), M2(1,2), M3(-1,-2).
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def P(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return (2 * x - y) * (x - 2)


def Q(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return x * y - 2


def normalize_vectors(u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mag = np.hypot(u, v)
    mag[mag == 0] = 1.0
    return u / mag, v / mag


def system_ode(t: float, yv: np.ndarray) -> list[float]:
    x, y = yv
    return [float(P(x, y)), float(Q(x, y))]


# Singular points (user labelling)
M1 = np.array([2.0, 1.0], dtype=float)  # unstable node
M2 = np.array([1.0, 2.0], dtype=float)  # saddle
M3 = np.array([-1.0, -2.0], dtype=float)  # stable node

# Linearization at M2 (saddle) for separatrices: J = [[-2, 1], [2, 1]]
J2 = np.array([[-2.0, 1.0], [2.0, 1.0]], dtype=float)
eig2, V2 = np.linalg.eig(J2)
# order: positive eigenvalue first (unstable direction)
order = np.argsort(-eig2.real)
eig2 = eig2[order]
V2 = V2[:, order]
v_unstable = np.real(V2[:, 0]).astype(float)
v_stable = np.real(V2[:, 1]).astype(float)
v_unstable /= np.linalg.norm(v_unstable)
v_stable /= np.linalg.norm(v_stable)


def integrate_separatrix(
    x0: float,
    y0: float,
    t_span: tuple[float, float],
    max_step: float = 0.02,
) -> tuple[np.ndarray, np.ndarray]:
    sol = solve_ivp(
        system_ode,
        t_span,
        [x0, y0],
        dense_output=True,
        max_step=max_step,
        rtol=1e-9,
        atol=1e-10,
    )
    if not sol.success:
        return np.array([]), np.array([])
    t = sol.t
    y = sol.y
    return y[0], y[1]


def plot_base(
    ax: plt.Axes,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    quiver_n: int = 25,
) -> None:
    x = np.linspace(xlim[0], xlim[1], quiver_n)
    y = np.linspace(ylim[0], ylim[1], quiver_n)
    X, Y = np.meshgrid(x, y)
    U, V = P(X, Y), Q(X, Y)
    Un, Vn = normalize_vectors(U, V)
    ax.quiver(X, Y, Un, Vn, color="black", alpha=0.45, pivot="mid", scale=24, width=0.0025)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="black", linewidth=0.6)
    ax.axvline(0, color="black", linewidth=0.6)


def plot_dx_dy_zero_curves(
    ax: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]
) -> None:
    """Curves where dx/dt=0 (P=0) and dy/dt=0 (Q=0); drawn as contours."""
    nx, ny = 400, 400
    xg = np.linspace(xlim[0], xlim[1], nx)
    yg = np.linspace(ylim[0], ylim[1], ny)
    X, Y = np.meshgrid(xg, yg)
    Zp, Zq = P(X, Y), Q(X, Y)
    ax.contour(X, Y, Zp, levels=[0], colors="tab:blue", linewidths=1.8, linestyles="-")
    ax.contour(X, Y, Zq, levels=[0], colors="tab:orange", linewidths=1.8, linestyles="-")
    ax.plot([], [], color="tab:blue", label=r"$P(x,y)=0$")
    ax.plot([], [], color="tab:orange", label=r"$Q(x,y)=0$")


def stream_on_ax(
    ax: plt.Axes,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    density: float,
    seeds: np.ndarray,
    color: str = "royalblue",
) -> None:
    x = np.linspace(xlim[0], xlim[1], 55)
    y = np.linspace(ylim[0], ylim[1], 55)
    X, Y = np.meshgrid(x, y)
    U, V = P(X, Y), Q(X, Y)
    ax.streamplot(
        X,
        Y,
        U,
        V,
        color=color,
        density=density,
        linewidth=1.8,
        arrowsize=1.15,
        start_points=np.asarray(seeds, dtype=float),
    )


def mark_equilibria(ax: plt.Axes, only: np.ndarray | None = None) -> None:
    items = [
        (M1, "o", "crimson", 10, r"$M_1$ (нестійкий вузол)"),
        (M2, "s", "darkgreen", 9, r"$M_2$ (сідло)"),
        (M3, "D", "slateblue", 9, r"$M_3$ (стійкий вузол)"),
    ]
    for point, marker, color, size, label in items:
        if only is not None and not np.allclose(point, only):
            continue
        ax.plot(point[0], point[1], marker, color=color, markersize=size, zorder=5, label=label)


def saddle_separatrices_plot(
    ax: plt.Axes,
    eps: float = 0.02,
    t_max: float = 8.0,
) -> None:
    """Integrate unstable/stable manifolds from linearized directions at M2."""
    starts = []
    for sgn in (-1.0, 1.0):
        starts.append(M2 + sgn * eps * v_unstable)
        starts.append(M2 + sgn * eps * v_stable)
    colors_sep = ["darkgreen", "forestgreen", "purple", "darkviolet"]
    for i, (x0, y0) in enumerate(starts):
        for tforward in (True, False):
            if tforward:
                t_span = (0.0, t_max)
            else:
                t_span = (0.0, -t_max)
            xs, ys = integrate_separatrix(float(x0), float(y0), t_span)
            if xs.size == 0:
                continue
            ax.plot(xs, ys, "--", color=colors_sep[i % len(colors_sep)], linewidth=2.0, alpha=0.85)


def make_seed_grid(
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    n: int = 8,
    avoid: list[tuple[np.ndarray, float]] | None = None,
) -> np.ndarray:
    """Regular grid of starting points; optionally drop points near equilibria."""
    xs = np.linspace(xlim[0] + 0.08 * (xlim[1] - xlim[0]), xlim[1] - 0.08 * (xlim[1] - xlim[0]), n)
    ys = np.linspace(ylim[0] + 0.08 * (ylim[1] - ylim[0]), ylim[1] - 0.08 * (ylim[1] - ylim[0]), n)
    pts = []
    for x in xs:
        for y in ys:
            ok = True
            if avoid:
                for c, r in avoid:
                    if np.hypot(x - c[0], y - c[1]) < r:
                        ok = False
                        break
            if ok:
                pts.append([x, y])
    return np.array(pts, dtype=float)


def plot_global() -> None:
    xlim, ylim = (-4.0, 4.5), (-4.0, 4.5)
    fig, ax = plt.subplots(figsize=(9, 9), dpi=140)
    plot_base(ax, xlim, ylim, quiver_n=26)
    plot_dx_dy_zero_curves(ax, xlim, ylim)
    seeds = make_seed_grid(xlim, ylim, n=10)
    stream_on_ax(ax, xlim, ylim, density=1.35, seeds=seeds, color="royalblue")
    saddle_separatrices_plot(ax, eps=0.025, t_max=12.0)
    mark_equilibria(ax)
    ax.set_xlabel("$x$", fontsize=13)
    ax.set_ylabel("$y$", fontsize=13)
    ax.set_title("Загальний фазовий портрет (задача 3.7)", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig("global_phase_portrait.png")
    plt.close(fig)
    print("Saved global_phase_portrait.png")


def plot_local(center: np.ndarray, tag: str, title: str, density: float = 1.55) -> None:
    span = 0.9
    xlim = (float(center[0] - span), float(center[0] + span))
    ylim = (float(center[1] - span), float(center[1] + span))
    fig, ax = plt.subplots(figsize=(7, 7), dpi=140)
    plot_base(ax, xlim, ylim, quiver_n=22)
    plot_dx_dy_zero_curves(ax, xlim, ylim)
    avoid = [(M1, 0.12), (M2, 0.12), (M3, 0.12)]
    seeds = make_seed_grid(xlim, ylim, n=11, avoid=avoid)
    # add more seeds near the window border
    extra = [
        [xlim[0] + 0.05, ylim[0] + 0.05],
        [xlim[1] - 0.05, ylim[1] - 0.05],
        [xlim[0] + 0.05, ylim[1] - 0.05],
        [xlim[1] - 0.05, ylim[0] + 0.05],
    ]
    seeds = np.vstack([seeds, np.array(extra)])
    stream_on_ax(ax, xlim, ylim, density=density, seeds=seeds, color="royalblue")
    if np.allclose(center, M2):
        saddle_separatrices_plot(ax, eps=0.018, t_max=5.0)
    mark_equilibria(ax, only=center)
    ax.set_xlabel("$x$", fontsize=13)
    ax.set_ylabel("$y$", fontsize=13)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fname = f"local_{tag}.png"
    fig.savefig(fname)
    plt.close(fig)
    print(f"Saved {fname}")


if __name__ == "__main__":
    import os

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    plot_global()
    plot_local(M1, "M1", r"Локально: $M_1(2,1)$ — нестійкий вузол")
    plot_local(M2, "M2", r"Локально: $M_2(1,2)$ — сідло")
    plot_local(M3, "M3", r"Локально: $M_3(-1,-2)$ — стійкий вузол")
