"""1D Burgers FDM: exact solution, DS [burgers.pdf], one-step implicit sigma=0.5 [dis (2.3)] + Newton."""
from __future__ import annotations

import time
from typing import Callable, List, Tuple

import numpy as np

# Problem parameters (lr2 assignment + burgers.pdf experiment)
BETA = 1.0
GAMMA = 1.0
U01 = 3.0
U02 = 1.0
C_WAVE = 0.5 * (U01 + U02)
L_DOM = 100.0
T_FINAL = 50.0
H = 1.0
TAU = 1.0 / 3.0


def f_profile(x: np.ndarray) -> np.ndarray:
    """Steady profile f(x) from assignment."""
    return (U01 - U02) / (1.0 + np.exp(-(U01 - U02) * x / (2.0 * U01)))


def u_exact(x: np.ndarray, t: float) -> np.ndarray:
    """u*(x,t) = f(x - c*t)."""
    return f_profile(x - C_WAVE * t)


def apply_bc(u: np.ndarray, x: np.ndarray, t: float) -> None:
    u[0] = u_exact(np.array([x[0]]), t)[0]
    u[-1] = u_exact(np.array([x[-1]]), t)[0]


def burger_rhs(u: np.ndarray, i: int, h: float, beta: float, gamma: float) -> float:
    """u_t = -beta*u*u_x + gamma*u_xx at interior index i."""
    ux = (u[i + 1] - u[i - 1]) / (2.0 * h)
    uxx = (u[i + 1] - 2.0 * u[i] + u[i - 1]) / (h * h)
    return -beta * u[i] * ux + gamma * uxx


def implicit_node(
    u_old: np.ndarray,
    u_nb: np.ndarray,
    i: int,
    dt: float,
    h: float,
    beta: float,
    gamma: float,
) -> float:
    """Local implicit solve (frozen advection at u_old[i], BE diffusion)."""
    um, up = u_nb[i - 1], u_nb[i + 1]
    adv = -beta * u_old[i] * (up - um) / (2.0 * h)
    coef = 1.0 + 2.0 * dt * gamma / (h * h)
    rhs = u_old[i] + dt * adv + (dt * gamma / (h * h)) * (um + up)
    return rhs / coef


def ds_burgers_step(
    u: np.ndarray,
    n: int,
    tau: float,
    h: float,
    x: np.ndarray,
    beta: float = BETA,
    gamma: float = GAMMA,
    t_n: float = 0.0,
) -> np.ndarray:
    """Two-step symmetrized DS algorithm (4')-(7'), burgers.pdf; substep dt=tau/2."""
    dt = tau / 2.0
    u_h = u.copy()

    for i in range(1, len(u) - 1):
        if (i + n) % 2 == 1:
            u_h[i] = u[i] + dt * burger_rhs(u, i, h, beta, gamma)
    apply_bc(u_h, x, t_n + dt)

    for i in range(1, len(u) - 1):
        if (i + n) % 2 == 0:
            u_h[i] = implicit_node(u, u_h, i, dt, h, beta, gamma)
    apply_bc(u_h, x, t_n + dt)

    u_new = u_h.copy()
    for i in range(1, len(u) - 1):
        if (i + n) % 2 == 1:
            u_new[i] = u_h[i] + dt * burger_rhs(u_h, i, h, beta, gamma)
    apply_bc(u_new, x, t_n + tau)

    for i in range(1, len(u) - 1):
        if (i + n) % 2 == 0:
            u_new[i] = implicit_node(u_h, u_new, i, dt, h, beta, gamma)
    apply_bc(u_new, x, t_n + tau)
    return u_new


