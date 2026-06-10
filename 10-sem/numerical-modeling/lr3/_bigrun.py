"""Large-grid / long-time LR3 run.

Uses a one-time LU factorization (splu) of the SAME discrete pressure system (10)
as PoissonDirect/SOR - mathematically identical, just fast enough for big grids.
Verifies velocity convergence and the (non-convergent) pressure artifact at scale.
"""
import warnings
warnings.filterwarnings("ignore")
import time

import numpy as np
from scipy.sparse.linalg import splu

from nb_loader import load_solver

ns = load_solver()
Params = ns["Params"]
build_grid = ns["build_grid"]
u_exact, v_exact, p_exact = ns["u_exact"], ns["v_exact"], ns["p_exact"]
divergence, laplacian_h, grad_p = ns["divergence"], ns["laplacian_h"], ns["grad_p"]
ds_diffusion_step = ns["ds_diffusion_step"]
apply_velocity_bc = ns["apply_velocity_bc"]
_apply_p_neumann = ns["_apply_p_neumann"]
p_y_bc = ns["p_y_bc"]
PoissonDirect = ns["PoissonDirect"]


class PoissonLU:
    """Same matrix as PoissonDirect, but prefactorized once with splu."""

    def __init__(self, nx, ny, h1, beta):
        self.pd = PoissonDirect(nx, ny, h1, beta)
        self.lu = splu(self.pd.A.tocsc())

    def solve(self, S, X, t, par, P_init):
        pd = self.pd
        b = np.zeros(pd.nunk)
        h2 = par.h2
        py0 = p_y_bc(0.0, X[:, 0], t, par)
        pyd = p_y_bc(par.d, X[:, 0], t, par)
        off_y = pd.b2 / pd.h1 ** 2
        for j in pd.j_vals:
            for i in range(pd.nx):
                row = pd.index[(i, j)]
                b[row] = S[i, j]
                if j == pd.j_vals[0]:
                    b[row] += off_y * h2 * py0[i]
                if j == pd.j_vals[-1]:
                    b[row] -= off_y * h2 * pyd[i]
        sol = self.lu.solve(b)
        P = P_init.copy()
        for j in pd.j_vals:
            for i in range(pd.nx):
                P[i, j] = sol[pd.index[(i, j)]]
        _apply_p_neumann(P, X, t, par)
        return P


def run(par, n_record=11, label=""):
    X, Y = build_grid(par)
    U = u_exact(X, Y, 0.0, par)
    V = v_exact(X, Y, 0.0, par)
    P = p_exact(X, Y, 0.0, par)
    _apply_p_neumann(P, X, 0.0, par)
    poisson = PoissonLU(X.shape[0], X.shape[1], par.h1, par.beta)

    n_steps = int(np.ceil(par.T_final / par.tau))
    tau = par.T_final / n_steps
    rec_t = np.linspace(0.0, par.T_final, n_record)
    rec_t = sorted(set(float(x) for x in rec_t) | {par.T_final})
    m = np.zeros_like(U, bool)
    m[:, 1:-1] = True

    def bc_u(f, tb):
        f = f.copy()
        f[:, 0] = u_exact(X[:, 0], Y[:, 0], tb, par)
        f[:, -1] = u_exact(X[:, -1], Y[:, -1], tb, par)
        return f

    def bc_v(f, tb):
        f = f.copy()
        f[:, 0] = v_exact(X[:, 0], Y[:, 0], tb, par)
        f[:, -1] = v_exact(X[:, -1], Y[:, -1], tb, par)
        return f

    hist = {"t": [], "u": [], "v": [], "p_raw": [], "p_align": []}

    def record(t):
        Ue, Ve, Pe = u_exact(X, Y, t, par), v_exact(X, Y, t, par), p_exact(X, Y, t, par)
        Pa = P - P[m].mean()
        Pea = Pe - Pe[m].mean()
        hist["t"].append(t)
        hist["u"].append(np.max(np.abs((U - Ue)[m])))
        hist["v"].append(np.max(np.abs((V - Ve)[m])))
        hist["p_raw"].append(np.max(np.abs((P - Pe)[m])))
        hist["p_align"].append(np.max(np.abs((Pa - Pea)[m])))

    t = 0.0
    next_rec = 1
    record(0.0)
    t0 = time.time()
    for step in range(n_steps):
        t_n, t_np1 = t, t + tau
        D = divergence(U, V, par.h1, par.h2)
        S = D / tau + laplacian_h(D, par.h1, par.h2) / par.Re
        P = poisson.solve(S, X, t_np1, par, P)
        px, py = grad_p(P, par.h1, par.h2)
        su = lambda tt, px=px: -px / par.rho
        sv = lambda tt, py=py: -py / par.rho
        U = ds_diffusion_step(U, tau, t_n, su, par, bc_u)
        V = ds_diffusion_step(V, tau, t_n, sv, par, bc_v)
        U, V = apply_velocity_bc(U, V, X, Y, t_np1, par)
        t = t_np1
        while next_rec < len(rec_t) and t >= rec_t[next_rec] - 1e-9:
            record(t)
            next_rec += 1
    dt = time.time() - t0

    Pe_fin = p_exact(X, Y, par.T_final, par)
    pemax = np.max(np.abs((Pe_fin - Pe_fin[m].mean())[m]))
    print(f"[{label}] N={par.Nx}x{par.Ny} T={par.T_final} steps={n_steps} "
          f"tau={tau:.2e} time={dt:.1f}s")
    print(f"    final: u={hist['u'][-1]:.4e}  v={hist['v'][-1]:.4e}  "
          f"p_raw={hist['p_raw'][-1]:.3f}  p_align={hist['p_align'][-1]:.3f} "
          f"(rel {hist['p_align'][-1] / pemax * 100:.0f}%)")
    return hist


if __name__ == "__main__":
    print("=== Long time: N=40, T=2.0 ===")
    h = run(Params(Nx=40, Ny=40, T_final=2.0, cfl=0.25, pressure_use_direct=True),
            n_record=9, label="long-time")
    for i in range(len(h["t"])):
        print(f"    t={h['t'][i]:.3f}  u={h['u'][i]:.3e}  v={h['v'][i]:.3e}  "
              f"p_align={h['p_align'][i]:.3f}")
    print()
    print("=== Big grid: N=96, N=128, T=0.5 ===")
    run(Params(Nx=96, Ny=96, T_final=0.5, cfl=0.25, pressure_use_direct=True),
        n_record=6, label="N96")
    run(Params(Nx=128, Ny=128, T_final=0.5, cfl=0.25, pressure_use_direct=True),
        n_record=6, label="N128")
