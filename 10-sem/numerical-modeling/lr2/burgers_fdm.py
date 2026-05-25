"""1D Burgers FDM: exact solution, DS [burgers.pdf], one-step implicit sigma=0.5 [dis (2.3)] + Newton."""
from __future__ import annotations

import time
from typing import Callable, List, Tuple

import numpy as np

# --- Problem parameters 

BETA = 1.0
GAMMA = 1.0
U01 = 3.0
U02 = 1.0
C_WAVE = 0.5 * (U01 + U02)  # c = (u01+u02)/2 = 2; traveling wave moves right
L_DOM = 100.0
T_FINAL = 50.0
H = 1.0
TAU = 0.01  # reduced from 1/3 (lab nominal) — DS [1] stable at this step on the test problem


def f_profile(x: np.ndarray) -> np.ndarray:
    """Initial profile u(x,0) = u02 + (u01-u02) / (1 + exp((u01-u02)*x / (2*gamma)))."""
    arg = (U01 - U02) * np.asarray(x, dtype=float) / (2.0 * GAMMA)
    return U02 + (U01 - U02) / (1.0 + np.exp(arg))


def u_exact(x: np.ndarray, t) -> np.ndarray:
    """Analytical traveling-wave solution from the lab assignment.

    u*(x,t) = u02 + (u01-u02) / (1 + exp((u01-u02)*(x - c*t) / (2*gamma)))
    With default parameters: u*(x,t) = 1 + 2 / (1 + exp(x - 2*t)).
    ``t`` may be a scalar or array (broadcast with ``x``).
    """
    xi = np.asarray(x, dtype=float) - C_WAVE * np.asarray(t, dtype=float)
    arg = (U01 - U02) * xi / (2.0 * GAMMA)
    return U02 + (U01 - U02) / (1.0 + np.exp(arg))


def apply_bc(u: np.ndarray, x: np.ndarray, t: float) -> None:
    """In-place Dirichlet BC: boundary values from u* at the current time layer."""
    u[0] = u_exact(np.array([x[0]]), t)[0]
    u[-1] = u_exact(np.array([x[-1]]), t)[0]


def ds_step_paper(
    u_n: np.ndarray,
    n: int,
    tau: float,
    h: float,
    x: np.ndarray,
    beta: float = BETA,
    gamma: float = GAMMA,
    t_n: float = 0.0,
) -> np.ndarray:
    """DS algorithm per [1], formulas (4')--(8'): one full step n -> n+1.

    On layer t_{n+1}:
      1) nodes of one parity: semi-implicit update from layer n;
      2) opposite parity: update using neighbours already on the new layer.

    Local discretisation of
      u_t + beta*u*u_x - gamma*u_xx = 0
    with the advection/diffusion stencil as in the article (k in {0,1,2}).
    """
    u_next = u_n.copy()
    t_next = t_n + tau
    h2 = h * h

    def explicit_update(i: int) -> None:
        dx_old = (u_n[i + 1] - u_n[i - 1]) / (2.0 * h)
        dxx_old = (u_n[i + 1] - 2.0 * u_n[i] + u_n[i - 1]) / h2
        denom = 1.0 + tau * beta * dx_old
        u_next[i] = (u_n[i] + tau * gamma * dxx_old) / denom

    def implicit_update(i: int) -> None:
        dx_new = (u_next[i + 1] - u_next[i - 1]) / (2.0 * h)
        dxx_new_num = (u_next[i + 1] + u_next[i - 1]) / h2
        denom = 1.0 + tau * beta * dx_new + 2.0 * tau * gamma / h2
        u_next[i] = (u_n[i] + tau * gamma * dxx_new_num) / denom

    for i in range(1, len(u_n) - 1):
        if (i + n) % 2 == 1:
            explicit_update(i)
    apply_bc(u_next, x, t_next)

    for i in range(1, len(u_n) - 1):
        if (i + n) % 2 == 0:
            implicit_update(i)
    apply_bc(u_next, x, t_next)
    return u_next


ds_burgers_step = ds_step_paper


def thomas_tridiag_solve(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> np.ndarray:
    """Thomas algorithm for tridiagonal system; used inside Newton iterations."""
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
    """sigma=0.5 (Crank–Nicolson-type) implicit residual on interior nodes.

    Time derivative and spatial operators averaged between layers n and n+1;
    see dis.pdf eq. (2.3) with sigma = 1/2.
    """
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
    """Advance one time layer with sigma=0.5 implicit scheme + Newton + Thomas.

    Nonlinear coupling from beta*u*u_x makes each layer a tridiagonal Newton system.
    Dirichlet BC u*(x,t) enforced after each Newton correction (same as DS step).
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
            # Jacobian of the sigma=0.5 residual w.r.t. u[i], u[i±1] (tridiagonal).
            b[k] = 1.0 / tau + gamma / (h * h) - beta * 0.25 * (u[i + 1] - u[i - 1]) / h
            a[k] = -gamma / (2.0 * h * h) - beta * u_mid / (4.0 * h)
            c[k] = -gamma / (2.0 * h * h) + beta * u_mid / (4.0 * h)
            d[k] = -F[k]
        if n_in > 0:
            a[0] = 0.0   # no coupling below the first interior node
            c[-1] = 0.0  # no coupling above the last interior node
            du = thomas_tridiag_solve(a, b, c, d)
            u[1:-1] += du
        apply_bc(u, x, t_n + tau)
    return u


# Backward-compatible alias (historical name; implementation is sigma=0.5, not CN).
implicit_cn_newton_step = implicit_sigma05_newton_step


def run_solver(
    step_fn: Callable,
    tau: float,
    T_final: float,
    x: np.ndarray,
    record_every: int = 1,
) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray], int, float]:
    """Time-march from t=0 to T_final with the given single-step integrator.

    Returns final field, time history, list of recorded snapshots, step count, CPU time.
    Last step may be shortened so t never overshoots T_final.
    """
    t = 0.0
    u = u_exact(x, t).copy()
    apply_bc(u, x, t)
    hist_t = [t]
    hist_u = [u.copy()]
    nstep = 0
    t0 = time.perf_counter()
    while t < T_final - 1e-12:
        tau_eff = min(tau, T_final - t)
        # DS step needs step index n for odd/even line pattern; implicit step does not.
        if step_fn in (ds_burgers_step, ds_step_paper):
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
    """Discrete L-infinity norm ||e||_inf = max|e_i|."""
    return float(np.max(np.abs(e)))


def norm_l2(e: np.ndarray, h: float) -> float:
    """Discrete L2 norm with trapezoid/quadrature weight h: sqrt(h * sum(e_i^2))."""
    return float(np.sqrt(h * np.sum(e * e)))


def build_grid() -> Tuple[np.ndarray, int]:
    """Uniform spatial grid x in [0, L_DOM] with spacing H."""
    x = np.linspace(0.0, L_DOM, int(L_DOM / H) + 1)
    return x, len(x)
