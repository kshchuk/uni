#!/usr/bin/env python3
"""Generate figures and summary for lr2 Burgers report."""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
os.chdir(HERE)

from burgers_fdm import (  # noqa: E402
    GAMMA,
    H,
    L_DOM,
    T_FINAL,
    TAU,
    build_grid,
    ds_burgers_step,
    implicit_sigma05_newton_step,
    norm_l2,
    norm_linf,
    run_solver,
    u_exact,
)

PINN_ITERS = int(os.environ.get("PINN_ITERS", "10000"))
INVERSE_ITERS = int(os.environ.get("INVERSE_ITERS", "8000"))
PYTHON_PINN = os.environ.get("PYTHON_PINN", "/Users/user/miniconda3/bin/python")


def save_profiles(x, hist_t_ds, hist_u_ds, hist_t_im, hist_u_im, u_pinn, times_plot):
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    axes = axes.ravel()
    for ax, tp in zip(axes, times_plot):
        ue = u_exact(x, tp)
        i_ds = np.argmin(np.abs(hist_t_ds - tp))
        i_im = np.argmin(np.abs(hist_t_im - tp))
        ax.plot(x, ue, "k-", lw=2, label="точний")
        ax.plot(x, hist_u_ds[i_ds], "--", lw=1.5, label="ДС")
        ax.plot(x, hist_u_im[i_im], "-.", lw=1.5, label="неявна")
        if u_pinn is not None:
            it = int(round(tp / T_FINAL * (u_pinn.shape[1] - 1)))
            ax.plot(x, u_pinn[:, it], ":", lw=1.5, label="PINN")
        ax.set_title(f"$t={tp:g}$")
        ax.set_xlabel("$x$")
        ax.set_ylabel("$u$")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    fig.suptitle("Порівняння розв'язків $u(x)$")
    fig.tight_layout()
    fig.savefig("profiles_compare.png", dpi=150)
    plt.close(fig)


def save_heatmap(u_xt, x, t_arr, title, fname, vmin=None, vmax=None):
    fig, ax = plt.subplots(figsize=(10, 4))
    pcm = ax.pcolormesh(t_arr, x, u_xt, shading="auto", cmap="inferno", vmin=vmin, vmax=vmax)
    plt.colorbar(pcm, ax=ax, label="$u$")
    ax.set_xlabel("$t$")
    ax.set_ylabel("$x$")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(fname, dpi=150)
    plt.close(fig)


def save_surface(x, t_arr, u_xt, fname, title):
    Tg, Xg = np.meshgrid(t_arr, x)
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(Xg, Tg, u_xt, cmap="inferno", linewidth=0, antialiased=True)
    ax.set_xlabel("$x$")
    ax.set_ylabel("$t$")
    ax.set_zlabel("$u$")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(fname, dpi=150)
    plt.close(fig)


def field_from_history(x, hist_t, hist_u):
    t_arr = np.array(hist_t)
    u_xt = np.stack(hist_u, axis=1)
    return t_arr, u_xt


def save_sanity_exact(x, times, fname="sanity_exact.png"):
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    for ax, tp in zip(axes.ravel(), times):
        u = u_exact(x, tp)
        ax.plot(x, u, "b-", lw=2)
        ax.axvline(2.0 * tp, color="r", ls="--", alpha=0.6, label=r"$x=2t$ (front)")
        ax.set_ylim(0.8, 3.2)
        ax.set_title(f"$t={tp:g}$, $u(0)={u[0]:.3g}$, $u(L)={u[-1]:.3g}$")
        ax.set_xlabel("$x$")
        ax.set_ylabel("$u$")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    fig.suptitle(r"Exact solution $u^*(x,t)=1+2/(1+\exp(x-2t))$")
    fig.tight_layout()
    fig.savefig(fname, dpi=150)
    plt.close(fig)


def save_gamma_convergence(hist, gamma_true, fname="gamma_convergence.png"):
    steps = [h[0] for h in hist]
    gammas = [h[2] for h in hist]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(steps, gammas, "o-", ms=3, label=r"$\hat{\gamma}$ (зворотний PINN)")
    ax.axhline(gamma_true, color="k", ls="--", label=f"істинне $\\gamma={gamma_true:g}$")
    ax.set_xlabel("ітерація")
    ax.set_ylabel(r"$\hat{\gamma}$")
    ax.set_title("Зворотний PINN: оцінка коефіцієнта дифузії")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(fname, dpi=150)
    plt.close(fig)


