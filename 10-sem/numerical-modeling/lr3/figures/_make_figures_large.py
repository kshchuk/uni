#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate LR3 report figures on a large grid (direct Poisson = same system as SOR)."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, str(Path(ROOT)))
os.chdir(HERE)

from nb_loader import load_solver  # noqa: E402

sys.path.insert(0, ROOT)
from _bigrun import PoissonLU  # noqa: E402

ns = load_solver(Path(ROOT))
ns["PoissonDirect"] = PoissonLU  # splu: ˜˜ ˜˜˜˜ ˜˜˜˜˜˜˜, ~10x ˜˜˜˜˜˜ ˜˜ spsolve
Params = ns["Params"]
build_grid = ns["build_grid"]
p_exact = ns["p_exact"]
laplacian_h = ns["laplacian_h"]
sor_pressure = ns["sor_pressure"]
solve_ns = ns["solve_ns"]
_apply_p_neumann = ns["_apply_p_neumann"]

plt.rcParams.update({"font.size": 10, "figure.dpi": 120})

NX, NY, T_FINAL, CFL = 96, 96, 1.0, 0.25


def gauge_errors(P, Pe, mask):
    Pa = P - P[mask].mean()
    Pea = Pe - Pe[mask].mean()
    raw = float(np.max(np.abs((P - Pe)[mask])))
    aligned = float(np.max(np.abs((Pa - Pea)[mask])))
    pemax = float(np.max(np.abs(Pea[mask])))
    rel = 100.0 * aligned / pemax if pemax > 0 else float("nan")
    l2 = float(np.sqrt(np.mean((Pa - Pea)[mask] ** 2)))
    return raw, aligned, rel, l2, pemax


def run_large_solve():
    par = Params(Nx=NX, Ny=NY, T_final=T_FINAL, cfl=CFL, pressure_use_direct=True)
    times = np.linspace(0.0, T_FINAL, 21)
    print(f"Large run N={NX} T={T_FINAL} (splu Poisson) ...")
    t0 = time.time()
    res = solve_ns(par, record_times=times, verbose=True)
    print(f"  wall time {time.time()-t0:.1f}s")
    res["par"] = par

    m = np.zeros_like(res["U"], bool)
    m[:, 1:-1] = True
    hist_gauge = {"t": [], "p_align": []}
    for rec in res["records"]:
        Pe = rec["Pe"]
        _, align, _, _, _ = gauge_errors(rec["P"], Pe, m)
        hist_gauge["t"].append(rec["t"])
        hist_gauge["p_align"].append(align)
    res["hist_gauge"] = hist_gauge
    return res


def save_field_figures(res):
    X, Y = res["X"], res["Y"]
    rec = res["records"][-1]
    t_fin = rec["t"]
    U, V, P = rec["U"], rec["V"], rec["P"]
    Ue, Ve, Pe = rec["Ue"], rec["Ve"], rec["Pe"]
    step = max(1, NX // 32)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.quiver(
        X[::step, ::step], Y[::step, ::step],
        U[::step, ::step], V[::step, ::step],
        np.hypot(U, V)[::step, ::step], cmap="viridis", scale=25,
    )
    ax.set_xlabel("$x$")
    ax.set_ylabel("$y$")
    ax.set_title(f"Chyselne pole shvydkosti, $t={t_fin:.2f}$, $N={NX}$")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig("velocity_quiver.png")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8))
    for ax, data, title in zip(
        axes, [P, Pe, P - Pe],
        ["Chyselnyi $p$", "Tochnyi $p$", "Pokhybka $p$"],
    ):
        im = ax.pcolormesh(X, Y, data, shading="auto", cmap="RdBu_r")
        ax.set_title(title)
        ax.set_xlabel("$x$")
        ax.set_ylabel("$y$")
        ax.set_aspect("equal")
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle(f"Tysk, $t={t_fin:.2f}$, $N={NX}$")
    fig.tight_layout()
    fig.savefig("pressure_compare.png")
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(12, 6))
    for row, (F, Fe, name) in enumerate([(U, Ue, "u"), (V, Ve, "v")]):
        for col, (d, ttl) in enumerate(
            [(F, f"Chysl. ${name}$"), (Fe, f"Tochnyi ${name}$"), (F - Fe, f"Pokhybka ${name}$")]
        ):
            ax = axes[row, col]
            im = ax.pcolormesh(X, Y, d, shading="auto", cmap="RdBu_r")
            ax.set_title(ttl)
            ax.set_aspect("equal")
            fig.colorbar(im, ax=ax, fraction=0.046)
    fig.suptitle(f"Komponenty shvydkosti, $t={t_fin:.2f}$, $N={NX}$")
    fig.tight_layout()
    fig.savefig("velocity_compare.png")
    plt.close(fig)


