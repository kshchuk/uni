"""Лабораторна №1 ТЧМ: стаціонарна течія навколо перешкоди методом дискретних особливостей (МДО).

Нумерація формул — за посібником Довгий, Троценко, Черній (2024), розд. 7.1.
"""
import numpy as np

TWO_PI = 2.0 * np.pi


# ---------- Крок 1. Контур ----------

def normalize(vertices):
    """Масштабує контур до характерного розміру 1 (найбільша відстань між точками) і центрує в (0, 0)."""
    P = np.asarray(vertices, float)
    diff = P[:, None, :] - P[None, :, :]
    P = P / np.sqrt((diff ** 2).sum(-1)).max()
    return P - 0.5 * (P.min(0) + P.max(0))


def resample(vertices, M):
    """M точок ω0j, майже рівномірно за довжиною дуги ламаної; кутові вершини ламаної зберігаються."""
    P = np.asarray(vertices, float)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    t = np.linspace(0.0, s[-1], M)
    for si in s[1:-1]:
        t[np.argmin(np.abs(t - si))] = si
    return np.column_stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])])


# ---------- Крок 2. Точки колокації та нормалі ----------

def collocation(P):
    """Точки колокації (між сусідніми особливостями) та одиничні нормалі в них, (7.1.2)."""
    C = 0.5 * (P[:-1] + P[1:])
    d = np.diff(P, axis=0)
    N = np.column_stack([-d[:, 1], d[:, 0]]) / np.hypot(d[:, 0], d[:, 1])[:, None]
    return C, N


# ---------- Крок 3. Швидкість від одиничного вихору ----------

def vortex_velocity(x, y, x0, y0, delta=0.0):
    """V_j з (7.1.17); при delta > 0 — регуляризований варіант (7.1.17'), (7.1.18)."""
    dx, dy = x - x0, y - y0
    R2 = np.maximum(dx * dx + dy * dy, delta * delta)
    return -dy / (TWO_PI * R2), dx / (TWO_PI * R2)


# ---------- Крок 4. СЛАР ----------

def solve_gammas(P, v_inf, gamma0):
    """Розв'язує систему (7.1.19)-(7.1.20) відносно Γ_1..Γ_M."""
    M = len(P)
    C, N = collocation(P)
    u, v = vortex_velocity(C[:, [0]], C[:, [1]], P[None, :, 0], P[None, :, 1])
    A = np.empty((M, M))
    b = np.empty(M)
    A[:-1] = N[:, [0]] * u + N[:, [1]] * v
    b[:-1] = -N @ np.asarray(v_inf, float)
    A[-1] = 1.0
    b[-1] = gamma0
    return np.linalg.solve(A, b)


# ---------- Крок 5-6. Поля на сітці ----------

def grid(n=400, lim=1.0):
    """Сітка «пікселів»: кожному пікселю (i, j) відповідає точка (x, y) у координатах задачі."""
    s = np.linspace(-lim, lim, n)
    return np.meshgrid(s, s)


def theta(x, y, x0, y0):
    """Круговий арктангенс (7.1.14): arg(z − ω0)/(2π) ∈ [0, 1)."""
    return np.mod(np.arctan2(y - y0, x - x0), TWO_PI) / TWO_PI


def velocity(X, Y, P, G, v_inf, delta):
    """Векторне поле (7.1.16')."""
    U = np.full_like(X, v_inf[0])
    V = np.full_like(X, v_inf[1])
    for (x0, y0), g in zip(P, G):
        du, dv = vortex_velocity(X, Y, x0, y0, delta)
        U += g * du
        V += g * dv
    return U, V


def phi_direct(X, Y, P, G, v_inf):
    """Потенціал за прямою формулою (7.1.13'): має розрізи-промені від кожної особливості."""
    F = X * v_inf[0] + Y * v_inf[1]
    for (x0, y0), g in zip(P, G):
        F += g * theta(X, Y, x0, y0)
    return F


def psi_direct(X, Y, P, G, v_inf, delta):
    """Функція течії (7.1.15')."""
    F = Y * v_inf[0] - X * v_inf[1]
    for (x0, y0), g in zip(P, G):
        F -= g / TWO_PI * np.log(np.maximum(np.hypot(X - x0, Y - y0), delta))
    return F


def _dipoles(P, G):
    S = np.cumsum(G)[:-1]
    mid = 0.5 * (P[:-1] + P[1:])
    d = np.diff(P, axis=0)
    return S, mid, d


def phi_transformed(X, Y, P, G, v_inf, delta):
    """Перетворений потенціал (7.1.22'): диполі + один вихор Γ0 в ω0M — один розріз замість M."""
    gamma0 = G.sum()
    F = X * v_inf[0] + Y * v_inf[1] + gamma0 * theta(X, Y, *P[-1])
    for Sj, (xj, yj), (dxj, dyj) in zip(*_dipoles(P, G)):
        R2 = np.maximum((X - xj) ** 2 + (Y - yj) ** 2, delta * delta)
        F += Sj / TWO_PI * (dyj * (X - xj) - dxj * (Y - yj)) / R2
    return F


def psi_transformed(X, Y, P, G, v_inf, delta):
    """Перетворена функція течії (7.1.23')."""
    gamma0 = G.sum()
    RM = np.maximum(np.hypot(X - P[-1, 0], Y - P[-1, 1]), delta)
    F = Y * v_inf[0] - X * v_inf[1] - gamma0 / TWO_PI * np.log(RM)
    for Sj, (xj, yj), (dxj, dyj) in zip(*_dipoles(P, G)):
        R2 = np.maximum((X - xj) ** 2 + (Y - yj) ** 2, delta * delta)
        F -= Sj / TWO_PI * (dxj * (X - xj) + dyj * (Y - yj)) / R2
    return F


# ---------- Перевірка: пластина, аналітичний розв'язок ----------

def plate_exact_velocity(X, Y, a, gamma):
    """Точна швидкість для вертикальної пластини [-ia, ia] у потоці V∞ = (1, 0) з циркуляцією gamma.

    У системі пластини z' = -iz (пластина на [-a, a], потік під кутом -π/2):
    dw/dz' = cos α − i sin α · z'/√(z'²−a²) + Γ/(2πi √(z'²−a²)).
    """
    zp = -1j * (X + 1j * Y)
    root = np.sqrt(zp - a) * np.sqrt(zp + a)
    alpha = -np.pi / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        dw = np.cos(alpha) - 1j * np.sin(alpha) * zp / root + gamma / (2j * np.pi * root)
    conj_v = -1j * dw
    return conj_v.real, -conj_v.imag