def main():
    print("FDM: DS (paper) + implicit...")
    x, _ = build_grid()
    rec = max(1, int(T_FINAL / TAU) // 30)
    u_ds, t_ds, h_ds, n_ds, time_ds = run_solver(ds_burgers_step, TAU, T_FINAL, x, record_every=rec)
    u_im, t_im, h_im, n_im, time_im = run_solver(
        implicit_sigma05_newton_step, TAU, T_FINAL, x, record_every=rec
    )
    ue = u_exact(x, T_FINAL)
    print(f"DS: Linf={norm_linf(u_ds-ue):.4e} L2={norm_l2(u_ds-ue,H):.4e} steps={n_ds} t={time_ds:.2f}s")
    print(f"IM: Linf={norm_linf(u_im-ue):.4e} L2={norm_l2(u_im-ue,H):.4e} steps={n_im} t={time_im:.2f}s")

    sanity_times = [0.0, T_FINAL / 3.0, 2 * T_FINAL / 3.0, T_FINAL]
    save_sanity_exact(x, sanity_times)

    t_ds, U_ds = field_from_history(x, t_ds, h_ds)
    t_im, U_im = field_from_history(x, t_im, h_im)
    t_ex = np.linspace(0, T_FINAL, U_ds.shape[1])
    U_ex = np.stack([u_exact(x, t) for t in t_ex], axis=1)

    vmin = min(U_ex.min(), U_im.min())
    vmax = max(U_ex.max(), U_im.max(), 3.5)

    save_heatmap(U_ex, x, t_ex, "Точний розв'язок $u^*(x,t)$", "heatmap_exact.png", vmin, vmax)
    save_heatmap(U_ds, x, t_ds, "ДС-алгоритм [1]", "heatmap_ds.png", vmin, vmax)
    save_heatmap(U_im, x, t_im, "Неявна схема", "heatmap_implicit.png", vmin, vmax)
    save_surface(x, t_ex, U_ex, "surface_exact.png", "Точний розв'язок")

    Linf_ds, L2_ds, Linf_im, L2_im = [], [], [], []
    for k, tk in enumerate(t_ds):
        e_ds = h_ds[k] - u_exact(x, tk)
        e_im = h_im[min(k, len(h_im) - 1)] - u_exact(x, t_im[min(k, len(t_im) - 1)])
        Linf_ds.append(norm_linf(e_ds))
        L2_ds.append(norm_l2(e_ds, H))
        Linf_im.append(norm_linf(e_im))
        L2_im.append(norm_l2(e_im, H))

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].semilogy(t_ds, Linf_ds, label="ДС")
    ax[0].semilogy(t_im, Linf_im, label="неявна")
    ax[0].set_xlabel("$t$")
    ax[0].set_ylabel(r"$\|e\|_\infty$")
    ax[0].legend()
    ax[0].grid(True, alpha=0.3)
    ax[1].semilogy(t_ds, L2_ds, label="ДС")
    ax[1].semilogy(t_im, L2_im, label="неявна")
    ax[1].set_xlabel("$t$")
    ax[1].set_ylabel(r"$\|e\|_2$")
    ax[1].legend()
    ax[1].grid(True, alpha=0.3)
    fig.suptitle("Похибка відносно $u^*$")
    fig.tight_layout()
    fig.savefig("error_norms.png", dpi=150)
    plt.close(fig)

    u_pinn = None
    pinn_time = 0.0
    pinn_loss = None
    gamma_hat = None
    inverse_time = 0.0
    inverse_hist = None

    if os.path.isfile(os.path.join(ROOT, "burgers_pinn.py")):
        print(f"PINN forward ({PINN_ITERS} iters)...")
        import subprocess

        code_fwd = f"""
import sys, os, numpy as np
sys.path.insert(0, {repr(ROOT)})
os.chdir({repr(HERE)})
from burgers_pinn import train_pinn
from burgers_fdm import build_grid, u_exact, norm_linf, norm_l2, H, T_FINAL
elapsed, hist, ug = train_pinn(iters={PINN_ITERS}, log_every=max(500, {PINN_ITERS}//10))
u = np.asarray(ug)
np.save('pinn_field.npy', u)
np.save('pinn_hist.npy', np.array(hist))
open('pinn_meta.txt','w').write(f'{{elapsed}}\\n{{hist[-1][1]}}')
x,_=build_grid()
print('PINN Linf', norm_linf(u[:,-1]-u_exact(x,T_FINAL)))
"""
        subprocess.run([PYTHON_PINN, "-c", code_fwd], check=True, cwd=HERE)
        u_pinn = np.load(os.path.join(HERE, "pinn_field.npy"))
        pinn_meta = open(os.path.join(HERE, "pinn_meta.txt")).read().splitlines()
        pinn_time = float(pinn_meta[0])
        pinn_loss = float(pinn_meta[1])
        t_pinn = np.linspace(0, T_FINAL, u_pinn.shape[1])
        save_heatmap(u_pinn, x, t_pinn, "PINN (прямий, TF+PhiFlow)", "heatmap_pinn.png", vmin, vmax)
        save_surface(x, t_pinn, u_pinn, "surface_pinn.png", "PINN (прямий)")
        e_p = u_pinn[:, -1] - ue
        print(f"PINN forward: Linf={norm_linf(e_p):.4e} L2={norm_l2(e_p,H):.4e} loss={pinn_loss:.4e}")

        print(f"PINN inverse ({INVERSE_ITERS} iters, gamma_init=0.5)...")
        code_inv = f"""
import sys, os, numpy as np
sys.path.insert(0, {repr(ROOT)})
os.chdir({repr(HERE)})
from burgers_pinn import train_inverse_pinn, GAMMA_INIT_DEFAULT
from burgers_fdm import GAMMA
elapsed, hist, _, g = train_inverse_pinn(gamma_init=0.5, iters={INVERSE_ITERS}, log_every=max(500, {INVERSE_ITERS}//8))
np.save('inverse_hist.npy', np.array(hist, dtype=object))
open('inverse_meta.txt','w').write(f'{{elapsed}}\\n{{g}}\\n{{GAMMA}}')
print('gamma_hat', g)
"""
        subprocess.run([PYTHON_PINN, "-c", code_inv], check=True, cwd=HERE)
        inverse_meta = open(os.path.join(HERE, "inverse_meta.txt")).read().splitlines()
        inverse_time = float(inverse_meta[0])
        gamma_hat = float(inverse_meta[1])
        inverse_hist = list(np.load(os.path.join(HERE, "inverse_hist.npy"), allow_pickle=True))
        save_gamma_convergence(inverse_hist, GAMMA)
        print(f"Inverse PINN: gamma_hat={gamma_hat:.4f} (true={GAMMA})")

    times_plot = [0.0, T_FINAL / 3.0, 2 * T_FINAL / 3.0, T_FINAL]
    save_profiles(x, t_ds, h_ds, t_im, h_im, u_pinn, times_plot)

    with open("summary.txt", "w") as f:
        f.write(f"tau={TAU}\n")
        f.write(f"steps_ds={n_ds} steps_im={n_im}\n")
        f.write(f"time_ds={time_ds:.3f} time_im={time_im:.3f}\n")
        f.write(f"Linf_ds={norm_linf(u_ds-ue):.6e} L2_ds={norm_l2(u_ds-ue,H):.6e}\n")
        f.write(f"Linf_im={norm_linf(u_im-ue):.6e} L2_im={norm_l2(u_im-ue,H):.6e}\n")
        if u_pinn is not None:
            e_p = u_pinn[:, -1] - ue
            f.write(f"pinn_iters={PINN_ITERS} pinn_time={pinn_time:.3f} pinn_loss={pinn_loss:.6e}\n")
            f.write(f"Linf_pinn={norm_linf(e_p):.6e} L2_pinn={norm_l2(e_p,H):.6e}\n")
        if gamma_hat is not None:
            f.write(f"inverse_iters={INVERSE_ITERS} inverse_time={inverse_time:.3f}\n")
            f.write(f"gamma_init=0.5 gamma_hat={gamma_hat:.6f} gamma_true={GAMMA}\n")
    print("Figures saved to", HERE)


if __name__ == "__main__":
    main()
