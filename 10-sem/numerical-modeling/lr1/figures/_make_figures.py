#!/usr/bin/env python3
"""Generate all figures for LaTeX report from the notebook computations.

Outputs PNGs in this folder (lr1/figures/). Safe to re-run.
"""
import os
import sys
import time
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)


# ------------------------------------------------------------------ problem
a = 1.0
l1 = l2 = 1.0
T_final = 1.0
A = 1.0
x0, y0 = 0.5, 0.5
t0 = -0.1
Nx = Ny = 40
hx = l1 / Nx
hy = l2 / Ny
h = hx
x = np.linspace(0.0, l1, Nx + 1)
y = np.linspace(0.0, l2, Ny + 1)
X, Y = np.meshgrid(x, y, indexing="ij")


def w_exact(x, y, t):
    dt = np.maximum(t - t0, 1e-15)
    r2 = (x - x0) ** 2 + (y - y0) ** 2
    return (A / dt) * np.exp(-r2 / (4.0 * a * dt))


def dxx(U, h):
    L = np.zeros_like(U)
    L[1:-1, 1:-1] = (U[2:, 1:-1] - 2 * U[1:-1, 1:-1] + U[:-2, 1:-1]) / h ** 2
    return L


def dyy(U, h):
    L = np.zeros_like(U)
    L[1:-1, 1:-1] = (U[1:-1, 2:] - 2 * U[1:-1, 1:-1] + U[1:-1, :-2]) / h ** 2
    return L


def laplacian_2d(U, h):
    return dxx(U, h) + dyy(U, h)


def rhs_f(X, Y, t):
    return np.zeros_like(X)


def apply_dirichlet(U, t):
    U[0, :] = w_exact(X[0, :], Y[0, :], t)
    U[-1, :] = w_exact(X[-1, :], Y[-1, :], t)
    U[:, 0] = w_exact(X[:, 0], Y[:, 0], t)
    U[:, -1] = w_exact(X[:, -1], Y[:, -1], t)
    return U


