#!/usr/bin/env python3
"""Generate figures for LR3 LaTeX report and notebook."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.chdir(HERE)

from nb_loader import load_solver  # noqa: E402

_solver = load_solver(Path(ROOT))
Params = _solver["Params"]
build_grid = _solver["build_grid"]
laplacian_h = _solver["laplacian_h"]
p_exact = _solver["p_exact"]
sor_pressure = _solver["sor_pressure"]
solve_ns = _solver["solve_ns"]
_apply_p_neumann = _solver["_apply_p_neumann"]

plt.rcParams.update({"font.size": 10, "figure.dpi": 120})


def run_main():
    par = Params(Nx=40, Ny=40, T_final=0.5, cfl=0.25)  # SOR (за умовою)
    times = np.linspace(0.0, par.T_final, 25)
    method = "прямий (порівняння)" if par.pressure_use_direct else "SOR (за умовою)"
    print(f"Running NS simulation (тиск: {method}) ...")
    t0 = time.time()
    res = solve_ns(par, record_times=times)
    print(f"  done in {time.time() - t0:.1f}s; SOR iters mean={np.mean(res['sor_iters']):.0f}")
    X, Y = res["X"], res["Y"]
    rec = res["records"][-1]
    t_fin = rec["t"]
    U, V, P = rec["U"], rec["V"], rec["P"]
    Ue, Ve, Pe = rec["Ue"], rec["Ve"], rec["Pe"]

    # --- velocity quiver at T_final
    fig, ax = plt.subplots(figsize=(7, 4))
    step = 2
    ax.quiver(
        X[::step, ::step], Y[::step, ::step],
        U[::step, ::step], V[::step, ::step],
        np.hypot(U, V)[::step, ::step], cmap="viridis", scale=25,
    )
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title(f"Чисельне поле швидкості, $t={t_fin:.2f}$")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig("velocity_quiver.png")
    plt.close(fig)

    # --- pressure heatmap
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    for ax, data, title in zip(
        axes,
        [P, Pe, P - Pe],
        ["Чисельний $p$", "Точний $p$", "Похибка $p$"],
    ):
        im = ax.pcolormesh(X, Y, data, shading="auto", cmap="RdBu_r")
        ax.set_title(title)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
        ax.set_aspect("equal")
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle(f"Тиск, $t={t_fin:.2f}$")
    fig.tight_layout()
    fig.savefig("pressure_compare.png")
    plt.close(fig)

    # --- u, v compare
    fig, axes = plt.subplots(2, 3, figsize=(12, 6))
    for row, (F, Fe, name) in enumerate([(U, Ue, "u"), (V, Ve, "v")]):
        for col, (d, ttl) in enumerate(
            [(F, f"Числ. ${name}$"), (Fe, f"Точний ${name}$"), (F - Fe, f"Похибка ${name}$")]
        ):
            ax = axes[row, col]
            im = ax.pcolormesh(X, Y, d, shading="auto", cmap="RdBu_r")
            ax.set_title(ttl)
            ax.set_aspect("equal")
            fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle(f"Компоненти швидкості, $t={t_fin:.2f}$")
    fig.tight_layout()
    fig.savefig("velocity_compare.png")
    plt.close(fig)

    # --- error vs time
    eh = res["err_hist"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.semilogy(eh["t"], eh["u_linf"], "o-", label=r"$\|e_u\|_\infty$")
    ax.semilogy(eh["t"], eh["v_linf"], "s-", label=r"$\|e_v\|_\infty$")
    ax.semilogy(eh["t"], eh["p_linf"], "^-", label=r"$\|e_p\|_\infty$")
    ax.set_xlabel("$t$")
    ax.set_ylabel("Норма похибки")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_title("Похибка відносно точного розв'язку")
    fig.tight_layout()
    fig.savefig("error_vs_time.png")
    plt.close(fig)

    # --- GIF velocity
    print("Building velocity GIF ...")
    fig, ax = plt.subplots(figsize=(6, 4))

    def update(k):
        ax.clear()
        r = res["records"][k]
        u, v = r["U"], r["V"]
        ax.quiver(
            X[::step, ::step], Y[::step, ::step],
            u[::step, ::step], v[::step, ::step],
            np.hypot(u, v)[::step, ::step], cmap="viridis", scale=25,
        )
        ax.set_title(f"$t={r['t']:.3f}$")
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
        ax.set_aspect("equal")

    ani = FuncAnimation(fig, update, frames=len(res["records"]), interval=200)
    ani.save("velocity_anim.gif", writer=PillowWriter(fps=5))
    plt.close(fig)

    # --- GIF pressure
    print("Building pressure GIF ...")
    fig, ax = plt.subplots(figsize=(6, 4))
    vmin, vmax = -1.2, 1.2

    def update_p(k):
        ax.clear()
        r = res["records"][k]
        im = ax.pcolormesh(X, Y, r["P"], shading="auto", cmap="RdBu_r", vmin=vmin, vmax=vmax)
        ax.set_title(f"Тиск, $t={r['t']:.3f}$")
        ax.set_aspect("equal")
        return [im]

    ani_p = FuncAnimation(fig, update_p, frames=len(res["records"]), interval=200)
    ani_p.save("pressure_anim.gif", writer=PillowWriter(fps=5))
    plt.close(fig)

    # --- combined MP4 video (velocity + pressure)
    print("Building MP4 video ...")
    figv, (axv, axp) = plt.subplots(1, 2, figsize=(12, 4.5))
    pmax = max(np.max(np.abs(r["P"])) for r in res["records"])

    def update_v(k):
        axv.clear()
        axp.clear()
        r = res["records"][k]
        u, v, p = r["U"], r["V"], r["P"]
        axv.quiver(
            X[::step, ::step], Y[::step, ::step],
            u[::step, ::step], v[::step, ::step],
            np.hypot(u, v)[::step, ::step], cmap="viridis", scale=25,
        )
        axv.set_title(f"Поле швидкості, $t={r['t']:.3f}$")
        axv.set_xlabel("$x$"); axv.set_ylabel("$y$"); axv.set_aspect("equal")
        axp.pcolormesh(X, Y, p, shading="auto", cmap="RdBu_r", vmin=-pmax, vmax=pmax)
        axp.set_title(f"Поле тиску, $t={r['t']:.3f}$")
        axp.set_xlabel("$x$"); axp.set_ylabel("$y$"); axp.set_aspect("equal")
        return []

    ani_v = FuncAnimation(figv, update_v, frames=len(res["records"]), interval=150)
    try:
        ani_v.save("ns_dynamics.mp4", writer=FFMpegWriter(fps=8, bitrate=2400))
        print("  saved ns_dynamics.mp4")
    except Exception as exc:  # ffmpeg недоступний -> запасний gif
        print(f"  ffmpeg unavailable ({exc}); saving ns_dynamics.gif")
        ani_v.save("ns_dynamics.gif", writer=PillowWriter(fps=8))
    plt.close(figv)

    # --- SOR convergence demo
    print("SOR convergence demo ...")
    t_sor = 0.1
    Pe = p_exact(X, Y, t_sor, par)
    _apply_p_neumann(Pe, X, t_sor, par)
    S = laplacian_h(Pe, par.h1, par.h2)
    par_sor = Params(Nx=par.Nx, Ny=par.Ny, omega=1.7, sor_max_iter=800, sor_tol=1e-12,
                     pressure_use_direct=False)
    hist = []
    P = np.zeros_like(Pe)
    for mx in [50, 100, 200, 400, 800]:
        par_sor.sor_max_iter = mx
        Ps, nit, _ = sor_pressure(S, P.copy(), X, t_sor, par_sor)
        hist.append((mx, np.max(np.abs(Ps - Pe))))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([h[0] for h in hist], [h[1] for h in hist], "o-")
    ax.set_xlabel("Кількість ітерацій SOR")
    ax.set_ylabel(r"$\|P-P_{exact}\|_\infty$")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3)
    ax.set_title("Збіжність SOR для рівняння Пуассона (10)")
    fig.tight_layout()
    fig.savefig("sor_convergence.png")
    plt.close(fig)

    # --- grid convergence
    print("Grid convergence ...")
    errs = []
    for N in [20, 30, 40]:
        p2 = Params(Nx=N, Ny=N, T_final=0.2, cfl=0.2)
        r2 = solve_ns(p2, record_times=[0.2])
        e = r2["err_hist"]
        errs.append((N, e["u_linf"][-1], e["v_linf"][-1], p2.h2))

    fig, ax = plt.subplots(figsize=(6, 4))
    hs = [e[3] for e in errs]
    ax.loglog(hs, [e[1] for e in errs], "o-", label="$u$")
    ax.loglog(hs, [e[2] for e in errs], "s-", label="$v$")
    h_ref = np.array(hs)
    ax.loglog(h_ref, errs[0][1] / hs[0] * h_ref, "k--", alpha=0.5, label="$O(h)$")
    ax.set_xlabel("$h$")
    ax.set_ylabel(r"$\|e\|_\infty$ при $t=0.2$")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_title("Збіжність по просторовому кроку")
    fig.tight_layout()
    fig.savefig("spatial_convergence.png")
    plt.close(fig)

    # summary
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(f"Nx={par.Nx}, Ny={par.Ny}, T={par.T_final}\n")
        f.write(f"u_linf={eh['u_linf'][-1]:.6e}\n")
        f.write(f"v_linf={eh['v_linf'][-1]:.6e}\n")
        f.write(f"p_linf={eh['p_linf'][-1]:.6e}\n")
    print("All figures saved to", HERE)


if __name__ == "__main__":
    run_main()