def save_error_plots(res):
    eh = res["err_hist"]
    hg = res["hist_gauge"]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.semilogy(eh["t"], eh["u_linf"], "o-", label=r"$\|e_u\|_\infty$")
    ax.semilogy(eh["t"], eh["v_linf"], "s-", label=r"$\|e_v\|_\infty$")
    ax.semilogy(eh["t"], eh["p_linf"], "^-", label=r"$\|e_p\|_\infty$ (syra)")
    ax.semilogy(hg["t"], hg["p_align"], "d-", label=r"$\|e_p\|_\infty$ (kalibr.)")
    ax.set_xlabel("$t$")
    ax.set_ylabel("Norma pokhybky")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_title(f"Pokhybky vid chasu, $N={NX}$, $T={T_FINAL}$")
    fig.tight_layout()
    fig.savefig("error_vs_time.png")
    plt.close(fig)


def grid_convergence():
    print("Grid convergence (direct Poisson) ...")
    rows = []
    for N in [20, 40, 64, 96]:
        par = Params(Nx=N, Ny=N, T_final=0.5, cfl=CFL, pressure_use_direct=True)
        t0 = time.time()
        r = solve_ns(par, record_times=[0.5])
        print(f"  N={N} in {time.time()-t0:.1f}s")
        X, Y = r["X"], r["Y"]
        m = np.zeros_like(r["U"], bool)
        m[:, 1:-1] = True
        Pe = p_exact(X, Y, 0.5, par)
        raw, align, rel, l2, pemax = gauge_errors(r["P"], Pe, m)
        e = r["err_hist"]
        rows.append({
            "N": N, "h": par.h2,
            "u_linf": e["u_linf"][-1], "v_linf": e["v_linf"][-1],
            "u_l2": e["u_l2"][-1], "v_l2": e["v_l2"][-1],
            "p_raw": raw, "p_align": align, "p_rel_pct": rel, "p_l2": l2,
        })

    fig, ax = plt.subplots(figsize=(6, 4))
    hs = [r["h"] for r in rows]
    ax.loglog(hs, [r["u_linf"] for r in rows], "o-", label="$u$")
    ax.loglog(hs, [r["v_linf"] for r in rows], "s-", label="$v$")
    h_ref = np.array(hs)
    ax.loglog(h_ref, rows[0]["u_linf"] / hs[0] * h_ref, "k--", alpha=0.5, label="$O(h)$")
    ax.set_xlabel("$h$")
    ax.set_ylabel(r"$\|e\|_\infty$ pry $t=0.5$")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_title("Prostorova zbizhnist shvydkostei")
    fig.tight_layout()
    fig.savefig("spatial_convergence.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogy(hs, [r["p_align"] for r in rows], "o-", label=r"$p$ (kalibr.)")
    ax.semilogy(hs, [r["p_raw"] for r in rows], "s--", label=r"$p$ (syra)")
    ax.set_xlabel("$h$")
    ax.set_ylabel(r"$\|e_p\|_\infty$")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_title("Pokhybka tysku vs $h$")
    fig.tight_layout()
    fig.savefig("pressure_convergence.png")
    plt.close(fig)
    return rows


def sor_demo():
    print("SOR convergence demo ...")
    par = Params(Nx=40, Ny=40, omega=1.7, pressure_use_direct=False)
    X, Y = build_grid(par)
    t_sor = 0.1
    Pe = p_exact(X, Y, t_sor, par)
    _apply_p_neumann(Pe, X, t_sor, par)
    S = laplacian_h(Pe, par.h1, par.h2)
    hist = []
    P0 = np.zeros_like(Pe)
    for mx in [50, 100, 200, 400, 800]:
        par.sor_max_iter = mx
        Ps, _, _ = sor_pressure(S, P0.copy(), X, t_sor, par)
        hist.append((mx, float(np.max(np.abs(Ps - Pe)))))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([h[0] for h in hist], [h[1] for h in hist], "o-")
    ax.set_xlabel("Chyslo iteratsii SOR")
    ax.set_ylabel(r"$\|P-P_{exact}\|_\infty$")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3)
    ax.set_title("Zbizhnist SOR dlia rivniannia Poissona (10)")
    fig.tight_layout()
    fig.savefig("sor_convergence.png")
    plt.close(fig)