def thomas(a_sub, b_diag, c_sup, d):
    n = len(d)
    cp = np.zeros(n)
    dp = np.zeros(n)
    cp[0] = c_sup[0] / b_diag[0]
    dp[0] = d[0] / b_diag[0]
    for i in range(1, n):
        denom = b_diag[i] - a_sub[i] * cp[i - 1]
        if i < n - 1:
            cp[i] = c_sup[i] / denom
        dp[i] = (d[i] - a_sub[i] * dp[i - 1]) / denom
    x_sol = np.zeros(n)
    x_sol[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x_sol[i] = dp[i] - cp[i] * x_sol[i + 1]
    return x_sol


def solve_implicit_x(rhs, tau_half, h, t_bc):
    r = tau_half / h ** 2
    ni, nj = rhs.shape
    out = np.zeros_like(rhs)
    apply_dirichlet(out, t_bc)
    n = ni - 2
    a_ = np.full(n, -r)
    a_[0] = 0.0
    b_ = np.full(n, 1.0 + 2.0 * r)
    c_ = np.full(n, -r)
    c_[-1] = 0.0
    for j in range(1, nj - 1):
        d_vec = rhs[1:-1, j].copy()
        d_vec[0] += r * out[0, j]
        d_vec[-1] += r * out[-1, j]
        out[1:-1, j] = thomas(a_, b_, c_, d_vec)
    apply_dirichlet(out, t_bc)
    return out


def solve_implicit_y(rhs, tau_half, h, t_bc):
    r = tau_half / h ** 2
    ni, nj = rhs.shape
    out = np.zeros_like(rhs)
    apply_dirichlet(out, t_bc)
    n = nj - 2
    a_ = np.full(n, -r)
    a_[0] = 0.0
    b_ = np.full(n, 1.0 + 2.0 * r)
    c_ = np.full(n, -r)
    c_[-1] = 0.0
    for i in range(1, ni - 1):
        d_vec = rhs[i, 1:-1].copy()
        d_vec[0] += r * out[i, 0]
        d_vec[-1] += r * out[i, -1]
        out[i, 1:-1] = thomas(a_, b_, c_, d_vec)
    apply_dirichlet(out, t_bc)
    return out


def explicit_step(U, tau, t_n):
    Un = U.copy()
    F = rhs_f(X, Y, t_n)
    Lap = laplacian_2d(Un, h)
    Un[1:-1, 1:-1] += tau * (Lap[1:-1, 1:-1] + F[1:-1, 1:-1])
    apply_dirichlet(Un, t_n + tau)
    return Un


def adi_step(U, tau, t_n):
    """Метод змінних напрямків [1, с. 237]: f на обох півкроках у t_n + τ/2."""
    Un = U.copy()
    t_half = t_n + tau / 2.0
    F_mid = rhs_f(X, Y, t_half)
    rhs_star = np.zeros_like(Un)
    rhs_star[1:-1, 1:-1] = (
        Un[1:-1, 1:-1]
        + (tau / 2.0) * dyy(Un, h)[1:-1, 1:-1]
        + (tau / 2.0) * F_mid[1:-1, 1:-1]
    )
    Wstar = solve_implicit_x(rhs_star, tau / 2.0, h, t_half)
    rhs_np1 = np.zeros_like(Wstar)
    rhs_np1[1:-1, 1:-1] = (
        Wstar[1:-1, 1:-1]
        + (tau / 2.0) * dxx(Wstar, h)[1:-1, 1:-1]
        + (tau / 2.0) * F_mid[1:-1, 1:-1]
    )
    return solve_implicit_y(rhs_np1, tau / 2.0, h, t_n + tau)


def neighbor_sum_4(U):
    """Сума чотирьох сусідів на внутрішніх вузлах (результат у внутрішньому прямокутнику)."""
    S = np.zeros_like(U)
    S[1:-1, 1:-1] = (
        U[:-2, 1:-1] + U[2:, 1:-1] + U[1:-1, :-2] + U[1:-1, 2:]
    )
    return S


def ds_checkerboard_step(U, tau, t_n):
    """ДС-алгоритм (шахівниця, σ=1/2): два півкроки τ/2 — явний на одному кольорі,
    CN-неявний на іншому [2]; коефіцієнти CN: (1±τ/h²). Крок τ як у явної схеми (CFL)."""
    dt2 = tau / 2.0
    t_mid = t_n + dt2
    t_np1 = t_n + tau
    ni, nj = U.shape
    h2 = h * h
    coef_imp = 1.0 + tau / h2
    coef_exp = 1.0 - tau / h2
    U0 = U.copy()
    F_n = rhs_f(X, Y, t_n)
    F_mid = rhs_f(X, Y, t_mid)
    F_np1 = rhs_f(X, Y, t_np1)
    W = U0.copy()
    Lap0 = laplacian_2d(U0, h)
    I = np.arange(ni)[:, None]
    J = np.arange(nj)[None, :]
    interior = (I > 0) & (I < ni - 1) & (J > 0) & (J < nj - 1)
    white = interior & ((I + J) % 2 == 0)
    black = interior & ((I + J) % 2 == 1)
    W[white] = U0[white] + dt2 * (Lap0[white] + F_n[white])
    apply_dirichlet(W, t_mid)
    Sc = neighbor_sum_4(W)
    So = neighbor_sum_4(U0)
    rhs_b = coef_exp * U0 + (tau / 4.0) * (Sc + So) / h2 + (tau / 2.0) * F_mid
    W[black] = rhs_b[black] / coef_imp
    apply_dirichlet(W, t_mid)
    U2 = W.copy()
    LapW = laplacian_2d(W, h)
    U2[black] = W[black] + dt2 * (LapW[black] + F_mid[black])
    apply_dirichlet(U2, t_mid)
    Sc2 = neighbor_sum_4(U2)
    So2 = neighbor_sum_4(W)
    rhs_w = coef_exp * W + (tau / 4.0) * (Sc2 + So2) / h2 + (tau / 2.0) * F_np1
    U2[white] = rhs_w[white] / coef_imp
    apply_dirichlet(U2, t_np1)
    return U2


def run(method_fn, tau, record_every):
    U = w_exact(X, Y, 0.0)
    apply_dirichlet(U, 0.0)
    t = 0.0
    hist_t = [0.0]
    hist_w = [U.copy()]
    step = 0
    t0c = time.perf_counter()
    while t < T_final - 1e-15:
        dt = min(tau, T_final - t)
        U = method_fn(U, dt, t)
        t += dt
        step += 1
        if step % record_every == 0:
            hist_t.append(t)
            hist_w.append(U.copy())
    elapsed = time.perf_counter() - t0c
    if hist_t[-1] < T_final - 1e-12:
        hist_t.append(T_final)
        hist_w.append(U.copy())
    return U, np.array(hist_t), hist_w, step, elapsed


def norm_l2(E):
    return float(np.sqrt(np.sum(E ** 2) * h * h))


def norm_linf(E):
    return float(np.max(np.abs(E)))


# ------------------------------------------------------------------ run
tau_expl = 0.2 * h ** 2 / a
tau_adi = h
tau_ds = tau_expl  # явний підкрок на «білих» — умова CFL τ ≤ h²/2 для півкроку τ/2

print("Running explicit...")
W_e, tE, hE, nE, timeE = run(explicit_step, tau_expl, record_every=max(1, 8000 // 80))
print("Running ADI...")
W_a, tA, hA, nA, timeA = run(adi_step, tau_adi, record_every=max(1, 40 // 40))
print("Running DS checkerboard...")
W_s, tS, hS, nS, timeS = run(ds_checkerboard_step, tau_ds, record_every=max(1, 8000 // 80))


def save_heatmap(U, title, fname, vmin=None, vmax=None, cmap="inferno"):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    pcm = ax.pcolormesh(y, x, U.T, shading="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xlabel("y")
    ax.set_ylabel("x")
    ax.set_title(title)
    fig.colorbar(pcm, ax=ax)
    fig.tight_layout()
    fig.savefig(fname, dpi=140)
    plt.close(fig)


def save_surface(U, title, fname):
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, U, cmap="viridis", edgecolor="none", alpha=0.95)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("w")
    ax.set_title(title)
    fig.colorbar(surf, shrink=0.55)
    fig.tight_layout()
    fig.savefig(fname, dpi=140)
    plt.close(fig)


# Snapshots at several times (explicit)
for tv in [0.0, 0.25, 0.5, 1.0]:
    if tv == 0.0:
        U = w_exact(X, Y, 0.0)
    else:
        idx = int(np.argmin(np.abs(tE - tv)))
        U = hE[idx]
    save_heatmap(U, f"Явна схема: w(x,y) при t={tv:.2f}", f"heatmap_explicit_t{int(tv*100):03d}.png")

# Final surfaces for all three
save_surface(W_e, "Явна схема: w(x,y) при t=1", "surface_explicit.png")
save_surface(W_a, "ADI: w(x,y) при t=1", "surface_adi.png")
save_surface(W_s, "ДС-алгоритм (шахівниця): w(x,y) при t=1", "surface_sym.png")

# Error heatmaps at t=1
for name, W, slug in [("Явна", W_e, "explicit"), ("ADI", W_a, "adi"), ("ДС", W_s, "sym")]:
    E = np.abs(W - w_exact(X, Y, T_final))
    save_heatmap(E, f"{name}: |w_num - w_exact| при t=1", f"err_{slug}.png", vmin=0,
                 vmax=np.percentile(E, 99), cmap="magma")


# Error norms over time
def norms(tarr, warr):
    Linf = []
    L2 = []
    for tk, Wk in zip(tarr, warr):
        E = np.abs(Wk - w_exact(X, Y, tk))
        Linf.append(norm_linf(E))
        L2.append(norm_l2(E))
    return np.array(Linf), np.array(L2)


LeI, LeL2 = norms(tE, hE)
LaI, LaL2 = norms(tA, hA)
LsI, LsL2 = norms(tS, hS)

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(tE, LeI, label="Явна", lw=2)
ax[0].plot(tA, LaI, label="ADI", lw=2)
ax[0].plot(tS, LsI, label="ДС [2]", lw=2, linestyle="--")
ax[0].set_xlabel("t")
ax[0].set_ylabel("||e||_inf")
ax[0].set_title("Max-норма похибки")
ax[0].legend()
ax[0].grid(True)

ax[1].semilogy(tE, LeL2, label="Явна", lw=2)
ax[1].semilogy(tA, LaL2, label="ADI", lw=2)
ax[1].semilogy(tS, LsL2, label="ДС [2]", lw=2, linestyle="--")
ax[1].set_xlabel("t")
ax[1].set_ylabel("||e||_2  (log)")
ax[1].set_title("Дискретна L2-норма похибки")
ax[1].legend()
ax[1].grid(True, which="both")
fig.tight_layout()
fig.savefig("error_norms.png", dpi=140)
plt.close(fig)


# Extension Д.2: BC experiments
def laplacian_neumann(U, h):
    nx, ny = U.shape
    G = np.empty((nx + 2, ny + 2))
    G[1:-1, 1:-1] = U
    G[0, 1:-1] = G[2, 1:-1]
    G[-1, 1:-1] = G[-3, 1:-1]
    G[1:-1, 0] = G[1:-1, 2]
    G[1:-1, -1] = G[1:-1, -3]
    G[0, 0] = G[2, 2]
    G[0, -1] = G[2, -3]
    G[-1, 0] = G[-3, 2]
    G[-1, -1] = G[-3, -3]
    L = np.zeros_like(U)
    L[1:-1, 1:-1] = (
        (G[3 : nx + 1, 2:ny] - 2 * G[2:nx, 2:ny] + G[1 : nx - 1, 2:ny])
        + (G[2:nx, 3 : ny + 1] - 2 * G[2:nx, 2:ny] + G[2:nx, 1 : ny - 1])
    ) / (h * h)
    return L


def run_bc(bc, T_end, tau):
    t = 0.0
    U = w_exact(X, Y, 0.0)
    if bc == "dirichlet_zero":
        U[0, :] = U[-1, :] = U[:, 0] = U[:, -1] = 0.0
    means = [float(np.mean(U))]
    ts = [0.0]
    while t < T_end - 1e-15:
        dt = min(tau, T_end - t)
        if bc == "dirichlet_zero":
            F = rhs_f(X, Y, t)
            U[1:-1, 1:-1] = U[1:-1, 1:-1] + dt * (laplacian_2d(U, h)[1:-1, 1:-1] + F[1:-1, 1:-1])
            U[0, :] = U[-1, :] = U[:, 0] = U[:, -1] = 0.0
        else:
            Lap = laplacian_neumann(U, h)
            U[1:-1, 1:-1] += dt * Lap[1:-1, 1:-1]
        t += dt
        ts.append(t)
        means.append(float(np.mean(U)))
    return U, ts, means


U_cold, ts_c, m_c = run_bc("dirichlet_zero", 0.5, tau_expl)
U_iso, ts_i, m_i = run_bc("neumann", 0.5, tau_expl)

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
p0 = ax[0].pcolormesh(y, x, U_cold.T, shading="auto", cmap="coolwarm")
ax[0].set_title("Охолодження: w=0 на межі (t=0.5)")
ax[0].set_xlabel("y")
ax[0].set_ylabel("x")
fig.colorbar(p0, ax=ax[0])
p1 = ax[1].pcolormesh(y, x, U_iso.T, shading="auto", cmap="inferno")
ax[1].set_title("Ізоляція: Нейман (t=0.5)")
ax[1].set_xlabel("y")
ax[1].set_ylabel("x")
fig.colorbar(p1, ax=ax[1])
fig.tight_layout()
fig.savefig("bc_experiments.png", dpi=140)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(ts_c, m_c, label="Охолодження (Дирихле = 0)", lw=2)
ax.plot(ts_i, m_i, label="Ізоляція (Нейман)", lw=2, linestyle="--")
ax.set_xlabel("t")
ax.set_ylabel("середнє w")
ax.set_title("Середня температура по області у часі")
ax.legend()
ax.grid(True)
fig.tight_layout()
fig.savefig("bc_mean.png", dpi=140)
plt.close(fig)


# ------------------------------------------------------------------ 3D
# 3D-розширення: тонка пластина із нагрівачем позаду та ізоляцією ззаду+по краях.
# Геометрія: Lx = Ly = 1, Lz = 1/50 = 0.02 (пластина-плівка).
# Нагрівач: локалізоване джерело у площині z ≈ 0 (позаду).
# ГУ: Нейман = 0 на z=0 (позаду), x=0, x=Lx, y=0, y=Ly (по краях);
#     Дирихле = 0 на z = Lz (передня поверхня, охолодження у навколишнє середовище).
# ПУ: w(x,y,z,0) = 0.

Lx3 = 1.0
Ly3 = 1.0
Lz3 = 1.0 / 50.0

Nx3 = 30
Ny3 = 30
Nz3 = 6
hx3 = Lx3 / Nx3
hy3 = Ly3 / Ny3
hz3 = Lz3 / Nz3

x3 = np.linspace(0.0, Lx3, Nx3 + 1)
y3 = np.linspace(0.0, Ly3, Ny3 + 1)
z3 = np.linspace(0.0, Lz3, Nz3 + 1)
X3, Y3, Z3 = np.meshgrid(x3, y3, z3, indexing="ij")

# Центр нагрівача
x0_h = 0.5 * Lx3
y0_h = 0.5 * Ly3

# Параметри нагрівача
Q = 1200.0             # потужність джерела (у безрозмірних одиницях)
sigma_xy = 0.15        # радіус нагрівача у площині
sigma_z = Lz3 / 6.0    # локалізація по товщині біля z=0

def heater_source(Xv, Yv, Zv):
    return Q * np.exp(
        -((Xv - x0_h) ** 2 + (Yv - y0_h) ** 2) / (2 * sigma_xy ** 2)
    ) * np.exp(-(Zv ** 2) / (2 * sigma_z ** 2))

F3 = heater_source(X3, Y3, Z3)

BIOT_FRONT = 0.35


def laplacian_3d_mixed_bc(U, hx, hy, hz, Lz_plate, biot_front):
    """Нейман на z=0 і бічних гранях; на z=Lz — Робен ∂w/∂z + (biot/Lz) w = 0
    (w — надлишок відносно кімнатної температури)."""
    nx, ny, nz = U.shape
    G = np.empty((nx + 2, ny + 2, nz + 2))
    G[1:-1, 1:-1, 1:-1] = U
    # x = 0 (Нейман): ghost = interior+1
    G[0, 1:-1, 1:-1] = G[2, 1:-1, 1:-1]
    # x = Lx (Нейман)
    G[-1, 1:-1, 1:-1] = G[-3, 1:-1, 1:-1]
    # y = 0, y = Ly (Нейман)
    G[1:-1, 0, 1:-1] = G[1:-1, 2, 1:-1]
    G[1:-1, -1, 1:-1] = G[1:-1, -3, 1:-1]
    # z = 0 (Нейман, позаду)
    G[1:-1, 1:-1, 0] = G[1:-1, 1:-1, 2]
    # z = Lz: конвекція (ghost для другого порядку по z)
    G[1:-1, 1:-1, -1] = G[1:-1, 1:-1, -3] - 2.0 * hz * (biot_front / Lz_plate) * G[1:-1, 1:-1, -2]
    L = np.zeros_like(U)
    L[:, :, :] = (
        (G[2:, 1:-1, 1:-1] - 2 * G[1:-1, 1:-1, 1:-1] + G[:-2, 1:-1, 1:-1]) / (hx * hx)
        + (G[1:-1, 2:, 1:-1] - 2 * G[1:-1, 1:-1, 1:-1] + G[1:-1, :-2, 1:-1]) / (hy * hy)
        + (G[1:-1, 1:-1, 2:] - 2 * G[1:-1, 1:-1, 1:-1] + G[1:-1, 1:-1, :-2]) / (hz * hz)
    )
    return L


# CFL-умова для неоднорідного кроку
tau3_max = 1.0 / (2.0 * a * (1.0 / hx3 ** 2 + 1.0 / hy3 ** 2 + 1.0 / hz3 ** 2))
tau3 = 0.4 * tau3_max

T3 = 0.01
U3 = np.zeros_like(X3)

t3 = 0.0
# Збережемо знімки (слабко вибірково)
snap_times = [0.0, T3 * 0.1, T3 * 0.3, T3]
snaps = {0.0: U3.copy()}

nsteps = int(np.ceil(T3 / tau3))
for step in range(nsteps):
    dt = min(tau3, T3 - t3)
    Lap = laplacian_3d_mixed_bc(U3, hx3, hy3, hz3, Lz3, BIOT_FRONT)
    U3 = U3 + dt * (Lap + F3)
    t3 += dt
    for st in snap_times:
        if st not in snaps and t3 >= st:
            snaps[st] = U3.copy()
snaps[T3] = U3.copy()

# --- Рисунок 1: Джерело тепла (перетин по z=0, ззаду)
fig, ax = plt.subplots(figsize=(6, 4.5))
pcm = ax.pcolormesh(y3, x3, F3[:, :, 0].T, shading="auto", cmap="hot")
ax.set_xlabel("y")
ax.set_ylabel("x")
ax.set_title("Інтенсивність нагрівача у площині z = 0 (позаду)")
fig.colorbar(pcm, ax=ax, label="Q(x,y,0)")
fig.tight_layout()
fig.savefig("heater_3d.png", dpi=140)
plt.close(fig)


# --- Рисунок 2: Температура на передній поверхні (z = Lz) у різні моменти часу
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
ts_to_show = [T3 * 0.1, T3 * 0.3, T3]
# Передня грань z=Lz (конвекція до кімнати; w>0 — тепліше за повітря)
for ax_i, tv in zip(axes, ts_to_show):
    Ut = snaps[tv]
    pcm = ax_i.pcolormesh(
        y3, x3, Ut[:, :, -1].T, shading="auto", cmap="inferno"
    )
    ax_i.set_xlabel("y")
    ax_i.set_ylabel("x")
    ax_i.set_title(f"надлишок w на z=Lz, t = {tv:.4f}")
    fig.colorbar(pcm, ax=ax_i)
fig.tight_layout()
fig.savefig("front_face_3d.png", dpi=140)
plt.close(fig)


# --- Рисунок 3: Перетин (y = y0) по (x, z): видно «стовп» тепла від задньої до передньої сторони
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
j0 = Ny3 // 2  # y близько до центру
# Лівий: t малий
Ut_small = snaps[ts_to_show[0]]
pcm = axes[0].pcolormesh(
    z3, x3, Ut_small[:, j0, :], shading="auto", cmap="inferno"
)
axes[0].set_xlabel("z (товщина пластини)")
axes[0].set_ylabel("x")
axes[0].set_title(f"Перетин y = y0: t = {ts_to_show[0]:.4f}")
fig.colorbar(pcm, ax=axes[0])

Ut_big = snaps[T3]
pcm = axes[1].pcolormesh(z3, x3, Ut_big[:, j0, :], shading="auto", cmap="inferno")
axes[1].set_xlabel("z (товщина пластини)")
axes[1].set_ylabel("x")
axes[1].set_title(f"Перетин y = y0: t = {T3:.4f}")
fig.colorbar(pcm, ax=axes[1])
fig.tight_layout()
fig.savefig("cross_section_3d.png", dpi=140)
plt.close(fig)


# --- Рисунок 4: Профіль температури уздовж z через центр нагрівача, у кілька моментів часу
fig, ax = plt.subplots(figsize=(7, 4.5))
i0 = Nx3 // 2
j0 = Ny3 // 2
for tv in sorted(snaps.keys()):
    ax.plot(z3, snaps[tv][i0, j0, :], label=f"t = {tv:.4f}", lw=2)
ax.set_xlabel("z")
ax.set_ylabel("w(x0, y0, z, t)")
ax.set_title("Температурний профіль уздовж товщини пластини")
ax.axvline(0, color="red", lw=1, ls="--", alpha=0.5, label="z=0 (нагрівач, ізоляція)")
ax.axvline(Lz3, color="blue", lw=1, ls="--", alpha=0.5, label="z=Lz (охолодження)")
ax.legend()
ax.grid(True)
fig.tight_layout()
fig.savefig("z_profile_3d.png", dpi=140)
plt.close(fig)


# --- Рисунок 4b: 3D-рендер пластини-паралелепіпеда з температурою на поверхнях
def render_3d_box(U, fname, title, z_scale=15.0):
    """Малюємо тонку пластину як паралелепіпед; на кожну з 6 граней
    накладаємо температурне поле на відповідному шарі сітки.
    z_scale -- коефіцієнт візуального розтягу по z, аби побачити товщину.
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    from matplotlib import cm
    from matplotlib.colors import PowerNorm

    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111, projection="3d")

    vmin = 0.0
    vmax = float(max(U.max(), 1e-12))
    norm = PowerNorm(gamma=0.55, vmin=vmin, vmax=vmax)
    cmap = cm.magma

    Xg, Yg, Zg = X3, Y3, Z3 * z_scale  # розтягнута по z сітка для візуалізації
    Lzv = Lz3 * z_scale

    # Передня грань: z = Lz, використовуємо останній k
    Zf = np.full_like(X3[:, :, 0], Lzv)
    ax.plot_surface(
        X3[:, :, 0], Y3[:, :, 0], Zf,
        facecolors=cmap(norm(U[:, :, -1])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=0.95,
    )
    # Задня грань: z = 0
    Zb = np.zeros_like(X3[:, :, 0])
    ax.plot_surface(
        X3[:, :, 0], Y3[:, :, 0], Zb,
        facecolors=cmap(norm(U[:, :, 0])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=0.95,
    )
    # Ліва грань: x = 0 (фіксуємо i=0, малюємо (y, z))
    Yl, Zl = np.meshgrid(y3, z3 * z_scale, indexing="ij")
    Xl = np.zeros_like(Yl)
    ax.plot_surface(
        Xl, Yl, Zl,
        facecolors=cmap(norm(U[0, :, :])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=0.95,
    )
    # Права грань: x = Lx
    Xr = np.full_like(Yl, Lx3)
    ax.plot_surface(
        Xr, Yl, Zl,
        facecolors=cmap(norm(U[-1, :, :])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=0.95,
    )
    # Нижня грань: y = 0 (малюємо (x, z))
    Xb, Zb2 = np.meshgrid(x3, z3 * z_scale, indexing="ij")
    Yb_ = np.zeros_like(Xb)
    ax.plot_surface(
        Xb, Yb_, Zb2,
        facecolors=cmap(norm(U[:, 0, :])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=0.95,
    )
    # Верхня грань: y = Ly
    Yt = np.full_like(Xb, Ly3)
    ax.plot_surface(
        Xb, Yt, Zb2,
        facecolors=cmap(norm(U[:, -1, :])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=0.95,
    )

    # Каркас паралелепіпеда
    corners = [
        (0, 0, 0), (Lx3, 0, 0), (Lx3, Ly3, 0), (0, Ly3, 0),
        (0, 0, Lzv), (Lx3, 0, Lzv), (Lx3, Ly3, Lzv), (0, Ly3, Lzv),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    for a_i, b_i in edges:
        xs = [corners[a_i][0], corners[b_i][0]]
        ys = [corners[a_i][1], corners[b_i][1]]
        zs = [corners[a_i][2], corners[b_i][2]]
        ax.plot(xs, ys, zs, color="black", lw=0.8)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel(f"z (×{int(z_scale)}, реальна товщина {Lz3:.3f})")
    ax.set_title(title)
    ax.set_xlim(0, Lx3)
    ax.set_ylim(0, Ly3)
    ax.set_zlim(0, Lzv)
    try:
        ax.set_box_aspect((1, 1, 0.35))
    except Exception:
        pass
    # Камера ззаду-знизу: видно задню грань z=0 (нагрівач) і низ пластини.
    # НЕ інвертуємо z: нагрівач фізично залишається позаду (z=0).
    ax.view_init(elev=-20, azim=-60)

    # colorbar
    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array([])
    fig.colorbar(mappable, ax=ax, shrink=0.55, label="w (температура, γ=0.55)")
    fig.tight_layout()
    fig.savefig(fname, dpi=140)
    plt.close(fig)


render_3d_box(
    U3,
    "box_3d.png",
    f"3D-рендер пластини (t = {T3}). Вигляд з тилу -- видно нагріту задню грань z=0",
)

# Cutaway-рендер: розтин вздовж y = y0 показує внутрішню структуру поля
def render_3d_box_cut(U, fname, title, z_scale=15.0):
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    from matplotlib import cm
    from matplotlib.colors import PowerNorm

    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    vmax = float(max(U.max(), 1e-12))
    norm = PowerNorm(gamma=0.55, vmin=0.0, vmax=vmax)
    cmap = cm.magma
    Lzv = Lz3 * z_scale
    j_cut = Ny3 // 2
    y_cut = y3[j_cut]

    # Задня (нагріта) грань z=0 -- повністю
    Zb = np.zeros_like(X3[:, :, 0])
    ax.plot_surface(
        X3[:, :, 0], Y3[:, :, 0], Zb,
        facecolors=cmap(norm(U[:, :, 0])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=1.0,
    )
    # Передня (холодна) грань -- лише «дальша» половина (y > y_cut)
    Xf = X3[:, j_cut:, 0]
    Yf = Y3[:, j_cut:, 0]
    Zf = np.full_like(Xf, Lzv)
    ax.plot_surface(
        Xf, Yf, Zf,
        facecolors=cmap(norm(U[:, j_cut:, -1])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=1.0,
    )
    # Ліва/права грані -- лише дальша половина
    Yl, Zl = np.meshgrid(y3[j_cut:], z3 * z_scale, indexing="ij")
    Xl = np.zeros_like(Yl)
    ax.plot_surface(
        Xl, Yl, Zl, facecolors=cmap(norm(U[0, j_cut:, :])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=1.0,
    )
    Xr = np.full_like(Yl, Lx3)
    ax.plot_surface(
        Xr, Yl, Zl, facecolors=cmap(norm(U[-1, j_cut:, :])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=1.0,
    )
    # Дальша грань y = Ly
    Xb, Zb2 = np.meshgrid(x3, z3 * z_scale, indexing="ij")
    Yt = np.full_like(Xb, Ly3)
    ax.plot_surface(
        Xb, Yt, Zb2, facecolors=cmap(norm(U[:, -1, :])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=1.0,
    )
    # Внутрішня площина розтину y = y_cut (видно внутрішній розподіл)
    Yc = np.full_like(Xb, y_cut)
    ax.plot_surface(
        Xb, Yc, Zb2, facecolors=cmap(norm(U[:, j_cut, :])),
        rstride=1, cstride=1, antialiased=False, shade=False, alpha=1.0,
    )

    # Каркас паралелепіпеда (контур)
    corners = [
        (0, 0, 0), (Lx3, 0, 0), (Lx3, Ly3, 0), (0, Ly3, 0),
        (0, 0, Lzv), (Lx3, 0, Lzv), (Lx3, Ly3, Lzv), (0, Ly3, Lzv),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    for a_i, b_i in edges:
        xs = [corners[a_i][0], corners[b_i][0]]
        ys = [corners[a_i][1], corners[b_i][1]]
        zs = [corners[a_i][2], corners[b_i][2]]
        ax.plot(xs, ys, zs, color="black", lw=0.9)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel(f"z (×{int(z_scale)}, реальна товщина {Lz3:.3f})")
    ax.set_title(title)
    ax.set_xlim(0, Lx3)
    ax.set_ylim(0, Ly3)
    ax.set_zlim(0, Lzv)
    try:
        ax.set_box_aspect((1, 1, 0.35))
    except Exception:
        pass
    # Камера згори-спереду: видно холодну передню грань та внутрішній розтин,
    # нагрівач залишається позаду (z=0, «дно» пластини).
    ax.view_init(elev=22, azim=-55)

    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array([])
    fig.colorbar(mappable, ax=ax, shrink=0.55, label="w (γ=0.55)")
    fig.tight_layout()
    fig.savefig(fname, dpi=140)
    plt.close(fig)


render_3d_box_cut(
    U3,
    "box_3d_cut.png",
    f"Розтин пластини: 3D-вигляд з внутрішньою площиною y = y0, t = {T3}",
)


# --- Рисунок 5: Повна «енергія» (інтеграл w по об'єму) у часі
energy_ts = []
energy_vals = []
U3e = np.zeros_like(X3)
t_e = 0.0
energy_ts.append(0.0)
energy_vals.append(0.0)
rec_every = max(1, nsteps // 120)
for step in range(nsteps):
    dt = min(tau3, T3 - t_e)
    Lap = laplacian_3d_mixed_bc(U3e, hx3, hy3, hz3, Lz3, BIOT_FRONT)
    U3e = U3e + dt * (Lap + F3)
    t_e += dt
    if (step + 1) % rec_every == 0:
        energy_ts.append(t_e)
        energy_vals.append(float(np.sum(U3e) * hx3 * hy3 * hz3))

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(energy_ts, energy_vals, lw=2)
ax.set_xlabel("t")
ax.set_ylabel("∫∫∫ w dx dy dz")
ax.set_title("Загальна теплова енергія пластини у часі")
ax.grid(True)
fig.tight_layout()
fig.savefig("energy_3d.png", dpi=140)
plt.close(fig)


# Summary numbers for report
with open("summary.txt", "w", encoding="utf-8") as f:
    f.write(f"tau_explicit = {tau_expl:.6e}\n")
    f.write(f"tau_adi = {tau_adi:.6e}\n")
    f.write(f"tau_ds = {tau_ds:.6e}\n")
    f.write(f"steps: explicit={nE}, ADI={nA}, ds={nS}\n")
    f.write(f"time: explicit={timeE:.3f}, ADI={timeA:.3f}, ds={timeS:.3f}\n")
    f.write(f"Linf@t=1: explicit={norm_linf(W_e - w_exact(X,Y,T_final)):.3e}, "
            f"ADI={norm_linf(W_a - w_exact(X,Y,T_final)):.3e}, "
            f"ds={norm_linf(W_s - w_exact(X,Y,T_final)):.3e}\n")
    f.write(f"L2@t=1:   explicit={norm_l2(W_e - w_exact(X,Y,T_final)):.3e}, "
            f"ADI={norm_l2(W_a - w_exact(X,Y,T_final)):.3e}, "
            f"ds={norm_l2(W_s - w_exact(X,Y,T_final)):.3e}\n")
    f.write(
        f"3D setup: Lx=Ly={Lx3}, Lz={Lz3:.4f} (={Lz3*50:.1f}/50 of side); "
        f"Nx=Ny={Nx3}, Nz={Nz3}; tau={tau3:.3e}, steps={nsteps}; T={T3}\n"
    )
    f.write(
        f"3D: max w = {U3.max():.3e}, max w на передній грані z=Lz = "
        f"{U3[:, :, -1].max():.3e} (Робен до Т_кімн)\n"
    )

print("Figures written to", HERE)