def thomas_tridiag_solve(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> np.ndarray:
    n = len(d)
    cp = np.zeros(n)
    dp = np.zeros(n)
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        denom = b[i] - a[i] * cp[i - 1]
        if i < n - 1:
            cp[i] = c[i] / denom
        dp[i] = (d[i] - a[i] * dp[i - 1]) / denom
    x = np.zeros(n)
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def _sigma05_residual(
    u: np.ndarray,
    u_n: np.ndarray,
    h: float,
    tau: float,
    beta: float,
    gamma: float,
) -> np.ndarray:
    """sigma=0.5 (two-layer) implicit residual on interior nodes; dis.pdf (2.3), sigma=1/2."""
    r = np.zeros(len(u))
    for i in range(1, len(u) - 1):
        u_mid = 0.5 * (u[i] + u_n[i])
        ux_mid = 0.5 * (u[i + 1] - u[i - 1] + u_n[i + 1] - u_n[i - 1]) / (2.0 * h)
        uxx_mid = 0.5 * (
            (u[i + 1] - 2 * u[i] + u[i - 1]) / (h * h)
            + (u_n[i + 1] - 2 * u_n[i] + u_n[i - 1]) / (h * h)
        )
        r[i] = (u[i] - u_n[i]) / tau + beta * u_mid * ux_mid - gamma * uxx_mid
    return r


def implicit_sigma05_newton_step(
    u_n: np.ndarray,
    tau: float,
    h: float,
    x: np.ndarray,
    beta: float = BETA,
    gamma: float = GAMMA,
    t_n: float = 0.0,
    max_iter: int = 12,
    tol: float = 1e-10,
) -> np.ndarray:
    """One-step implicit sigma-weighted scheme (sigma=0.5) on the full grid.

    Course reference: dis.pdf (2.3), burgers.pdf sec. 6 (comparison with DS).
    Nonlinear system per time layer: Newton + Thomas tridiagonal solve.
    Dirichlet BC u*(x,t) at boundaries, same as ds_burgers_step (apply_bc).
    """
    u = u_n.copy()
    apply_bc(u, x, t_n + tau)
    n_in = len(u) - 2
    a = np.zeros(n_in)
    b = np.zeros(n_in)
    c = np.zeros(n_in)

    for _ in range(max_iter):
        F = _sigma05_residual(u, u_n, h, tau, beta, gamma)[1:-1]
        if np.max(np.abs(F)) < tol:
            break
        d = np.zeros(n_in)
        for k, i in enumerate(range(1, len(u) - 1)):
            u_mid = 0.5 * (u[i] + u_n[i])
            # d/du_i of sigma=0.5 residual
            b[k] = 1.0 / tau + gamma / (h * h) - beta * 0.25 * (u[i + 1] - u[i - 1]) / h
            a[k] = -gamma / (2.0 * h * h) - beta * u_mid / (4.0 * h)
            c[k] = -gamma / (2.0 * h * h) + beta * u_mid / (4.0 * h)
            d[k] = -F[k]
        if n_in > 0:
            a[0] = 0.0
            c[-1] = 0.0
            du = thomas_tridiag_solve(a, b, c, d)
            u[1:-1] += du
        apply_bc(u, x, t_n + tau)
    return u


# Backward-compatible alias (same implementation).
implicit_cn_newton_step = implicit_sigma05_newton_step


def run_solver(
    step_fn: Callable,
    tau: float,
    T_final: float,
    x: np.ndarray,
    record_every: int = 1,
) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray], int, float]:
    t = 0.0
    u = u_exact(x, t).copy()
    apply_bc(u, x, t)
    hist_t = [t]
    hist_u = [u.copy()]
    nstep = 0
    t0 = time.perf_counter()
    while t < T_final - 1e-12:
        tau_eff = min(tau, T_final - t)
        if step_fn is ds_burgers_step:
            u = step_fn(u, nstep, tau_eff, H, x, t_n=t)
        elif step_fn in (implicit_sigma05_newton_step, implicit_cn_newton_step):
            u = step_fn(u, tau_eff, H, x, t_n=t)
        else:
            u = step_fn(u, nstep, tau_eff, H, x, t_n=t)
        t += tau_eff
        nstep += 1
        if record_every <= 1 or nstep % record_every == 0:
            hist_t.append(t)
            hist_u.append(u.copy())
    if hist_t[-1] < T_final - 1e-9:
        hist_t.append(t)
        hist_u.append(u.copy())
    return u, np.array(hist_t), hist_u, nstep, time.perf_counter() - t0


def norm_linf(e: np.ndarray) -> float:
    return float(np.max(np.abs(e)))


def norm_l2(e: np.ndarray, h: float) -> float:
    return float(np.sqrt(h * np.sum(e * e)))


def build_grid() -> Tuple[np.ndarray, int]:
    x = np.linspace(0.0, L_DOM, int(L_DOM / H) + 1)
    return x, len(x)
