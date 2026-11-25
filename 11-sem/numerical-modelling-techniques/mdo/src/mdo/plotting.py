"""Рисунки: контур з колокаціями, чотири графіки полів, вихровий слід."""
import matplotlib.pyplot as plt
import numpy as np

from .fields import flow_box, grid


def plot_contour(contour, ax=None, every=1):
    """Вихори ω0j з колами радіуса δ, колокації, нормалі, точки відриву."""
    c = contour
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    for xj, yj in zip(c.x0, c.y0):
        ax.add_patch(plt.Circle((xj, yj), c.delta, fill=False, color="0.6", lw=0.8))
    ax.plot(c.x0, c.y0, "o-", color="tab:red", ms=3, label="дискретні вихори ω0j")
    ax.plot(c.x0[c.separation], c.y0[c.separation], "s", mfc="none", mec="k", ms=10,
            label="точки відриву")
    ax.plot(c.xc, c.yc, "x", color="k", ms=4, label="колокації")
    k = slice(None, None, every)
    ax.quiver(c.xc[k], c.yc[k], c.nx[k], c.ny[k], color="tab:green", scale=12, width=0.005)
    ax.set_aspect("equal")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    return ax


def plot_four(solution, xlim=None, ylim=None, n=300, title=None, delta=None):
    """Чотири графіки: V на тлі |V|, |V| = const, φ = const, ψ = const.

    solution — SteadySolution (лаб. №1) або Simulation (лаб. №2, поточний стан).
    """
    c = solution.contour
    v_inf = solution.v_inf
    if xlim is None or ylim is None:
        xlim, ylim = flow_box(v_inf, 1.0, 2.0 if not hasattr(solution, "fx") else 4.0, 1.2)
    X, Y = grid(xlim, ylim, n)
    if hasattr(solution, "fx"):                      # Simulation
        u, v = solution.velocity(X, Y)
        phi, psi = solution.phi(X, Y), solution.psi(X, Y)
        free = (solution.fx, solution.fy)
    else:                                            # SteadySolution
        u, v = solution.velocity(X, Y, delta)
        phi, psi = solution.phi(X, Y, delta), solution.psi(X, Y, delta)
        free = None
    speed = np.hypot(u, v)
    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    ext = (X.min(), X.max(), Y.min(), Y.max())
    s = max(1, n // 35)
    ax[0, 0].imshow(speed, extent=ext, origin="lower", cmap="Blues",
                    vmax=np.percentile(speed, 99))
    ax[0, 0].quiver(X[::s, ::s], Y[::s, ::s], (u / speed)[::s, ::s], (v / speed)[::s, ::s],
                    scale=45, width=0.002)
    ax[0, 0].set_title("1) векторне поле V на тлі |V|")
    for a, F, t, cmap in [(ax[0, 1], speed, "2) |V| = const", "Blues"),
                          (ax[1, 0], phi, "3) φ = const", "RdBu_r"),
                          (ax[1, 1], psi, "4) ψ = const", "RdBu_r")]:
        levels = np.linspace(*np.percentile(F, [1, 99]), 26)
        cs = a.contourf(X, Y, F, levels=levels, cmap=cmap, extend="both")
        a.contour(X, Y, F, levels=levels, colors="k", linewidths=0.3)
        fig.colorbar(cs, ax=a)
        a.set_title(t)
    for a in ax.flat:
        a.plot(c.x0, c.y0, "k-", lw=2)
        if free is not None:
            a.plot(*free, ".", color="0.3", ms=1)
        a.set_xlim(*xlim)
        a.set_ylim(*ylim)
        a.set_aspect("equal")
    if title:
        fig.suptitle(title)
    return fig


def plot_wake(sim, times=None, back=0.6, half=1.6):
    """Вільні вихори в кілька моментів (синій — γ < 0, червоний — γ > 0), рамка вздовж потоку."""
    if times is None:
        T = sim.t
        times = [T * f for f in (1 / 16, 1 / 4, 1 / 2, 1)]
    xlim, ylim = flow_box(sim.v_inf, back, sim.x_max, half)
    fig, axes = plt.subplots(2, 2, figsize=(13, 7.5))
    for ax, tw in zip(axes.flat, times):
        tf, _, fx, fy, fg = sim.frame_at(tw)
        ax.scatter(fx, fy, s=3, c=np.sign(fg), cmap="bwr", vmin=-1, vmax=1)
        ax.plot(sim.contour.x0, sim.contour.y0, "k-", lw=2)
        ax.set_aspect("equal")
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_title(f"t = {tf:.1f}")
    fig.suptitle("Вільні вихори: синій — γ < 0 (за год. стрілкою), червоний — γ > 0")
    return fig
