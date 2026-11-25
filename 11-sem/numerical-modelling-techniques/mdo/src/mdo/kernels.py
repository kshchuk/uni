"""Ядра методу дискретних особливостей: швидкість від вихору, сума від багатьох вихорів, кут.

Формули: швидкість від вихору одиничної інтенсивності (7.1.17), (7.2.24)–(7.2.25) з регуляризацією
R = max(δ, r) (7.1.18), (7.2.26); круговий арктангенс θ = arg(z − ω)/2π ∈ [0, 1) (7.1.14).
"""
import numpy as np


def vortex_velocity(x, y, x0j, y0j, delta=0.0):
    """(u, v) від вихору Γ = 1 у точці (x0j, y0j) з регуляризацією R ≥ delta."""
    dx = x - x0j
    dy = y - y0j
    R2 = np.maximum(dx**2 + dy**2, delta**2)
    return -dy / (2 * np.pi * R2), dx / (2 * np.pi * R2)


def induced(x, y, xs, ys, gs, delta, chunk=4000):
    """Сумарна швидкість у точках (x, y) від вихорів (xs, ys) з інтенсивностями gs.

    x, y — масиви будь-якої форми (результат має ту саму форму); точки обробляються шматками,
    щоб таблиця «точка × вихор» не забивала пам'ять.
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    shape = x.shape
    xf, yf = x.ravel(), y.ravel()
    xs, ys, gs = (np.asarray(a, float).ravel() for a in (xs, ys, gs))
    u = np.zeros(len(xf))
    v = np.zeros(len(xf))
    if len(gs):
        for s in range(0, len(xf), chunk):
            U, V = vortex_velocity(xf[s:s + chunk, None], yf[s:s + chunk, None],
                                   xs[None, :], ys[None, :], delta)
            u[s:s + chunk] = U @ gs
            v[s:s + chunk] = V @ gs
    return u.reshape(shape), v.reshape(shape)


def theta(x, y, xs, ys):
    """Круговий арктангенс (7.1.14): arg(z − ω)/2π у межах [0, 1); розріз — вправо від ω."""
    return np.mod(np.arctan2(y - ys, x - xs), 2 * np.pi) / (2 * np.pi)
