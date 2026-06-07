"""2D linearized Navier-Stokes solver (LR3).

Pressure: Poisson equation + SOR (Roache).
Velocities: DS (hopscotch) scheme adapted from LR1 heat equation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

import numpy as np


@dataclass
class Params:
    """Physical and numerical parameters."""

    rho: float = 1.0
    d: float = 1.0
    a: float = np.pi  # periodic length in x
    Re: float = 1.0
    T_final: float = 0.5
    Nx: int = 40
    Ny: int = 40
    omega: float = 1.7  # SOR relaxation
    sor_tol: float = 1e-8
    sor_max_iter: int = 5000
    cfl: float = 0.2  # tau = cfl * min(h1^2, h2^2) * Re
    pressure_use_direct: bool = True  # direct sparse for time loop; SOR for demos

    @property
    def nu(self) -> float:
        return 1.0 / self.Re

    @property
    def h1(self) -> float:
        return self.a / self.Nx

    @property
    def h2(self) -> float:
        return self.d / self.Ny

    @property
    def beta(self) -> float:
        return self.h1 / self.h2

    @property
    def tau(self) -> float:
        h_min = min(self.h1, self.h2)
        return self.cfl * h_min * h_min * self.Re


def build_grid(p: Params) -> Tuple[np.ndarray, np.ndarray]:
    x = np.linspace(0.0, p.a, p.Nx, endpoint=False)
    y = np.linspace(0.0, p.d, p.Ny + 1)
    return np.meshgrid(x, y, indexing="ij")


def u_exact(X: np.ndarray, Y: np.ndarray, t: float, p: Params) -> np.ndarray:
    d = p.d
    e = np.exp(-t) * np.exp(2.0 * Y / d)
    return -e * np.sin(2.0 * X / d)


def v_exact(X: np.ndarray, Y: np.ndarray, t: float, p: Params) -> np.ndarray:
    d = p.d
    e = np.exp(-t) * np.exp(2.0 * Y / d)
    return e * np.cos(2.0 * X / d)


def p_exact(X: np.ndarray, Y: np.ndarray, t: float, par: Params) -> np.ndarray:
    d, rho = par.d, par.rho
    return 0.5 * d * rho * np.exp(-t) * np.exp(2.0 * Y / d) * np.cos(2.0 * X / d)


def p_y_bc(y_val: float, X: np.ndarray, t: float, par: Params) -> np.ndarray:
    d, rho = par.d, par.rho
    return rho * np.exp(-t) * np.exp(2.0 * y_val / d) * np.cos(2.0 * X / d)


def ip1(i: int, nx: int) -> int:
    return (i + 1) % nx


def im1(i: int, nx: int) -> int:
    return (i - 1) % nx


def L1_x(U: np.ndarray, h1: float) -> np.ndarray:
    """Central difference dU/dx with periodic x."""
    return (np.roll(U, -1, axis=0) - np.roll(U, 1, axis=0)) / (2.0 * h1)


def L2_y(U: np.ndarray, h2: float) -> np.ndarray:
    """Central difference dU/dy (non-periodic y)."""
    out = np.zeros_like(U)
    out[:, 1:-1] = (U[:, 2:] - U[:, :-2]) / (2.0 * h2)
    return out


def laplacian_h(U: np.ndarray, h1: float, h2: float) -> np.ndarray:
    """Five-point Laplacian; periodic in x, interior in y."""
    out = np.zeros_like(U)
    out[:, 1:-1] = (
        (np.roll(U, -1, axis=0)[:, 1:-1] - 2.0 * U[:, 1:-1] + np.roll(U, 1, axis=0)[:, 1:-1]) / h1 ** 2
        + (U[:, 2:] - 2.0 * U[:, 1:-1] + U[:, :-2]) / h2 ** 2
    )
    return out


def divergence(U: np.ndarray, V: np.ndarray, h1: float, h2: float) -> np.ndarray:
    return L1_x(U, h1) + L2_y(V, h2)


def grad_p(P: np.ndarray, h1: float, h2: float) -> Tuple[np.ndarray, np.ndarray]:
    return L1_x(P, h1), L2_y(P, h2)


def apply_velocity_bc(
    U: np.ndarray,
    V: np.ndarray,
    X: np.ndarray,
    Y: np.ndarray,
    t: float,
    par: Params,
) -> Tuple[np.ndarray, np.ndarray]:
    U = U.copy()
    V = V.copy()
    U[:, 0] = u_exact(X[:, 0], Y[:, 0], t, par)
    U[:, -1] = u_exact(X[:, -1], Y[:, -1], t, par)
    V[:, 0] = v_exact(X[:, 0], Y[:, 0], t, par)
    V[:, -1] = v_exact(X[:, -1], Y[:, -1], t, par)
    return U, V


def apply_pressure_neumann_ghost(
    P: np.ndarray,
    X: np.ndarray,
    t: float,
    par: Params,
) -> np.ndarray:
    """Extend P with ghost rows for Neumann BC at y=0 and y=d."""
    nx, ny = P.shape
    Pg = np.zeros((nx, ny + 2))
    Pg[:, 1:-1] = P
    py0 = p_y_bc(0.0, X[:, 0], t, par)
    pyd = p_y_bc(par.d, X[:, 0], t, par)
    Pg[:, 0] = Pg[:, 2] - 2.0 * par.h2 * py0
    Pg[:, -1] = Pg[:, -3] + 2.0 * par.h2 * pyd
    return Pg


def _apply_p_neumann(P: np.ndarray, X: np.ndarray, t: float, par: Params) -> None:
    """In-place Neumann BC for p at y=0 and y=d (eq. 7--8).

    SOR runs on j=2..Ny-1; rows j=1 and j=Ny-1 are recovered from one-sided
    differences consistent with dp/dy = p^(0), p^(d).
    """
    h2 = par.h2
    py0 = p_y_bc(0.0, X[:, 0], t, par)
    pyd = p_y_bc(par.d, X[:, 0], t, par)
    P[:, 1] = P[:, 2] - h2 * py0
    P[:, -2] = P[:, -3] + h2 * pyd
    # ghost / boundary rows for visualization
    P[:, 0] = P[:, 1] - h2 * py0
    P[:, -1] = P[:, -2] + h2 * pyd


def sor_pressure(
    S: np.ndarray,
    P_init: np.ndarray,
    X: np.ndarray,
    t: float,
    par: Params,
) -> Tuple[np.ndarray, int, float]:
    """Solve Lap_h P = S by SOR (Roache, p.182-183)."""
    nx, ny = P_init.shape
    h1, beta = par.h1, par.beta
    omega = par.omega
    coef = omega / (2.0 * (1.0 + beta ** 2))
    b2 = beta ** 2

    P = P_init.copy()
    _apply_p_neumann(P, X, t, par)

    for it in range(par.sor_max_iter):
        max_diff = 0.0
        for j in range(2, ny - 1):
            for i in range(nx):
                im, ip = (i - 1) % nx, (i + 1) % nx
                gs = (
                    P[ip, j]
                    + P[im, j]
                    + b2 * (P[i, j + 1] + P[i, j - 1])
                    - h1 ** 2 * S[i, j]
                    - 2.0 * (1.0 + b2) * P[i, j]
                )
                new_val = P[i, j] + coef * gs
                max_diff = max(max_diff, abs(new_val - P[i, j]))
                P[i, j] = new_val
        _apply_p_neumann(P, X, t, par)

        if max_diff < par.sor_tol:
            return P, it + 1, max_diff

    return P, par.sor_max_iter, max_diff


from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve


class PoissonDirect:
    """Sparse direct solver for eq. (10) — same discrete system as SOR."""

    def __init__(self, nx: int, ny: int, h1: float, beta: float):
        self.nx, self.ny = nx, ny
        self.h1 = h1
        self.b2 = beta ** 2
        self.j_vals = list(range(2, ny - 1))
        self.nunk = nx * len(self.j_vals)
        self.index = {}
        for k, j in enumerate(self.j_vals):
            for i in range(nx):
                self.index[(i, j)] = k * nx + i

        A = lil_matrix((self.nunk, self.nunk))
        diag = -2.0 * (1.0 + self.b2) / h1 ** 2
        off_x = 1.0 / h1 ** 2
        off_y = self.b2 / h1 ** 2
        for j in self.j_vals:
            for i in range(nx):
                row = self.index[(i, j)]
                A[row, row] = diag
                A[row, self.index[((i + 1) % nx, j)]] += off_x
                A[row, self.index[((i - 1) % nx, j)]] += off_x
                if j - 1 in self.j_vals:
                    A[row, self.index[(i, j - 1)]] += off_y
                else:
                    A[row, row] += off_y  # P[i,j-1] = P[i,j] - h2*g
                if j + 1 in self.j_vals:
                    A[row, self.index[(i, j + 1)]] += off_y
                else:
                    A[row, row] += off_y  # P[i,j+1] = P[i,j] + h2*g
        self.A = csr_matrix(A)

    def solve(
        self,
        S: np.ndarray,
        X: np.ndarray,
        t: float,
        par: Params,
        P_init: np.ndarray,
    ) -> np.ndarray:
        b = np.zeros(self.nunk)
        h2 = par.h2
        py0 = p_y_bc(0.0, X[:, 0], t, par)
        pyd = p_y_bc(par.d, X[:, 0], t, par)
        off_y = self.b2 / self.h1 ** 2
        for j in self.j_vals:
            for i in range(self.nx):
                row = self.index[(i, j)]
                b[row] = S[i, j]
                if j == self.j_vals[0]:
                    b[row] += off_y * h2 * py0[i]
                if j == self.j_vals[-1]:
                    b[row] -= off_y * h2 * pyd[i]
        sol = spsolve(self.A, b)
        P = P_init.copy()
        for j in self.j_vals:
            for i in range(self.nx):
                P[i, j] = sol[self.index[(i, j)]]
        _apply_p_neumann(P, X, t, par)
        return P


def solve_pressure(
    S: np.ndarray,
    P_init: np.ndarray,
    X: np.ndarray,
    t: float,
    par: Params,
    direct: PoissonDirect | None = None,
) -> Tuple[np.ndarray, int, float]:
    """Pressure Poisson solve: SOR (assignment) or direct sparse fallback."""
    if direct is not None:
        return direct.solve(S, X, t, par, P_init), 1, 0.0
    return sor_pressure(S, P_init, X, t, par)


def neighbor_sum_4_periodic(U: np.ndarray) -> np.ndarray:
    """Sum of four neighbours (periodic in x)."""
    S = np.zeros_like(U)
    S[:, 1:-1] = (
        np.roll(U, -1, axis=0)[:, 1:-1]
        + np.roll(U, 1, axis=0)[:, 1:-1]
        + U[:, :-2]
        + U[:, 2:]
    )
    return S


def ds_diffusion_step(
    U: np.ndarray,
    tau: float,
    t_n: float,
    source_fn: Callable[[float], np.ndarray],
    par: Params,
    apply_bc: Callable[[np.ndarray, float], np.ndarray],
) -> np.ndarray:
    """DS hopscotch step for u_t = nu*Lap(u) + f — LR1 [2] structure, nu-scaled."""
    h1, h2, nu = par.h1, par.h2, par.nu
    dt2 = tau / 2.0
    t_mid = t_n + dt2
    t_np1 = t_n + tau
    # LR1 uses full-tau in CN coefficients; h_ref = min spacing for stability
    h_ref = min(h1, h2)
    h_ref2 = h_ref * h_ref
    coef_imp = 1.0 + nu * tau / h_ref2
    coef_exp = 1.0 - nu * tau / h_ref2

    U0 = apply_bc(U.copy(), t_n)
    F_n = source_fn(t_n)
    F_mid = source_fn(t_mid)
    F_np1 = source_fn(t_np1)

    nx, ny = U0.shape
    I = np.arange(nx)[:, None]
    J = np.arange(ny)[None, :]
    interior = (J > 0) & (J < ny - 1)
    white = interior & ((I + J) % 2 == 0)
    black = interior & ((I + J) % 2 == 1)

    W = U0.copy()
    Lap0 = laplacian_h(U0, h1, h2)
    W[white] = U0[white] + dt2 * (nu * Lap0[white] + F_n[white])
    W = apply_bc(W, t_mid)

    Sc = neighbor_sum_4_periodic(W)
    So = neighbor_sum_4_periodic(U0)
    rhs_b = coef_exp * U0 + (nu * tau / 4.0) * (Sc + So) / h_ref2 + (tau / 2.0) * F_mid
    W[black] = rhs_b[black] / coef_imp
    W = apply_bc(W, t_mid)

    U2 = W.copy()
    LapW = laplacian_h(W, h1, h2)
    U2[black] = W[black] + dt2 * (nu * LapW[black] + F_mid[black])
    U2 = apply_bc(U2, t_mid)

    Sc2 = neighbor_sum_4_periodic(U2)
    So2 = neighbor_sum_4_periodic(W)
    rhs_w = coef_exp * W + (nu * tau / 4.0) * (Sc2 + So2) / h_ref2 + (tau / 2.0) * F_np1
    U2[white] = rhs_w[white] / coef_imp
    return apply_bc(U2, t_np1)


def solve_ns(
    par: Params,
    record_times: np.ndarray | None = None,
    verbose: bool = False,
) -> dict:
    """Full time integration."""
    X, Y = build_grid(par)
    nx, ny = X.shape[0], X.shape[1] - 1  # Y is (nx, ny+1)

    U = u_exact(X, Y, 0.0, par)
    V = v_exact(X, Y, 0.0, par)
    P = p_exact(X, Y, 0.0, par)
    _apply_p_neumann(P, X, 0.0, par)

    poisson = PoissonDirect(X.shape[0], X.shape[1], par.h1, par.beta) if par.pressure_use_direct else None

    t = 0.0
    tau = par.tau
    n_steps = int(np.ceil(par.T_final / tau))
    tau = par.T_final / n_steps

    if record_times is None:
        record_times = np.linspace(0.0, par.T_final, 11)
    # ensure target times are sorted, unique and include the final time
    record_times = sorted(set(float(tt) for tt in record_times) | {par.T_final})

    records = []
    sor_iters = []
    err_hist = {"t": [], "u_linf": [], "v_linf": [], "p_linf": [],
                "u_l2": [], "v_l2": [], "p_l2": []}

    def record_state(t_now: float):
        ue = u_exact(X, Y, t_now, par)
        ve = v_exact(X, Y, t_now, par)
        pe = p_exact(X, Y, t_now, par)
        mask = np.zeros_like(U, dtype=bool)
        mask[:, 1:-1] = True
        eu, ev, ep = U - ue, V - ve, P - pe
        err_hist["t"].append(t_now)
        err_hist["u_linf"].append(np.max(np.abs(eu[mask])))
        err_hist["v_linf"].append(np.max(np.abs(ev[mask])))
        err_hist["p_linf"].append(np.max(np.abs(ep[mask])))
        err_hist["u_l2"].append(np.sqrt(np.mean(eu[mask] ** 2)))
        err_hist["v_l2"].append(np.sqrt(np.mean(ev[mask] ** 2)))
        err_hist["p_l2"].append(np.sqrt(np.mean(ep[mask] ** 2)))
        records.append({"t": t_now, "U": U.copy(), "V": V.copy(), "P": P.copy(),
                        "Ue": ue, "Ve": ve, "Pe": pe})

    recorded = set()
    if record_times[0] <= 1e-12:
        record_state(0.0)
        recorded.add(0)
    next_rec = 1 if (record_times and record_times[0] <= 1e-12) else 0

    def bc_u(field, t_bc):
        out = field.copy()
        out[:, 0] = u_exact(X[:, 0], Y[:, 0], t_bc, par)
        out[:, -1] = u_exact(X[:, -1], Y[:, -1], t_bc, par)
        return out

    def bc_v(field, t_bc):
        out = field.copy()
        out[:, 0] = v_exact(X[:, 0], Y[:, 0], t_bc, par)
        out[:, -1] = v_exact(X[:, -1], Y[:, -1], t_bc, par)
        return out

    for step in range(n_steps):
        t_n = t
        t_np1 = t + tau

        D = divergence(U, V, par.h1, par.h2)
        LapD = laplacian_h(D, par.h1, par.h2)
        S = D / tau + (1.0 / par.Re) * LapD

        P, nit, res = solve_pressure(S, P, X, t_np1, par, poisson)
        sor_iters.append(nit)

        px, py = grad_p(P, par.h1, par.h2)

        def src_u(tt):
            pp, _ = grad_p(P if abs(tt - t_np1) < 1e-14 else P, par.h1, par.h2)
            # pressure fixed at t_np1 during velocity substep
            return -px / par.rho

        def src_v(tt):
            _, pp = grad_p(P, par.h1, par.h2)
            return -py / par.rho

        U = ds_diffusion_step(U, tau, t_n, src_u, par, bc_u)
        V = ds_diffusion_step(V, tau, t_n, src_v, par, bc_v)
        U, V = apply_velocity_bc(U, V, X, Y, t_np1, par)

        t = t_np1

        # record any target times reached by this step
        while next_rec < len(record_times) and t >= record_times[next_rec] - 1e-9:
            record_state(t)
            recorded.add(next_rec)
            next_rec += 1

        if verbose and (step + 1) % max(1, n_steps // 10) == 0:
            print(f"  step {step+1}/{n_steps}, t={t:.4f}, SOR iters={nit}")

    if not records or records[-1]["t"] < par.T_final - 1e-9:
        record_state(t)

    return {
        "X": X, "Y": Y, "par": par,
        "records": records,
        "err_hist": err_hist,
        "sor_iters": sor_iters,
        "U": U, "V": V, "P": P,
    }


def interior_mask(shape: Tuple[int, int]) -> np.ndarray:
    m = np.zeros(shape, dtype=bool)
    m[:, 1:-1] = True
    return m
