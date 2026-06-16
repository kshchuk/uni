"""
Lab 2 — nonlinear system (task 3.6):
    dx/dt = ln(2 - y^2),   dy/dt = e^x - e^y

Domain: |y| < sqrt(2).
Singular points: M1(1, 1)  -- stable focus,
                 M2(-1,-1) -- saddle.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


SQRT2 = float(np.sqrt(2.0))
Y_EPS = 1e-3  # keep away from the domain boundary |y| = sqrt(2)


def P(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """ln(2 - y^2); NaN outside the strip |y| < sqrt(2)."""
    arg = 2.0 - np.asarray(y) ** 2
    safe = np.where(arg > 0, arg, 1.0)
    out = np.log(safe)
    out = np.where(arg > 0, out, np.nan)
    return out


def Q(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.exp(np.asarray(x, dtype=float)) - np.exp(np.asarray(y, dtype=float))


def normalize_vectors(u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mag = np.hypot(u, v)
    mag[mag == 0] = 1.0
    return u / mag, v / mag


def system_ode(t: float, yv: np.ndarray) -> list[float]:
    x, y = yv
    y_clip = float(np.clip(y, -SQRT2 + Y_EPS, SQRT2 - Y_EPS))
    return [float(P(np.array(x), np.array(y_clip))), float(Q(np.array(x), np.array(y)))]


# Singular points
M1 = np.array([1.0, 1.0], dtype=float)   # stable focus
M2 = np.array([-1.0, -1.0], dtype=float)  # saddle


# Jacobian at M2 (saddle) for separatrices: [[0, 2], [1/e, -1/e]]
J2 = np.array([[0.0, 2.0], [np.exp(-1.0), -np.exp(-1.0)]], dtype=float)
eig2, V2 = np.linalg.eig(J2)
order = np.argsort(-eig2.real)  # positive eigenvalue first (unstable)
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
    def event_y_top(t, yv):
        return yv[1] - (SQRT2 - Y_EPS)

    def event_y_bot(t, yv):
        return yv[1] + (SQRT2 - Y_EPS)

    event_y_top.terminal = True
    event_y_bot.terminal = True
    event_y_top.direction = 1
    event_y_bot.direction = -1

    sol = solve_ivp(
        system_ode,
        t_span,
        [x0, y0],
        dense_output=False,
        max_step=max_step,
        rtol=1e-9,
        atol=1e-10,
        events=(event_y_top, event_y_bot),
    )
    if not sol.success:
        return np.array([]), np.array([])
    return sol.y[0], sol.y[1]


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
    """Curves where dx/dt=0 (P=0, i.e. y=+/-1) and dy/dt=0 (Q=0, i.e. x=y)."""
    nx, ny = 400, 400
    xg = np.linspace(xlim[0], xlim[1], nx)
    yg = np.linspace(ylim[0], ylim[1], ny)
    X, Y = np.meshgrid(xg, yg)
    Zp, Zq = P(X, Y), Q(X, Y)
    ax.contour(X, Y, Zp, levels=[0], colors="tab:blue", linewidths=1.8, linestyles="-")
    ax.contour(X, Y, Zq, levels=[0], colors="tab:orange", linewidths=1.8, linestyles="-")
    ax.plot([], [], color="tab:blue", label=r"$P(x,y)=0$")
    ax.plot([], [], color="tab:orange", label=r"$Q(x,y)=0$")


def plot_domain_band(
    ax: plt.Axes, xlim: tuple[float, float], ylim: tuple[float, float]
) -> None:
    """Shade the forbidden region |y| >= sqrt(2) and draw the boundary lines."""
    if ylim[1] > SQRT2:
        ax.axhspan(SQRT2, ylim[1], color="lightgray", alpha=0.55, zorder=0)
    if ylim[0] < -SQRT2:
        ax.axhspan(ylim[0], -SQRT2, color="lightgray", alpha=0.55, zorder=0)
    for yl in (SQRT2, -SQRT2):
        if ylim[0] <= yl <= ylim[1]:
            ax.axhline(yl, color="dimgray", linestyle=":", linewidth=1.2)
    ax.plot([], [], color="dimgray", linestyle=":", label=r"$|y|=\sqrt{2}$")


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
        (M1, "o", "crimson", 10, r"$M_1(1,1)$ (стійкий фокус)"),
        (M2, "s", "darkgreen", 9, r"$M_2(-1,-1)$ (сідло)"),
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
            t_span = (0.0, t_max) if tforward else (0.0, -t_max)
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
    xs = np.linspace(xlim[0] + 0.08 * (xlim[1] - xlim[0]), xlim[1] - 0.08 * (xlim[1] - xlim[0]), n)
    ys = np.linspace(ylim[0] + 0.08 * (ylim[1] - ylim[0]), ylim[1] - 0.08 * (ylim[1] - ylim[0]), n)
    pts = []
    for x in xs:
        for y in ys:
            if abs(y) >= SQRT2 - 0.01:
                continue
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
    xlim = (-2.5, 2.5)
    ylim = (-1.39, 1.39)
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=140)
    plot_base(ax, xlim, ylim, quiver_n=30)
    plot_domain_band(ax, xlim, ylim)
    plot_dx_dy_zero_curves(ax, xlim, ylim)
    seeds = make_seed_grid(xlim, ylim, n=10, avoid=[(M1, 0.08), (M2, 0.08)])
    stream_on_ax(ax, xlim, ylim, density=1.35, seeds=seeds, color="royalblue")
    saddle_separatrices_plot(ax, eps=0.02, t_max=10.0)
    mark_equilibria(ax)
    ax.set_xlabel("$x$", fontsize=13)
    ax.set_ylabel("$y$", fontsize=13)
    ax.set_title("Загальний фазовий портрет (задача 3.6)", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig("global_phase_portrait_3_6.png")
    plt.close(fig)
    print("Saved global_phase_portrait_3_6.png")


def plot_local(center: np.ndarray, tag: str, title: str, density: float = 1.55) -> None:
    span = 0.4
    xlim = (float(center[0] - span), float(center[0] + span))
    ylim = (float(center[1] - span), float(center[1] + span))
    fig, ax = plt.subplots(figsize=(7, 7), dpi=140)
    plot_base(ax, xlim, ylim, quiver_n=22)
    plot_domain_band(ax, xlim, ylim)
    plot_dx_dy_zero_curves(ax, xlim, ylim)
    avoid = [(M1, 0.05), (M2, 0.05)]
    seeds = make_seed_grid(xlim, ylim, n=11, avoid=avoid)
    extra = np.array([
        [xlim[0] + 0.03, ylim[0] + 0.03],
        [xlim[1] - 0.03, ylim[1] - 0.03],
        [xlim[0] + 0.03, ylim[1] - 0.03],
        [xlim[1] - 0.03, ylim[0] + 0.03],
    ])
    seeds = np.vstack([seeds, extra])
    stream_on_ax(ax, xlim, ylim, density=density, seeds=seeds, color="royalblue")
    if np.allclose(center, M2):
        saddle_separatrices_plot(ax, eps=0.012, t_max=3.0)
    mark_equilibria(ax, only=center)
    ax.set_xlabel("$x$", fontsize=13)
    ax.set_ylabel("$y$", fontsize=13)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fname = f"local_{tag}_3_6.png"
    fig.savefig(fname)
    plt.close(fig)
    print(f"Saved {fname}")


if __name__ == "__main__":
    import os

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    plot_global()
    plot_local(M1, "M1", r"Локально: $M_1(1,1)$ — стійкий фокус")
    plot_local(M2, "M2", r"Локально: $M_2(-1,-1)$ — сідло")