def save_mp4(res):
    X, Y = res["X"], res["Y"]
    step = max(1, NX // 32)
    print("Building MP4 ...")
    figv, (axv, axp) = plt.subplots(1, 2, figsize=(12, 4.5))
    pmax = max(np.max(np.abs(r["P"])) for r in res["records"])

    def update_v(k):
        axv.clear()
        axp.clear()
        r = res["records"][k]
        axv.quiver(
            X[::step, ::step], Y[::step, ::step],
            r["U"][::step, ::step], r["V"][::step, ::step],
            np.hypot(r["U"], r["V"])[::step, ::step], cmap="viridis", scale=25,
        )
        axv.set_title(f"Shvydkist, t={r['t']:.3f}")
        axv.set_aspect("equal")
        axp.pcolormesh(X, Y, r["P"], shading="auto", cmap="RdBu_r", vmin=-pmax, vmax=pmax)
        axp.set_title(f"Tysk, t={r['t']:.3f}")
        axp.set_aspect("equal")

    ani = FuncAnimation(figv, update_v, frames=len(res["records"]), interval=120)
    ani.save("ns_dynamics.mp4", writer=FFMpegWriter(fps=8, bitrate=2400))
    plt.close(figv)


def main():
    res = run_large_solve()
    save_field_figures(res)
    save_error_plots(res)
    save_mp4(res)
    sor_demo()
    grid_rows = grid_convergence()

    par = res["par"]
    eh = res["err_hist"]
    X, Y = res["X"], res["Y"]
    m = np.zeros_like(res["U"], bool)
    m[:, 1:-1] = True
    Pe = p_exact(X, Y, T_FINAL, par)
    raw, align, rel, pl2, pemax = gauge_errors(res["P"], Pe, m)

    summary = {
        "Nx": NX, "Ny": NY, "T_final": T_FINAL, "cfl": CFL,
        "u_linf": eh["u_linf"][-1], "v_linf": eh["v_linf"][-1],
        "u_l2": eh["u_l2"][-1], "v_l2": eh["v_l2"][-1],
        "p_linf_raw": raw, "p_linf_aligned": align, "p_l2_aligned": pl2,
        "p_rel_pct": rel, "p_exact_max": pemax,
        "grid_convergence": grid_rows,
    }
    with open("summary_large.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(f"Nx={NX}, Ny={NY}, T={T_FINAL}\n")
        f.write(f"u_linf={eh['u_linf'][-1]:.6e}\n")
        f.write(f"v_linf={eh['v_linf'][-1]:.6e}\n")
        f.write(f"p_linf_raw={raw:.6e}\n")
        f.write(f"p_linf_aligned={align:.6e}\n")
        f.write(f"p_rel_pct={rel:.2f}\n")
    print("summary_large.json written")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
